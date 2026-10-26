# 04 · 错题本：把「踩过」变成「不再踩」

## 条目格式（一行一条）

```
序号 | 日期 | 现象 | 根因 | 预防 | 类型
```

- **现象**：可观察的报错/挂死/超时原文要点，不要概括成「失败了」。
- **根因**：机制层解释。写不出根因 = 还没诊断完，不该入库。
- **预防**：下次的具体动作（换命令/加参数/先检查什么），不是「要小心」。
- **类型**：工具层 / 流程层 / 环境层 / 设计层——用于同型识别。

## 热冷分层

热层保留最近 3 个月，单文件 ≤ 60 KB（或 ≤ 120 条）；更早的按月分卷进冷层，
冷层只留索引（编号 + 一句话 + 卷号），需要回溯时按编号定位。
避免「错题本自己变成上下文炸弹」。

**索引契约**：冷层索引可携带「卷表 + 条目级映射」，上限与单卷同（36 KB）。条目级映射是编号回溯保持 O(1) 的依赖，
不要为了「干净」把它压成纯卷表——回溯会退化成在 5 个卷里 grep。

**重建分卷的脚本属于生产代码**，必须满足四条：

1. 用**结构**识别索引（卷表：首列文件名 + 编号区间/条数/字节），不要用「文件里有没有 `1. ` 这种行」判——
   条目级映射长得就像条目，会被误当正文重解析；
2. 写盘前**全量备份**（热层、索引、每一个分卷、计数器），任一复制失败即中止；
3. 写前**算术自检**：解析出的条目总数必须等于各卷条数之和，否则拒绝写盘；
4. dry-run 与真跑共用同一条判定路径，保证「看到的卷数/条数」就是「会被写出的」。

（这四条是一次真实事故的产物：某次重建把自己的索引当正文，报 3 卷 115 条，真值 5 卷 155 条；
且备份清单漏掉了 `-unknown` 这类非年月命名的分卷。）

## 操作语义（借自记忆系统的 ADD/UPDATE/NOOP）

| 操作 | 触发 |
|---|---|
| ADD | 新类型、新根因 |
| UPDATE | 同型已有条目，补充新现象或修正预防措施（保留原条目，标注更新） |
| NOOP | 同型且预防一致，只更新时间戳/计数 |

计数很重要：**计数就是升级信号**。

计数有两种形态，缺一不可：

- **同一条目内 ×N**（同型重复），
- **跨条目同根因**——三条各自 `×1` 的开放条目若共享同一根因，仍是「同型第 2 次」以上。
  机械判据：把「现象」归一化（去版本号/路径/数字）后切成词元，共享判别词元的字符总数 ≥ 阈值
  （实测 12 个字符是零误报点，降到 8 开始连进无关条目），连通分量 ≥2 条即成组。
  只报不拦：输出一行告警，绝不自动改状态、绝不自动升级。

## 升级门（核心）

> 同型第 2 次 → 必须落成规则（协议/技能/脚本），或者改用法。
> 只记不升 = 台账变日记本，错误照旧。

写规则时留「规则位置指针」，否则半年后没人知道这条为什么存在。

## 什么该记

① 非预期失败；② 同型第 2 次；③ 造成 ≥1 轮返工。
其余（预料之中的探测失败、一次性环境噪音）不记，否则噪信比崩。

## 反模式

- 记成「注意 XX」——不可执行。
- 只记现象不记根因——下次照样不会修。
- 冷热不分——检索命中率下降，人会开始不信这套东西。

## English

### Entry format (one line each)

```
id | date | symptom | root cause | prevention | type
```

- **Symptom**: the observable error, timeout or hang — not "it failed".
- **Root cause**: a mechanism-level explanation. No cause, no entry — you have not diagnosed it yet.
- **Prevention**: the concrete next action (different flag, check X first), not "be careful".
- **Type**: tool / process / environment / design — used to detect repeats.

### Hot and cold tiers

Keep three months hot, at most 36 KB, and roll older entries into monthly volumes. Cold volumes
keep only an index (id + one sentence + volume). Otherwise the ledger itself becomes a context bomb.

### Operation semantics (borrowed from memory systems)

| Operation | Trigger |
|---|---|
| ADD | new type or new root cause |
| UPDATE | same type, add a symptom or fix the prevention (keep the original, mark the change) |
| NOOP | same type, same prevention — just bump the counter |

The counter matters: **the count is the escalation signal**.

### The escalation gate

> Second occurrence of the same type → it must become a rule (protocol / skill / script),
> or the usage must change. Recording without escalating turns a ledger into a diary.

When you write the rule, leave a pointer to where it lives.

### What to record

① unexpected failure; ② second occurrence; ③ caused at least one rework cycle.
Skip everything else — expected probe failures and one-off environment noise — or the signal drowns.

### Anti-patterns

- "Pay attention to X" — not actionable.
- Symptom without cause — next time it still will not be fixed.
- No hot/cold split — hit rate drops and people stop trusting the system.
