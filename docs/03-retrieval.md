# 03 · Retrieval: weighted grep, not vectors

## Why not embeddings

A full embedding rebuild was measured on a **resource-constrained single machine**: a few hundred
files took about two hours, load hit 5.7, and session requests were starved while it ran. Verdict:

- Rebuild cost ≫ retrieval benefit (the whole corpus is in the hundreds-of-KB to few-MB range).
- Incremental indexing is worse: the write path has to sync, handle deletes, and defend against
  drift between index and text.
- What you actually need is **exact recall** — "where did I write that trap down" — and keyword
  search beats semantic search for that.

So: **one entry point, plain grep, explainable, and failures are visible.**

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

## Tokenization

Chinese has no spaces, so split into **bigrams**: 记忆架构 → 记忆 / 忆架 / 架构. Latin words and
digits are lowercased whole tokens. The raw query string is kept as well, for the exact-match
bonus.

## Budget

- Skip files over 2 MB — usually logs or data, not answers.
- Five-second total budget; on timeout, abort and return a "skipped" marker. Better to return less
  than to hang.
- Persist only a hash of the query plus the hit count, for observing cold queries — never the
  query text.

## What comes back

{file, path, score, matching line snippet (≤120 characters)} — enough to decide whether to open the
full text. Opening the text is left to the next step, so one search does not blow up the context.

## 中文摘要

- 在资源受限的单机上实测过全量向量重建：几百个文件约两小时、负载 5.7、期间请求被挤掉，而记忆总量只有几百 KB 量级——重建成本远大于检索收益。
- 增量索引更糟（写入同步、删除处理、索引与正文漂移），真正需要的是「那条坑记在哪」这种精确命中。
- 于是只用**单一入口 + 纯 grep + 层级权重打分**：命中次数除以 sqrt(字节数)，再乘层级权重，整句精确命中加 0.5。
- 权重按「越靠上越该先读」：协议 1.35 / 索引 1.30 / 主题 1.25 / 目录索引 1.05 / 日志 0.55；除以长度是为了不让长日志霸榜。
- 中文按 bigram 切分，英文与数字整词小写，查询原文保留用于精确加分。
- 单文件 > 2 MB 直接跳过；总预算 5 秒、超时返回「已跳过」；查询只落 hash + 命中数，不留原文。
- 返回片段（≤120 字符）够判断要不要打开全文，避免一次检索把上下文撑爆。
