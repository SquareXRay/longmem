#!/usr/bin/env python3
"""memory_search.py - single retrieval entry: grep + CJK bigram + tier weighting.

No index, no embeddings, no LLM. Read-only.

Usage:
    python3 memory_search.py "query terms" --root ./examples/greenhouse [--top 5] [--daily]
"""
import argparse
import json
import math
import os
import re
import sys
import time

MAX_BYTES = 2 * 1024 * 1024
BUDGET_S = 5.0
SNIPPET_CHARS = 120

CJK = re.compile(r"[\u4e00-\u9fa5]")
DAILY = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def tokens(query):
    """Split a query into search grams: CJK -> bigrams, latin -> lowercase words."""
    clean = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]+", " ", query)
    grams = []
    for part in clean.split():
        if CJK.search(part):
            if len(part) == 1:
                grams.append(part)
            else:
                grams.extend(part[i:i + 2] for i in range(len(part) - 1))
        elif len(part) > 1:
            grams.append(part.lower())
    return grams


def candidates(root, include_daily=False, daily_dir_name="memory"):
    files = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isfile(path) and name.endswith(".md") and name.lower() != "readme.md":
            files.append(path)
    daily_dir = os.path.join(root, daily_dir_name)
    if include_daily and os.path.isdir(daily_dir):
        for name in sorted(os.listdir(daily_dir)):
            if DAILY.match(name):
                files.append(os.path.join(daily_dir, name))
    return files


def tier(path):
    name = os.path.basename(path)
    if name in ("AGENTS.md", "SOUL.md", "USER.md"):
        return 1.35
    if name in ("MEMORY.md", "memory-index.md"):
        return 1.30
    if name.startswith("MEMORY-") or name.startswith("memory-"):
        return 1.25
    if name == "INDEX.md":
        return 1.05
    if DAILY.match(name):
        return 0.55
    return 1.0


def score_file(path, grams, phrase):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None, None, "too-large"
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        return None, None, str(exc)

    low = text.lower()
    hits = sum(low.count(g) for g in grams)
    score = (hits / math.sqrt(len(text) + 1)) * tier(path)
    if phrase and phrase.lower() in low:
        score += 0.5

    snippet = ""
    for g in grams:
        i = low.find(g)
        if i >= 0:
            start = text.rfind(chr(10), 0, i) + 1
            end = text.find(chr(10), i)
            snippet = text[start:end if end > 0 else i + SNIPPET_CHARS][:SNIPPET_CHARS]
            break
    return score, snippet, None


def search(query, root, top, include_daily=False, daily_dir_name="memory"):
    grams = tokens(query)
    if not grams:
        return [], ["empty-query"], 0
    started = time.time()
    results, skipped = [], []
    for path in candidates(root, include_daily, daily_dir_name):
        if time.time() - started > BUDGET_S:
            skipped.append("budget")
            break
        score, snippet, err = score_file(path, grams, query)
        if err:
            skipped.append([os.path.basename(path), err])
            continue
        if score and score > 0:
            results.append({
                "file": os.path.basename(path),
                "path": path,
                "score": round(score, 3),
                "snippet": snippet,
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top], skipped, int((time.time() - started) * 1000)


def main(argv=None):
    ap = argparse.ArgumentParser(description="grep + bigram memory search")
    ap.add_argument("query")
    ap.add_argument("--root", default=".", help="memory root directory")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--daily", action="store_true", help="include daily notes YYYY-MM-DD.md")
    ap.add_argument("--daily-dir", default="memory", help="daily notes subdirectory (default: memory)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("not a directory: %s" % root, file=sys.stderr)
        return 2

    results, skipped, took = search(args.query, root, args.top, args.daily, args.daily_dir)
    if args.json:
        print(json.dumps({"query": args.query, "took_ms": took,
                          "skipped": skipped, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print("%.3f  %-24s %s" % (r["score"], r["file"], r["snippet"]))
        if not results:
            print("(no match)")
        if skipped:
            print("skipped: %s" % skipped, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
