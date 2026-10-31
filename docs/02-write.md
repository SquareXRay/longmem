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
   content is much smaller than the old) + timestamped backup + rename. The writer leaves a `.bak`
   next to the target and asserts that each anchor matched exactly once; if it cannot prove both,
   it has failed and must not touch the file.

**中文**

读取器会截断大文件，只返回前缀。把整个缓冲写回去 = 静默丢数据。三条安全的改法：

1. **锚点精确替换** —— 锚点找不到就失败退出。「大概在这个位置」不允许。
2. **追加** —— `>>` 或追加工具；天生安全。
3. **整段重写** —— 只走原子写：临时文件 + 缩水护栏（新内容比旧内容小很多就拒绝）+ 带时间戳的备份 + rename。写盘器会在目标旁留一份 `.bak`，并断言每个锚点恰好命中一次；两样都证不出来就算失败，不许碰文件。

## Append-only files stay append-only

Journals, incident ledgers and inboxes are write-once-append files. Block whole-file writes at the
hook layer with a protected-path list. The reason: a whole-file write silently drops someone
else's entries, and the diff does not show it.

The list is load-bearing, so it needs the same discipline as the files it protects: **a new ledger
file that is not registered is unprotected**, and the protection fails open exactly where nobody is
looking. Registering a new `MEMORY-<topic>.md` is part of creating it, not a follow-up.

**中文**

日志、错题本与收件箱都是一次写入、只追加的文件。在 hook 层用一张保护路径清单拦死整文件写入。原因：整文件写入会静默丢掉别人的条目，而 diff 上看不出来。

这张清单是承重的，所以它自己也要守同样的纪律：**没登记的新台账文件等于没有保护**，而保护恰恰会在没人看的地方失效。新建 `MEMORY-<主题>.md` 时同步登记是「创建」的一部分，不是后续补办。

## Shell redirect trap

`cmd > same-file` truncates **before** reading, which empties the file. Correct order: write a
temp file first, then copy it over. And if the reader itself reports **truncated**, stop: you hold a
prefix, not the file, so any rewrite is data loss. Truncation is a fail-closed signal, not a hint.

**中文**

`cmd > 同一个文件` 会在读取**之前**就把文件截断，等于把内容清空。正确顺序：先写临时文件，再拷贝覆盖过去。还有一条：只要读取器自己报了 **truncated**，立刻停手 —— 你手里只是前缀，不是文件，任何重写都是数据丢失。截断是 fail-closed 信号，不是提示。

## Temp files are not free

On many machines `/tmp` is a tmpfs: every byte there is RAM. A few GB of scratch files do not fail
as "disk full" — swap goes first, then memory commits fail, and everything that needs a page dies at
the same moment (browsers crash with resource errors, saves fail, background jobs drop their
deliveries). So:

- scratch data — database copies, unpacked trees, test fixtures, traces — goes to a **disk-backed**
  directory, and the task sets its temp variable to that directory explicitly;
- a single file over 50 MB never lands on the tmpfs;
- a periodic checker reports only when the tmpfs crosses a size line or holds an oversized file, and
  reclaim also runs on **prefix rules** with a much lower floor: tools that create one scratch
  directory per run leave hundreds of small directories, which a global "50 MB / 24 h" threshold
  never sees.

**中文**

在很多机器上 `/tmp` 是 tmpfs：那里每一个字节都是内存。几个 GB 的临时文件不会以「磁盘满」的方式失败 —— 先打满 swap，然后内存提交失败，所有需要换页的东西在同一刻一起死（浏览器报资源错误崩溃、保存失败、后台任务投递丢失）。所以：

- 临时数据 —— 数据库副本、解包目录、测试夹具、trace —— 一律落在**磁盘**目录，任务把临时目录变量显式指向那里；
- 单文件超过 50 MB 绝不落 tmpfs；
- 巡检只在 tmpfs 越过体积线或出现超大文件时报警，同时回收还按**前缀规则**用一个低得多的门槛跑：每次运行都自建一个临时目录的工具会留下成百上千个小目录，全局「50 MB / 24 小时」阈值永远抓不到它们。

## Quoting long text

Quote Chinese prose with 「」 so it never fights with quotes inside code; build multi-line strings
by joining an array rather than embedding escaped newlines.

**中文**

中文正文一律用「」引用，这样永远不会和代码里的引号打架；多行字符串用数组 join 拼出来，而不是把转义换行嵌进字面量。

## A write lock is not a place for I/O

When one ledger file is shared, writes serialize on a lock that carries a **5-second watchdog**. A
slow cross-process call made while holding it is the worst case: the call outlives the watchdog and
still completes, while the write is judged failed — one change half-applied. So the ordering is part
of write discipline, not an optimization:

- prepare everything that needs an external call **before** taking the lock;
- while the lock is held, only touch the file — no cross-process calls, and no reuse of the lock
  file for any other purpose;
- whatever fails after release is replayed by a worker, never retried inside the critical section.

**中文**

只有一个台账文件时，写入串行在一把带 **5 秒看门狗**的锁上。持锁期间做慢的跨进程调用是最坏情况：调用熬过看门狗并且仍然完成，而这次写入已被判失败 —— 一个改动只应用了一半。所以顺序属于写入纪律，不是优化：

- 需要外部调用的一切，在**取锁之前**准备好；
- 持锁期间只碰文件 —— 不发跨进程调用，也不把这个锁文件挪作他用；
- 放锁之后失败的，交给 worker 重放，绝不在临界区内重试。

## Pre-commit self-check

- `git show --stat`: the file set must be a subset of what this task was authorized to touch. Any
  unrelated change means: do not commit, report instead.
- Shrink guard: a pre-commit check that rejects a sudden drop in line or byte count.

**中文**

- `git show --stat`：文件集合必须是本轮任务被授权触碰范围的子集。出现任何无关改动就意味着：不提交，改为报告。
- 缩水护栏：一个 pre-commit 检查，拒绝行数或字节数骤降。
