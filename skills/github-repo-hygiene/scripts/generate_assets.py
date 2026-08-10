#!/usr/bin/env python3
"""Generate assets/header.svg and assets/footer.svg (canonical skill templates).

Pure Python 3 stdlib. Deterministic generation — the SVG templates embed the
canonical patterns from references/svg-animation.md (SMIL animation, mask-cut
"фон наплывает", 4-frame d-path morphing, 30% wave desync, 16s flash pass).

Usage:
    python3 generate_assets.py --name "Proj" --desc "Desc" --user "login" \
        --cold "#0ABAB5" --warm "#F64A8A" [--dir assets] [--force] [--only header]

Exit codes: 0 = generated, 1 = error / would-overwrite without --force.
"""
import argparse
import json
import re
import sys
from pathlib import Path

_FLASH_RECT = re.compile(
    r'\s*<rect width="1200" height="(?:290|60)" fill="url\(#flash\)">.*?</rect>',
    re.DOTALL,
)
_ANIMATE = re.compile(r"\s*<animate(?:Transform)?\b[^>]*/>")

HEADER_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="290" viewBox="0 0 1200 290" role="img" aria-label="{name} — {desc}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{cold}">
        <animate attributeName="stop-color" values="{cold};{warm};{cold}" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="{warm}">
        <animate attributeName="stop-color" values="{warm};{cold};{warm}" dur="8s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <mask id="wave">
      <rect width="1200" height="290" fill="#FFFFFF"/>
      <path fill="#000000" d="M0,290 L0,245 Q150,222 400,245 T800,245 T1200,245 L1200,290 Z">
        <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-3.6s"
          keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
          values="M0,290 L0,245 Q150,222 400,245 T800,245 T1200,245 L1200,290 Z;M0,290 L0,250 Q150,230 400,250 T800,250 T1200,250 L1200,290 Z;M0,290 L0,240 Q150,214 400,240 T800,240 T1200,240 L1200,290 Z;M0,290 L0,245 Q150,222 400,245 T800,245 T1200,245 L1200,290 Z"/>
      </path>
    </mask>
    <linearGradient id="flash" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="35%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="44%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="48%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.25"/>
      <stop offset="52%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="56%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="65%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <g mask="url(#wave)">
    <rect width="1200" height="290" fill="url(#bg)"/>

    <rect width="1200" height="290" fill="url(#flash)">
      <animateTransform attributeName="transform" type="translate" values="-600,0;-600,0;600,0;600,0" keyTimes="0;0.05;0.28;1" dur="16s" calcMode="linear" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0;1;1;1;0;0" keyTimes="0;0.03;0.05;0.28;0.35;1" dur="16s" repeatCount="indefinite"/>
    </rect>

    <path fill="#FFFFFF" opacity="0.25" d="M0,290 L0,232 Q200,210 500,232 T1000,232 T1200,232 L1200,290 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-1.8s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,290 L0,232 Q200,210 500,232 T1000,232 T1200,232 L1200,290 Z;M0,290 L0,238 Q200,220 500,238 T1000,238 T1200,238 L1200,290 Z;M0,290 L0,226 Q200,200 500,226 T1000,226 T1200,226 L1200,290 Z;M0,290 L0,232 Q200,210 500,232 T1000,232 T1200,232 L1200,290 Z"/>
    </path>
    <path fill="#FFFFFF" opacity="0.5" d="M0,290 L0,220 Q150,198 300,220 T600,220 T900,220 T1200,220 L1200,290 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="0s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,290 L0,220 Q150,198 300,220 T600,220 T900,220 T1200,220 L1200,290 Z;M0,290 L0,228 Q150,210 300,228 T600,228 T900,228 T1200,228 L1200,290 Z;M0,290 L0,212 Q150,186 300,212 T600,212 T900,212 T1200,212 L1200,290 Z;M0,290 L0,220 Q150,198 300,220 T600,220 T900,220 T1200,220 L1200,290 Z"/>
    </path>

    <g>
      <animate attributeName="opacity" values="0;1" dur="1.5s" fill="freeze"/>
      <text x="602" y="105" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="{name_size}" font-weight="bold" fill="#000000" opacity="0.28" text-anchor="middle">{name}</text>
      <text x="600" y="103" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="{name_size}" font-weight="bold" fill="{font_color}" text-anchor="middle">{name}</text>
    </g>

    <g>
      <animate attributeName="opacity" values="0;1" dur="1.5s" begin="0.5s" fill="freeze"/>
      <text x="602" y="162" font-family="'Helvetica Neue',Arial,sans-serif" font-size="26" fill="#000000" opacity="0.30" text-anchor="middle">{desc}</text>
      <text x="600" y="160" font-family="'Helvetica Neue',Arial,sans-serif" font-size="26" fill="{font_color}" opacity="0.95" text-anchor="middle">{desc}</text>
    </g>
  </g>
</svg>
"""

FOOTER_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="60" viewBox="0 0 1200 60" role="img" aria-label="@{user}">
  <defs>
    <linearGradient id="fg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{warm}">
        <animate attributeName="stop-color" values="{warm};{cold};{warm}" dur="6s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="{cold}">
        <animate attributeName="stop-color" values="{cold};{warm};{cold}" dur="6s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <mask id="wave">
      <rect width="1200" height="60" fill="#FFFFFF"/>
      <path fill="#000000" d="M0,-12 L0,21 Q200,29 400,21 T800,21 T1200,21 L1200,-12 Z">
        <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-3.6s"
          keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
          values="M0,-12 L0,21 Q200,29 400,21 T800,21 T1200,21 L1200,-12 Z;M0,-12 L0,23 Q200,32 400,23 T800,23 T1200,23 L1200,-12 Z;M0,-12 L0,19 Q200,26 400,19 T800,19 T1200,19 L1200,-12 Z;M0,-12 L0,21 Q200,29 400,21 T800,21 T1200,21 L1200,-12 Z"/>
      </path>
    </mask>
    <linearGradient id="flash" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="35%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="44%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="48%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.25"/>
      <stop offset="52%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="56%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="65%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <g mask="url(#wave)">
    <rect width="1200" height="60" fill="url(#fg)"/>

    <rect width="1200" height="60" fill="url(#flash)">
      <animateTransform attributeName="transform" type="translate" values="-600,0;-600,0;600,0;600,0" keyTimes="0;0.05;0.28;1" dur="16s" calcMode="linear" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0;1;1;1;0;0" keyTimes="0;0.03;0.05;0.28;0.35;1" dur="16s" repeatCount="indefinite"/>
    </rect>

    <path fill="#FFFFFF" opacity="0.25" d="M0,-12 L0,27 Q150,35 300,27 T600,27 T900,27 T1200,27 L1200,-12 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-1.8s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,-12 L0,27 Q150,35 300,27 T600,27 T900,27 T1200,27 L1200,-12 Z;M0,-12 L0,29 Q150,38 300,29 T600,29 T900,29 T1200,29 L1200,-12 Z;M0,-12 L0,25 Q150,32 300,25 T600,25 T900,25 T1200,25 L1200,-12 Z;M0,-12 L0,27 Q150,35 300,27 T600,27 T900,27 T1200,27 L1200,-12 Z"/>
    </path>
    <path fill="#FFFFFF" opacity="0.5" d="M0,-16 L0,35 Q120,44 240,35 T480,35 T720,35 T960,35 T1200,35 L1200,-16 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="0s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,-16 L0,35 Q120,44 240,35 T480,35 T720,35 T960,35 T1200,35 L1200,-16 Z;M0,-16 L0,38 Q120,48 240,38 T480,38 T720,38 T960,38 T1200,38 L1200,-16 Z;M0,-16 L0,32 Q120,40 240,32 T480,32 T720,32 T960,32 T1200,32 L1200,-16 Z;M0,-16 L0,35 Q120,44 240,35 T480,35 T720,35 T960,35 T1200,35 L1200,-16 Z"/>
    </path>

    <text x="602" y="51" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="bold" fill="#000000" opacity="0.30" text-anchor="middle">@{user}</text>
    <text x="600" y="49" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="bold" fill="{font_color}" text-anchor="middle">
      @{user}
      <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
    </text>
  </g>
</svg>
"""


def xml_escape(text: str) -> str:
    """HTML/XML-entities per skill rules (spaces stay spaces, no URL-encoding)."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def name_font_size(name: str) -> str:
    """Skill rule: >20 chars -> 36, >30 -> 28, >40 -> warn (caller prints)."""
    length = len(name)
    if length > 30:
        return "28"
    if length > 20:
        return "36"
    return "48"


def validate_hex(value: str, arg_name: str) -> str:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        sys.exit(f"error: {arg_name} must be #RRGGBB, got {value!r}")
    return value.upper()


def render_header(name: str, desc: str, cold: str, warm: str, font_color: str) -> str:
    name = xml_escape(name)
    desc = xml_escape(desc)
    return HEADER_TEMPLATE.format(
        name=name, desc=desc, cold=cold, warm=warm,
        font_color=font_color, name_size=name_font_size(name),
    )


def render_footer(user: str, cold: str, warm: str, font_color: str) -> str:
    return FOOTER_TEMPLATE.format(user=xml_escape(user), cold=cold, warm=warm, font_color=font_color)


def apply_preset(svg: str, preset: str, cold: str, warm: str) -> str:
    """Transform the canonical template per preset (see references/svg-presets.md)."""
    if preset == "default":
        return svg
    if preset in ("minimal", "monochrome"):
        body = _ANIMATE.sub("", svg)          # strip all SMIL animation
        body = _FLASH_RECT.sub("", body)      # strip the flash layer (static nothing)
        if preset == "monochrome":
            body = body.replace(cold, "#2A2A2E").replace(warm, "#9A9AA2")
        return body
    if preset == "dark-first":
        bg_rect = '    <rect width="1200" height="290" fill="url(#bg)"/>'
        bg_rect_new = (
            '    <rect width="1200" height="290" fill="#0D1117"/>\n'
            '    <rect width="1200" height="290" fill="url(#bg)" opacity="0.78"/>'
        )
        fg_rect = '    <rect width="1200" height="60" fill="url(#fg)"/>'
        fg_rect_new = (
            '    <rect width="1200" height="60" fill="#0D1117"/>\n'
            '    <rect width="1200" height="60" fill="url(#fg)" opacity="0.78"/>'
        )
        return svg.replace(bg_rect, bg_rect_new).replace(fg_rect, fg_rect_new)
    raise ValueError(f"unknown preset: {preset}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate assets/header.svg + assets/footer.svg")
    parser.add_argument("--name", required=True, help="PROJECT_NAME (title text)")
    parser.add_argument("--desc", required=True, help="PROJECT_DESC (subtitle text)")
    parser.add_argument("--user", required=True, help="USERNAME (footer @nickname)")
    parser.add_argument("--cold", required=True, help="COLD color, #RRGGBB")
    parser.add_argument("--warm", required=True, help="WARM color, #RRGGBB")
    parser.add_argument("--font-color", default="#FFFFFF", help="text color, default #FFFFFF")
    parser.add_argument("--dir", default="assets", help="output directory, default assets/")
    parser.add_argument("--preset", choices=["default", "minimal", "dark-first", "monochrome"],
                        default="default", help="style preset (see references/svg-presets.md)")
    parser.add_argument("--only", choices=["header", "footer"], default=None,
                        help="generate only one asset")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing SVG files")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args()

    cold = validate_hex(args.cold, "--cold")
    warm = validate_hex(args.warm, "--warm")
    font_color = validate_hex(args.font_color, "--font-color")

    if font_color == warm or font_color == cold:
        print("warning: FONTCOLOR equals one of gradient colors — readability risk",
              file=sys.stderr)

    out_dir = Path(args.dir)
    targets = []
    if args.only in (None, "header"):
        targets.append(("header", "header.svg",
                        apply_preset(render_header(args.name, args.desc, cold, warm, font_color),
                                     args.preset, cold, warm)))
    if args.only in (None, "footer"):
        targets.append(("footer", "footer.svg",
                        apply_preset(render_footer(args.user, cold, warm, font_color),
                                     args.preset, cold, warm)))

    if len(args.name) > 40:
        print("warning: PROJECT_NAME > 40 chars — consider moving part to PROJECT_DESC",
              file=sys.stderr)

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"created": [], "skipped": [], "errors": []}

    for kind, filename, content in targets:
        path = out_dir / filename
        if path.exists() and not args.force:
            report["skipped"].append(str(path))
            continue
        path.write_text(content, encoding="utf-8")
        report["created"].append(str(path))

    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        for p in report["created"]:
            print(f"created: {p}")
        for p in report["skipped"]:
            print(f"skipped (exists, use --force): {p}", file=sys.stderr)

    if report["skipped"] and not report["created"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())