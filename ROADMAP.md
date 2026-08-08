# 🗺 Roadmap

> Living document: status of the `agent-skills` library.
> Format mirrors the [Keep a Changelog](https://keepachangelog.com/) philosophy —
> mark items `[x]` only after they are **merged to `main`** and CI is green.

---

## ✅ v1.0 — Foundation (released 2026-08-07, tag `v1.0.0`)

- [x] 5 core skills: `github-repo-hygiene`, `test-graphics`, `reddit-karma`,
      `presentation-maker`, `docs-system`
- [x] CI validation pipeline (JSON syntax, manifests, cross-check index ↔ folders)
- [x] Bilingual README (EN/RU) with language switcher
- [x] GitHub Pages site (`https://bestdeejay-design.github.io/agent-skills/`)
- [x] Discovery via `index.json` (triggers, categories, keywords)
- [x] Community health 100%: LICENSE, CODE_OF_CONDUCT, ISSUE/PR templates, SUPPORT, SECURITY

## 🚧 v1.1 — Code & Repository (in progress)

- [x] `commit-message-writer` — Conventional Commits from `git diff --staged`
- [ ] `changelog-generator` — git log → Keep a Changelog
- [x] `code-review` — PR/diff review with checklists (security/perf/style/tests/docs)
- [ ] `api-doc-generator` — FastAPI/Express → OpenAPI/Markdown
- [ ] `test-generator` — AST-based unit test skeletons (pytest/jest/go)
- [ ] `plan-skill` — DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP lifecycle (per `obra/superpowers`)
- [ ] `systematic-debugger` — hypothesis-driven debugging workflow (per `obra/superpowers`)

## 🔮 v1.2 — Visual & Docs

- [x] `diagram-maker` — text → Mermaid → PNG/SVG (flowchart/sequence/ER/arch)
- [ ] `mermaid-to-image` — `.mmd` → PNG/SVG renderer
- [ ] `pdf-report-builder` — markdown → PDF reports
- [ ] `video-script-writer` — structured video scripts (hook/body/CTA)

## 🚀 v1.3 — Data

- [ ] `sql-helper` — SQL generation, EXPLAIN analysis, formatting
- [ ] `csv-pro` — CSV/Excel profiling, anomalies, visualization
- [ ] `web-scraper` — polite scraping with legal guardrails
- [ ] `data-analysis` — dataset profiling/anomalies/visualization (per `K-Dense-AI`,
      `teng-lin/notebooklm-py`)

## 🛡️ v1.4 — Security

- [ ] `security-review` — dependency/linting security audit for a repo (per `trailofbits/skills`)
- [ ] `secret-scanner` — detect leaked tokens/keys in a codebase (per `NVIDIA/SkillSpector`)

## 🌟 v2.0 — Ecosystem

- [ ] MCP adapter (load skills via Model Context Protocol)
- [ ] CLI installer (`npx install-skill <name>` / `pip install agent-skills-cli`)
- [ ] Skill templates repository (scaffold a new skill in one command)
- [ ] Community showcase (`SHOWCASE.md` — how people use the skills)
- [ ] `skills.sh.json` catalog — publish to the skills.sh registry (per `vercel-labs`)
- [ ] Multi-harness packaging — convert skills to `.claude-plugin`/`.codex-plugin`/`.cursor-plugin` (per `obra/superpowers`)
- [x] `skill-suggester` — auto-recommend a skill from task description
- [ ] `task-decomposer`, `prompt-optimizer` — meta/agent skills

## 💡 Backlog (unordered)

- `diagram-svg-theming` — custom palettes/themes for Mermaid output
- `infra-diagram` — AWS/GCP topology renderer
- `pr-description-writer` — auto PR description from changeset
- `release-notes` — tag-to-tag notes for release page
- `code-explainer` — walk through an unfamiliar module for onboarding
- `seo-basics` — On-page/GEO basics for new pages (per `coreyhaines31`, `AgriciDaniel`)
- `pkm-obsidian` — export notes to Obsidian-compatible markdown (per `kepano/obsidian-skills`)
- `career-builder` — resume/ATS optimization toolkit (per `Paramchoudhary/ResumeSkills`)
- `mock-data-synth` — synthetic test data beyond images (rows/JSON/API fixtures)

## 🤝 Contributing

Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md) and pick an unclaimed
item from this roadmap. Open an issue or PR with the skill proposal first.