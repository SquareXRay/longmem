# 06 · 治理：决策台账、收件箱与机械闸

## 为什么需要台账

长会话里最贵的不是算力，是**同一个取舍被讨论五遍**。
决策台账 = 「已经定了什么」的唯一真相源。

条目格式（一行）：

```
N. **问题**｜A 选项（推荐）｜B 选项
```

拍板后立刻写结论 + 日期，做完立刻**销账**并附证据（commit / 报告路径）。
留在台账里的必须是**真需要人处理的事**；做完不留痕。
按归属分文件（主会话 / 各子会话 / 定时任务），共享文件只放无主条目。

## 待决策收件箱

无人值守（后台任务、定时任务）遇到授权或凭证问题 → 写收件箱并挂起，
只允许继续只读操作。**无人值守 ≠ 更高自主度。**

## 夜间策展

停掉会话后跑，只做机械动作：

- 重建日文件索引（内容不变不写盘）。
- 体积/条目数超限告警。
- 同型错误计数，超阈值打标。
- 过期待办与已销账条目清理。

不做「让模型重写记忆」这类动作——不可回滚的整理等于销毁。

## 机械闸，而不是「记得遵守」

纪律写成文字，模型迟早会忘。所以：

| 纪律 | 机制 |
|---|---|
| 共享文件禁整写 | hook 层保护路径，fail-closed |
| 配置只能收紧 | 写前校验 + 白名单 |
| 提交范围受限 | pre-commit 文件集合检查 |
| 错题同型必升级 | 计数 + 巡检提醒 |

**未知情况按更严处理**（fail-closed），不做「看起来没问题就放过」。

## 闸上线必须双探针

1. **真阳必须拦**：构造一个该被拦的样本，确认 exit ≠ 0。
2. **假阳必须放行**：正文提及、参数里提到、非写类工具调用，确认通过。

缺任一侧 = 半验证，不允许上线。修假阳时禁止顺手改成 fail-open。

## 周期检查的节流

同类检查合并、拉长间隔、连续 3 次无变化就降频或停。
定时任务失控的成本，往往高于它带来的收益。

## English

### Why a ledger

The most expensive thing in a long session is not compute — it is re-discussing the same
trade-off five times. The decision ledger is the single source of truth for "what has been decided".

Entry format (one line):

```
N. **question** | A: option (recommended) | B: option
```

Record the verdict and date immediately; close the entry as soon as the work is done, with
evidence (commit or report path). Anything still on the ledger must be something a human really
has to handle. Scope files by owner; keep the shared file for unowned items only.

### Pending-decision inbox

Unattended work (background jobs, scheduled tasks) that hits an authorization or credential
question writes an inbox entry and suspends. Read-only work may continue.
**Unattended does not mean more autonomy.**

### Nightly curation

Runs while sessions are stopped, and only does mechanical work: rebuild the daily index
(skip writing when content is unchanged), warn on size and entry-count limits, count repeat
incident types, prune stale and closed items.

Never let a model "rewrite memory" unattended — an irreversible cleanup is a deletion.

### Gates, not prose

Rules written as prose get forgotten. Therefore:

| Rule | Mechanism |
|---|---|
| append-only files | protected paths at the hook layer, fail-closed |
| config can only tighten | pre-write validation + allowlist |
| commit scope | pre-commit file-set check |
| repeats must escalate | counters + a periodic scan |

Unknown cases resolve to the stricter branch, never to "looks fine".

### Dual probes for every gate

1. **True positive**: build a sample that must be blocked, confirm a non-zero exit.
2. **False positive**: prose mentions, values in arguments, non-writing tool calls — confirm they pass.

Missing either side means half-verified; do not ship. Fixing a false positive must not turn the
gate into fail-open.

### Throttle periodic checks

Merge similar checks, stretch intervals, and slow down or stop after three consecutive no-change
runs. Runaway scheduled work usually costs more than it returns.
