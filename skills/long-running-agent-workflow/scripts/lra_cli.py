#!/usr/bin/env python3
"""lra_cli.py — Long-Running Agent (LRA) workflow CLI.

Pure Python 3 standard library. Maintains a `.lra/` directory inside the
current project:

  .lra/feature-list.json   atomic features with status
  .lra/progress.txt        session-by-session progress log

Subcommands:
  init <description>                       create .lra/ scaffolding
  add <name> --priority P --criteria C    append a feature
  mark <id> <todo|wip|done>               update a feature status
  checkpoint <message>                    append a timestamped log line
  status                                  print feature table
  recover                                 show recent log + in-flight features

Exit codes: 0 = ok, 1 = usage/data error.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

LRA_DIR = Path(".lra")
FEATURES_FILE = LRA_DIR / "feature-list.json"
PROGRESS_FILE = LRA_DIR / "progress.txt"

VALID_PRIORITIES = ("high", "medium", "low")
VALID_STATUSES = ("todo", "wip", "done")
STATUS_ORDER = {"todo": 0, "wip": 1, "done": 2}


def _today() -> str:
    return datetime.now().date().isoformat()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def _require_lra() -> None:
    if not LRA_DIR.is_dir():
        _die(".lra/ not found — run `init` first")


def _load_features() -> dict:
    _require_lra()
    if not FEATURES_FILE.is_file():
        _die(f"{FEATURES_FILE} missing")
    try:
        return json.loads(FEATURES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _die(f"corrupt {FEATURES_FILE}: {exc}")


def _save_features(data: dict) -> None:
    FEATURES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _next_id(features: list) -> str:
    max_n = 0
    for f in features:
        fid = str(f.get("id", ""))
        digits = "".join(ch for ch in fid if ch.isdigit())
        if digits.isdigit():
            max_n = max(max_n, int(digits))
    return f"f{max_n + 1}"


def _normalize_id(raw: str) -> str:
    raw = raw.strip().lower()
    if raw.startswith("f") and raw[1:].isdigit():
        return raw
    if raw.isdigit():
        return f"f{raw}"
    _die(f"invalid feature id: {raw!r} (expected e.g. f1 or 1)")


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #
def cmd_init(args: argparse.Namespace) -> None:
    if LRA_DIR.exists():
        _die(f"{LRA_DIR} already exists — refusing to overwrite")
    LRA_DIR.mkdir()
    data = {
        "project": args.description,
        "features": [],
        "created": _today(),
    }
    _save_features(data)
    header = (
        "# Long-Running Agent Progress Log\n"
        f"# Project: {args.description}\n"
        f"# Created: {_today()}\n"
    )
    PROGRESS_FILE.write_text(header, encoding="utf-8")
    print(f"initialized .lra/ for project: {args.description}")


def cmd_add(args: argparse.Namespace) -> None:
    data = _load_features()
    features = data.setdefault("features", [])
    name = args.name.strip()
    if not name:
        _die("feature name must not be empty")
    if any(f.get("name", "").lower() == name.lower() for f in features):
        _die(f"duplicate feature name: {name!r}")
    if args.priority not in VALID_PRIORITIES:
        _die(f"priority must be one of {VALID_PRIORITIES}")
    if not args.criteria or not args.criteria.strip():
        _die("acceptance criteria must not be empty")
    feature = {
        "id": _next_id(features),
        "name": name,
        "priority": args.priority,
        "criteria": args.criteria.strip(),
        "status": "todo",
        "added": _today(),
    }
    features.append(feature)
    _save_features(data)
    print(f"added {feature['id']}: {name} [{args.priority}]")


def cmd_mark(args: argparse.Namespace) -> None:
    data = _load_features()
    features = data.get("features", [])
    fid = _normalize_id(args.id)
    status = args.status
    if status not in VALID_STATUSES:
        _die(f"status must be one of {VALID_STATUSES}")
    for f in features:
        if f.get("id", "").lower() == fid:
            f["status"] = status
            _save_features(data)
            print(f"marked {fid}: {status}")
            return
    _die(f"feature not found: {args.id!r}")


def cmd_checkpoint(args: argparse.Namespace) -> None:
    _require_lra()
    message = args.message.strip()
    if not message:
        _die("checkpoint message must not be empty")
    with PROGRESS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"[{_now()}] {message}\n")
    print(f"checkpoint saved: {message}")


def cmd_status(args: argparse.Namespace) -> None:
    data = _load_features()
    features = data.get("features", [])
    if not features:
        print("no features yet")
        return
    ordered = sorted(
        features, key=lambda f: (STATUS_ORDER.get(f.get("status", "todo"), 9), f.get("id", ""))
    )
    print(f"Project: {data.get('project', '(unnamed)')}")
    print(f"{'ID':<6}{'NAME':<40}{'PRIORITY':<10}{'STATUS'}")
    print("-" * 64)
    for f in ordered:
        name = f.get("name", "")
        if len(name) > 38:
            name = name[:35] + "..."
        print(
            f"{f.get('id', ''):<6}{name:<40}{f.get('priority', ''):<10}{f.get('status', '')}"
        )
    counts = {s: sum(1 for f in features if f.get("status") == s) for s in VALID_STATUSES}
    print("-" * 64)
    print(
        f"todo: {counts['todo']}  wip: {counts['wip']}  done: {counts['done']}  "
        f"total: {len(features)}"
    )


def cmd_recover(args: argparse.Namespace) -> None:
    _require_lra()
    if not PROGRESS_FILE.is_file():
        _die(f"{PROGRESS_FILE} missing")
    lines = PROGRESS_FILE.read_text(encoding="utf-8").splitlines()
    print("=== Last 10 progress lines ===")
    for line in lines[-10:]:
        print(line)
    data = _load_features()
    wip = [f for f in data.get("features", []) if f.get("status") == "wip"]
    print("\n=== In-flight (wip) features ===")
    if not wip:
        print("(none)")
    else:
        for f in wip:
            print(f"  {f.get('id')}: {f.get('name')} [{f.get('priority')}]")
    print("\nTip: resume the highest-priority wip/todo feature, then checkpoint.")


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lra_cli.py", description="Long-Running Agent workflow CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create .lra/ scaffolding")
    p_init.add_argument("description", help="short project description")
    p_init.set_defaults(func=cmd_init)

    p_add = sub.add_parser("add", help="append a feature")
    p_add.add_argument("name", help="feature name / description")
    p_add.add_argument(
        "--priority", required=True, choices=VALID_PRIORITIES, help="feature priority"
    )
    p_add.add_argument("--criteria", required=True, help="acceptance criteria")
    p_add.set_defaults(func=cmd_add)

    p_mark = sub.add_parser("mark", help="update a feature status")
    p_mark.add_argument("id", help="feature id, e.g. f1 or 1")
    p_mark.add_argument("status", choices=VALID_STATUSES, help="new status")
    p_mark.set_defaults(func=cmd_mark)

    p_cp = sub.add_parser("checkpoint", help="append a timestamped log line")
    p_cp.add_argument("message", help="session summary message")
    p_cp.set_defaults(func=cmd_checkpoint)

    p_status = sub.add_parser("status", help="print feature table")
    p_status.set_defaults(func=cmd_status)

    p_rec = sub.add_parser("recover", help="show recent log + in-flight features")
    p_rec.set_defaults(func=cmd_recover)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
