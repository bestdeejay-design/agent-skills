#!/usr/bin/env python3
"""frontend-perfection — Security / Privacy / i18n static audit (Python stdlib).

Offline, dependency-free check of a static frontend (HTML + CSS + JS) covering the
Front-End-Checklist *Security* (22), *Privacy* (5) and *Internationalization* (5)
categories that are statically verifiable. It is the companion to `meta_audit.py`
(which owns document/images/JS/CSS/SEO/tokens/a11y + the two basic `security:https`
and `security:noopener` rules) and to the dedicated sibling skills
`frontend-a11y`, `frontend-performance`, `frontend-testing`.

This script owns ONLY the Security/Privacy/i18n static surface. Runtime/header
checks (real CSP header, HSTS/XCTO/XFO/Referrer-Policy/Permissions-Policy as
response headers, live cookie flags, CSP violation reporting) are out of scope
here — verify them with `frontend-performance`'s `perf_headers.py` or `curl -I`.

Usage:
  python3 security_privacy_audit.py --html index.html [--html h2.html]
                                     [--css main.css ...] [--js app.js ...]
                                     [--out report.json] [--json]

Exit codes: 0 = no violations; 1 = at least one violation; 2 = runner error.

Report shape (machine-readable JSON only on stdout):
  {
    "tool": "frontend-perfection/security_privacy_audit",
    "html": [...], "css": [...], "js": [...],
    "checks": [ {"id","title","severity","ok","detail","file"}, ... ],
    "summary": {"total","passed","violations"}
  }

No PyYAML, no requests, no bs4/lxml — standard library only.
"""
import argparse
import html.parser
import json
import os
import re
import sys


# ---------------------------------------------------------------- helpers
LOCALHOST_RE = re.compile(
    r"^(https?://)?(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|::1)([:/]|$)",
    re.IGNORECASE,
)

SECRET_PARAM_RE = re.compile(
    r"(?<=[?&])((?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|token|"
    r"secret|client[_-]?secret|password|passwd|private[_-]?key|key|session[_-]?id)"
    r"(?:[_-]?(?:key|token|secret))?)\s*=",
    re.IGNORECASE,
)

SECRET_KEY_RE = re.compile(
    r"(token|secret|password|passwd|api[_-]?key|apikey|private[_-]?key|"
    r"credential|auth)",
    re.IGNORECASE,
)

TRACKING_RE = re.compile(
    r"(google-analytics\.com|googletagmanager\.com|gtag|fbq\(|connect\.facebook\.net|"
    r"mc\.yandex\.ru|yandex\.ru/metrika|matomo|hotjar|segment\.io|amplitude|"
    r"analytics\.|doubleclick\.net|scorecardresearch|pixel\.)",
    re.IGNORECASE,
)

CSRF_INPUT_RE = re.compile(
    r"name\s*=\s*[\"'](?:_?csrf|csrf[_-]?token|authenticity[_-]?token|"
    r"_token|csrfmiddlewaretoken)[\"']",
    re.IGNORECASE,
)

DEPRECATED_CRYPTO_RE = re.compile(
    r"(CryptoJS\.(?:MD5|SHA1)|\.md5\s*\(|md5\s*\(|sha1\s*\(|"
    r"createHash\s*\(\s*['\"](?:md5|sha1)['\"]|"
    r"createHash\(['\"]md5|createHash\(['\"]sha1)",
    re.IGNORECASE,
)

EVAL_RE = re.compile(
    r"\beval\s*\(|new\s+Function\s*\(|setTimeout\s*\(\s*[\"'`]",
)

INTL_RE = re.compile(r"Intl\.(?:NumberFormat|DateTimeFormat|Locale|ListFormat|RelativeTimeFormat)")

INTERNAL_IP_RE = re.compile(
    r"(?:\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|"
    r"\b192\.168\.\d{1,3}\.\d{1,3}\b|"
    r"\b172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b)"
)

ENV_LEAK_RE = re.compile(r"\.env\b|secrets\.(?:json|ya?ml)|credentials\.(?:json|ya?ml)", re.IGNORECASE)

RTL_LANGS = ("ar", "he", "fa", "ur", "yi")

BCP47_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,4})?$")

SEC_HEADER_NAMES = {
    "strict-transport-security": "HSTS",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}


# ---------------------------------------------------------------- HTML parsing
class SPExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []          # {href, rel, target}
        self.scripts = []        # {src, integrity, inline}
        self.styles = []         # {href, integrity}  (external stylesheets)
        self.metas = []          # (http_equiv_lower, content)
        self.html_attrs = {}
        self.forms = []          # {method, action}
        self.inputs = []         # raw name attrs
        self.http_urls = []      # absolute http:// urls found in href/src
        self.inline_js = []
        self._in_script = False
        self._script_buf = []
        self._script_type = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.html_attrs = attrs
        elif tag == "a":
            self.links.append({
                "href": attrs.get("href", ""),
                "rel": (attrs.get("rel") or "").lower(),
                "target": attrs.get("target", ""),
            })
            h = attrs.get("href", "")
            if h.startswith("http://") and not LOCALHOST_RE.match(h):
                self.http_urls.append(h)
        elif tag == "link":
            rel = (attrs.get("rel") or "").lower()
            if "stylesheet" in rel:
                self.styles.append({
                    "href": attrs.get("href", ""),
                    "integrity": attrs.get("integrity", ""),
                })
                h = attrs.get("href", "")
                if h.startswith("http://") and not LOCALHOST_RE.match(h):
                    self.http_urls.append(h)
        elif tag == "script":
            t = (attrs.get("type") or "").lower()
            self._script_type = t
            self._in_script = True
            self._script_buf = []
            src = attrs.get("src", "")
            self.scripts.append({
                "src": src,
                "integrity": attrs.get("integrity", ""),
                "inline": not src,
            })
            if src.startswith("http://") and not LOCALHOST_RE.match(src):
                self.http_urls.append(src)
        elif tag == "meta":
            he = (attrs.get("http-equiv") or "").lower()
            if he:
                self.metas.append((he, attrs.get("content", "")))
        elif tag == "form":
            self.forms.append({
                "method": (attrs.get("method") or "get").lower(),
                "action": attrs.get("action", ""),
            })
        elif tag == "input":
            name = attrs.get("name", "")
            if name:
                self.inputs.append(name)

    def handle_data(self, data):
        if self._in_script and self._script_type not in ("application/ld+json", "application/json"):
            self._script_buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script:
            self.inline_js.append("".join(self._script_buf))
            self._in_script = False
            self._script_buf = []
            self._script_type = ""


# ---------------------------------------------------------------- checks
def make_check(cid, title, severity, ok, detail, file):
    return {
        "id": cid,
        "title": title,
        "severity": severity,
        "ok": ok,
        "detail": detail,
        "file": file,
    }


def audit(ext, html_src, css_src, js_src, html_file, css_files, js_files):
    checks = []
    primary = html_file or (css_files[0] if css_files else (js_files[0] if js_files else ""))

    # ---- SECURITY: https everywhere / mixed content (href/src) ----
    bad_https = ext.http_urls
    checks.append(make_check(
        "sec:https", "HTTPS everywhere (no http:// in href/src)", "high",
        not bad_https,
        (f"{len(bad_https)} http:// URL(s) in href/src (use https): "
         + ", ".join(bad_https[:5])) if bad_https else "no http:// URLs in href/src",
        primary,
    ))

    # ---- SECURITY: mixed content in CSS url()/@import/srcset ----
    css_http = []
    if css_src:
        for m in re.finditer(r"url\(\s*['\"]?(.*?)['\"]?\s*\)", css_src):
            u = m.group(1).strip()
            if u.startswith("http://") and not LOCALHOST_RE.match(u):
                css_http.append(u)
        for m in re.finditer(r"@import\s+['\"]([^'\"]+)['\"]", css_src):
            u = m.group(1).strip()
            if u.startswith("http://") and not LOCALHOST_RE.match(u):
                css_http.append(u)
    # also srcset in html
    for m in re.finditer(r"srcset\s*=\s*[\"']([^\"']+)[\"']", html_src, re.IGNORECASE):
        for part in m.group(1).split(","):
            u = part.strip().split()[0] if part.strip() else ""
            if u.startswith("http://") and not LOCALHOST_RE.match(u):
                css_http.append(u)
    checks.append(make_check(
        "sec:mixed-content", "No mixed content in CSS url()/@import/srcset", "high",
        not css_http,
        (f"{len(css_http)} http:// subresource(s) (mixed content on https): "
         + ", ".join(css_http[:5])) if css_http else "no http:// subresources in CSS/srcset",
        (css_files[0] if css_files else primary),
    ))

    # ---- SECURITY: Content-Security-Policy ----
    csp_meta = any(h == "content-security-policy" for h, _ in ext.metas)
    checks.append(make_check(
        "sec:csp", "Content-Security-Policy present", "medium",
        csp_meta,
        ("CSP <meta http-equiv> found" if csp_meta
         else "No Content-Security-Policy detected in HTML — set via response header "
              "or <meta http-equiv=\"Content-Security-Policy\"> (OWASP A05/XSS mitigation)"),
        primary,
    ))

    # ---- SECURITY: Subresource Integrity on external scripts/styles ----
    ext_scripts = [s for s in ext.scripts if s["src"] and s["src"].startswith(("http://", "https://"))]
    ext_styles = [s for s in ext.styles if s["href"] and s["href"].startswith(("http://", "https://"))]
    no_sri = [s["src"] for s in ext_scripts if not s["integrity"]]
    no_sri += [s["href"] for s in ext_styles if not s["integrity"]]
    checks.append(make_check(
        "sec:sri", "Subresource Integrity on external scripts/styles", "high",
        not no_sri,
        (f"{len(no_sri)} external resource(s) without integrity (SRI): "
         + ", ".join(no_sri[:5]) + " — CDN tamper protection") if no_sri
        else f"{len(ext_scripts) + len(ext_styles)} external resource(s) — SRI present (local exempt)",
        primary,
    ))

    # ---- SECURITY: security response headers (meta only; server-side canonical) ----
    present = [SEC_HEADER_NAMES[h] for h, _ in ext.metas if h in SEC_HEADER_NAMES]
    checks.append(make_check(
        "sec:security-headers", "Security headers (HSTS/XCTO/XFO/Referrer/Permissions)", "low",
        True,  # info: these are response headers; meta is a weak proxy
        (f"{len(present)} of 5 present as <meta http-equiv>: {', '.join(present)}. "
         "HSTS/X-Content-Type-Options/X-Frame-Options/Referrer-Policy/Permissions-Policy "
         "are response headers — verify via frontend-performance perf_headers.py or `curl -I`.")
        if present else
        "0 of 5 security headers present as <meta http-equiv>. They are response headers — "
        "verify via frontend-performance perf_headers.py (perf:sec:*) or `curl -I` (info).",
        primary,
    ))

    # ---- SECURITY: target=_blank rel=noopener ----
    blank = [a["href"] for a in ext.links
             if a["target"] == "_blank" and "noopener" not in (a["rel"] or "")]
    checks.append(make_check(
        "sec:noopener", "target=_blank uses rel=noopener noreferrer", "high",
        not blank,
        (f"{len(blank)} target=_blank link(s) without rel=noopener (reverse-tabnabbing): "
         + ", ".join(blank[:5])) if blank else "all target=_blank links carry rel=noopener",
        primary,
    ))

    # ---- SECURITY: secrets in URL query strings ----
    secret_urls = []
    for a in ext.links:
        h = a["href"]
        if "?" in h or "#" in h:
            q = h.split("?", 1)[1] if "?" in h else ""
            if SECRET_PARAM_RE.search(h):
                secret_urls.append(h)
    checks.append(make_check(
        "sec:secrets-in-url", "No secrets/tokens in URL query strings", "critical",
        not secret_urls,
        (f"{len(secret_urls)} URL(s) with secret-like param (token=/api_key=/secret=...): "
         + ", ".join(secret_urls[:5]) + " — URLs leak into logs/referrers") if secret_urls
        else "no secret-like params in URLs",
        primary,
    ))

    # ---- SECURITY: secrets in localStorage/sessionStorage ----
    store_secrets = []
    for blob in (js_src + "\n".join(ext.inline_js)):
        for m in re.finditer(r"(?:sessionStorage|localStorage)\.setItem\s*\(\s*['\"]([^'\"]+)", blob):
            if SECRET_KEY_RE.search(m.group(1)):
                store_secrets.append(m.group(1))
    checks.append(make_check(
        "sec:localstorage-secrets", "No secret keys in localStorage/sessionStorage", "medium",
        not store_secrets,
        (f"{len(store_secrets)} secret-like key(s) in web storage: "
         + ", ".join(sorted(set(store_secrets))[:5]) + " — storage is readable by any JS") if store_secrets
        else "no secret-like keys in localStorage/sessionStorage",
        (js_files[0] if js_files else primary),
    ))

    # ---- SECURITY: CSRF token on state-changing forms ----
    post_forms = [f for f in ext.forms if f["method"] == "post"]
    has_csrf = CSRF_INPUT_RE.search(" ".join(ext.inputs)) is not None
    csrf_ok = True
    csrf_detail = "no POST/state-changing forms — CSRF token not required"
    if post_forms and not has_csrf:
        csrf_ok = False
        csrf_detail = (f"{len(post_forms)} POST form(s) without a CSRF token field "
                       "(name=_csrf|_token|csrf_token|authenticity_token) — add one")
    elif post_forms and has_csrf:
        csrf_detail = f"{len(post_forms)} POST form(s) — CSRF token field present"
    checks.append(make_check(
        "sec:csrf", "State-changing forms carry a CSRF token", "medium",
        csrf_ok, csrf_detail, primary,
    ))

    # ---- SECURITY: no eval() / new Function() ----
    js_all = js_src + "\n".join(ext.inline_js)
    eval_hits = len(EVAL_RE.findall(js_all))
    checks.append(make_check(
        "sec:eval", "No eval()/new Function() in JS", "high",
        eval_hits == 0,
        (f"{eval_hits} eval()/new Function()/setTimeout(string) call(s) — code-injection risk")
        if eval_hits else "no eval()/new Function() found",
        (js_files[0] if js_files else primary),
    ))

    # ---- SECURITY: deprecated/unsafe crypto ----
    crypto_hits = len(DEPRECATED_CRYPTO_RE.findall(js_all))
    checks.append(make_check(
        "sec:deprecated-crypto", "No md5/sha1 in security context", "medium",
        crypto_hits == 0,
        (f"{crypto_hits} md5/sha1 usage(s) (CryptoJS.MD5, createHash('md5'|'sha1'), .md5()) "
         "— use SHA-256+ for security") if crypto_hits else "no md5/sha1 crypto usage found",
        (js_files[0] if js_files else primary),
    ))

    # ---- SECURITY: external script origins (info) ----
    origins = set()
    for s in ext.scripts:
        src = s["src"]
        if src.startswith(("http://", "https://")):
            m = re.match(r"https?://([^/]+)", src)
            if m:
                origins.add(m.group(1))
    checks.append(make_check(
        "sec:external-origins", "External script origins enumerated", "low",
        True,
        (f"{len(origins)} external script origin(s): {', '.join(sorted(origins)) or 'none'} "
         "(limit third-party origins; prefer self-hosting)") if origins
        else "no external script origins (info)",
        primary,
    ))

    # ---- SECURITY: internal IP / .env leak ----
    leak_hits = set()
    blob = html_src + css_src + js_src
    for m in INTERNAL_IP_RE.findall(blob):
        leak_hits.add(m)
    for m in ENV_LEAK_RE.findall(blob):
        leak_hits.add(m)
    checks.append(make_check(
        "sec:internal-leak", "No internal IPs / .env references leaked", "medium",
        not leak_hits,
        (f"leaked internal reference(s): {', '.join(sorted(leak_hits)[:5])} "
         "— do not expose internal IPs/secret files") if leak_hits
        else "no internal IPs / .env references found",
        primary,
    ))

    # ---- SECURITY: cookie flags on document.cookie assignments ----
    cookie_bad = []
    for line in js_all.splitlines():
        if re.search(r"document\.cookie\s*=", line):
            if "Secure" not in line:
                cookie_bad.append(line.strip()[:80])
    checks.append(make_check(
        "sec:cookie-flags", "document.cookie assignments use Secure flag", "low",
        not cookie_bad,
        (f"{len(cookie_bad)} document.cookie assignment(s) without Secure flag "
         "(Set-Cookie response flags HttpOnly/SameSite also required — verify server-side)")
        if cookie_bad else "no insecure document.cookie assignments (response flags verified server-side)",
        (js_files[0] if js_files else primary),
    ))

    # ---- PRIVACY: cookie/consent banner ----
    low = html_src.lower()
    consent = any(k in low for k in ("cookie", "consent", "gdpr", "152-фз", "согласие", "accept"))
    consent_el = re.search(r"class\s*=\s*[\"'][^\"']*cookie[^\"']*[\"']", html_src, re.IGNORECASE)
    priv_ok = consent or bool(consent_el)
    checks.append(make_check(
        "priv:cookie-consent", "Cookie/consent banner before non-essential tracking", "medium",
        priv_ok,
        ("cookie/consent mention or banner element found" if priv_ok
         else "no cookie/consent mention — required before non-essential tracking (GDPR / 152-ФЗ)"),
        primary,
    ))

    # ---- PRIVACY: tracking before consent ----
    tracking = bool(TRACKING_RE.search(js_all + html_src))
    if tracking and not priv_ok:
        checks.append(make_check(
            "priv:tracking-before-consent", "No tracking scripts before consent", "medium",
            False,
            "tracking script (GA/GTM/fbq/Metrika/Matomo) present but no consent gate — "
            "load only after consent",
            primary,
        ))
    else:
        checks.append(make_check(
            "priv:tracking-before-consent", "No tracking scripts before consent", "medium",
            True,
            ("tracking script present but consent gate detected — ok"
             if tracking else "no known tracking scripts detected"),
            primary,
        ))

    # ---- PRIVACY: privacy policy link ----
    policy = bool(re.search(r"href\s*=\s*[\"'][^\"']*(?:privacy|policy|политик|confidential|datenschutz)[^\"']*[\"']",
                            html_src, re.IGNORECASE))
    checks.append(make_check(
        "priv:privacy-policy", "Privacy policy link present", "low",
        policy,
        ("privacy policy link found" if policy
         else "no privacy-policy link — add one (legal requirement)"),
        primary,
    ))

    # ---- PRIVACY: DNT / GPC respected (info) ----
    checks.append(make_check(
        "priv:dnt", "Do Not Track / Global Privacy Control respected", "low",
        True,
        "DNT/GPC must be honored at runtime — verify the consent/analytics layer reads "
        "navigator.doNotTrack / navigator.globalPrivacyControl (manual/info).",
        primary,
    ))

    # ---- PRIVACY: no PII to third parties without consent (info) ----
    checks.append(make_check(
        "priv:third-party-data", "No PII sent to third parties without consent", "low",
        True,
        (f"third-party tracking present: gate it behind consent (info)."
         if tracking else
         "no third-party tracking detected — ensure any future PII sharing is consent-gated (info)."),
        primary,
    ))

    # ---- I18N: lang ----
    lang = ext.html_attrs.get("lang", "")
    lang_ok = bool(lang) and bool(BCP47_RE.match(lang))
    checks.append(make_check(
        "i18n:lang", "<html lang> present and valid (BCP 47)", "medium",
        lang_ok,
        (f"<html lang>={lang or 'MISSING'}" + ("" if lang_ok else " — invalid BCP 47 code"))
        if lang else "<html lang> MISSING — required for a11y/SEO",
        primary,
    ))

    # ---- I18N: dir for RTL ----
    if lang[:2] in RTL_LANGS:
        dir_ok = ext.html_attrs.get("dir") == "rtl"
        checks.append(make_check(
            "i18n:dir", "RTL language sets dir=rtl", "medium",
            dir_ok,
            f"lang={lang} requires dir=\"rtl\" — " + ("OK" if dir_ok else "MISSING"),
            primary,
        ))
    else:
        checks.append(make_check(
            "i18n:dir", "dir attribute correct", "medium",
            True,
            "no RTL language — dir attribute not required (set explicitly if mixed-direction content)",
            primary,
        ))

    # ---- I18N: Intl API used (info) ----
    uses_intl = bool(INTL_RE.search(js_all))
    checks.append(make_check(
        "i18n:intl-api", "Intl API used for number/date/currency formatting", "low",
        True,
        ("Intl.NumberFormat/DateTimeFormat detected — locale-aware formatting OK (info)"
         if uses_intl else
         "no Intl API usage detected — use Intl.* for locale-aware number/date/currency (info)"),
        (js_files[0] if js_files else primary),
    ))

    # ---- I18N: charset declared early (<1024 bytes) ----
    m = re.search(r"<meta[^>]+charset", html_src, re.IGNORECASE)
    if not m:
        charset_ok = False
        charset_detail = "<meta charset> MISSING — declare utf-8 early"
    else:
        pos = m.start()
        charset_ok = pos < 1024
        charset_detail = (f"<meta charset> at byte {pos} (within 1024) — OK"
                          if charset_ok else
                          f"<meta charset> at byte {pos} — declare within first 1024 bytes (prevents encoding sniff)")

    checks.append(make_check(
        "i18n:charset-early", "Charset declared within first 1024 bytes", "medium",
        charset_ok, charset_detail, primary,
    ))

    # ---- I18N: no hardcoded locale-specific strings (info) ----
    checks.append(make_check(
        "i18n:hardcoded-locale", "No hardcoded locale-specific strings", "low",
        True,
        "avoid hardcoding currency symbols/date formats in markup — drive from locale data (info).",
        primary,
    ))

    return checks


def main():
    ap = argparse.ArgumentParser(
        description="Static Security/Privacy/i18n audit (Front-End-Checklist) — Python stdlib, offline")
    ap.add_argument("--html", action="append", default=[], help="HTML file(s)")
    ap.add_argument("--css", action="append", default=[], help="CSS file(s)")
    ap.add_argument("--js", action="append", default=[], help="JS file(s)")
    ap.add_argument("--out", help="Write JSON report to file")
    ap.add_argument("--json", action="store_true", help="Print report as JSON to stdout")
    args = ap.parse_args()

    if not args.html and not args.css and not args.js:
        print("ERROR: provide at least one --html/--css/--js file", file=sys.stderr)
        sys.exit(2)

    for f in args.html + args.css + args.js:
        if not os.path.isfile(f):
            print(f"ERROR: file not found: {f}", file=sys.stderr)
            sys.exit(2)

    def read(path):
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()

    html_src = "\n".join(read(f) for f in args.html)
    css_src = "\n".join(read(f) for f in args.css)
    js_src = "\n".join(read(f) for f in args.js)

    ext = SPExtractor()
    ext.feed(html_src)

    checks = audit(ext, html_src, css_src, js_src,
                   args.html[0] if args.html else "",
                   args.css, args.js)

    violations = [c for c in checks if not c["ok"]]
    report = {
        "tool": "frontend-perfection/security_privacy_audit",
        "html": args.html,
        "css": args.css,
        "js": args.js,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": len(checks) - len(violations),
            "violations": len(violations),
        },
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)

    # Evidence gate: print ONLY the machine-readable JSON (no human summary).
    print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()
