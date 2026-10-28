# 04 · The incident ledger: from "it bit me" to "it never bites again"

## Entry format (one line each)

```
id | date | symptom | root cause | prevention | type
```

- **Symptom**: the observable error / hang / timeout, quoted — not summarized as "it failed".
- **Root cause**: a mechanism-level explanation. If you cannot write the cause, you have not
  finished diagnosing, and the entry does not belong here yet.
- **Prevention**: the concrete next action (different command / extra flag / check X first), not
  "be careful".
- **Type**: tool / process / environment / design — used to detect repeats.

**中文**

条目格式（代码块同上）：`编号 | 日期 | 现象 | 根因 | 预防 | 类型`。

- **现象**：可观察的错误 / 挂死 / 超时，原样引用 —— 不是概括成「它失败了」。
- **根因**：机制层面的解释。写不出根因，说明你还没诊断完，这条还不该入库。
- **预防**：具体的下一个动作（换命令 / 加参数 / 先检查 X），不是「小心点」。
- **类型**：工具 / 流程 / 环境 / 设计 —— 用于识别重复。

## Hot and cold tiers

Keep the last 30 days hot, at most 60 KB (or 120 entries); anything untouched for 45 days moves
out regardless of its state, and older entries roll into monthly volumes at 36 KB per volume. Cold
volumes keep only an index (id + one sentence + volume number), and you locate an entry by id when
you need to go back. This stops the ledger from turning into a context bomb on its own.

The hot layer also carries a **work-in-progress cap of 60 open entries**, and the cap never refuses
a write: past the limit the writer evicts exactly one entry — the oldest with no hits and no
enforced route — to the cold layer and logs the eviction. With no qualifying entry it records a
warning and the write still succeeds. The cap is housekeeping, not an admission gate.

**Index contract**: a cold index may carry a volume table plus an entry-level map, with the same
36 KB cap as a single volume. The entry-level map is what keeps id lookup O(1) — do not flatten it
into a pure volume table for the sake of tidiness, or lookup degrades into grepping across five
volumes.

**The volume-rebuild script is production code**, and must satisfy four requirements:

1. Identify the index by **structure** (a volume table: filename in the first column plus id range
   / entry count / byte count), never by "does the file contain a line like `1. `" — an
   entry-level map looks exactly like entries and gets re-parsed as body text;
2. **Back up everything** before writing (hot file, index, every volume, the counter); abort if any
   copy fails;
3. **Arithmetic self-check** before writing: the parsed entry total must equal the sum of the
   per-volume counts, otherwise refuse to write;
4. dry-run and the real run must share the same decision path, so "the volumes and counts you see"
   are "the ones that will be written".

(These four came out of a real incident: a rebuild parsed its own index as body text and reported
3 volumes / 115 entries when the truth was 5 volumes / 155 entries; and the backup list had missed
volumes that are not named by year-month, such as `-unknown`.)

The repair path is a **rebuild-from-disk mode** of the same script, and it follows the same four
rules: recompute the volume table from the files that are actually on disk, dry-run by default, back
up before applying, self-check the arithmetic, stay idempotent — and rewrite only the index, never
an entry body. A later drift where the table said 155 entries while the disk held 159 was closed by
that mode alone; no body text moved.

**中文**

最近 30 天留在热层，最多 60 KB（或 120 条）；未触碰满 45 天的条目不论状态一律迁出，更早的条目按月分卷滚进冷层，每卷 36 KB。冷卷只保留索引（编号 + 一句话 + 卷号），需要回溯时按编号定位。这样错题本才不会自己变成上下文炸弹。

热层另有**未结条目上限 60 条**，而上限**永不拒写**：超过后写入者只驱逐一条 —— 最旧且无命中、无强制落点的条目 —— 迁到冷层并留一行驱逐记录；没有合格对象就记一条告警，写入照样成功。上限是整理信号，不是准入闸。

上面那四条规则的修复路径是同一脚本的**按盘重建模式**：按磁盘上真实存在的文件重算卷表、默认 dry-run、写入前备份、算术自检、幂等，并且只重写索引、绝不碰条目正文。后来一次「卷表写 155、磁盘实为 159」的漂移，就是靠这个模式单独修掉的，正文一个字没动。

**索引契约**：冷层索引可以带一张卷表加一份条目级映射，与单卷同一个 36 KB 上限。条目级映射是编号查找保持 O(1) 的依赖 —— 不要为了「干净」把它压成纯卷表，否则查找会退化成在五个卷里 grep。

**分卷重建脚本是生产代码**，必须满足四条要求：

1. 按**结构**识别索引（一张卷表：第一列是文件名，加编号区间 / 条目数 / 字节数），绝不按「文件里有没有 `1. ` 这样的行」判断 —— 条目级映射看起来和条目一模一样，会被当成正文重新解析；
2. 写入前**全量备份**（热文件、索引、每一个卷、计数器）；任何一份拷贝失败就中止；
3. 写入前做**算术自检**：解析出的条目总数必须等于各卷计数之和，否则拒绝写入；
4. dry-run 与真跑必须共用同一条判定路径，这样「你看到的卷和计数」就是「将要写下去的卷和计数」。

（这四条出自一次真实事故：某次重建把自己的索引当成正文解析，报了 3 卷 / 115 条，而真相是 5 卷 / 155 条；备份清单还漏掉了不以年月命名的卷，例如 `-unknown`。）

## Operation semantics (borrowed from memory systems: ADD / UPDATE / NOOP)

| Operation | Trigger |
|---|---|
| ADD | a new type, or a new root cause |
| UPDATE | the type already exists — add the new symptom or fix the prevention (keep the original, mark the update) |
| NOOP | same type and same prevention — only bump the timestamp / counter |

The counter matters: **the counter is the escalation signal.**

The counter has two forms, and both are required:

- **×N within one entry** (the same type repeating),
- **the same root cause across entries** — three open entries each at ×1 that share one root cause
  are still at "second occurrence of the same type" or worse. Mechanical test: normalize each
  symptom (fold case, strip whitespace and version numbers) and score character-bigram Jaccard
  similarity; ≥ 0.25 is the primary line, ≥ 0.22 the watch line, both calibrated on a real ledger
  (208 entries: 12 pairs at ≥ 0.25, 20 at ≥ 0.22, fixture precision 1.00). Two or more connected
  entries form a group. Report only, never block: print one warning line with the candidate id,
  never change state, never escalate automatically.

**中文**

| 操作 | 触发 |
|---|---|
| ADD | 一个新类型，或一个新根因 |
| UPDATE | 类型已存在 —— 补上新的现象，或修正预防（保留原来的，标出这次更新） |
| NOOP | 同类型且同预防 —— 只更新时间戳 / 计数器 |

计数器很重要：**计数器就是升级信号。**

计数器有两种形态，两种都必须有：

- **条目内 ×N**（同一类型反复发生），
- **跨条目的同一根因** —— 三条各为 ×1 的未销账条目共享一个根因，那仍然是「同型第 2 次」或更糟。机械判据：把每条现象归一化（大小写折叠、去空白与版本号）后算字符 bigram 的 Jaccard 相似度；≥ 0.25 是主线，≥ 0.22 是观察线，两档都在真实台账上标定过（208 条：≥ 0.25 共 12 对，≥ 0.22 共 20 对，fixture 精确率 1.00）。2 条及以上连通的条目成一组。只报告，绝不拦截：打印一行带候选编号的告警，绝不改状态，绝不自动升级。

## The escalation gate (the core)

> Second occurrence of the same type → it must become a rule (protocol / skill / script), or the
> usage must change.
> Recording without escalating turns the ledger into a diary, and the mistakes continue.

When you write the rule, leave a pointer to where the rule lives, or in six months nobody knows
why it exists.

**中文**

> 同型第 2 次 → 必须落成规则（协议 / 技能 / 脚本），或者改用法。
> 只记录不升级，错题本就会变成日记，错误继续发生。

写规则的时候，留一个指针说明规则住在哪，否则六个月后没人知道它为什么存在。

## What to record

① unexpected failure; ② second occurrence of the same type; ③ anything that caused at least one
rework cycle. Everything else — expected probe failures, one-off environment noise — stays out, or
the signal-to-noise ratio collapses.

**中文**

① 非预期失败；② 同型第 2 次；③ 任何造成了至少一轮返工的事。其余 —— 预期内的探针失败、一次性的环境噪音 —— 不进，否则噪信比会崩掉。

## Anti-patterns

- Writing "watch out for X" — not actionable.
- Recording the symptom without the root cause — next time it will not be fixed either.
- No hot/cold split — hit rate drops and people stop trusting the system.

**中文**

- 写「小心 X」—— 不可执行。
- 只记现象不记根因 —— 下次照样不会修好。
- 不分冷热 —— 命中率下降，人就不信这个系统了。

## The write path, mechanically

One writer, five outcomes — the client never edits the file by hand:

| Operation | Trigger | Effect |
|---|---|---|
| ADD | no near-duplicate | append a new entry; the line ends with a machine-readable field block (class, state, counter, rule pointer) |
| NOOP | same class, symptom similarity ≥ 0.90 | no new entry; append a record carrying a hash of the symptom, never the text |
| UPDATE | the entry exists but the text is wrong | rewrite in place, stamp `upd=<date>`; id, counter and status suffix stay untouched |
| EXPIRE | the failure mode is gone | `st=expired` plus `vt=<date>` in the field block; the body is never rewritten |
| MERGE | a human confirms a duplicate pair | `--dup-of #N`: target counter +1, one appendix line, audit trail; idempotent, and a cross-class merge needs an explicit force flag |

Two details worth stealing: the NOOP threshold (0.90) and the advisory threshold (0.25) are
**different measurements on purpose** — one asks "is this literally the same event", the other asks
"might this be the same type". And the duplicate detector must not lean on a file-size heuristic
("this report is under 200 bytes, so it is a placeholder"): shells and placeholders have to be
detected from their markers, and only in the first few non-empty lines, or a real report that
quotes a marker gets misjudged.

**中文**

一个写入者，五种结果 —— 客户端绝不手改文件：

| 操作 | 触发 | 效果 |
|---|---|---|
| ADD | 无近重复 | 追加一条；行尾带机读字段块（类别、状态、计数、规则落点） |
| NOOP | 同类且现象相似度 ≥ 0.90 | 不新增条目；只往独立日志追加一条记录，存现象的 hash，绝不存原文 |
| UPDATE | 条目在但文字错了 | 就地改写并标记 `upd=<日期>`；编号、计数与状态后缀一律不动 |
| EXPIRE | 失效模式已消失 | 字段块里 `st=expired` 加 `vt=<日期>`；正文绝不重写 |
| MERGE | 人工确认是重复对 | `--dup-of #N`：目标计数 +1、追加一行附注、留审计痕；幂等，跨类合并必须显式给强制旗标 |

两个值得抄走的细节：NOOP 阈值（0.90）与 advisory 阈值（0.25）**故意是两种不同的度量** —— 一个问「是不是同一件事」，另一个问「会不会是同一类」。另外，重复检测**不能靠文件大小启发式**（「这份报告不到 200 字节，所以是占位壳」）：壳与占位必须按标记判定，而且只在前几行非空内容里判定，否则一份引用了该标记的真报告会被误判。

## Instrument first: read-only baseline → advisory → gate

Six steps, in this order, each only shipping after the previous one is green. The first two change
nothing at all — that is the point.

| Step | What it does | Evidence it must produce |
|---|---|---|
| S0 baseline | read-only audit across every volume | entry count, pair count at the primary threshold, fixture precision |
| S0b advisory | after a write, scan all volumes and print the top-3 same-type candidates | candidates logged; state untouched |
| S1 dedupe | merge path above, plus placeholder detection by markers instead of by size | each merge is idempotent; a duplicate can no longer be re-added as a new entry |
| S2 injection | put only the most relevant entries in front of the agent, per task type | a threshold calibrated query↔entry, not entry↔entry (docs/03) |
| S3 fields | one serializer for the field block, lifecycle stamps, WIP cap; the gate that reads those fields treats them as authoritative | legitimate vs downgraded counts, and a reverse probe that must turn red |
| S4 report | recurrence report over the event stream, dry-run first | per-class split with blocked and failed kept apart |

Reference numbers from the run that shipped them: S0 measured 208 entries, 12 pairs at ≥ 0.25 and a
fixture precision of 1.00; the same baseline showed that the 0.25 line produces almost no pairs when
a query is scored against an entry, which is why S2 injects at 0.10; S3 normalized existing field
blocks and classified 86 as legitimate and 13 as soft.

Two limits of the current state, recorded rather than smoothed over: the recurrence fingerprint
still needs a message digest, because the reason code is empty across the board; and an entry
caused by a gate interception is not a recurrence — counting it would inflate the trend.

**中文**

六步，顺序不可换；前两步**什么也不改**，这正是重点。

| 步骤 | 做什么 | 必须产出什么证据 |
|---|---|---|
| S0 基线 | 全卷只读审计 | 条目数、主阈值下的相似对数、标定 fixture 的精确率 |
| S0b advisory | 写入后扫全卷，打印 top3 同型候选 | 候选落日志；状态一动不动 |
| S1 去重 | 上面的归并路径 + 按标记而非按大小判占位壳 | 每次归并幂等；重复事件不能再被当成新条目写进来 |
| S2 注入 | 按 task-type 只把最相关的条目摆到 agent 面前 | 阈值按**查询↔条目**标定，不是条目↔条目（见 docs/03） |
| S3 字段 | 机读字段单一序列化 + 生命周期标记 + WIP 上限；读这些字段的闸以机读字段为权威 | 合法化 vs 降 soft 的条数，以及一个必须变红的反向探针 |
| S4 报表 | 基于事件流的复发报表，先 dry-run | 分类报表，blocked 与 failed 分列不混 |

落地那一轮的参考数字：S0 实测 208 条、≥ 0.25 共 12 对、fixture 精确率 1.00；同一份基线也显示，把查询和条目直接对打分时 0.25 这一档几乎不出对，所以 S2 的注入线单独取 0.10；S3 把存量字段块归正，86 条判为合法、13 条降为 soft。

两条现状限制如实记下，不做抹平：复发指纹仍需要补消息摘要，因为 reason_code 全为空；被闸拦下（tool_blocked）的条目不算复发 —— 算进去会把趋势吹大。
