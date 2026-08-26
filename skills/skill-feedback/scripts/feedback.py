#!/usr/bin/env python3
"""Capture and aggregate Agent Skill usage feedback.

Stores entries as JSON-lines under feedback/<skill>/YYYY-MM-DD.jsonl and
provides report / export commands that feed the skill-forge improvement loop.

Pure Python 3 standard library. No third-party packages.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FEEDBACK_DIR = REPO_ROOT / "feedback"
TYPES = {
    "near_miss_trigger",
    "wrong_trigger",
    "output_issue",
    "manual_correction",
    "description_gap",
}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def add(skill: str, type_: str, request: str, detail: str, fix: str, source: str) -> int:
    if type_ not in TYPES:
        print(f"error: type must be one of {sorted(TYPES)}", file=sys.stderr)
        return 2
    d = FEEDBACK_DIR / skill
    d.mkdir(parents=True, exist_ok=True)
    path = d / (datetime.now().strftime("%Y-%m-%d") + ".jsonl")
    entry = {
        "ts": _now(),
        "skill": skill,
        "type": type_,
        "request": request or "",
        "detail": detail or "",
        "suggested_fix": fix or "",
        "source": source or "user",
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"ok: appended to {path}")
    return 0


def _load(skill=None):
    rows = []
    if skill:
        roots = [FEEDBACK_DIR / skill]
    else:
        roots = [p for p in FEEDBACK_DIR.iterdir() if p.is_dir()]
    for d in roots:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
    return rows


def report(skill=None) -> int:
    rows = _load(skill)
    if not rows:
        print("no feedback recorded" + (f" for {skill}" if skill else ""))
        return 0
    by_skill, by_type, near = {}, {}, []
    for r in rows:
        s = r.get("skill", "?")
        t = r.get("type", "?")
        by_skill[s] = by_skill.get(s, 0) + 1
        by_type[t] = by_type.get(t, 0) + 1
        if t in ("near_miss_trigger", "description_gap") and r.get("request"):
            near.append(r)
    print(f"# Skill feedback report" + (f" — {skill}" if skill else ""))
    print(f"\nTotal entries: {len(rows)}")
    print("\nBy skill:")
    for k, v in sorted(by_skill.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\nBy type:")
    for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"\nNear-miss / trigger-gap requests ({len(near)}) — feed into skill-forge Optimize-description:")
    for r in near[-20:]:
        print(f"  - [{r.get('skill')}] {r.get('request')}")
    return 0


def export(skill=None) -> int:
    rows = _load(skill)
    if not rows:
        print("no feedback to export")
        return 0
    print("# Skill-forge improvement digest")
    print("Feed near-miss requests into Optimize-description; feed suggested_fix into Improve.")
    for r in rows:
        fix = r.get("suggested_fix") or r.get("detail") or ""
        print(f"- skill={r.get('skill')} type={r.get('type')} request={r.get('request')!r} fix={fix!r}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Capture/aggregate Agent Skill usage feedback")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--skill", required=True)
    a.add_argument("--type", required=True)
    a.add_argument("--request", default="")
    a.add_argument("--detail", default="")
    a.add_argument("--fix", default="")
    a.add_argument("--source", default="user")
    r = sub.add_parser("report")
    r.add_argument("--skill", default=None)
    e = sub.add_parser("export")
    e.add_argument("--skill", default=None)
    args = ap.parse_args()
    if args.cmd == "add":
        return add(args.skill, args.type, args.request, args.detail, args.fix, args.source)
    if args.cmd == "report":
        return report(args.skill)
    if args.cmd == "export":
        return export(args.skill)
    return 2


if __name__ == "__main__":
    sys.exit(main())
