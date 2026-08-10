#!/usr/bin/env python3
"""Extract generation context (name/desc/stack/colors) from a repo checkout.

Formalizes the decision tree from references/color-tokens.md:
  PROJECT_NAME  : package.json name -> pyproject/setup/Cargo name ->
                  composer.json/pubspec.yaml name -> repo dir name -> first H1
  PROJECT_DESC  : manifest description -> git-repo description (optional gh) ->
                  README first paragraph -> stack auto-desc (table)
  COLD/WARM     : README badges/OG colors (heuristic #hex scan, best pair)
                  -> topic table (stack detection: package.json deps, pyproject,
                  bot keywords, CLI, mobile, game, docs, api, db, ai, devops...)
  USERNAME      : from git remote (github.com/owner/repo)

Pure Python 3 stdlib. Output: JSON (default) or key=value text.

Usage:
    python3 extract_context.py                      # inspect current dir
    python3 extract_context.py --path /repo/root
    python3 extract_context.py --gh-repo owner/repo # include GH description
    python3 extract_context.py --text               # human-readable output
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# topic -> (COLD, WARM) from references/color-tokens.md
TOPIC_COLORS = {
    "design": ("#0ABAB5", "#F64A8A"),
    "frontend": ("#0ABAB5", "#F64A8A"),
    "backend": ("#1E3A8A", "#F59E0B"),
    "api": ("#1E3A8A", "#F59E0B"),
    "ai": ("#7C3AED", "#06B6D4"),
    "data": ("#7C3AED", "#06B6D4"),
    "ml": ("#7C3AED", "#06B6D4"),
    "devops": ("#0EA5E9", "#10B981"),
    "cloud": ("#0EA5E9", "#10B981"),
    "mobile": ("#8B5CF6", "#EC4899"),
    "bot": ("#9B4DCA", "#00D4FF"),
    "automation": ("#9B4DCA", "#00D4FF"),
    "game": ("#DC2626", "#7C3AED"),
    "finance": ("#1E293B", "#FBBF24"),
    "crypto": ("#1E293B", "#FBBF24"),
    "security": ("#18181B", "#EF4444"),
    "education": ("#2563EB", "#F97316"),
    "opensource": ("#6366F1", "#EC4899"),
}
FALLBACK_COLORS = ("#0ABAB5", "#F64A8A")

# stack -> auto description (references/color-tokens.md table)
STACK_DESC = [
    (("react", "vue", "svelte", "next"), "Frontend Developer"),
    (("express", "fastify", "nestjs"), "Backend Engineer"),
    (("django", "flask"), "Backend Developer"),
    (("typescript",), "Type-Safe Code"),
    (("rust",), "Systems Programming"),
    (("go",), "Backend Tool"),
    (("telegram", "discord", "slack"), "Automation Tool"),
    (("cli",), "Developer Utility"),
    (("react-native", "flutter", "swift"), "Mobile App"),
    (("unity", "godot", "phaser"), "Game Development"),
    (("pytorch", "tensorflow", "transformers", "sklearn"), "AI / Machine Learning"),
    (("docker", "kubernetes", "k8s", "terraform"), "DevOps Tool"),
    (("chrome", "firefox", "browser-extension"), "Browser Extension"),
    (("vscode", "sublime"), "IDE Plugin"),
]

STACK_TOPIC = [
    ("react", "frontend"), ("vue", "frontend"), ("svelte", "frontend"), ("next", "frontend"),
    ("express", "backend"), ("fastify", "backend"), ("nestjs", "backend"),
    ("django", "backend"), ("flask", "backend"), ("fastapi", "api"),
    ("telegram", "bot"), ("discord", "bot"), ("slack", "bot"),
    ("pytorch", "ai"), ("tensorflow", "ai"), ("transformers", "ai"),
    ("docker", "devops"), ("kubernetes", "devops"), ("terraform", "devops"),
    ("react-native", "mobile"), ("flutter", "mobile"),
    ("unity", "game"), ("godot", "game"),
    ("solana", "crypto"), ("web3", "crypto"), ("ethers", "crypto"),
    ("opencv", "ai"),
]


def run(cmd, timeout=15):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, ""


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_first_lines(path: Path, count=50):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return [next(fh).strip() for _ in range(count)]
    except (OSError, StopIteration):
        return []


def extract_name(root: Path) -> str:
    for manifest, keys in (
        ("package.json", ("name",)),
        ("pyproject.toml", ("name",)),
        ("setup.py", ("name=",)),
        ("Cargo.toml", ("name",)),
        ("composer.json", ("name",)),
        ("pubspec.yaml", ("name",)),
    ):
        path = root / manifest
        if path.exists():
            if manifest == "package.json":
                data = read_json(path)
                if data and data.get("name"):
                    return str(data["name"]).replace("@", "").split("/")[-1]
            elif manifest == "pyproject.toml":
                for line in read_first_lines(path, 100):
                    m = re.match(r"\s*name\s*=\s*[\"']([^\"']+)[\"']", line)
                    if m:
                        return m.group(1)
            elif manifest == "setup.py":
                for line in read_first_lines(path, 200):
                    m = re.search(r"name\s*=\s*[\"']([^\"']+)[\"']", line)
                    if m:
                        return m.group(1)
            elif manifest == "Cargo.toml":
                for line in read_first_lines(path, 60):
                    m = re.match(r"\s*name\s*=\s*[\"']([^\"']+)[\"']", line)
                    if m:
                        return m.group(1)
            elif manifest == "composer.json":
                data = read_json(path)
                if data and data.get("name"):
                    return str(data["name"]).split("/")[-1]
    readme = root / "README.md"
    if readme.exists():
        for line in read_first_lines(readme, 20):
            m = re.match(r"^#\s+(.+)", line)
            if m:
                return m.group(1).strip()
    return root.name


def extract_desc(root: Path, gh_repo: str = "") -> str:
    pkg = root / "package.json"
    if pkg.exists():
        data = read_json(pkg)
        if data and data.get("description"):
            return str(data["description"])
    py = root / "pyproject.toml"
    if py.exists():
        for line in read_first_lines(py, 100):
            m = re.match(r"\s*description\s*=\s*[\"']([^\"']+)[\"']", line)
            if m:
                return m.group(1)
    if gh_repo:
        code, out = run(["gh", "repo", "view", gh_repo, "--json", "description",
                         "-q", ".description"])
        if code == 0 and out:
            return out
    readme = root / "README.md"
    if readme.exists():
        lines = read_first_lines(readme, 40)
        in_intro = False
        for line in lines:
            if re.match(r"^#\s", line):
                in_intro = True
                continue
            if in_intro and line and not line.startswith("#"):
                return line.strip()[:120]
    return auto_desc(root)


def detect_stack(root: Path):
    """Return (desc, topic) resolved from manifests/README keywords."""
    haystack = []
    for name in ("package.json", "requirements.txt", "pyproject.toml", "Cargo.toml",
                 "go.mod", "composer.json", "pubspec.yaml"):
        p = root / name
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace").lower()
            haystack.append(text)
    readme = root / "README.md"
    if readme.exists():
        haystack.append(readme.read_text(encoding="utf-8", errors="replace").lower()[:4000])
    if (root / "Dockerfile").exists():
        haystack.append("docker kubernetes")
    if (root / ".github/workflows").exists():
        haystack.append("devops ci")

    blob = "\n".join(haystack)
    desc, topic = "Open Source Project", "opensource"
    for keywords, d in STACK_DESC:
        if any(_word(k, blob) for k in keywords):
            desc = d
            break
    for kw, t in STACK_TOPIC:
        if _word(kw, blob):
            topic = t
            break
    return desc, topic


def _word(keyword: str, blob: str) -> bool:
    """Word-boundary keyword match (keywords may contain '-' like 'react-native')."""
    pattern = re.escape(keyword).replace(r"\-", r"[\-.]?")
    return re.search(rf"\b{pattern}\b", blob) is not None


def auto_desc(root: Path) -> str:
    desc, _ = detect_stack(root)
    return desc


def detect_colors(root: Path):
    """Best #hex pair from README badges/OG image markers, else topic table."""
    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="replace")
        hexes = re.findall(r"#[0-9A-Fa-f]{6}", text)
        # prefer two most frequent distinct colors (badges repeat)
        from collections import Counter
        counts = Counter(h.upper() for h in hexes if h.upper() not in ("#FFFFFF", "#000000"))
        top = [c for c, _ in counts.most_common(3)]
        if len(top) >= 2:
            return top[0], top[1]
        if len(top) == 1:
            return top[0], FALLBACK_COLORS[1]
    _desc, topic = detect_stack(root)
    return TOPIC_COLORS.get(topic, FALLBACK_COLORS)


def detect_user(root: Path) -> str:
    code, out = run(["git", "-C", str(root), "config", "--get", "remote.origin.url"])
    if code == 0 and out:
        m = re.search(r"(?:github\.com[:/])([^/\s]+)", out)
        if m:
            return m.group(1)
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract SVG generation context from a repo")
    parser.add_argument("--path", default=".", help="repo root, default .")
    parser.add_argument("--gh-repo", default="", help="owner/repo to fetch GH description from")
    parser.add_argument("--text", action="store_true", help="human-readable key=value output")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    name = extract_name(root)
    desc = extract_desc(root, args.gh_repo)
    cold, warm = detect_colors(root)
    user = detect_user(root)
    stack_desc, topic = detect_stack(root)

    report = {
        "name": name,
        "desc": desc,
        "stack_desc": stack_desc,
        "topic": topic,
        "cold": cold,
        "warm": warm,
        "user": user,
    }

    if args.text:
        for k, v in report.items():
            print(f"{k}={v}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()