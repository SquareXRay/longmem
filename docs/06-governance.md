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

**Unknown cases resolve to the stricter branch** (fail-closed) — never "looks fine, let it pass".

**中文**

把写入纪律写成正文，模型迟早会忘。因此：

| 纪律 | 机制 |
|---|---|
| 共享文件禁止整文件写入 | hook 层的保护路径，fail-closed |
| 配置改动只能收紧 | 写前校验 + 白名单 |
| 提交范围受限 | pre-commit 文件集检查 |
| 重复事故必须升级 | 计数器 + 定期扫描 |

**未知情况一律落到更严的那一支**（fail-closed）—— 绝不「看着没问题，放它过」。

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
