# 01 · The five-layer model and injection budgets

## Budget before content

The system prompt is the scarce resource. Set the budget first, then decide where anything gets
written:

| Layer | Budget | Action when exceeded |
|---|---|---|
| L0 protocol | 4 files, ≤ 45 KB total; the protocol file itself ≤ 24 KB | keep rules only, push the narrative down to the topic layer |
| L1 index | 36 KB | split into topics; L1 keeps a one-line pointer |
| L2 topic | 40 KB per file | split into monthly volumes, body to the cold layer |
| L3 journal | no daily cap (append-only) | archive after 4 weeks idle |
| L4 cold | 36 KB per volume; a cold index may carry a volume table plus an entry-level map under the same 36 KB | split again, keep the index hot |

**中文**

系统提示是稀缺资源。先定预算，再决定任何东西写到哪里：

| 层级 | 预算 | 超预算时的动作 |
|---|---|---|
| L0 协议 | 4 个文件，合计 ≤ 45 KB；其中协议文件本身 ≤ 24 KB | 只留规则，把叙述下沉到主题层 |
| L1 索引 | 36 KB | 拆成主题；L1 只留一行指针 |
| L2 主题 | 每文件 40 KB | 按月分卷拆开，正文进冷层 |
| L3 日志 | 每日无上限（只追加） | 闲置四周后归档 |
| L4 冷层 | 每卷 36 KB；冷层索引可含「卷表 + 条目级映射」，同样 ≤ 36 KB | 再拆一次，让索引保持热 |

Two ceilings apply to the protocol layer at once, and they are checked separately: a per-file
ceiling on the protocol file (24 KB) and a total ceiling on the four injected files (45 KB). The
index is measured on its own, not folded into that total — mixing them hides which file is actually
eating the budget. Every ceiling here is asserted by a script against real file size; a budget
nobody measures is a wish.

**中文**

协议层同时受两个上限约束，且分别检查：协议文件自身的单文件上限（24 KB）与四份注入文件合计上限（45 KB）。索引**单独量**，不折进这个合计 —— 混在一起就看不出到底是哪个文件在吃预算。这里每一条上限都由脚本按真实文件大小断言；没人量的预算只是愿望。

## One job per layer (do not mix)

**L0 protocol** holds identity, tone, red lines and routing — only rules that always hold.
Anything that changes (which model today, which port a service runs on) does not belong here.

**L1 index** is three tables that cover 80% of reads: a document map (where to look → where to
jump), hard rules (violating them means rework), and trigger words (hear what → open which file).
Only current state, rules and pointers; implementation history always goes to L3.

**L2 topic** is one file per topic, named <prefix>-<topic>.md. The split test is whether trigger
words are mutually exclusive: if two topics can never be hit by the same question, split them.

**L3 journal** is appended daily and records the raw process: what was tried, why it failed, the
final commit. It is never injected, only read as search hits. The journal is the only layer
allowed to be verbose.

**L4 cold** holds what is stale but may be worth recalling. Archiving must update the hot index at
the same time, otherwise it is a deletion. Names carry a date suffix, and synonymous directories
such as `archive/` and `_archive/` must not coexist. The same test governs data retention: export
with a checksum and a manifest first, then delete — a delete without a verified copy is destruction,
not housekeeping.

**中文**

**L0 协议**放身份、语气、红线与路由 —— 只有永远成立的规则。任何会变的东西（今天用哪个模型、某个服务跑在哪个端口）都不属于这里。

**L1 索引**是三张表，覆盖 80% 的读取：文档地图（去哪找 → 从哪跳）、硬规则（违反就要返工）、触发词（听到什么 → 打开哪个文件）。只放现状、规则与指针；实现历史一律进 L3。

**L2 主题**是一个主题一个文件，命名 <前缀>-<主题>.md。拆分判据是触发词是否互斥：如果两个主题永远不会被同一个问题命中，就拆开。

**L3 日志**每日追加，记录原始过程：试过什么、为什么失败、最终的 commit。它从不被注入，只作为检索命中被读取。日志是唯一允许啰嗦的层。

**L4 冷层**放已经陈旧、但可能值得回溯的东西。归档时必须同步更新热索引，否则那就是一次删除。文件名带日期后缀，`archive/` 与 `_archive/` 这类同义目录不得并存。数据保留期沿用同一条判据：先带校验和与 manifest 导出，再删 —— 没有可校验副本的删除是销毁，不是清理。

## The one hard test

> Before writing to L0/L1, ask: **will this still be true a year from now?**
> No → L3. True only for one topic → L2. A cross-topic rule → L1.

**中文**

> 写进 L0/L1 之前先问：**一年之后这还成立吗？**
> 不成立 → L3。只对一个主题成立 → L2。跨主题的规则 → L1。

## Common mistakes

- Writing "the current implementation" into the protocol layer → six months later protocol and
  code contradict each other.
- Filling the index with past decisions → the budget is eaten and the entry points you actually
  need can no longer be found.
- Writing the journal like documentation (structured, polished) → the field evidence is gone and
  every failure cause is smoothed away.

**中文**

- 把「当前的实现」写进协议层 → 六个月后协议和代码互相矛盾。
- 用过去的决策塞满索引 → 预算被吃掉，真正需要的入口再也找不到。
- 把日志写成文档（结构化、打磨过）→ 现场证据没了，每一个失败原因都被抹平。
