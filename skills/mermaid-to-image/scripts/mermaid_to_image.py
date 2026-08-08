#!/usr/bin/env python3
"""mermaid_to_image.py — рендер .mmd (Mermaid) в PNG/SVG.

Стратегия рендера (по приоритету):
  1. Локальный `mmdc` (mermaid-cli, npm i -g @mermaid-js/mermaid-cli)
     — полный контроль, офлайн, без лимитов размера.
  2. Публичный API mermaid.ink (https://mermaid.ink) — fallback без установки,
     для SVG вывод без ограничений, для PNG есть лимит на размер кода.

Вывод: файл изображения <output> или в stdout (поток байтов) при --stdout.

Примеры:
  python3 mermaid_to_image.py -i diagram.mmd -o diagram.svg
  python3 mermaid_to_image.py -i diagram.mmd -o diagram.png --background transparent
  mmd=$(cat <<'EOF'
  flowchart TD; A-->B
  EOF
  ); echo "$mmd" | python3 mermaid_to_image.py --stdin -o out.svg
"""

import argparse
import base64
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

API = "https://mermaid.ink"


def _mmdc_available() -> bool:
    return shutil.which("mmdc") is not None


def render_local(mmd_text: str, output: str, fmt: str, bg: str, scale: int) -> None:
    """Рендер через mermaid-cli (mmdc)."""
    ext = "svg" if fmt == "svg" else "png"
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as f:
        f.write(mmd_text)
        mmd_path = f.name
    argv = ["mmdc", "-i", mmd_path, "-o", output, "-b", bg if bg else "transparent"]
    if ext == "svg":
        argv += ["-s", str(scale)]
    try:
        subprocess.run(argv, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"mmdc failed: {e.stderr}\n")
        sys.exit(1)


def _ink_payload(mmd_text: str, bg: str, scale: int) -> bytes:
    data = {"code": mmd_text, "mermaid": {"theme": "default"}}
    if bg:
        data["mermaid"]["themeVariables"] = {"background": bg}
    return json.dumps(data, separators=(",", ":")).encode("utf-8")


def render_ink(mmd_text: str, output: str, fmt: str, bg: str, scale: int) -> None:
    """Рендер через mermaid.ink (SVG — с темой; PNG — plain, параметры в query)."""
    if fmt == "svg":
        payload = _ink_payload(mmd_text, bg, 1)
        url = f"{API}/svg/{_b64(payload)}"
    else:
        # endpoint /img/ (PNG) возвращает 400 на payload с секцией "mermaid"
        # и 400 на scale без width/height; bgColor передаётся через query
        payload = json.dumps({"code": mmd_text}, separators=(",", ":")).encode("utf-8")
        q = {}
        if bg:
            q["bgColor"] = bg
        url = f"{API}/img/{_b64(payload)}"
        if q:
            url += "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": "mermaid-to-image/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except urllib.error.URLError as e:
        sys.stderr.write(f"mermaid.ink request failed: {e}\n")
        sys.exit(2)
    if output == "-":
        sys.stdout.buffer.write(data)
    else:
        with open(output, "wb") as f:
            f.write(data)


def _b64(data: bytes) -> str:
    """Base64url без padding — формат mermaid.ink/클idx."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def main() -> None:
    ap = argparse.ArgumentParser(description="Render Mermaid .mmd to PNG/SVG")
    ap.add_argument("-i", "--input", help="input .mmd file (or --stdin)")
    ap.add_argument("-o", "--output", default="-", help="output file (default: stdout)")
    ap.add_argument("-f", "--format", choices=["png", "svg"], default=None,
                    help="output format (inferred from --output extension)")
    ap.add_argument("--stdin", action="store_true", help="read .mmd from stdin")
    ap.add_argument("--bg", default=None, help="background color (e.g. white, #ffffff)")
    ap.add_argument("--scale", type=int, default=2, help="SVG scale (mmdc only; mermaid.ink rejects)")
    ap.add_argument("--engine", choices=["auto", "mmdc", "ink"], default="auto",
                    help="renderer: mmdc (local CLI) or ink (mermaid.ink API)")
    ap.add_argument("--stdout", action="store_true", help="write image to stdout")
    args = ap.parse_args()

    if args.stdin:
        mmd_text = sys.stdin.read()
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            mmd_text = f.read()
    else:
        ap.error("need --input or --stdin")

    output = "-" if args.stdout else args.output

    fmt = args.format
    if not fmt:
        ext = output.rsplit(".", 1)[-1] if output and output != "-" else None
        fmt = "svg" if ext == "svg" else "png"
        if ext not in ("png", "svg"):
            fmt = "svg"  # default

    if args.engine == "mmdc" or (args.engine == "auto" and _mmdc_available()):
        render_local(mmd_text, output, fmt, args.bg, args.scale)
    else:
        if args.engine == "mmdc":
            sys.stderr.write("mmdc не найден (npm i -g @mermaid-js/mermaid-cli)\n")
            sys.exit(1)
        render_ink(mmd_text.strip(), output, fmt, args.bg, args.scale)


if __name__ == "__main__":
    main()