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

热层保留最近 3 个月，单文件 ≤ 36 KB；更早的按月分卷进冷层，
冷层只留索引（编号 + 一句话 + 卷号），需要回溯时按编号定位。
避免「错题本自己变成上下文炸弹」。

## 操作语义（借自记忆系统的 ADD/UPDATE/NOOP）

| 操作 | 触发 |
|---|---|
| ADD | 新类型、新根因 |
| UPDATE | 同型已有条目，补充新现象或修正预防措施（保留原条目，标注更新） |
| NOOP | 同型且预防一致，只更新时间戳/计数 |

计数很重要：**计数就是升级信号**。

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
