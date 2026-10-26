# 01 · 五层模型与注入预算

## 预算先于内容

系统提示是稀缺资源。先定预算，再决定写哪里：

| 层 | 上限 | 超出后的动作 |
|---|---|---|
| L0 协议 | ~2 KB × 3 文件 | 只留规则，把叙述删到主题层 |
| L1 索引 | 36 KB | 拆主题：L1 只留一行指针 |
| L2 主题 | 单文件 40 KB | 按月分卷，正文进冷层 |
| L3 日志 | 单日不设上限（只增不改） | 超过 4 周不动就归档 |
| 冷层 | 单卷 36 KB | 再分卷，索引留在热层 |

## 各层职责（不要混）

**L0 协议层**：身份、语气、红线、路由。只写「永远成立的规则」。
事实变化的东西（今天用什么模型、服务跑在哪个端口）不属于这里。

**L1 索引层**：三张表覆盖 80% 的读取需求——文档地图（看哪→跳哪）、
硬规则（违反=返工）、触发词（听到什么→读哪个文件）。
**只放现状 + 规则 + 指针**，实现过程一律进 L3。

**L2 主题层**：一个主题一个文件，命名 <前缀>-<主题>.md。
拆分判据是「触发词是否互斥」：两个主题永远不会被同一次提问命中，就拆。

**L3 日志层**：按天追加，写原始过程：试了什么、为什么失败、最终 commit。
**永不注入**，只在检索命中时读片段。日志是唯一允许啰嗦的层。

**L4 冷层**：过时但可能有回溯价值的内容。归档动作必须同时更新热层索引，
否则等于删除。命名带日期后缀，禁止 archive/ 与 _archive/ 这类同义目录并存。

## 一条硬判据

> 想写进 L0/L1 的内容，先回答：**它一年后还成立吗？**
> 不成立 → L3。只对某个主题成立 → L2。跨主题的规则 → L1。

## 常见错误

- 把「当前实现」写进协议层 → 半年后协议和代码互相打脸。
- 索引层写满历史决策 → 预算被吃干，真正要读的入口反而找不到。
- 日志层当文档写（结构化、修饰过）→ 丢了现场信息，失败原因全被抹平。

## English

### Budget before content

The system prompt is the scarce resource. Set the budget first, then decide what gets written.

| Layer | Budget | When it overflows |
|---|---|---|
| L0 protocol | ~2 KB × 3 files | keep rules only, move narrative down |
| L1 index | 36 KB | split into topic files, leave a one-line pointer |
| L2 topic | 40 KB per file | monthly volumes, body to cold layer |
| L3 journal | unlimited (append-only) | archive after 4 weeks idle |
| cold | 36 KB per volume | split again, keep the index hot |

### One job per layer

**L0 protocol** holds identity, tone, red lines, routing — rules that never change.
Anything that changes (which model, which port) does not belong here.

**L1 index** needs three tables to cover most reads: a map (where to look), hard rules
(violation means rework), and trigger words (what the user says → which file to open).
It stores current state, rules and pointers — never implementation history.

**L2 topic**: one file per topic. Split when trigger words are mutually exclusive.
**L3 journal**: append what you actually tried, why it failed, and the commit. Never injected,
only searched. The journal is the only layer allowed to be verbose.
**L4 cold**: stale but worth keeping. Archiving must update the hot index, otherwise it is a delete.

### The one hard test

> Before writing to L0/L1, ask: will this still be true in a year?
> No → L3. Only for one topic → L2. Cross-cutting rule → L1.

### Common mistakes

- Writing "current implementation" into the protocol layer; six months later it contradicts the code.
- Filling the index with history until the real entry points are buried.
- Writing the journal like documentation — the failure evidence gets polished away.
