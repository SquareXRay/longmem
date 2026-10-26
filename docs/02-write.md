# 02 · Write discipline and large-file safety

Half of all memory-system failures are not "forgot to write" — they are **writing it wrong**.

**中文**

记忆系统的失效有一半不是「忘了写」，而是**写坏了**。

## When to write

| Event | Action | Where |
|---|---|---|
| the user says "remember this" | write to disk in the same turn, do not keep it in your head | L2 or L1 |
| the user corrects your approach | record the preference in the same turn (format / style / naming / process) | L1 preferences section + L2 |
| a multi-step task completes | one paragraph: what was done / why / commit | L3 |
| a tool trap was hit | symptom → root cause → prevention, one line each | incident ledger |
| a trade-off was decided | numbered entry + options + verdict | decision ledger |

**"Same turn" is the operative word**: in a long session, "I'll note it later" means lost.

**中文**

| 事件 | 动作 | 写到哪里 |
|---|---|---|
| 用户说「记住这个」 | 当回合落盘，不要留在脑子里 | L2 或 L1 |
| 用户纠正你的做法 | 当回合记下这个偏好（格式 / 风格 / 命名 / 流程） | L1 偏好小节 + L2 |
| 多步任务完成 | 一段话：做了什么 / 为什么 / commit | L3 |
| 踩了一个工具坑 | 现象 → 根因 → 预防，各一行 | 错题本 |
| 拍板了一个取舍 | 编号条目 + 选项 + 裁决 | 决策台账 |

**「当回合」是这里的关键词**：在长会话里，「我稍后记一下」等于丢掉了。

## Never read-then-rewrite a large file

Readers truncate large files and return only a prefix. Writing the whole buffer back = silently
losing data. Three safe ways to edit:

1. **Anchored exact replace** — if the anchor is not found, fail closed. "Roughly here" is not
   allowed.
2. **Append** — `>>` or an append tool; inherently safe.
3. **Full rewrite** — only through an atomic writer: temp file + size guard (refuse when the new
   content is much smaller than the old) + timestamped backup + rename.

**中文**

读取器会截断大文件，只返回前缀。把整个缓冲写回去 = 静默丢数据。三条安全的改法：

1. **锚点精确替换** —— 锚点找不到就失败退出。「大概在这个位置」不允许。
2. **追加** —— `>>` 或追加工具；天生安全。
3. **整段重写** —— 只走原子写：临时文件 + 缩水护栏（新内容比旧内容小很多就拒绝）+ 带时间戳的备份 + rename。

## Append-only files stay append-only

Journals, incident ledgers and inboxes are write-once-append files. Block whole-file writes at the
hook layer with a protected-path list. The reason: a whole-file write silently drops someone
else's entries, and the diff does not show it.

**中文**

日志、错题本与收件箱都是一次写入、只追加的文件。在 hook 层用一张保护路径清单拦死整文件写入。原因：整文件写入会静默丢掉别人的条目，而 diff 上看不出来。

## Shell redirect trap

`cmd > same-file` truncates **before** reading, which empties the file. Correct order: write a
temp file first, then copy it over.

**中文**

`cmd > 同一个文件` 会在读取**之前**就把文件截断，等于把内容清空。正确顺序：先写临时文件，再拷贝覆盖过去。

## Quoting long text

Quote Chinese prose with 「」 so it never fights with quotes inside code; build multi-line strings
by joining an array rather than embedding escaped newlines.

**中文**

中文正文一律用「」引用，这样永远不会和代码里的引号打架；多行字符串用数组 join 拼出来，而不是把转义换行嵌进字面量。

## Pre-commit self-check

- `git show --stat`: the file set must be a subset of what this task was authorized to touch. Any
  unrelated change means: do not commit, report instead.
- Shrink guard: a pre-commit check that rejects a sudden drop in line or byte count.

**中文**

- `git show --stat`：文件集合必须是本轮任务被授权触碰范围的子集。出现任何无关改动就意味着：不提交，改为报告。
- 缩水护栏：一个 pre-commit 检查，拒绝行数或字节数骤降。
