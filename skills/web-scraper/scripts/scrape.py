#!/usr/bin/env python3
"""web-scraper: polite HTML scraping with robots.txt, rate limit and size cap.

Extracts rows/sections under a simple CSS selector (tag, tag#id, tag.class)
from a URL and prints them as Markdown or JSON. Python 3 stdlib only.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

USER_AGENT = "Mozilla/5.0 (compatible; web-scraper/1.0; +educational)"
MAX_BYTES = 10 * 1024 * 1024
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}


def parse_selector(selector):
    """'div#list' -> ('div', {'id': 'list'}); supports tag, tag#id, tag.class."""
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9]*)?((?:[.#][a-zA-Z0-9_-]+)*)$", selector.strip())
    if not m:
        raise ValueError(f"invalid selector {selector!r}: use tag, tag#id or tag.class")
    tag = m.group(1)
    attrs = {}
    for part in re.findall(r"[.#][a-zA-Z0-9_-]+", m.group(2)):
        if part[0] == "#":
            attrs["id"] = part[1:]
        else:
            attrs.setdefault("class", []).append(part[1:])
    return tag, attrs


def _matches(tag, attrs, want_tag, want_attrs):
    if want_tag and tag != want_tag:
        return False
    for key, value in want_attrs.items():
        if key == "class":
            classes = attrs.get("class", "").split()
            if not all(c in classes for c in value):
                return False
        elif attrs.get(key) != value:
            return False
    return True


class ScrapeParser(HTMLParser):
    """Collects text, links and tables under each selector match."""

    def __init__(self, want_tag, want_attrs):
        super().__init__(convert_charrefs=True)
        self.want_tag = want_tag
        self.want_attrs = want_attrs
        self.title = ""
        self.items = []
        self._stack = []
        self._item = None
        self._item_depth = 0
        self._text = []
        self._link = None
        self._table = None
        self._row = None
        self._cell = None
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
            return
        if tag in VOID_TAGS:
            return
        attrs = dict(attrs)
        self._stack.append(tag)
        if self._item is not None:
            self._collect_child(tag, attrs)
        elif _matches(tag, attrs, self.want_tag, self.want_attrs):
            self._item = {"links": [], "tables": []}
            self._item_depth = len(self._stack)
        if tag == "title":
            self._in_title = True

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
            return
        if tag == "title":
            self._in_title = False
        if self._item is not None:
            if tag == "a":
                self._link = None
            elif tag == "table":
                self._table = None
            elif tag == "tr":
                self._row = None
            elif tag in ("td", "th"):
                self._cell = None
            if self._stack and self._stack[-1] == tag:
                self._stack.pop()
                if tag == self.want_tag and len(self._stack) == self._item_depth - 1:
                    self._finalize_item()
        elif self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
            return
        if self._item is None:
            return
        if self._cell is not None:
            self._cell.append(data)
        elif self._link is not None:
            self._link["text"] += data
        elif self._row is not None:
            pass
        else:
            self._text.append(data)

    def close(self):
        super().close()
        if self._item is not None:
            self._finalize_item()

    def _collect_child(self, tag, attrs):
        if tag == "a" and attrs.get("href"):
            self._link = {"text": "", "href": attrs["href"]}
            self._item["links"].append(self._link)
        elif tag == "table":
            self._table = []
            self._item["tables"].append(self._table)
        elif tag == "tr" and self._table is not None:
            self._row = []
            self._table.append(self._row)
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            self._row.append(self._cell)

    def _finalize_item(self):
        text = " ".join("".join(self._text).split())
        links = [{"text": link["text"].strip(), "href": link["href"]}
                 for link in self._item["links"]]
        tables = []
        for table in self._item["tables"]:
            rows = []
            for row in table:
                cells = [" ".join("".join(cell).split()) for cell in row]
                if any(cells):
                    rows.append(cells)
            if rows:
                tables.append(rows)
        self.items.append({"text": text, "links": links, "tables": tables})
        self._item = None
        self._text = []


def _robots_groups(body):
    groups = []
    current = None
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            current = {"agents": [a.strip().lower() for a in value.split(",") if a.strip()],
                       "rules": []}
            groups.append(current)
        elif key in ("allow", "disallow") and current is not None:
            current["rules"].append((key, value))
    return groups


def _matching_group(groups, ua):
    wildcard = None
    for group in groups:
        for agent in group["agents"]:
            if agent == "*":
                wildcard = group
            elif agent and agent in ua:
                return group
    return wildcard


def _path_allowed(rules, path):
    best = None
    for kind, rule_path in rules:
        if not rule_path:
            continue
        if path.startswith(rule_path):
            if best is None or len(rule_path) > best[0]:
                best = (len(rule_path), kind == "allow")
    return True if best is None else best[1]


def robots_allows(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return True
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError):
        return True
    group = _matching_group(_robots_groups(body), USER_AGENT.lower())
    if group is None:
        return True
    return _path_allowed(group["rules"], parsed.path or "/")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        chunks = []
        total = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError(f"page exceeds {MAX_BYTES // (1024 * 1024)} MB limit")
            chunks.append(chunk)
    return b"".join(chunks)


def render_markdown(title, url, items):
    lines = [f"# {title}", "", f"Источник: {url}", ""]
    lines.append(f"## Элементы ({len(items)})")
    lines.append("")
    for i, item in enumerate(items, 1):
        lines.append(f"### Элемент {i}")
        lines.append("")
        if item["text"]:
            lines.append(item["text"])
            lines.append("")
        if item["links"]:
            lines.append("Ссылки:")
            for link in item["links"]:
                label = link["text"] or link["href"]
                lines.append(f"- [{label}]({link['href']})")
            lines.append("")
        for table in item["tables"]:
            lines.append(_render_table(table))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_table(table):
    width = max(len(row) for row in table)
    rows = [row + [""] * (width - len(row)) for row in table]
    out = ["| " + " | ".join(rows[0]) + " |"]
    out.append("| " + " | ".join("---" for _ in rows[0]) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def render_json(title, url, items):
    return json.dumps({
        "title": title,
        "url": url,
        "matched": len(items),
        "items": [{"text": item["text"], "href": [link["href"] for link in item["links"]]}
                  for item in items],
    }, ensure_ascii=False, indent=2)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Polite HTML scraping (stdlib only).")
    parser.add_argument("--url", required=True, help="page URL (http/https/file)")
    parser.add_argument("--selector", required=True, help="selector: tag, tag#id, tag.class")
    parser.add_argument("--output", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    args = parser.parse_args(argv)

    url = args.url
    try:
        tag, attrs = parse_selector(args.selector)
        scheme = urllib.parse.urlparse(url).scheme
        if scheme not in ("http", "https", "file"):
            raise ValueError(f"unsupported scheme {scheme!r} (use http, https or file)")
        if scheme in ("http", "https"):
            if not robots_allows(url):
                print(f"robots.txt disallows {url}; skipping", file=sys.stderr)
                return 3
            if args.delay > 0:
                time.sleep(args.delay)
        html = fetch(url).decode("utf-8", "replace")
        sp = ScrapeParser(tag, attrs)
        sp.feed(html)
        sp.close()
        title = sp.title.strip() or url
        if args.output == "json":
            print(render_json(title, url, sp.items))
        else:
            print(render_markdown(title, url, sp.items))
        return 0
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except urllib.error.HTTPError as e:
        print(f"error: HTTP {e.code} {e.reason} for {url}", file=sys.stderr)
        return 2
    except urllib.error.URLError as e:
        print(f"error: cannot fetch {url}: {e.reason}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: cannot fetch {url}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
