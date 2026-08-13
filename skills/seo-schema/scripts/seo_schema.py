#!/usr/bin/env python3
"""seo-schema helper: meta/headings/img audit + JSON-LD validation.

Pure Python 3 stdlib (html.parser, json, argparse). No external deps.
Usage:
  python3 seo_schema.py --meta <file.html>       # title/description/OG/canonical/h1/img
  python3 seo_schema.py --jsonld <file.html>     # extract + validate JSON-LD blocks
  Read from stdin when no file given.
"""
import argparse
import json
import sys
from html.parser import HTMLParser


class SeoParser(HTMLParser):
    """Extract meta tags, canonical, OG, headings and img alt attributes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.title = None
        self.canonical = None
        self.headings = []
        self.imgs = []
        self._in_title = False
        self._in_heading = False
        self._heading_buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = a.get("name") or a.get("property") or a.get("http-equiv")
            if key and a.get("content") is not None and key not in self.meta:
                self.meta[key] = a["content"]
        if tag in ("link",) and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._in_heading = True
            self._heading_buf = []
        if tag == "img":
            self.imgs.append((a.get("src", ""), a.get("alt")))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append((tag, " ".join("".join(self._heading_buf).split())))
            self._in_heading = False

    def handle_data(self, data):
        if self._in_title:
            self.title = self.title + data if self.title else data
        if self._in_heading:
            self._heading_buf.append(data)


class SelectJsonldParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.jsonld_blocks = []
        self._in = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._in = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "script" and self._in:
            self.jsonld_blocks.append("".join(self._buf))
            self._in = False

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)


def read_source(path):
    if path:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    return sys.stdin.read()


def cmd_meta(path):
    html = read_source(path)
    p = SeoParser()
    p.feed(html)
    print(f"title: {p.title.strip() if p.title else '(missing)'}")
    print(f"title_len: {len(p.title or '')}")
    print(f"description: {p.meta.get('description', '(missing)')}")
    print(f"canonical: {p.canonical or '(missing)'}")
    for key in ("og:title", "og:description", "og:image", "twitter:card"):
        print(f"{key}: {p.meta.get(key, '(missing)')}")
    if p.meta.get("robots"):
        print(f"robots: {p.meta['robots']}")
    print("--- headings ---")
    for lvl, text in p.headings:
        print(f"{lvl}: {text}")
    missing_alt = [src for src, alt in p.imgs if not alt]
    print(f"--- imgs: total={len(p.imgs)}, missing_alt={len(missing_alt)}")
    for src in missing_alt[:10]:
        print(f"  no-alt: {src[:80]}")


def cmd_jsonld(path):
    html = read_source(path)
    p = SelectJsonldParser()
    p.feed(html)
    print(f"json_ld_blocks: {len(p.jsonld_blocks)}")
    for i, block in enumerate(p.jsonld_blocks, 1):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            print(f"  block {i}: INVALID JSON — {e}")
            continue
        types = data.get("@type") if isinstance(data, dict) else "?list"
        errors = []
        if isinstance(data, dict):
            if not data.get("@context", "").startswith("https://schema.org"):
                errors.append("missing @context https://schema.org")
            t = data.get("@type")
            if not t:
                errors.append("missing @type")
            if t == "Product" and "offers" not in data and "name" not in data:
                errors.append("Product: expected name+offers")
            if t in ("Article", "BlogPosting") and not (
                data.get("headline") and data.get("author")
            ):
                errors.append("Article: expected headline+author")
            if t == "FAQPage" and "mainEntity" not in data:
                errors.append("FAQPage: expected mainEntity")
            if t == "Organization" and not (data.get("name") and data.get("url")):
                errors.append("Organization: expected name+url")
        print(f"  block {i}: @type={types} — {'OK' if not errors else '; '.join(errors)}")


def main():
    ap = argparse.ArgumentParser(description="seo-schema helper: meta/headings/img + JSON-LD")
    ap.add_argument("--meta", action="store_true", help="meta/headings/img audit")
    ap.add_argument("--jsonld", action="store_true", help="JSON-LD validation")
    ap.add_argument("--file", help="HTML file (or stdin if omitted)")
    ap.add_argument("paths", nargs="*", help="HTML file (positional)")
    args = ap.parse_args()
    file = args.file or (args.paths[0] if args.paths else None)
    if args.meta:
        cmd_meta(file)
    elif args.jsonld:
        cmd_jsonld(file)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
