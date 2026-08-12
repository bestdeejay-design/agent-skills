---
name: repo-metadata-health
description: "Audit and update GitHub repository metadata and community health: description (gh repo edit), topics (PUT /repos/topics, max 20), GitHub Pages link + homepage, community-health percentage via the Community Profile API, and a 16-point check checklist. Script: validate_repo.py (gh API + filesystem, auto-detect from git remote). Triggers: 'repo description', 'repo topics', 'github topics', 'github pages', 'community health', 'repo audit', 'repo metadata', 'repo checklist', 'health percentage', 'repo about'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "Requires gh CLI and network access to api.github.com for metadata checks; python3 (stdlib) for validate_repo.py"
---

# Repo Metadata Health — description, topics, Pages, community health

Use this skill to **audit and update a repository's metadata and community health**:
description, topics, GitHub Pages link, homepage in About, and the Community Standards
percentage. Keeps the GitHub page accurate after major changes.

## When to use

- A repository's description/topics are outdated after a major change.
- Need the Community Health score (Community Profile API) audited against a 16-point checklist.
- GitHub Pages should be linked in README/About.
- User asks for "repo description", "repo topics", "github pages", "community health",
  "repo audit", "repo checklist".

## Do NOT use

- For README content/visual header/footer — use `repo-readme-assets`.
- For legal/community files (LICENSE, CONTRIBUTING, SECURITY, templates) — use `repo-community-files`.
- For the social preview PNG — use `repo-social-preview`.

## Files

- `SKILL.md` — this file
- `scripts/validate_repo.py` — 16-point checklist (gh API + filesystem, auto-detect from git remote)
- `references/community-checklist.md` — the full 16-point checklist with check commands
- `examples/repo-hygiene.yml` — CI example wiring the checklist into a workflow

## Description and topics

Set via `gh api`:

```bash
# Description (UI limit ~350 chars) — list ALL key components
gh repo edit --description "<full description with keywords>"

# Topics (array via -f 'names[]=...') — PUT only, full list replacement
gh api -X PUT repos/<owner>/<repo>/topics \
  -f 'names[]=python' -f 'names[]=markdown' -f 'names[]=documentation' \
  -f 'names[]=agents' -f 'names[]=skills' -f 'names[]=opencode'
```

Topic rules:
- max **20 topics** per repository (GitHub limit)
- each topic: **≤ 50 chars**, lowercase letters/digits/hyphens only
- include language/framework/DB/broker (key ones), architectural patterns, project type
- **all significant components** must be reflected in both description and topics

## GitHub Pages

If Pages is enabled (`gh api repos/<owner>/<repo>/pages`):
- README must contain a working link `https://<owner>.github.io/<repo>/`
- About "Website" field = Pages URL (`gh repo edit --homepage https://…`)

## Community health audit

The 16-point checklist (files → metadata → community health → releases → final) with
check commands: **`references/community-checklist.md`**.

Automated run:

```bash
python3 scripts/validate_repo.py            # auto-detect from git remote
python3 scripts/validate_repo.py owner/repo # explicit repository
```

The canonical baseline is the GitHub **Community Profile API**
(`GET /repos/{owner}/{repo}/community/profile`, metric `health_percentage`;
reference repo `github/docs` = 100%). See `references/community-checklist.md` for the
full file checklist and the canonical analogues (org-level default health files, gh CLI,
GitHub REST API endpoints).

## Anti-patterns

- Topics replaced via POST (only PUT replaces the full list).
- Description that does not cover all significant components.
- Pages enabled but not linked in README/About.
- Broken or stale community-health files lowering the percentage.
