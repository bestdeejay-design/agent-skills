#!/usr/bin/env python3
"""Validate agent-skills repository manifests (CI helper).

Checks:
  1. index.json is a valid JSON file.
  2. Every skill folder has a well-formed skill.json with all required fields.
  3. index.json skills[] cross-match the skills/ folders.
  4. Every skill folder contains a SKILL.md.
  5. index.json entries mirror their skill.json (name, version, category,
     triggers, description, path) — drift between the two is forbidden
     (see CONTRIBUTING.md versioning rule).
Returns non-zero exit code on any failure so the GitHub Actions step fails.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
INDEX_PATH = os.path.join(REPO_ROOT, "index.json")

REQUIRED_FIELDS = [
    "name",
    "version",
    "description",
    "author",
    "license",
    "category",
    "entrypoint",
    "files",
    "requirements",
    "updated",
]


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)


def load_json(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        fail(f"Invalid or unreadable JSON at {path}: {e}")


def main() -> None:
    idx = load_json(INDEX_PATH)

    indexed_skills = {s["name"] for s in idx.get("skills", [])}
    if not os.path.isdir(SKILLS_DIR):
        fail(f"Missing skills directory: {SKILLS_DIR}")

    folder_skills = {
        d
        for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d))
    }

    # Every indexed skill must have a folder + skill.json.
    for name in sorted(indexed_skills):
        folder = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(folder):
            fail(f"Skill {name} is in index.json but folder is missing")
        manifest = os.path.join(folder, "skill.json")
        if not os.path.isfile(manifest):
            fail(f"Skill {name} is missing skill.json")
        data = load_json(manifest)
        missing = [r for r in REQUIRED_FIELDS if r not in data]
        if missing:
            fail(f"Skill {name} is missing required fields: {missing}")
        if not os.path.isfile(os.path.join(folder, "SKILL.md")):
            fail(f"Skill {name} is missing SKILL.md")
        print(f"✅ {data.get('name', name)} v{data.get('version', '?')} OK")

    # Drift check: every index.json entry must mirror its skill.json.
    drift_problems = []
    for entry in sorted(idx.get("skills", []), key=lambda s: s.get("name", "")):
        name = entry.get("name")
        manifest = os.path.join(SKILLS_DIR, name, "skill.json")
        if not os.path.isfile(manifest):
            continue  # missing manifest already fails above
        data = load_json(manifest)
        mism = []
        if entry.get("version") != data.get("version"):
            mism.append(f"version index={entry.get('version')!r} json={data.get('version')!r}")
        if entry.get("category") != data.get("category"):
            mism.append(f"category index={entry.get('category')!r} json={data.get('category')!r}")
        if set(entry.get("triggers", [])) != set(data.get("triggers", [])):
            mism.append(f"triggers differ (index={len(entry.get('triggers', []))} json={len(data.get('triggers', []))})")
        if entry.get("description") != data.get("description"):
            mism.append("description differs")
        if entry.get("path") != f"skills/{name}":
            mism.append(f"path index={entry.get('path')!r} expected=skills/{name}")
        if mism:
            drift_problems.append(f"{name}: " + "; ".join(mism))
    if drift_problems:
        fail("DRIFT между index.json и skill.json:\n  - " + "\n  - ".join(drift_problems))
    print(f"✅ Drift check: all {len(idx.get('skills', []))} index entries mirror skill.json")

    # Every folder should be listed in index.json (warning only).
    for name in sorted(folder_skills - indexed_skills):
        print(f"⚠️ Skill folder {name} not listed in index.json")

    print(f"✅ Cross-check passed: {len(indexed_skills)} indexed, {len(folder_skills)} folders")


if __name__ == "__main__":
    main()