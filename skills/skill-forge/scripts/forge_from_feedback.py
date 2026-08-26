#!/usr/bin/env python3
"""Improve skills locally from accumulated usage feedback (portable loop).

Reads feedback/<skill>/*.jsonl, calls an LLM (DeepSeek by default) to rewrite
each flagged skill's SKILL.md, and commits the change locally (NO push). This is
the "grow your own skills" command: any consumer of the skill collection can run
it on their fork/clone without any central service or the curator's secrets.

Pure Python 3 stdlib (urllib). LLM key from env DEEPSEEK_API_KEY or opencode auth.json.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FEEDBACK_DIR = REPO_ROOT / "feedback"
SKILLS_DIR = REPO_ROOT / "skills"


def _api_key() -> str:
    env = os.environ.get("DEEPSEEK_API_KEY")
    if env:
        return env
    for p in (Path.home() / ".config/opencode/auth.json", Path.home() / ".config/opencode/auth.jsonc"):
        if p.exists():
            try:
                txt = p.read_text(encoding="utf-8")
                m = re.search(r'"deepseek"[^}]*?"api_key"\s*:\s*"([^"]+)"', txt)
                if m:
                    return m.group(1)
            except Exception:
                pass
    return ""


def _load_feedback(skill=None):
    rows = []
    roots = [FEEDBACK_DIR / skill] if skill else [d for d in FEEDBACK_DIR.iterdir() if d.is_dir()]
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


def _call_llm(api_key, model, system, user):
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }).encode("utf-8")
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def _strip_fences(text):
    if text.lstrip().startswith("```"):
        lines = text.strip().split("\n")
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


def improve(skill, dry_run, no_commit, model, api_key):
    skill_md = SKILLS_DIR / skill / "SKILL.md"
    if not skill_md.exists():
        print(f"skip {skill}: no SKILL.md")
        return
    rows = _load_feedback(skill)
    if not rows:
        print(f"skip {skill}: no feedback")
        return
    print(f"== {skill}: {len(rows)} feedback entries ==")
    current = skill_md.read_text(encoding="utf-8")
    feedback_text = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    system = ("You improve an Agent Skill's SKILL.md from real usage feedback. "
              "Preserve YAML frontmatter (name must match the folder; keep description, "
              "when_to_use, license, metadata). Keep concise. Return ONLY the full improved "
              "SKILL.md content, no commentary, no markdown code fences.")
    user = (f"CURRENT SKILL.md:\n{current}\n\nUSAGE FEEDBACK (JSON):\n{feedback_text}\n\n"
            "Improve the skill using this feedback: add missing trigger phrases to "
            "when_to_use, tighten description, address issues noted. Return the complete SKILL.md.")
    if dry_run:
        print("  [dry-run] would call LLM and rewrite SKILL.md. Sample feedback:")
        for r in rows[:3]:
            print("   -", r.get("type"), (r.get("request") or r.get("detail")))
        return
    if not api_key:
        print("  ERROR: no DEEPSEEK_API_KEY (env) or opencode auth.json deepseek key. Aborting.")
        return
    new = _strip_fences(_call_llm(api_key, model, system, user))
    if "---" not in new:
        print("  ERROR: LLM output does not look like SKILL.md (no frontmatter). Aborting.")
        return
    backup = skill_md.with_suffix(".md.bak")
    backup.write_text(current, encoding="utf-8")
    skill_md.write_text(new, encoding="utf-8")
    print(f"  wrote improved SKILL.md (backup {backup.name})")
    if not no_commit:
        subprocess.run(["git", "-C", str(REPO_ROOT), "add", str(skill_md)], check=False)
        subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "-m",
                        f"fix(skill): improve {skill} from usage feedback ({len(rows)} entries)"], check=False)
        print("  committed locally (no push)")


def main():
    ap = argparse.ArgumentParser(description="Improve skills locally from accumulated feedback")
    ap.add_argument("--skill", default=None, help="limit to one skill")
    ap.add_argument("--dry-run", action="store_true", help="preview only, do not call LLM")
    ap.add_argument("--no-commit", action="store_true", help="write file but do not commit")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--api-key", default=None)
    args = ap.parse_args()
    rows_all = _load_feedback(args.skill)
    if not rows_all:
        print("no feedback collected" + (f" for {args.skill}" if args.skill else ""))
        return
    skills_sorted = sorted({r.get("skill") for r in rows_all})
    key = args.api_key or _api_key()
    for s in skills_sorted:
        improve(s, args.dry_run, args.no_commit, args.model, key)


if __name__ == "__main__":
    main()
