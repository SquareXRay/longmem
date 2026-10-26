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

**中文**

一次全量向量重建是在**资源受限的单机**上实测的：几百个文件花了约两小时，负载冲到 5.7，重建跑着的时候会话请求被饿死。结论：

- 重建成本 ≫ 检索收益（整个语料只有几百 KB 到几 MB 的量级）。
- 增量索引更糟：写入路径要同步、要处理删除，还要防索引与正文漂移。
- 你真正需要的是**精确召回** —— 「那个坑我记在哪了」—— 而这类需求上关键词搜索胜过语义搜索。

所以：**一个入口，纯 grep，可解释，而且失败看得见。**

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
