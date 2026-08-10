#!/usr/bin/env python3
"""Validate generated SVG assets against the skill's hard-earned rules.

Checks (pure Python 3 stdlib, xml.etree.ElementTree):
  - XML is well-formed
  - no <script> elements (GitHub blocks scripts)
  - no base64 payloads (plain assets only)
  - no <style> / CSS @keyframes (only SMIL animation works in <img>)
  - every <mask> has a white <rect> covering the whole canvas
  - every d-path morph (<animate attributeName="d">) keeps one command
    sequence across ALL frames (otherwise morphing breaks)
  - mask cut paths have edge clearance: header keeps min_y away from top,
    footer keeps max_y away from bottom and starts above canvas (y<=0)
  - <animateTransform> only type="translate" (canonical pattern)

Usage:
    python3 validate_svg.py assets/                     # scan directory
    python3 validate_svg.py assets/header.svg [more]    # explicit files
    python3 validate_svg.py --json assets/              # machine-readable

Exit codes: 0 = all passed, 1 = any failed, 2 = error.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"


def tag(name: str) -> str:
    return f"{SVG_NS}{name}"


def extract_commands(d_path: str) -> str:
    """Command letters only (numbers/exponents stripped) — used to compare frames."""
    cleaned = re.sub(r"-?\d*\.?\d+(?:[eE][+-]?\d+)?", "", d_path)
    return "".join(ch for ch in cleaned if ch.isalpha())


def extract_coords(d_path: str):
    """All numeric tokens of a d-path in order."""
    return [float(m) for m in re.findall(r"-?\d*\.?\d+(?:[eE][+-]?\d+)?", d_path)]


def coord_pairs_xy(d_path: str):
    """Yield (x, y) pairs from a d-path, honoring H/V single-coordinate commands."""
    tokens = iter(extract_coords(d_path))
    for ch in extract_commands(d_path):
        if ch in ("H", "h"):
            yield (next(tokens, 0.0), None)
        elif ch in ("V", "v"):
            yield (None, next(tokens, 0.0))
        else:
            yield (next(tokens, 0.0), next(tokens, 0.0))


def path_y_values(d_path: str):
    ys = []
    for _x, y in coord_pairs_xy(d_path):
        if y is not None:
            ys.append(y)
    return ys


def frame_values(animate_el: ET.Element):
    """Split <animate> values="a;b;c" into per-frame strings."""
    values = animate_el.get("values", "")
    return [v.strip() for v in values.split(";")] if values else []


def canvas_size(root: ET.Element):
    """(width, height) from viewBox (fallback to width/height attrs)."""
    vb = root.get("viewBox")
    if vb:
        parts = vb.replace(",", " ").split()
        if len(parts) == 4:
            try:
                return float(parts[2]), float(parts[3])
            except ValueError:
                pass
    try:
        return float(root.get("width", "0")), float(root.get("height", "0"))
    except ValueError:
        return 0.0, 0.0


def is_white(fill: str) -> bool:
    return fill.strip().lower() in ("#fff", "#ffffff", "white")


def check_file(path: Path):
    failed = []
    warnings = []
    file_str = str(path)

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return {"file": file_str, "passed": [], "failed": [
            {"item": "well-formed XML", "reason": str(exc), "fix_suggestion": "Regenerate via scripts/generate_assets.py"}],
            "warnings": [], "ok": False}

    root = tree.getroot()
    width, height = canvas_size(root)
    text = path.read_text(encoding="utf-8")

    # 1. No <script>
    if root.findall(f".//{tag('script')}"):
        failed.append({"item": "no <script>", "reason": "contains <script> — GitHub blocks it",
                       "fix_suggestion": "Remove script; use SMIL <animate> only"})

    # 2. No base64
    if re.search(r"base64", text, re.IGNORECASE):
        failed.append({"item": "no base64", "reason": "contains base64 payload",
                       "fix_suggestion": "Use plain files in assets/"})

    # 3. No <style> / CSS keyframes (SMIL only)
    if root.findall(f".//{tag('style')}") or "@keyframes" in text:
        failed.append({"item": "SMIL only", "reason": "CSS animation (<style>/@keyframes) does not work in <img>",
                       "fix_suggestion": "Replace CSS animation with SMIL <animate> attributes"})

    # 4. No event-handler / javascript: attributes
    for el in root.iter():
        for attr in el.attrib:
            if attr.startswith("on") or "javascript" in str(el.attrib.get(attr, "")).lower():
                failed.append({"item": "no inline script", "reason": f"attribute {attr!r} on <{el.tag.split('}')[-1]}>",
                               "fix_suggestion": "Remove event-handler attributes"})
                break

    # 5. Masks have a white full-canvas rect
    for mask in root.findall(f".//{tag('mask')}"):
        rects = mask.findall(f".//{tag('rect')}")
        full_white = any(
            r.get("width") is not None and r.get("height") is not None
            and _number(r.get("width")) >= width and _number(r.get("height")) >= height
            and is_white(r.get("fill", ""))
            for r in rects
        )
        if not full_white:
            failed.append({"item": "mask white rect", "reason": f"<mask {mask.get('id', '?')}> lacks a white <rect> covering the full canvas",
                           "fix_suggestion": "Add <rect width=W height=H fill='#FFFFFF'/> as first child of the mask"})

    # 6. d-path morphing: identical command sequence across frames
    for anim in root.findall(f".//{tag('animate')}"):
        if anim.get("attributeName") != "d":
            continue
        frames = frame_values(anim)
        if len(frames) < 2:
            warnings.append({"item": "d-morph frames", "reason": "<animate attributeName=d> has <2 frames",
                             "fix_suggestion": "Canonical pattern uses 4 frames (keyTimes 0;0.333;0.667;1)"})
            continue
        sequences = {extract_commands(f) for f in frames}
        if len(sequences) > 1:
            failed.append({"item": "d-path command consistency",
                           "reason": f"frames use different command sequences: {sorted(sequences)}",
                           "fix_suggestion": "Keep identical command letters in all values frames (e.g. M L Q T T L Z)"})
        if len(frames) != 4:
            warnings.append({"item": "d-morph 4 frames", "reason": f"got {len(frames)} frames",
                             "fix_suggestion": "Canonical pattern: 4 frames, 4th == 1st (closed loop)"})
        if anim.get("calcMode") != "spline":
            warnings.append({"item": "d-morph calcMode", "reason": f"calcMode={anim.get('calcMode', 'missing')!r}",
                             "fix_suggestion": "Canonical pattern: calcMode='spline' with keySplines"})
        # First and last frame must be identical (closed loop)
        if len(frames) >= 2 and frames[0] != frames[-1]:
            warnings.append({"item": "d-morph loop", "reason": "4th frame != 1st frame",
                             "fix_suggestion": "Canonical pattern: 4th frame equals 1st (seamless loop)"})

    # 7. Mask cut path edge clearance
    for mask in root.findall(f".//{tag('mask')}"):
        for p_el in mask.findall(f".//{tag('path')}"):
            frames = frame_values_of_path(p_el)
            all_ys = [y for f in frames for y in path_y_values(f)] \
                if frames else path_y_values(p_el.get("d", ""))
            if not all_ys:
                continue
            min_y, max_y = min(all_ys), max(all_ys)
            span = max_y - min_y
            # Header-like (canvas tall, path covers bottom): bottom edge must be fully covered
            if height >= 200 and max_y >= height - 0.5:
                if min_y < 10:
                    failed.append({"item": "mask edge clearance",
                                   "reason": f"cut wave reaches near top (min_y={min_y:.0f}) in header mask",
                                   "fix_suggestion": "Keep the morphing band away from the top edge"})
            # Footer-like: starts above canvas (clearance) and stays away from bottom
            if height < 200:
                if min_y > 0.5:
                    failed.append({"item": "mask edge clearance",
                                   "reason": f"footer cut wave must start above canvas (min_y={min_y:.0f} > 0)",
                                   "fix_suggestion": "Start patches at negative y (e.g. y=-12/-16), clearance > morph span"})
                if max_y >= height - 0.5:
                    failed.append({"item": "mask edge clearance",
                                   "reason": f"footer cut wave touches bottom (max_y={max_y:.0f} >= {height:.0f})",
                                   "fix_suggestion": "Keep the morphing band away from the bottom edge"})

    # 8. animateTransform: translate only
    for at in root.findall(f".//{tag('animateTransform')}"):
        if at.get("type") != "translate":
            warnings.append({"item": "animateTransform type", "reason": f"type={at.get('type', 'missing')!r}",
                             "fix_suggestion": "Canonical flash pattern animates transform of the rect, type='translate'"})

    # 9. SMIL presence (informative)
    if not root.findall(f".//{tag('animate')}") and not root.findall(f".//{tag('animateTransform')}"):
        warnings.append({"item": "SMIL animation", "reason": "no <animate>/<animateTransform> found",
                         "fix_suggestion": "Skill default is animated; static SVG is allowed only for minimal preset"})

    return {"file": file_str, "passed": ["well-formed XML", "no script/base64/style",
                                          "mask white rect", "d-morph consistency", "edge clearance", "SMIL-only"] if not failed else [],
            "failed": failed, "warnings": warnings, "ok": not failed}


def frame_values_of_path(path: ET.Element):
    """Frames from child <animate attributeName='d'> of this path."""
    frames = []
    for anim in path.findall(f".//{tag('animate')}"):
        if anim.get("attributeName") == "d":
            frames.extend(frame_values(anim))
    return frames


def _number(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SVG assets against skill rules")
    parser.add_argument("paths", nargs="+", help="SVG files or directories (dirs are scanned for *.svg)")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON report")
    args = parser.parse_args()

    files = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.glob("*.svg")))
        elif path.is_file():
            files.append(path)
        else:
            print(f"error: no such path: {path}", file=sys.stderr)
            return 2
    if not files:
        print("error: no .svg files found", file=sys.stderr)
        return 2

    results = [check_file(f) for f in files]
    any_failed = any(not r["ok"] for r in results)

    if args.json:
        print(json.dumps({"files": results, "total_failed": sum(len(r["failed"]) for r in results),
                          "ok": not any_failed}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "FAIL" if r["failed"] else "PASS"
            print(f"[{status}] {r['file']}")
            for f in r["failed"]:
                print(f"  ✗ {f['item']}: {f['reason']}")
                print(f"      fix: {f['fix_suggestion']}")
            for w in r["warnings"]:
                print(f"  ! {w['item']}: {w['reason']}")

    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()