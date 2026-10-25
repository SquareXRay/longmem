# 03 · 检索：grep 加权，不用向量

## 为什么不用 embedding

在**资源受限的单机**上实测过全量重建向量索引：几百个文件跑了约两小时，
系统负载打到 5.7，期间会话请求被挤掉。结论：

- 重建成本 ≫ 检索收益（记忆总量在几百 KB～几 MB 量级）。
- 增量索引维护更糟：写入路径要同步、要处理删除、要防索引与正文漂移。
- 真正需要的是**精确命中**：「那条坑记在哪」——关键词检索比语义检索更准。

于是：**单一入口、纯 grep、可解释、失败可见**。

## 打分

```
score = (命中词次数 / sqrt(文件字节数 + 1)) * 层级权重 + 0.5（整句精确命中）
```

层级权重（经验值，按「越靠上越该先读」排）：

| 文件 | 权重 |
|---|---|
| 协议层 | 1.35 |
| 索引层 | 1.30 |
| 主题层 | 1.25 |
| 目录索引 | 1.05 |
| 日志层 | 0.55 |

除以 sqrt(长度) 是为了压住长文件——否则日志层永远霸榜。

## 分词

中文没有空格，按 **bigram** 切：「记忆架构」→ 记忆/忆架/架构。
英文/数字整词小写。查询里同时保留原串，用于精确命中加分。

## 预算

- 单文件 > 2 MB 跳过（多半是日志或数据，不该进结果）。
- 总预算 5 秒，超时中止并返回「已跳过」标记——宁可少给，不可卡死。
- 查询落盘只记 hash + 命中数，用于观察冷查询，不记原文。

## 返回什么

{文件, 路径, 分数, 命中行片段(≤120字符)}——片段足够决定要不要打开全文。
把「读全文」留给下一步，避免一次检索把上下文撑爆。

## English

### Why not embeddings

A full embedding rebuild over a few hundred files took about two hours on a resource-constrained
single machine, pushed load to 5.7, and starved session requests while it ran. The corpus itself
was only a few hundred KB. Conclusions:

- Rebuild cost far exceeds retrieval benefit at this size.
- Incremental index maintenance is worse: writes, deletes, and drift between index and text.
- What you actually need is **exact recall** ("where did I write that trap down"), and keyword
  search beats semantic search for that.

So: one entry point, plain grep, explainable, and failures are visible.

### Scoring

```
score = (sum of term hits / sqrt(bytes + 1)) * tier_weight + 0.5 (exact phrase bonus)
```

| File | Weight |
|---|---|
| protocol | 1.35 |
| index | 1.30 |
| topic | 1.25 |
| directory index | 1.05 |
| journal | 0.55 |

Dividing by sqrt(length) stops long logs from always winning.

### Tokenization

Chinese has no spaces, so split into bigrams: 记忆架构 → 记忆 / 忆架 / 架构. Latin and digits
are lowercased whole words. The raw query is kept for the exact-phrase bonus.

### Budget

- Skip files over 2 MB — usually logs or data, not answers.
- Five-second budget; on timeout return partial results plus a "skipped" marker.
- Log only a query hash and hit count, never the query text.

### Output

`{file, path, score, matching line (≤120 chars)}` — enough to decide whether to open the file.
Reading the full text is a separate, deliberate step.
