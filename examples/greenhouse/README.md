# Example: a project with memory (synthetic)

本目录是一个**虚构**的记忆库，用来演示分层与检索。所有数据都是假的。
This directory is a **synthetic** memory root used to demonstrate the layers and retrieval.
Every value in it is made up.

| 这里 · here | 部署时 · in a real deployment |
|---|---|
| memory-index.md | the always-injected index file |
| memory-sensors.md | one file per topic, read on trigger |
| mistakes.md | incident ledger (hot tier) |
| journal/2026-01-15.md | daily journal, never injected |

Retrieval demo:

```bash
python3 ../../scripts/memory_search.py "丢包率" --root . --daily --daily-dir journal
python3 ../../scripts/memory_search.py "回放 内存" --root . --daily --daily-dir journal --json
```

Why `journal/` instead of `memory/` here? So that a public example never collides with the
protected paths of the system it was extracted from. In your own project, name it whatever
your tooling expects.
