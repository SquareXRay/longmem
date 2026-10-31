# 06 · Governance: decision ledger, inbox, and mechanical gates

## Why a ledger

The most expensive thing in a long session is not compute — it is **the same trade-off being
discussed five times**. The decision ledger is the single source of truth for "what has already
been decided".

Entry format (one line):

```
N. **question** | A: option (recommended) | B: option
```

Write the verdict and the date as soon as it is decided; **close the entry** as soon as the work is
done, with evidence (commit / report path). Anything left in the ledger must be something a human
really has to handle — finished work leaves no residue. Split files by owner (main session / each
sub-session / scheduled jobs); the shared file holds only unowned items.

**中文**

长会话里最贵的东西不是算力，是**同一个取舍被讨论五遍**。决策台账是「已经定了什么」的唯一真相源。

条目格式（一行，代码块同上）：`N. **问题** | A: 选项（推荐） | B: 选项`

拍板当下就写结论和日期；活做完当下就**销账**，并附证据（commit / 报告路径）。台账里留下的每一件事，都必须是真需要人处理的 —— 做完的事不留残渣。按归属分文件（主会话 / 各子会话 / 定时任务）；共享文件只放无主条目。

## Pending-decision inbox

Unattended work (background jobs, scheduled tasks) that hits an authorization or credential
question writes an inbox entry and suspends; only read-only work may continue. **Unattended does
not mean more autonomy.**

**中文**

无人值守的活（后台任务、定时任务）撞到授权或凭证问题，就写一条收件箱条目并挂起；只允许只读的活继续。**无人值守不等于更高自主度。**

## Retention: export first, then delete

Deleting old rows is the only irreversible thing in housekeeping, so the delete is gated on a
verified export:

- each table is exported **per month** to `jsonl.zst`, next to a `.sha256` sidecar and a manifest
  (row count, byte count, time range, source database, sqlite and zstd versions, predicate used);
- **idempotent by verification**: an existing file is reused only when its manifest, checksum and
  decompressed row count all re-verify; a second run in the same month writes a **separate shard**
  — overwriting would destroy rows that were already deleted;
- **fail-closed**: zstd missing, write failure, checksum mismatch or row-count mismatch means
  **zero rows deleted** and a non-zero exit;
- deleting requires the explicit apply flag, and is refused while the gateway is running;
- what is deleted is compared with what was exported, and the archive itself expires after 30 days.

Two retention clocks, not one: **transcript and trajectory 7 days** (it was 14), **audit events
14 days**. One number would either keep debugging traces too long or lose the audit trail too early;
the split is stated per table because that is where it is enforced.

**中文**

巡检里唯一不可逆的动作就是删旧行，所以删除必须以一次**已校验的导出**为前提：

- 每张表**按月**导出成 `jsonl.zst`，旁边配 `.sha256` 与 manifest（行数、字节数、时间范围、源库、sqlite 与 zstd 版本、所用 predicate）；
- **靠校验幂等**：只有 manifest、校验和与解压后的行数三者复核一致才复用旧文件；同月第二次运行写**独立分片** —— 覆盖会销毁已经被删掉的行；
- **fail-closed**：zstd 缺失、写盘失败、校验不一致或行数不符，都意味着**一行都不删**并非零退出；
- 删除需要显式 apply 开关，且网关运行中拒绝执行；
- 删除行数与导出行数比对通过才继续；归档自身 30 天后过期。

保留期是**两套口径，不是一个数**：**transcript 与 trajectory 7 天**（原为 14），**audit events 14 天**。用一个数要么把调试痕迹留太久，要么把审计线索删太早；口径按表分开写，因为执行点就在表上。

## The ledger ages in shards

The decision ledger is not exempt from retention. Terminal entries leave the hot file after a
**default of 14 days**, with carrier-specific overrides that may only **shorten** it — scheduled
(automation) and exec carriers go after **1 day**, because they are the bulk of the volume and age
fastest. Entries still referenced by a live entry are skipped. Moves go to a dated archive volume
with a backup and a **tombstone index**, so an archived id can never be reused by accident, and a
scheduled GC job drives the whole pass — dry-run first, with counts broken down per carrier.

**中文**

决策台账同样有保留期。终态条目**默认 14 天**后离开热文件；按 carrier 的覆盖**只允许缩短** —— 定时任务（automation）与 exec 类是条数大头、复盘价值衰减最快，**1 天**即可。仍被活跃条目引用的不迁。迁出写进带日期的归档卷，先备份，并维护**墓碑索引**，归档 id 永远不会被无意复用；整轮由定时 GC 任务驱动 —— 先 dry-run，输出按 carrier 分类的条数。

## One writer path, and no RPC inside its lock

Ledger writes serialize on an exclusive file lock with a **5-second watchdog**. A cross-process
call to the card system inside that lock pushes the critical section past the watchdog: the watchdog
then fails the write while the call still completes, leaving a half-applied change. So the order is
fixed: **prepare (RPC) outside, lock, write, release**. A card RPC attempted while the lock is held
is rejected outright, and a guard test asserts the rejection. The lock file is not a general-purpose
mutex either — reusing it under another name is blocked by a per-file allowlist.

**中文**

台账写入串行在一把独占文件锁上，锁带 **5 秒看门狗**。在锁内发跨进程调用到卡片系统，会把临界区顶过看门狗：看门狗随后把这次写判失败，而调用其实已经完成 —— 留下一个半应用的改动。所以顺序是固定的：**RPC 在外准备，取锁，写，放锁**。持锁期间尝试卡片 RPC 会被直接拒绝，有守卫用例断言这一点。锁文件也不是通用互斥量 —— 换个名字复用它会被逐文件白名单拦下。

## The card is a projection of the ledger

A card is a projection, not a second state machine. The ledger's state vocabulary is the single
source, and the mapping from ledger state to board state is one function shared by every projector.
Projection is triggered by the **release of the write lock**, not by each caller remembering to call
it; a failed projection is logged and left for the worker to replay, never silently dropped and
never allowed to fail the ledger write. Projection is idempotent: a card already at the target state
is a no-op, and a missing card is recorded and skipped — never auto-created. `cancelled` maps to
**archived**, not done; otherwise the vocabulary says "released" while the board says "completed".

**中文**

卡片是台账的投影，不是第二个状态机。台账的状态词表是唯一来源，台账状态到工作板状态的映射只有一个函数，所有投影方共用。投影由**写锁释放**触发，而不是靠每个调用方记得去调；投影失败会落日志留给 worker 重放，绝不静默丢弃，也绝不允许反过来把台账写入判失败。投影是幂等的：卡已在目标态即 no-op，卡不存在只记一笔并跳过 —— 绝不自动建卡。`cancelled` 映射为**归档**而不是完成，否则词表说「已释放」、工作板说「已完成」，两套答案。

## Nightly curation

Runs with sessions stopped, and performs mechanical actions only:

- rebuild the daily file index (do not write when the content is unchanged);
- warn on size or entry-count limits;
- count same-type incidents, and tag the ones over the threshold;
- prune expired todos and already-closed entries.

Never do things like "let a model rewrite memory" — an irreversible cleanup is a destruction.

**中文**

在会话停止时运行，只做机械动作：

- 重建每日文件索引（内容没变就不写）；
- 对大小或条目数超限告警；
- 统计同型事故，把超过阈值的打上标记；
- 清理过期的 todo 与已经关闭的条目。

绝不做「让模型重写记忆」这类事 —— 不可逆的清理就是销毁。

## Mechanical gates, not "remember to comply"

Write discipline as prose and the model will forget it sooner or later. Therefore:

| Discipline | Mechanism |
|---|---|
| no whole-file writes on shared files | protected paths at the hook layer, fail-closed |
| config changes may only tighten | pre-write validation + allowlist |
| restricted commit scope | pre-commit file-set check |
| repeat incidents must escalate | counters + a periodic scan |
| duplicate hints must never merge on their own | advisory path: prints candidates, writes nothing |

**Unknown cases resolve to the stricter branch** (fail-closed) — never "looks fine, let it pass".

But not every signal belongs in a gate. "This looks like the same incident", "these two entries
probably share a root cause" — those must stay **advisory**: printed, logged, and never allowed to
change state. Promoting a hint into an admission gate destroys the ledger's value, because the
writer then starts failing on judgement calls. The mirror rule holds for housekeeping limits (hot
size, open-entry count): they evict or warn, and the write still succeeds. A gate you cannot afford
to be wrong about is not a gate, it is an outage waiting for a false positive.

**中文**

把写入纪律写成正文，模型迟早会忘。因此：

| 纪律 | 机制 |
|---|---|
| 共享文件禁止整文件写入 | hook 层的保护路径，fail-closed |
| 配置改动只能收紧 | 写前校验 + 白名单 |
| 提交范围受限 | pre-commit 文件集检查 |
| 重复事故必须升级 | 计数器 + 定期扫描 |
| 重复提示绝不自动归并 | advisory 通道：只打印候选，不写任何东西 |

**未知情况一律落到更严的那一支**（fail-closed）—— 绝不「看着没问题，放它过」。

但并不是每个信号都该做成闸。「这看着像同一起事故」「这两条大概同一个根因」这类必须留在 **advisory**：只打印、只落日志，绝不允许改状态。把提示提升成准入闸会毁掉台账的价值 —— 写入者从此开始因为判断题而失败。整理类上限（热层体积、未结条数）同理：它们只驱逐或告警，写入照样成功。一个「错不起」的闸不是闸，是一次等着假阳来触发的宕机。

## Every gate needs dual probes before shipping

1. **True positive must be blocked**: build a sample that should be blocked, confirm exit ≠ 0.
2. **False positive must pass**: prose mentions, values inside arguments, non-writing tool calls —
   confirm they go through.

Missing either side means half-verified, and it must not ship. When fixing a false positive, never
turn the gate into fail-open along the way.

**中文**

1. **真阳必须被拦**：构造一个本该被拦的样例，确认 exit ≠ 0。
2. **假阳必须放行**：正文提及、参数里的值、非写类工具调用 —— 确认它们能过。

缺任何一侧都算半验证，不许上线。修假阳的时候，绝不能顺手把闸改成 fail-open。

## Throttling periodic checks

Merge similar checks, stretch the intervals, and slow down or stop after three consecutive runs
with no change. Runaway scheduled work usually costs more than it returns.

**中文**

同类检查合并、拉长间隔，连续三次无变化就降频或停。失控的定时任务通常花的比挣的多。
