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

**中文**

最近三个月留在热层，最多 60 KB（或 120 条）；更早的条目按月分卷滚进冷层，每卷 36 KB。冷卷只保留索引（编号 + 一句话 + 卷号），需要回溯时按编号定位。这样错题本才不会自己变成上下文炸弹。

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
  are still at "second occurrence of the same type" or worse. Mechanical test: normalize the
  symptom (strip version numbers, paths, digits), split it into tokens, and require the shared
  discriminating tokens to total at least 12 characters (measured as the zero-false-positive point;
  dropping to 8 starts pulling in unrelated entries). Two or more connected entries form a group.
  Report only, never block: print one warning line, never change state, never escalate
  automatically.

**中文**

| 操作 | 触发 |
|---|---|
| ADD | 一个新类型，或一个新根因 |
| UPDATE | 类型已存在 —— 补上新的现象，或修正预防（保留原来的，标出这次更新） |
| NOOP | 同类型且同预防 —— 只更新时间戳 / 计数器 |

计数器很重要：**计数器就是升级信号。**

计数器有两种形态，两种都必须有：

- **条目内 ×N**（同一类型反复发生），
- **跨条目的同一根因** —— 三条各为 ×1 的未销账条目共享一个根因，那仍然是「同型第 2 次」或更糟。机械判据：把现象归一化（去掉版本号、路径、数字），切成词元，要求共享的判别词元合计至少 12 个字符（实测的零假阳点；降到 8 就开始把无关条目也拉进来）。2 条及以上连通的条目成一组。只报告，绝不拦截：打印一行告警，绝不改状态，绝不自动升级。

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
