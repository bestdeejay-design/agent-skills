---
name: github-repo-hygiene
description: "DEPRECATED meta-skill. Routes to the four focused repository skills that replaced it: repo-readme-assets (README + animated SVG header/footer), repo-community-files (LICENSE/CODE_OF_CONDUCT/CONTRIBUTING/SECURITY/SUPPORT/templates), repo-metadata-health (description/topics/GitHub Pages/community health/audit), repo-social-preview (og:image PNG). Load one of the four directly instead. Triggers: 'github hygiene', 'repo polish', 'github repo docs', 'оформить репозиторий', 'репозиторий готов к публикации'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "2.0.0"
compatibility: "Router only — delegates to the four focused repo skills"
when_to_use: "Use when polishing a GitHub repo for publication: 'github hygiene', 'repo polish', 'github repo docs', 'оформить репозиторий', 'репозиторий готов к публикации'. Routes to the four focused repo skills. Examples: 'make my repo publish-ready', 'оформи репозиторий для публикации на GitHub'."
---

# GitHub Repo Hygiene — DEPRECATED (router)

> **This skill is deprecated.** It was split into four focused skills. Do **not** run
> workflows from this file — load the matching sub-skill directly.

## Routing table

| Need | Load this skill instead |
|------|-------------------------|
| README (EN + localized mirror) + animated SVG header/footer | `repo-readme-assets` |
| LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates, FUNDING | `repo-community-files` |
| description, topics, GitHub Pages link, community-health audit, 16-point checklist | `repo-metadata-health` |
| social preview (og:image) PNG 1280×640 | `repo-social-preview` |

The old scripts/references were moved into the four new skills:

- `generate_assets.py`, `validate_svg.py`, `extract_context.py` + svg references → `repo-readme-assets`
- `validate_repo.py` + `community-checklist.md` + `repo-hygiene.yml` example → `repo-metadata-health`
- `generate_social_preview.py` + `social-preview.md` → `repo-social-preview`

## Removal plan

Keep this router for one release cycle for backward compatibility (global AGENTS.md
rules may still reference `github-repo-hygiene`), then delete the folder.
