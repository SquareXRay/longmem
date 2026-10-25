# 05 · 程序性记忆：把步骤变成技能

事实记忆回答「是什么」，程序记忆回答「怎么做」。两者不该混在一个文件里。

## 结构

```
skills/<name>/SKILL.md    触发词 + 步骤 + 验收门 + 反模式
skills/<family>/SKILL.md  角色族入口：成员清单 + 族级验收门
```

技能文件只写**可执行步骤**和**客观验收判据**（「算做完」的标准），
不写背景故事——背景进仓库文档或日志层。

## 提案 → 审阅 → 应用

1. 做完一件可复用的活 → 提一条提案（改哪个技能、改什么、为什么）。
2. 审阅：有没有和现有步骤冲突？会不会把特例写成通则？
3. 应用：**保留上一版**（快照/备份），可回滚。
4. 应用后发一条「已学习」通知，并在台账留一行。

关键约束：**知识属于一个代码库的，进那个仓库的文档；只有跨项目复用的流程才进技能。**
否则技能库会变成第二个垃圾场。

## 触发词

每个技能开头写 3–8 个触发词（用户会怎么说这件事），
让「读哪个技能」不依赖模型猜。触发词覆盖不到的技能 = 事实上不存在。

## 验收门

族级验收门写客观事实：commit 存在、索引同步、探针通过、状态一致。
「感觉不错」不算验收。

## English

Factual memory answers "what is true"; procedural memory answers "how to do it".
They should not share a file.

### Structure

```
skills/<name>/SKILL.md    triggers + steps + acceptance gate + anti-patterns
skills/<family>/SKILL.md  family entry: members + family-level gates
```

A skill holds executable steps and objective acceptance criteria. Background stories belong in
repository docs or the journal — otherwise the skill library becomes a second dumping ground.

### Propose → review → apply

1. Finish something reusable → file a proposal (which skill, what change, why).
2. Review: does it conflict with existing steps? Is a special case being written as a general rule?
3. Apply, keeping the previous version (snapshot or backup) so it can be rolled back.
4. Announce the change and leave one line in the ledger.

Hard constraint: knowledge about one codebase belongs in that repo's docs. Only cross-project
procedures become skills.

### Triggers

Each skill starts with 3–8 trigger phrases — how the user would actually ask for this.
A skill whose triggers cannot be reached effectively does not exist.

### Acceptance gates

State objective facts: the commit exists, the index is in sync, the probes pass, the card state
matches. "Feels right" is not acceptance.
