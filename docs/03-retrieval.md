# 03 · Retrieval: weighted grep, not vectors

## Why not embeddings

A full embedding rebuild was measured on a **resource-constrained single machine**: a few hundred
files took about two hours, load hit 5.7, and session requests were starved while it ran. Verdict:

- Rebuild cost ≫ retrieval benefit (the whole corpus is in the hundreds-of-KB to few-MB range).
- Incremental indexing is worse: the write path has to sync, handle deletes, and defend against
  drift between index and text.
- What you actually need is **exact recall** — "where did I write that trap down" — and keyword
  search beats semantic search for that.

So: **one entry point, plain grep, explainable, and failures are visible.** Operationally the
ranking provider is pinned to keyword/FTS and the semantic provider stays off; turning it on is a
measured change of its own, not a setting someone flips for a week.

**中文**

一次全量向量重建是在**资源受限的单机**上实测的：几百个文件花了约两小时，负载冲到 5.7，重建跑着的时候会话请求被饿死。结论：

- 重建成本 ≫ 检索收益（整个语料只有几百 KB 到几 MB 的量级）。
- 增量索引更糟：写入路径要同步、要处理删除，还要防索引与正文漂移。
- 你真正需要的是**精确召回** —— 「那个坑我记在哪了」—— 而这类需求上关键词搜索胜过语义搜索。

所以：**一个入口，纯 grep，可解释，而且失败看得见。** 落地时排序只在关键词 / FTS 这一侧，语义 provider 保持关闭；要打开它必须当成一次独立的、带实测的变更，而不是谁顺手改个开关试一周。

## Scoring

```
score = (term hits / sqrt(file bytes + 1)) * tier weight + 0.5 (exact phrase match)
```

Tier weights (empirical, ordered by "higher layers should be read first"):

| File | Weight |
|---|---|
| protocol | 1.35 |
| index | 1.30 |
| topic | 1.25 |
| directory index | 1.05 |
| journal | 0.55 |

Dividing by sqrt(length) is what stops the journal from always winning.

**中文**

打分公式（代码块同上）：得分 =（命中词元数 / sqrt(文件字节数 + 1)）× 层级权重 + 0.5（整句精确命中）。

层级权重（经验值，按「越靠上的层越该先读」排序）：

| 文件 | 权重 |
|---|---|
| 协议 | 1.35 |
| 索引 | 1.30 |
| 主题 | 1.25 |
| 目录索引 | 1.05 |
| 日志 | 0.55 |

除以 sqrt(长度) 正是让日志不再永远霸榜的原因。

## Tokenization

Chinese has no spaces, so split into **bigrams**: 记忆架构 → 记忆 / 忆架 / 架构. Latin words and
digits are lowercased whole tokens. The raw query string is kept as well, for the exact-match
bonus.

**中文**

中文没有空格，所以切成 **bigram**：记忆架构 → 记忆 / 忆架 / 架构。拉丁词与数字整词小写。查询原文也一并保留，用于精确命中加分。

## Budget

- Skip files over 2 MB — usually logs or data, not answers.
- Five-second total budget; on timeout, abort and return a "skipped" marker. Better to return less
  than to hang.
- Persist only a hash of the query plus the hit count, for observing cold queries — never the
  query text.

**中文**

- 超过 2 MB 的文件直接跳过 —— 那通常是日志或数据，不是答案。
- 总预算 5 秒；超时即中止，返回一个「已跳过」标记。少返回一点，好过挂住。
- 只持久化查询的 hash 加命中数，用来观察冷查询 —— 绝不存查询原文。

## What comes back

{file, path, score, matching line snippet (≤120 characters)} — enough to decide whether to open the
full text. Opening the text is left to the next step, so one search does not blow up the context.

**中文**

{file, path, score, 命中行片段（≤120 字符）} —— 足够判断要不要打开全文。打开全文留给下一步，于是一次检索不会把上下文撑爆。


## Two similarity thresholds, never one

Scoring a *short entry* against another *short entry* is a different measurement from scoring a
*long query* against a short entry.

| Comparison | Threshold |
|---|---|
| entry ↔ entry (near-duplicate, advisory candidates) | 0.25 primary, 0.22 watch |
| query ↔ entry (which two incidents to inject) | 0.10 |

The reason is length dilution: a query carries a label, a file set and an acceptance criterion, so
Jaccard collapses. Measured against a full ledger, the best query↔entry score was 0.158 and the top
six sat at 0.107–0.158 — keeping 0.25 there would fall back on every single task, which is a silent
deactivation rather than a safety margin. The fallback (best score below the line) is "newest entry
of the same class", and it is labelled as a fallback so it can be counted.

The rest of that injection, for reference: at most 2 entries, 120 bytes of body each, 800 bytes of
digest in total, a 0.05 penalty for crossing classes, and no injection when a static mini-memory
line already covers the entry (bigram coverage ≥ 0.5).

**中文**

拿**短条目**和另一条**短条目**比，与拿**长查询**和短条目比，是两种不同的度量。

| 比较 | 阈值 |
|---|---|
| 条目 ↔ 条目（近重复、advisory 候选） | 主线 0.25，观察线 0.22 |
| 查询 ↔ 条目（注入哪两条错题） | 0.10 |

原因是长度稀释：查询里带着标签、文件集和验收判据，Jaccard 会被摊薄。在全卷上实测，查询↔条目的最高分只有 0.158，前六名落在 0.107–0.158 —— 这里继续用 0.25 会导致每个任务都回退，那不是安全边际，而是静默停用。回退策略（最高分低于线）是「同类别最新一条」，并且会被明确标记为回退，以便统计。

同一条注入链的其余常数一并记下：最多 2 条、正文各 120 字节、摘要合计 800 字节、跨类扣 0.05、若该条目已被静态 mini-memory 行覆盖（bigram 覆盖率 ≥ 0.5）则不重复注入。
