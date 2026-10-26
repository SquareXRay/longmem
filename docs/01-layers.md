# 01 · The five-layer model and injection budgets

## Budget before content

The system prompt is the scarce resource. Set the budget first, then decide where anything gets
written:

| Layer | Budget | Action when exceeded |
|---|---|---|
| L0 protocol | ~2 KB × 3 files | keep rules only, push the narrative down to the topic layer |
| L1 index | 36 KB | split into topics; L1 keeps a one-line pointer |
| L2 topic | 40 KB per file | split into monthly volumes, body to the cold layer |
| L3 journal | no daily cap (append-only) | archive after 4 weeks idle |
| L4 cold | 36 KB per volume | split again, keep the index hot |

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
such as `archive/` and `_archive/` must not coexist.

## The one hard test

> Before writing to L0/L1, ask: **will this still be true a year from now?**
> No → L3. True only for one topic → L2. A cross-topic rule → L1.

## Common mistakes

- Writing "the current implementation" into the protocol layer → six months later protocol and
  code contradict each other.
- Filling the index with past decisions → the budget is eaten and the entry points you actually
  need can no longer be found.
- Writing the journal like documentation (structured, polished) → the field evidence is gone and
  every failure cause is smoothed away.

## 中文摘要

- 系统提示是稀缺资源，先定预算：L0 ~2 KB × 3、L1 36 KB、L2 单文件 40 KB、冷层单卷 36 KB。
- 超预算的动作是「往下拆」而不是删内容：L1 超了拆主题、L2 超了按月分卷、冷层超了再分卷并保留热层索引。
- 每层只干一件事：协议层只放永远成立的规则，索引层只放现状、规则与指针，日志层才是唯一允许啰嗦的地方。
- 拆分判据是「触发词是否互斥」，不是文件大小。
- 一条硬判据：写进 L0/L1 之前先问「一年后还成立吗」——不成立进 L3，只对一个主题成立进 L2。
- 常见错误：把当前实现写进协议层、索引塞满历史决策、把日志写成文档。
