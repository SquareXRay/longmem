# 05 · Procedural memory: turn steps into skills

Factual memory answers "what is true"; procedural memory answers "how to do it". The two should
not live in the same file.

## Structure

```
skills/<name>/SKILL.md    triggers + steps + acceptance gate + anti-patterns
skills/<family>/SKILL.md  family entry: member list + family-level acceptance gates
```

A skill file holds **executable steps** and **objective acceptance criteria** (the standard for
"counts as done"). It does not hold background stories — those belong in repository docs or the
journal layer.

## Propose → review → apply

1. Finish something reusable → file a proposal (which skill, what change, why).
2. Review: does it conflict with existing steps? Is a special case being written as a general rule?
3. Apply, **keeping the previous version** (snapshot or backup) so it can be rolled back.
4. After applying, send a "learned" notice and leave one line in the ledger.

The key constraint: **knowledge that belongs to one codebase goes into that repo's docs; only
cross-project procedures become skills.** Otherwise the skill library becomes a second dumping
ground.

## Triggers

Every skill opens with 3–8 trigger phrases (how the user would actually ask for this), so "which
skill to read" does not depend on the model guessing. A skill whose triggers cannot be reached
effectively does not exist.

## Acceptance gates

Family-level acceptance gates state objective facts: the commit exists, the index is in sync, the
probes pass, the state matches. "Feels right" is not acceptance.

## 中文摘要

- 事实记忆回答「是什么」，程序记忆回答「怎么做」，两者不该混在一个文件里。
- 技能文件只写可执行步骤和客观验收判据，背景故事进仓库文档或日志层。
- 提案 → 审阅 → 应用：应用时保留上一版（快照/备份）可回滚，并在台账留一行。
- 关键约束：知识属于某个代码库就进那个仓库的文档，只有跨项目复用的流程才进技能，否则技能库会变成第二个垃圾场。
- 每个技能开头写 3–8 个触发词，让「读哪个技能」不靠模型猜；触发词覆盖不到的技能事实上不存在。
- 族级验收门写客观事实（commit 存在、索引同步、探针通过、状态一致），「感觉不错」不算验收。
