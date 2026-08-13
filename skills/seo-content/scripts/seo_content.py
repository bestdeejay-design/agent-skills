#!/usr/bin/env python3
"""seo-content helper: keyword density + top terms.

Pure Python 3 stdlib (re, argparse). No external deps.
Usage:
  python3 seo_content.py --density --file <file.html> --keyword <kw>
  Read from stdin when no file given.
"""
import argparse
import re
import sys

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "for", "with", "on",
    "in", "at", "from", "by", "is", "are", "was", "were", "be", "it", "this",
    "that", "as", "we", "you", "your", "our", "their", "i", "he", "she", "they",
}


def read_source(path):
    if path:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    return sys.stdin.read()


def cmd_density(path, keyword):
    html = read_source(path)
    # Strip <script>/<style> content first: CSS/JS source is not visible text
    # and must not inflate the word count (density gets skewed ~2-3x otherwise).
    text = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1\s*>", " ", html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).lower()
    words = re.findall(r"[a-zа-я0-9]+", text)
    total = len(words)
    kw = keyword.lower().strip()
    kw_hits = text.count(kw)
    density = 100.0 * kw_hits / total if total else 0.0
    freq = {}
    for w in words:
        if len(w) > 2 and w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda x: -x[1])[:15]
    print(f"words_total: {total}")
    print(f"keyword: {kw}")
    print(f"keyword_hits: {kw_hits}")
    print(f"density: {density:.2f}%")
    print("top_terms:")
    for w, c in top:
        print(f"  {w}: {c}")


def main():
    ap = argparse.ArgumentParser(description="seo-content helper: keyword density")
    ap.add_argument("--density", action="store_true", help="keyword density")
    ap.add_argument("--file", help="HTML file (or stdin if omitted)")
    ap.add_argument("--keyword", default="", help="keyword for --density")
    ap.add_argument("paths", nargs="*", help="HTML file (positional)")
    args = ap.parse_args()
    file = args.file or (args.paths[0] if args.paths else None)
    if args.density:
        if not args.keyword:
            ap.error("--density requires --keyword")
        cmd_density(file, args.keyword)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
