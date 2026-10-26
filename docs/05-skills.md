# 05 · Procedural memory: turn steps into skills

Factual memory answers "what is true"; procedural memory answers "how to do it". The two should
not live in the same file.

**中文**

事实记忆回答「什么是真的」；程序记忆回答「怎么做」。两者不该住在同一个文件里。

## Structure

```
skills/<name>/SKILL.md    triggers + steps + acceptance gate + anti-patterns
skills/<family>/SKILL.md  family entry: member list + family-level acceptance gates
```

A skill file holds **executable steps** and **objective acceptance criteria** (the standard for
"counts as done"). It does not hold background stories — those belong in repository docs or the
journal layer.

**中文**

技能文件结构（代码块同上）：`skills/<name>/SKILL.md` 放触发词 + 步骤 + 验收门 + 反模式；`skills/<family>/SKILL.md` 是族入口：成员清单 + 族级验收门。

一个技能文件放**可执行的步骤**与**客观验收判据**（「算做完」的标准）。它不放背景故事 —— 那些属于仓库文档或日志层。

## Propose → review → apply

1. Finish something reusable → file a proposal (which skill, what change, why).
2. Review: does it conflict with existing steps? Is a special case being written as a general rule?
3. Apply, **keeping the previous version** (snapshot or backup) so it can be rolled back.
4. After applying, send a "learned" notice and leave one line in the ledger.

The key constraint: **knowledge that belongs to one codebase goes into that repo's docs; only
cross-project procedures become skills.** Otherwise the skill library becomes a second dumping
ground.

**中文**

1. 做完一件可复用的事 → 提一个提案（改哪个技能、改什么、为什么）。
2. 审阅：和现有步骤冲突吗？是不是把一个特例写成了通用规则？
3. 应用，**保留上一版**（快照或备份），以便回滚。
4. 应用之后发一条「已学到」通知，并在台账留一行。

关键约束：**属于某个代码库的知识进那个仓库的文档；只有跨项目的流程才成为技能。** 否则技能库会变成第二个垃圾场。

## Triggers

Every skill opens with 3–8 trigger phrases (how the user would actually ask for this), so "which
skill to read" does not depend on the model guessing. A skill whose triggers cannot be reached
effectively does not exist.

**中文**

每个技能开头写 3–8 个触发短语（用户实际会怎么问这件事），这样「该读哪个技能」不依赖模型去猜。触发词事实上够不到的技能等于不存在。

## Acceptance gates

Family-level acceptance gates state objective facts: the commit exists, the index is in sync, the
probes pass, the state matches. "Feels right" is not acceptance.

**中文**

族级验收门陈述客观事实：commit 存在、索引同步、探针通过、状态一致。「感觉对」不算验收。
