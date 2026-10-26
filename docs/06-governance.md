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

## Pending-decision inbox

Unattended work (background jobs, scheduled tasks) that hits an authorization or credential
question writes an inbox entry and suspends; only read-only work may continue. **Unattended does
not mean more autonomy.**

## Nightly curation

Runs with sessions stopped, and performs mechanical actions only:

- rebuild the daily file index (do not write when the content is unchanged);
- warn on size or entry-count limits;
- count same-type incidents, and tag the ones over the threshold;
- prune expired todos and already-closed entries.

Never do things like "let a model rewrite memory" — an irreversible cleanup is a destruction.

## Mechanical gates, not "remember to comply"

Write discipline as prose and the model will forget it sooner or later. Therefore:

| Discipline | Mechanism |
|---|---|
| no whole-file writes on shared files | protected paths at the hook layer, fail-closed |
| config changes may only tighten | pre-write validation + allowlist |
| restricted commit scope | pre-commit file-set check |
| repeat incidents must escalate | counters + a periodic scan |

**Unknown cases resolve to the stricter branch** (fail-closed) — never "looks fine, let it pass".

## Every gate needs dual probes before shipping

1. **True positive must be blocked**: build a sample that should be blocked, confirm exit ≠ 0.
2. **False positive must pass**: prose mentions, values inside arguments, non-writing tool calls —
   confirm they go through.

Missing either side means half-verified, and it must not ship. When fixing a false positive, never
turn the gate into fail-open along the way.

## Throttling periodic checks

Merge similar checks, stretch the intervals, and slow down or stop after three consecutive runs
with no change. Runaway scheduled work usually costs more than it returns.

## 中文摘要

- 长会话里最贵的不是算力，是同一个取舍被讨论五遍；决策台账是「已经定了什么」的唯一真相源。
- 条目一行：N. 问题｜A 选项（推荐）｜B 选项；拍板即写结论 + 日期，做完立刻销账并附证据（commit / 报告路径）。
- 台账里只留真需要人处理的事，按归属分文件，共享文件只放无主条目。
- 无人值守遇到授权或凭证问题 → 写收件箱并挂起，只允许继续只读；无人值守 ≠ 更高自主度。
- 夜间策展只做机械动作（重建索引、超限告警、同型计数、清理过期项），绝不「让模型重写记忆」——不可回滚的整理等于销毁。
- 纪律要落成闸：保护路径、写前校验 + 白名单、pre-commit 提交范围检查、计数 + 巡检；未知情况按更严处理。
- 闸上线必须双探针：真阳必须拦（exit ≠ 0）、假阳必须放行；缺一侧就是半验证，且修假阳时禁止改成 fail-open。
- 周期检查要节流：同类合并、拉长间隔、连续 3 次无变化就降频或停。
