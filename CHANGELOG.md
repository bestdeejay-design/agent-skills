# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This repository tracks the **skill collection** (`agent-skills`) as a whole,
not the internal version bumps of individual skills.

## [Unreleased]

### Added
- Product documentation branch and 3 product templates (VISION/PRD/ROADMAP) to
  `docs-system`.
- **`commit-message-writer`** — Conventional Commits messages from
  `git diff --staged` (`suggest.py`): type/scope inference, breaking-change
  detection, optional gitmoji; analyzes staged changes only, never commits.
- **`code-review`** — structured PR/diff review (`review.py` + `checklists.py`):
  categories correctness/security/performance/style/tests/edge-cases, output
  `[severity] file:line` findings with suggested fixes; GH PR comment template.
- **`diagram-maker`** — text → Mermaid diagrams: flowchart/sequence/architecture/ER
  (`mermaid_to_markdown.py` + 4 templates + 2 examples).
- **`skill-suggester`** — recommends a skill from `index.json` for a task
  (`skill_suggest.py`): trigger (weight 3) + description (weight 1) scoring,
  top-5 output, combo chains up to 3 skills.
- `ROADMAP.md` — living roadmap (v1.0 released, v1.1–v2.0 planned).
- Catalog (`index.json`) version bumped to 1.1.0 with the 4 new entries;
  README/README.ru skill tables and repo tree updated (9 skills).

### Changed
- Restructured `docs-system` as a product-vs-project documentation guide
  (catalog split into `product-docs.md` / `project-docs.md`).
- **De-personalized `reddit-karma`**: removed the owner's username,
  subreddits/karma snapshot, personal log paths and target-resource references;
  replaced with per-user placeholders (`ВАШ_НИКНЕЙМ`, `ВАШ_РЕСУРС`, configurable
  log paths) so the skill is portable/installable by anyone. README (EN+RU),
  `index.json`, `skill.json` and the local `~/.config` copy synced.
- **De-personalized `docs-system` pmos example**: renamed `examples/pmos/` →
  `examples/example-monorepo/`, removed the owner's repo URL
  (`bestdeejay-design/pmos`) and project name from SKILL.md, ROADMAP, references,
  templates and the example README; event-subject prefixes `pmos.*` → `app.*`;
  paths in README tree and `skill.json` updated.

## [1.0.0] - 2026-08-07

### Added
- 5 skills: `github-repo-hygiene`, `test-graphics`, `reddit-karma`,
  `presentation-maker`, `docs-system`.
- `index.json` repository manifest with discovery by triggers/categories.
- CI workflow validating skill manifests, cross-checking index ↔ folders.
- GitHub Pages deployment.
- EN/RU README pair with a language switcher.

### Changed
- English-primary language convention across all skills (Russian optional).

[Unreleased]: https://github.com/bestdeejay-design/agent-skills/compare/v1.0.0...main
[1.0.0]: https://github.com/bestdeejay-design/agent-skills/releases/tag/v1.0.0