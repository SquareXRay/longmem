# 02 · Write discipline and large-file safety

Half of all memory-system failures are not "forgot to write" — they are **writing it wrong**.

## When to write

| Event | Action | Where |
|---|---|---|
| the user says "remember this" | write to disk in the same turn, do not keep it in your head | L2 or L1 |
| the user corrects your approach | record the preference in the same turn (format / style / naming / process) | L1 preferences section + L2 |
| a multi-step task completes | one paragraph: what was done / why / commit | L3 |
| a tool trap was hit | symptom → root cause → prevention, one line each | incident ledger |
| a trade-off was decided | numbered entry + options + verdict | decision ledger |

**"Same turn" is the operative word**: in a long session, "I'll note it later" means lost.

## Never read-then-rewrite a large file

Readers truncate large files and return only a prefix. Writing the whole buffer back = silently
losing data. Three safe ways to edit:

1. **Anchored exact replace** — if the anchor is not found, fail closed. "Roughly here" is not
   allowed.
2. **Append** — `>>` or an append tool; inherently safe.
3. **Full rewrite** — only through an atomic writer: temp file + size guard (refuse when the new
   content is much smaller than the old) + timestamped backup + rename.

## Append-only files stay append-only

Journals, incident ledgers and inboxes are write-once-append files. Block whole-file writes at the
hook layer with a protected-path list. The reason: a whole-file write silently drops someone
else's entries, and the diff does not show it.

## Shell redirect trap

`cmd > same-file` truncates **before** reading, which empties the file. Correct order: write a
temp file first, then copy it over.

## Quoting long text

Quote Chinese prose with 「」 so it never fights with quotes inside code; build multi-line strings
by joining an array rather than embedding escaped newlines.

## Pre-commit self-check

- `git show --stat`: the file set must be a subset of what this task was authorized to touch. Any
  unrelated change means: do not commit, report instead.
- Shrink guard: a pre-commit check that rejects a sudden drop in line or byte count.

## 中文摘要

- 记忆系统失效有一半不是「忘了写」，而是**写坏了**：时机与安全改法是这一篇的全部内容。
- 写入时机：说「记住」/被纠正 → 当回合落盘；多步任务完成 → 一段进日志层；工具坑 → 错题本一行；拍板取舍 → 决策台账。
- 大文件禁「读→整写」：读工具会截断，整写回等于静默丢尾部。三条安全改法：锚点精确替换（找不到就失败退出）、追加、原子写脚本（临时文件 + 缩水护栏 + 备份 + rename）。
- 共享 / 追加型文件在 hook 层用保护路径清单拦死整写，因为 diff 里看不出被删的别人的条目。
- `cmd > 同一个文件` 会先截断再读，等于清空；先写临时文件再拷贝覆盖。
- 提交前自查：`git show --stat` 的文件集合必须落在本轮授权范围内；缩水护栏拦住行数/字节数骤降。
