#!/usr/bin/env python3
"""pdf_report_builder.py — markdown → PDF отчёт без обязательных зависимостей.

Конвейер:
  1) Markdown → HTML: pandoc (если установлен) или встроенный минимальный
     конвертер (заголовки/списки/код/таблицы/ссылки/цитаты).
  2) HTML → PDF: первый доступный кандидат:
       - Chromium/Chrome/Edge --headless --print-to-pdf
       - weasyprint (python module)
       - pandoc с движком PDF (pdflatex/tectonic/typst/context)

Вход: файл markdown (или stdin). Выход: PDF в --out (по умолчанию report.pdf).

Примеры:
  python3 pdf_report_builder.py -i README.md -o readme.pdf --title "README"
  cat report.md | python3 pdf_report_builder.py --stdin -o out.pdf
"""

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse


HTML_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
          margin: 40px 52px; color: #1a1a1a; line-height: 1.55; font-size: 14px; }}
  h1 {{ border-bottom: 2px solid #ccc; padding-bottom: 6px; }}
  h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 28px; }}
  pre {{ background: #f6f8fa; border-radius: 6px; padding: 12px; overflow-x: auto;
         font-size: 12.5px; }}
  code {{ background: #f6f8fa; padding: 1px 5px; border-radius: 4px; }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ border-left: 4px solid #b6b6b6; margin-left: 0; padding-left: 14px;
               color: #555; }}
  table {{ border-collapse: collapse; margin: 12px 0; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
  th {{ background: #f0f0f0; }}
  img {{ max-width: 100%; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

CHROME_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)


def _find_browser() -> str | None:
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chrome")


def md_to_html_pandoc(md: str) -> str:
    r = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--standalone"],
        input=md, capture_output=True, text=True, check=True,
    )
    return r.stdout


def _inline(m: str) -> str:
    m = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", m)
    m = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", m)
    m = re.sub(r"`([^`]+)`", r"<code>\1</code>", m)
    m = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', m)
    return m


def md_to_html_builtin(md: str) -> str:
    rows, in_list, in_quote = [], False, False
    fence = False
    table_open = False
    buf = []
    def flush_list():
        nonlocal in_list, buf
        if in_list:
            rows.append("<ul>" + "".join(buf) + "</ul>")
            buf, in_list = [], False
    def flush_quote():
        nonlocal in_quote, buf
        if in_quote:
            rows.append("<blockquote>" + "".join(buf) + "</blockquote>")
            buf, in_quote = [], False
    def flush_table():
        nonlocal table_open
        if table_open:
            rows.append("</table>")
            table_open = False
    for line in md.splitlines():
        if line.strip().startswith("```"):
            flush_list(); flush_quote(); flush_table()
            if fence:
                rows.append("</pre>")
                fence = False
            else:
                fence = True
                rows.append("<pre><code>")
            continue
        if fence:
            rows.append(html.escape(line))
            continue
        s = line.strip()
        if not s:
            flush_list(); flush_quote(); flush_table()
            rows.append("")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush_list(); flush_quote(); flush_table()
            lvl = len(m.group(1))
            rows.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            continue
        if re.match(r"^[-*+]\s+", s):
            flush_quote(); flush_table()
            if not in_list:
                flush_list()
                in_list = True
            buf.append(f"<li>{_inline(re.sub(r'^[-*+]\s+', '', s))}</li>")
            continue
        if s.startswith(">"):
            flush_list(); flush_table()
            if not in_quote:
                in_quote = True
            buf.append(f"<p>{_inline(s.lstrip('> '))}</p>")
            continue
        if re.match(r"^\d+\.\s+", s):
            flush_quote(); flush_table()
            if not in_list:
                in_list = True
            buf.append(f"<li>{_inline(re.sub(r'^\d+\.\s+', '', s))}</li>")
            continue
        if re.match(r"^\|.*\|$", s):
            flush_list(); flush_quote()
            if not table_open:
                table_open = True
                rows.append("<table>")
            cells = [c.strip() for c in s.strip("|").split("|")]
            if re.match(r"^[\s:|-]+$", "".join(cells)) and "-" in "".join(cells):
                continue  # separator row
            tag = "th" if not any(re.match(r"^[\s:|-]+$", c) for c in cells) else "td"
            rows.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
            continue
        if re.match(r"^---+\s*$", s):
            flush_list(); flush_quote()
            rows.append("<hr>")
            continue
        flush_list(); flush_quote(); flush_table()
        rows.append(f"<p>{_inline(s)}</p>")
    flush_list(); flush_quote(); flush_table()
    return "\n".join(rows)


def html_to_pdf_browser(html_text: str, out: str) -> bool:
    browser = _find_browser()
    if not browser:
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html_text)
        html_path = f.name
    uri = "file://" + urllib.parse.quote(html_path)
    cmd = [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           "--print-to-pdf=" + out, uri]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return os.path.exists(out)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def html_to_pdf_weasyprint(html_text: str, out: str) -> bool:
    try:
        from weasyprint import HTML  # type: ignore
        HTML(string=html_text).write_pdf(out)
        return os.path.exists(out)
    except Exception:
        return False


def html_to_pdf_pandoc(html_text: str, out: str) -> bool:
    engines = ("pdflatex", "xelatex", "lualatex", "tectonic", "typst", "context")
    engine = next((e for e in engines if shutil.which(e)), None)
    if not engine:
        return False
    try:
        subprocess.run(
            ["pandoc", "-f", "html", "-t", "pdf", "--pdf-engine=" + engine,
             "-o", out],
            input=html_text, capture_output=True, timeout=180, check=True,
        )
        return os.path.exists(out)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def render_html(md: str, title: str) -> str:
    if shutil.which("pandoc"):
        body = md_to_html_pandoc(md)
    else:
        body = md_to_html_builtin(md)
    body = re.sub(r"<body(?:[^>]*)>|</body>|<!DOCTYPE[^>]*>|<html[^>]*>|</html>|<head>.*?</head>",
                  "", body, flags=re.S)
    return HTML_TMPL.format(title=html.escape(title), body=body)


def main() -> None:
    ap = argparse.ArgumentParser(description="Markdown → PDF отчёт (без обязательных зависимостей)")
    ap.add_argument("-i", "--input", help="input markdown file (default: stdin)")
    ap.add_argument("-o", "--out", default="report.pdf", help="output PDF (default: report.pdf)")
    ap.add_argument("--title", default="Report", help="document title")
    args = ap.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            md = f.read()
    else:
        md = sys.stdin.read()

    html_text = render_html(md, args.title)

    ok = (html_to_pdf_browser(html_text, args.out)
          or html_to_pdf_weasyprint(html_text, args.out)
          or html_to_pdf_pandoc(html_text, args.out))
    if not ok:
        sys.stderr.write(
            "Не найден HTML→PDF конвертер. Установите одно из:\n"
            "  - Google Chrome/Chromium (headless --print-to-pdf)\n"
            "  - python3 -m pip install weasyprint\n"
            "  - pandoc + движок (pdflatex/tectonic/typst)\n")
        sys.exit(1)
    print(f"OK: {args.out} ({os.path.getsize(args.out)} bytes)")


if __name__ == "__main__":
    main()