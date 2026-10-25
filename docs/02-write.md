# 02 · 写入纪律与大文件安全

记忆系统的失效，一半不是「忘了写」，而是**写坏了**。

## 写入时机

| 事件 | 动作 | 落哪 |
|---|---|---|
| 用户说「记住」 | 当回合写盘，不做心记 | L2 或 L1 |
| 用户纠正你的做法 | 当回合写进对应记忆（格式/风格/命名/流程） | L1 偏好段 + L2 |
| 完成一个多步任务 | 一段：做了什么/为什么/commit | L3 |
| 踩了工具坑 | 现象→根因→预防，一行一条 | 错题本 |
| 拍板了一个取舍 | 编号条目 + 选项 + 结论 | 决策台账 |

**「当回合」是关键词**：跨回合的「稍后记」在长会话里等于丢失。

## 大文件禁「读→整写」

读取工具对大文件会截断，只返回前缀。此时整文件写回 = 静默丢数据。
三种安全改法：

1. **锚点精确替换**：找不到锚点就失败退出（fail-closed），不允许「大概这里」。
2. **追加**：>> 或 append 工具，天然安全。
3. **整段重写**：必须走原子写脚本 —— 临时文件 + 大小护栏（新内容比旧内容小太多就拒写）
   + 时间戳备份 + rename。

## 共享/追加型文件禁整写

日记、错题本、收件箱这类**只增不改**的文件，用保护路径清单在 hook 层拦死。
理由：整写会静默删掉别人的条目，而且 diff 里看不出来。

## Shell 重定向的陷阱

cmd > 同一个文件 会**先截断再读**，等于清空。正确做法：先写临时文件，再拷贝覆盖。

## 长文本引号

中文内容统一用「」，避免和代码里的引号打架；多行文本用数组 join 构造，别塞转义换行。

## 提交前自查

- git show --stat：文件集合 ⊆ 本轮授权范围，出现无关改动就不提交、报告。
- 缩水护栏：pre-commit 检查行数/字节数骤降。

## English

### When to write

| Event | Action | Layer |
|---|---|---|
| "remember this" | write during the same turn, not later | L2 or L1 |
| the user corrects your approach | record the preference immediately | L1 + L2 |
| a multi-step task completes | what / why / commit | L3 |
| a tool trap was hit | symptom → cause → prevention, one line | incident ledger |
| a trade-off was decided | numbered entry + options + verdict | decision ledger |

"Same turn" is the operative word: in long sessions "I'll note it later" means lost.

### Never read-then-rewrite a large file

Readers truncate large files and return a prefix. Writing the whole file back silently deletes
the tail. Three safe edits:

1. **Anchored replace** — if the anchor is missing, fail closed. No "roughly here".
2. **Append** — inherently safe.
3. **Full rewrite** — only through an atomic writer: temp file, shrink guard (refuse if the new
   content is much smaller), timestamped backup, rename.

### Append-only files stay append-only

Journals, incident ledgers and inboxes must be blocked from whole-file writes at the hook layer.
A whole-file write silently drops someone else's entry, and the diff hides it.

### Shell redirect trap

`cmd > same-file` truncates **before** reading. Write to a temp file, then copy over.

### Pre-commit self-check

- `git show --stat`: the file set must be a subset of what this task was allowed to touch.
- Shrink guard: reject commits that drop a large number of lines unexpectedly.
