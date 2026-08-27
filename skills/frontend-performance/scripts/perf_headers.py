#!/usr/bin/env python3
"""
frontend-performance — perf_headers.py

Offline-capable performance auditor. Pure Python 3 standard library only
(no requests, no PyYAML, no third-party packages).

Two modes:

  1. URL mode  (--url <http(s)://...>)
     Fetches the target with urllib.request (HEAD then GET) and inspects
     response headers + protocol version + transfer timing for the
     network/header layer of the Front-End-Checklist Performance rules:
       - HTTP/2 or /3 (best-effort; urllib is HTTP/1.1 only — see note)
       - text compression (content-encoding: gzip/brotli)
       - browser caching (cache-control / etag)
       - HSTS + reused security headers
       - content-type correctness
       - TTFB (from response timing)

  2. Directory mode  (--dir <path>)
     Analyzes a built asset tree (static HTML/CSS/JS or a bundled SPA):
       - total page weight (warn >1500KB, ideal <500KB)
       - largest JS/CSS files
       - duplicate JS libraries (content-hash + version-stripped name)
       - missing preload for above-the-fold critical resources
       - GIF usage (candidate for video conversion)
       - source-map presence, service worker registration, speculationrules,
         fetchpriority / preconnect / resource hints, lazy-loading hints

Both modes emit a single JSON report and use exit codes:
  0 = no `fail` checks (pass/warn/info acceptable)
  1 = at least one `fail`
  2 = runner error (bad URL, unreachable host, unreadable dir)

The script deliberately does NOT reimplement the contrast/token/SEO/a11y
checks owned by frontend-perfection — it owns performance depth only.
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict

# --------------------------------------------------------------------------
# Constants / thresholds
# --------------------------------------------------------------------------
PAGE_WEIGHT_WARN_KB = 1500
PAGE_WEIGHT_IDEAL_KB = 500
JS_BUNDLE_WARN_KB = 250          # single JS file considered oversized
CSS_FILE_WARN_KB = 100           # single CSS file considered oversized
LARGE_DOM_LIST_THRESHOLD = 500   # heuristic: very large static list -> virtualize

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
]

# --------------------------------------------------------------------------
# Result accumulator
# --------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.checks = []
        self.errors = []

    def add(self, cid, tag, status, detail, evidence=""):
        # status: pass | warn | fail | info
        self.checks.append({
            "id": cid,
            "tag": tag,
            "status": status,
            "detail": detail,
            "evidence": evidence,
        })

    def count(self, status):
        return sum(1 for c in self.checks if c["status"] == status)

    def exit_code(self):
        if self.errors:
            return 2
        if self.count("fail") > 0:
            return 1
        return 0


def human_bytes(n):
    if n < 1024:
        return f"{n}B"
    if n < 1024 * 1024:
        return f"{n/1024:.1f}KB"
    return f"{n/(1024*1024):.2f}MB"


# --------------------------------------------------------------------------
# URL mode
# --------------------------------------------------------------------------
def fetch(url, timeout=15):
    """Return (response, elapsed_seconds) or raise."""
    opener = urllib.request.build_opener()
    # HEAD first to read headers cheaply, then GET for body + timing.
    req_head = urllib.request.Request(url, method="HEAD",
                                      headers={"User-Agent": "frontend-performance/1.0"})
    req_get = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "frontend-performance/1.0"})
    # HEAD
    t0 = time.time()
    resp_head = opener.open(req_head, timeout=timeout)
    head_elapsed = time.time() - t0
    # GET (full timing / TTFB-ish)
    t1 = time.time()
    resp_get = opener.open(req_get, timeout=timeout)
    body = resp_get.read()
    get_elapsed = time.time() - t1
    return resp_head, resp_get, body, head_elapsed, get_elapsed


def audit_url(url, rep):
    try:
        resp_head, resp_get, body, head_elapsed, get_elapsed = fetch(url)
    except urllib.error.HTTPError as e:
        rep.errors.append(f"HTTP error fetching {url}: {e.code} {e.reason}")
        return
    except urllib.error.URLError as e:
        rep.errors.append(f"Network error fetching {url}: {e.reason}")
        return
    except Exception as e:  # noqa: BLE001
        rep.errors.append(f"Unexpected error fetching {url}: {e}")
        return

    headers = {k.lower(): v for k, v in resp_get.getheaders()}
    status = resp_get.status
    version = getattr(resp_get, "version", None)  # 10=1.0, 11=1.1, 20=2.0

    # --- perf:http2-3 -----------------------------------------------------
    # NOTE: CPython's urllib/http.client speaks HTTP/1.1 only. A real HTTP/2
    # or /3 connection cannot be observed here; we report the observed
    # protocol and mark the rule as info (confirm via Lighthouse/WebPageTest).
    if version in (20, 30):
        rep.add("perf:http2-3", "static", "pass",
                "Server negotiated a modern HTTP protocol.",
                f"HTTP/{version/10:.1f}")
    else:
        rep.add("perf:http2-3", "static", "info",
                "urllib observes HTTP/1.1 only; HTTP/2 or /3 cannot be "
                "confirmed offline. Verify with Lighthouse / WebPageTest.",
                f"observed HTTP/{version/10:.1f}" if version else "unknown")

    # --- perf:text-compression --------------------------------------------
    enc = headers.get("content-encoding", "").lower()
    if "br" in enc:
        rep.add("perf:text-compression", "static", "pass",
                "Brotli compression enabled.", f"content-encoding: {enc}")
    elif "gzip" in enc:
        rep.add("perf:text-compression", "static", "pass",
                "Gzip compression enabled.", f"content-encoding: {enc}")
    else:
        rep.add("perf:text-compression", "static", "fail",
                "No text compression (gzip/brotli) on the response.",
                f"content-encoding: {enc or 'none'}")

    # --- perf:browser-caching ---------------------------------------------
    cc = headers.get("cache-control", "").lower()
    etag = headers.get("etag")
    if ("max-age" in cc or "immutable" in cc) and etag:
        rep.add("perf:browser-caching", "static", "pass",
                "Cache-Control + ETag configured for static caching.",
                f"cache-control: {headers.get('cache-control','')}; etag: {etag}")
    elif "max-age" in cc or "immutable" in cc:
        rep.add("perf:browser-caching", "static", "warn",
                "Cache-Control present but no ETag; add validation.",
                f"cache-control: {headers.get('cache-control','')}")
    elif etag:
        rep.add("perf:browser-caching", "static", "warn",
                "ETag present but no Cache-Control max-age.",
                f"etag: {etag}")
    else:
        rep.add("perf:browser-caching", "static", "fail",
                "No browser caching headers (Cache-Control / ETag).",
                f"cache-control: {headers.get('cache-control','none')}")

    # --- perf:hsts (security header reused) -------------------------------
    hsts = headers.get("strict-transport-security")
    if hsts:
        rep.add("perf:hsts", "static", "pass",
                "HSTS enabled (strict-transport-security).", hsts)
    else:
        rep.add("perf:hsts", "static", "warn",
                "Missing HSTS header (strict-transport-security).", "none")

    # --- security headers (reused from a11y/security layer) ---------------
    for h in SECURITY_HEADERS[1:]:  # skip HSTS already reported
        if h in headers:
            rep.add(f"perf:sec:{h}", "static", "pass",
                    f"Security header present: {h}.", headers[h])
        else:
            rep.add(f"perf:sec:{h}", "static", "info",
                    f"Security header absent: {h} (reused from security layer).",
                    "none")

    # --- perf:content-type -----------------------------------------------
    ct = headers.get("content-type", "")
    if ct:
        rep.add("perf:content-type", "static", "pass",
                "Content-Type header present.", ct)
    else:
        rep.add("perf:content-type", "static", "warn",
                "Missing Content-Type header.", "none")

    # --- perf:ttfb --------------------------------------------------------
    # Best-effort: time-to-first-byte approximated by HEAD latency.
    ttfb_ms = head_elapsed * 1000
    if ttfb_ms <= 800:
        rep.add("perf:ttfb", "static", "pass",
                f"TTFB ~{ttfb_ms:.0f}ms (good, target <800ms).",
                f"{ttfb_ms:.0f}ms")
    elif ttfb_ms <= 1800:
        rep.add("perf:ttfb", "static", "warn",
                f"TTFB ~{ttfb_ms:.0f}ms (acceptable, target <800ms).",
                f"{ttfb_ms:.0f}ms")
    else:
        rep.add("perf:ttfb", "static", "fail",
                f"TTFB ~{ttfb_ms:.0f}ms (too high, target <800ms).",
                f"{ttfb_ms:.0f}ms")

    # --- perf:page-weight (single document size) --------------------------
    doc_bytes = len(body)
    if doc_bytes > PAGE_WEIGHT_WARN_KB * 1024:
        rep.add("perf:page-weight", "static", "fail",
                f"HTML document is {human_bytes(doc_bytes)} (>1500KB).",
                human_bytes(doc_bytes))
    elif doc_bytes > PAGE_WEIGHT_IDEAL_KB * 1024:
        rep.add("perf:page-weight", "static", "warn",
                f"HTML document is {human_bytes(doc_bytes)} (>500KB ideal).",
                human_bytes(doc_bytes))
    else:
        rep.add("perf:page-weight", "static", "pass",
                f"HTML document is {human_bytes(doc_bytes)} (<500KB ideal).",
                human_bytes(doc_bytes))

    # --- perf:cdn (heuristic by host/header) ------------------------------
    server = headers.get("server", "")
    via = headers.get("via", "")
    cdn_hint = any(t in (server + " " + via).lower() for t in
                   ("cloudflare", "fastly", "akamai", "cloudfront", "cdn",
                    "edge", "vercel", "netlify"))
    if cdn_hint:
        rep.add("perf:cdn", "static", "pass",
                "Response served via a CDN (header/host heuristic).",
                f"server: {server}; via: {via}")
    else:
        rep.add("perf:cdn", "static", "info",
                "No CDN signature in response headers (heuristic). "
                "Confirm asset hosts separately.",
                f"server: {server}; via: {via}")


# --------------------------------------------------------------------------
# Directory mode
# --------------------------------------------------------------------------
LIB_RE = re.compile(r"^(?P<name>[a-z0-9][a-z0-9._-]*?)[-._]?v?\d+", re.I)
VERSION_RE = re.compile(r"[-._]?v?\d+\.\d+(\.\d+)?")

def strip_version(name):
    base = os.path.basename(name)
    base = VERSION_RE.sub("", base)
    base = re.sub(r"\.(min|prod|bundle|chunk)\.?(js|css)$", "", base, flags=re.I)
    return base.lower()

def audit_dir(directory, rep):
    if not os.path.isdir(directory):
        rep.errors.append(f"Not a directory: {directory}")
        return

    files = []
    for root, _dirs, names in os.walk(directory):
        for n in names:
            files.append(os.path.join(root, n))

    js_files, css_files, html_files, gif_files, other = [], [], [], [], []
    total_bytes = 0
    hashes = defaultdict(list)

    for f in files:
        try:
            sz = os.path.getsize(f)
        except OSError:
            continue
        total_bytes += sz
        ext = os.path.splitext(f)[1].lower()
        if ext == ".js":
            js_files.append((f, sz))
            try:
                with open(f, "rb") as fh:
                    hashes[hashlib.md5(fh.read()).hexdigest()].append(f)
            except OSError:
                pass
        elif ext == ".css":
            css_files.append((f, sz))
        elif ext in (".html", ".htm"):
            html_files.append((f, sz))
        elif ext == ".gif":
            gif_files.append((f, sz))
        else:
            other.append((f, sz))

    # --- perf:page-weight (whole tree) ------------------------------------
    total_kb = total_bytes / 1024
    if total_kb > PAGE_WEIGHT_WARN_KB:
        rep.add("perf:page-weight", "static", "fail",
                f"Total built weight {human_bytes(total_bytes)} (>1500KB).",
                human_bytes(total_bytes))
    elif total_kb > PAGE_WEIGHT_IDEAL_KB:
        rep.add("perf:page-weight", "static", "warn",
                f"Total built weight {human_bytes(total_bytes)} (>500KB ideal).",
                human_bytes(total_bytes))
    else:
        rep.add("perf:page-weight", "static", "pass",
                f"Total built weight {human_bytes(total_bytes)} (<500KB ideal).",
                human_bytes(total_bytes))

    # --- perf:js-bundle-size / perf:css-size ------------------------------
    js_files.sort(key=lambda x: -x[1])
    for f, sz in js_files[:10]:
        if sz > JS_BUNDLE_WARN_KB * 1024:
            rep.add("perf:js-bundle-size", "static", "warn",
                    f"Large JS file {os.path.relpath(f, directory)} "
                    f"= {human_bytes(sz)}.", human_bytes(sz))
    if not js_files:
        rep.add("perf:js-bundle-size", "static", "info",
                "No JS files found in tree.", "")
    elif all(sz <= JS_BUNDLE_WARN_KB * 1024 for _, sz in js_files):
        rep.add("perf:js-bundle-size", "static", "pass",
                f"All {len(js_files)} JS files under {JS_BUNDLE_WARN_KB}KB.",
                "")

    css_files.sort(key=lambda x: -x[1])
    for f, sz in css_files[:10]:
        if sz > CSS_FILE_WARN_KB * 1024:
            rep.add("perf:css-size", "static", "warn",
                    f"Large CSS file {os.path.relpath(f, directory)} "
                    f"= {human_bytes(sz)}.", human_bytes(sz))
    if not css_files:
        rep.add("perf:css-size", "static", "info",
                "No CSS files found in tree.", "")
    elif all(sz <= CSS_FILE_WARN_KB * 1024 for _, sz in css_files):
        rep.add("perf:css-size", "static", "pass",
                f"All {len(css_files)} CSS files under {CSS_FILE_WARN_KB}KB.", "")

    # --- perf:no-dup-js-libs ----------------------------------------------
    # 1) identical content under different paths
    dup_content = {h: ps for h, ps in hashes.items() if len(ps) > 1}
    for h, ps in dup_content.items():
        rep.add("perf:no-dup-js-libs", "static", "fail",
                f"Duplicate JS content ({len(ps)} copies, md5={h[:8]}): "
                + ", ".join(os.path.relpath(p, directory) for p in ps), "")
    # 2) same library, multiple versions (by version-stripped name)
    by_lib = defaultdict(set)
    for f, _ in js_files:
        by_lib[strip_version(f)].add(os.path.basename(f))
    for lib, variants in by_lib.items():
        if len(variants) > 1:
            rep.add("perf:no-dup-js-libs", "static", "warn",
                    f"Possible duplicate library '{lib}': "
                    + ", ".join(sorted(variants)), "")
    if not dup_content and not any(len(v) > 1 for v in by_lib.values()):
        rep.add("perf:no-dup-js-libs", "static", "pass",
                "No duplicate JS libraries detected.", "")

    # --- perf:gif-to-video ------------------------------------------------
    if gif_files:
        total_gif = sum(sz for _, sz in gif_files)
        rep.add("perf:gif-to-video", "static", "warn",
                f"{len(gif_files)} GIF(s) found ({human_bytes(total_gif)}); "
                "consider MP4/WebM for animated content.",
                ", ".join(os.path.relpath(f, directory) for f, _ in gif_files[:5]))
    else:
        rep.add("perf:gif-to-video", "static", "pass",
                "No GIF files; nothing to convert to video.", "")

    # --- HTML-level static heuristics -------------------------------------
    index_html = None
    for f, _ in html_files:
        if os.path.basename(f).lower() == "index.html":
            index_html = f
            break
    if not index_html and html_files:
        index_html = html_files[0][0]

    if index_html:
        try:
            with open(index_html, "r", encoding="utf-8", errors="ignore") as fh:
                html_text = fh.read()
        except OSError:
            html_text = ""
    else:
        html_text = ""

    if html_text:
        _audit_html_static(html_text, directory, rep, js_files, css_files)
    else:
        rep.add("perf:resource-hints", "static", "info",
                "No HTML file found to inspect resource hints.", "")


def _audit_html_static(html_text, directory, rep, js_files, css_files):
    low = html_text.lower()

    # --- perf:resource-hints / preconnect / fetchpriority -----------------
    has_preload = "rel=\"preload\"" in low or "rel='preload'" in low
    has_preconnect = "rel=\"preconnect\"" in low or "rel='preconnect'" in low
    has_prefetch = "rel=\"prefetch\"" in low or "rel='prefetch'" in low
    has_fetchpriority = "fetchpriority" in low

    if has_preload or has_preconnect or has_prefetch:
        rep.add("perf:resource-hints", "static", "pass",
                f"Resource hints present (preload={has_preload}, "
                f"preconnect={has_preconnect}, prefetch={has_prefetch}).", "")
    else:
        rep.add("perf:resource-hints", "static", "warn",
                "No preload/preconnect/prefetch hints found.", "")

    if has_preconnect:
        rep.add("perf:preconnect", "static", "pass",
                "preconnect hints present for critical origins.", "")
    else:
        rep.add("perf:preconnect", "static", "warn",
                "No preconnect hints for critical third-party origins.", "")

    if has_fetchpriority:
        rep.add("perf:fetchpriority", "static", "pass",
                "fetchpriority attribute used.", "")
    else:
        rep.add("perf:fetchpriority", "static", "info",
                "fetchpriority not detected (optional optimization).", "")

    # --- perf:no-lazy-above-fold -----------------------------------------
    # Heuristic: above-the-fold hero images should NOT be lazy.
    above_fold_img = re.search(r"<img[^>]+>", low)
    lazy_above = bool(re.search(r"<img[^>]+loading=[\"']lazy[\"']", low))
    if above_fold_img and lazy_above:
        rep.add("perf:no-lazy-above-fold", "static", "warn",
                "Lazy loading detected on an early <img>; ensure above-the-fold "
                "images are eager.", "")
    else:
        rep.add("perf:no-lazy-above-fold", "static", "pass",
                "No lazy loading on likely above-the-fold image.", "")

    # --- perf:lazy-offscreen ---------------------------------------------
    img_count = len(re.findall(r"<img", low))
    if img_count >= 3 and "loading=\"lazy\"" in low:
        rep.add("perf:lazy-offscreen", "static", "pass",
                f"{img_count} images present and lazy loading is used.", "")
    elif img_count >= 3:
        rep.add("perf:lazy-offscreen", "static", "warn",
                f"{img_count} images present but none lazy-load offscreen.", "")
    else:
        rep.add("perf:lazy-offscreen", "static", "info",
                f"Only {img_count} images; lazy loading not critical.", "")

    # --- perf:service-worker ---------------------------------------------
    if "serviceworker" in low or "navigator.serviceworker" in low or \
       "sw.js" in low or "service-worker.js" in low:
        rep.add("perf:service-worker", "static", "pass",
                "Service worker registration detected.", "")
    else:
        rep.add("perf:service-worker", "static", "info",
                "No service worker registration detected (optional).", "")

    # --- perf:speculation-rules ------------------------------------------
    if "speculationrules" in low or "speculation-rules" in low:
        rep.add("perf:speculation-rules", "static", "pass",
                "Speculation Rules API detected.", "")
    else:
        rep.add("perf:speculation-rules", "static", "info",
                "Speculation Rules API not detected (optional).", "")

    # --- perf:stream-html ------------------------------------------------
    if "transfer-encoding" in low or "renderToPipeableStream" in low or \
       "readablestream" in low:
        rep.add("perf:stream-html", "static", "pass",
                "Streaming HTML indicators present.", "")
    else:
        rep.add("perf:stream-html", "static", "info",
                "No streaming-HTML indicators (optional).", "")

    # --- perf:source-maps ------------------------------------------------
    has_maps = any(f.endswith(".map") for f, _ in js_files) or \
               ".map\"" in low or ".map'" in low or "sourceMappingURL" in low
    if has_maps:
        rep.add("perf:source-maps", "static", "pass",
                "Source maps available for production debugging.", "")
    else:
        rep.add("perf:source-maps", "static", "info",
                "No source maps detected (optional for debugging).", "")

    # --- perf:virtualize-lists -------------------------------------------
    li_count = len(re.findall(r"<li[ >]", low))
    if li_count > LARGE_DOM_LIST_THRESHOLD:
        rep.add("perf:virtualize-lists", "static", "warn",
                f"Very large static list detected ({li_count} <li>); "
                "virtualize long lists/tables.", str(li_count))
    else:
        rep.add("perf:virtualize-lists", "static", "info",
                f"List size {li_count} < {LARGE_DOM_LIST_THRESHOLD}; "
                "virtualization not required.", str(li_count))

    # --- perf:third-party-async ------------------------------------------
    script_srcs = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", low)
    ext_scripts = [s for s in script_srcs
                   if s.startswith("http://") or s.startswith("https://")]
    async_defer = len(re.findall(r"<script[^>]+(async|defer)", low))
    if ext_scripts and async_defer < len(ext_scripts):
        rep.add("perf:third-party-async", "static", "warn",
                f"{len(ext_scripts)} external scripts; only {async_defer} "
                "marked async/defer.", "")
    elif ext_scripts:
        rep.add("perf:third-party-async", "static", "pass",
                "External scripts use async/defer.", "")
    else:
        rep.add("perf:third-party-async", "static", "info",
                "No external third-party scripts detected.", "")

    # --- perf:no-lazy-above-fold preload gap -----------------------------
    # Critical above-the-fold resources (first CSS + first JS) should be preloaded.
    css_links = re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)[\"']", low)
    if css_links and not has_preload:
        rep.add("perf:no-lazy-above-fold", "static", "warn",
                "Stylesheet present but no preload for critical CSS.", "")
    elif css_links and has_preload:
        rep.add("perf:no-lazy-above-fold", "static", "pass",
                "Critical CSS present and preload hints used.", "")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="frontend-performance offline auditor")
    ap.add_argument("--url", help="Target URL (http/https) to inspect headers.")
    ap.add_argument("--dir", help="Built asset directory to analyze.")
    ap.add_argument("--out", help="Write JSON report to this file.")
    ap.add_argument("--timeout", type=int, default=15, help="URL fetch timeout (s).")
    args = ap.parse_args()

    if not args.url and not args.dir:
        ap.error("provide --url <url> or --dir <path> (or both)")

    rep = Report()
    if args.url:
        audit_url(args.url, rep)
    if args.dir:
        audit_dir(args.dir, rep)

    summary = {
        "pass": rep.count("pass"),
        "warn": rep.count("warn"),
        "fail": rep.count("fail"),
        "info": rep.count("info"),
    }
    exit_code = rep.exit_code()

    report = {
        "tool": "perf_headers.py",
        "target": {"url": args.url, "dir": args.dir},
        "summary": summary,
        "exit_code": exit_code,
        "errors": rep.errors,
        "checks": rep.checks,
    }

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"[perf_headers] Report written to {args.out}")
    else:
        print(text)

    print(f"\n[perf_headers] pass={summary['pass']} warn={summary['warn']} "
          f"fail={summary['fail']} info={summary['info']} -> exit {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
