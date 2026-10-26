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

## Hot and cold tiers

Keep the last three months hot, at most 60 KB (or 120 entries); roll older entries into monthly
volumes at 36 KB per volume. Cold volumes keep only an index (id + one sentence + volume number),
and you locate an entry by id when you need to go back. This stops the ledger from turning into a
context bomb on its own.

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
  are still at "second occurrence of the same type" or worse. Mechanical test: normalize the
  symptom (strip version numbers, paths, digits), split it into tokens, and require the shared
  discriminating tokens to total at least 12 characters (measured as the zero-false-positive point;
  dropping to 8 starts pulling in unrelated entries). Two or more connected entries form a group.
  Report only, never block: print one warning line, never change state, never escalate
  automatically.

## The escalation gate (the core)

> Second occurrence of the same type → it must become a rule (protocol / skill / script), or the
> usage must change.
> Recording without escalating turns the ledger into a diary, and the mistakes continue.

When you write the rule, leave a pointer to where the rule lives, or in six months nobody knows
why it exists.

## What to record

① unexpected failure; ② second occurrence of the same type; ③ anything that caused at least one
rework cycle. Everything else — expected probe failures, one-off environment noise — stays out, or
the signal-to-noise ratio collapses.

## Anti-patterns

- Writing "watch out for X" — not actionable.
- Recording the symptom without the root cause — next time it will not be fixed either.
- No hot/cold split — hit rate drops and people stop trusting the system.

## 中文摘要

- 一条一行：序号｜日期｜现象｜根因｜预防｜类型；写不出根因 = 没诊断完，不该入库。
- 热层保留最近 3 个月，≤ 120 条（或按字节封顶）；更早的按月分卷进冷层，冷层只留索引（编号 + 一句话 + 卷号），避免错题本自己变成上下文炸弹。
- 冷层索引契约：可带「卷表 + 条目级映射」，条目级映射是编号回溯 O(1) 的依赖，别为「干净」压成纯卷表。
- 重建分卷脚本属生产代码，四条硬要求：按结构识别索引、写前全量备份、写前算术自检、dry-run 与真跑共用判定路径。
- 真实事故：某次重建把索引当正文，报了 115 条 / 3 卷，真值 155 条 / 5 卷，且备份清单漏掉非年月命名的分卷。
- 操作语义 ADD / UPDATE / NOOP；计数就是升级信号，且必须两种形态并存：条目内 ×N 与跨条目同根因（判别词元 ≥ 12 字符，连通分量 ≥ 2 条即成组），只告警不自动改状态。
- 升级门：同型第 2 次必须落成规则（协议/技能/脚本）或改用法；写规则时留规则位置指针。
- 该记的三类：非预期失败、同型第 2 次、造成 ≥1 轮返工；其余不记，否则噪信比崩掉。
