# 🗺 Roadmap

> Living document: status of the `agent-skills` library.
> Format mirrors the [Keep a Changelog](https://keepachangelog.com/) philosophy —
> mark items `[x]` only after they are **merged to `main`** and CI is green.
>
> Каждый скилл отслеживается двумя чекбоксами:
> 1. `[x]` — выпущен (merged to `main`, CI green);
> 2. `[x]` **verified & enriched** — прошёл канонический enrichment: найден аналоги
>    у канонических авторов (Anthropic, obra/superpowers, vercel-labs/skills,
>    trailofbits/skills, NVIDIA SkillSpector и др.) и добавлен
>    `references/canonical-patterns.md` с паттернами.

---

## ✅ v1.0 — Foundation (released 2026-08-07, tag `v1.0.0`)

- [x] `github-repo-hygiene` — GitHub repo descriptive section hygiene (README/LICENSE/community health)
  - [x] verified & enriched
- [x] `test-graphics` — placeholder images/icons/avatars for mocks & e2e
  - [x] verified & enriched
- [x] `reddit-karma` — Reddit karma routine (topics, replies, thank-yous)
  - [x] verified & enriched
- [x] `presentation-maker` — presentations: outline → 16:9 HTML/.pptx
  - [x] verified & enriched
- [x] `docs-system` — product & project documentation guide (branches, phases, L1/L2/L3)
  - [x] verified & enriched
- [x] CI validation pipeline (JSON syntax, manifests, cross-check index ↔ folders)
- [x] Bilingual README (EN/RU) with language switcher
- [x] GitHub Pages site (`https://bestdeejay-design.github.io/agent-skills/`)
- [x] Discovery via `index.json` (triggers, categories, keywords)
- [x] Community health 100%: LICENSE, CODE_OF_CONDUCT, ISSUE/PR templates, SUPPORT, SECURITY

## ✅ v1.1 — Code & Repository (released 2026-08-08)

- [x] `commit-message-writer` — Conventional Commits from `git diff --staged`
  - [x] verified & enriched
- [x] `changelog-generator` — git log → Keep a Changelog
  - [x] verified & enriched
- [x] `code-review` — PR/diff review with checklists (security/perf/style/tests/docs)
  - [x] verified & enriched
- [x] `api-doc-generator` — FastAPI/Express → OpenAPI/Markdown
  - [x] verified & enriched
- [x] `test-generator` — AST-based unit test skeletons (pytest/jest/go)
  - [x] verified & enriched
- [x] `plan-skill` — DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP lifecycle (per `obra/superpowers`)
  - [x] verified & enriched
- [x] `systematic-debugger` — hypothesis-driven debugging workflow (per `obra/superpowers`)
  - [x] verified & enriched
- [x] Bootstrap pipeline: each new skill validated with `plan-skill` + `plan_validator.py`

## ✅ v1.2 — Visual & Docs (released 2026-08-08)

- [x] `diagram-maker` — text → Mermaid → PNG/SVG (flowchart/sequence/ER/arch)
  - [x] verified & enriched
- [x] `mermaid-to-image` — `.mmd` → PNG/SVG renderer (mmdc / mermaid.ink)
  - [x] verified & enriched
- [x] `pdf-report-builder` — markdown → PDF reports (Chrome/weasyprint/pandoc)
  - [x] verified & enriched
- [x] `video-script-writer` — structured video scripts (hook/body/CTA)
  - [x] verified & enriched
- [x] Bootstrap: v1.2 спланирован и провалидирован через `plan-skill`

## ✅ v1.3 — Data (released 2026-08-08)

- [x] `sql-helper` — SQL generation, EXPLAIN analysis, formatting
  - [x] verified & enriched
- [x] `csv-pro` — CSV/Excel profiling, anomalies, visualization
  - [x] verified & enriched
- [x] `web-scraper` — polite scraping with legal guardrails
  - [x] verified & enriched
- [x] `data-analysis` — dataset profiling/anomalies/visualization (per `K-Dense-AI`,
      `teng-lin/notebooklm-py`)
  - [x] verified & enriched
- [x] Bootstrap: v1.3 спланирован и провалидирован через `plan-skill`

## 🛡️ v1.4 — Security

- [x] `security-review` — dependency/linting security audit for a repo (per `trailofbits/skills`) (v1.4.0)
  - [x] verified & enriched
- [x] `secret-scanner` — detect leaked tokens/keys in a codebase (per `NVIDIA/SkillSpector`) (v1.4.0)
  - [x] verified & enriched

## 🔁 v1.5 — Automation & Release

> Связки, замыкающие цикл кодовых скиллов v1.1 (`commit-message-writer` →
> `changelog-generator` → релиз/QA-автоматизация).

- [x] `version-bumper` — bump версии по Conventional Commits + тег релиза (замыкает `commit-message-writer`/`changelog-generator`)
  - [x] verified & enriched
  - [x] выпущен в каталог (v1.5.0): 25-й скилл, детерминированный bump, showcase `docs/showcase/showcase-version-bumper-lovii.md`
- [x] `commit-lint` — валидация Conventional Commits в CI (локальный аналог commitlint)
  - [x] verified & enriched
  - [x] выпущен в каталог (v1.5.0): 26-й скилл, showcase `docs/showcase/showcase-commit-lint-lovii.md`
- [x] `coverage-analyzer` — анализ и трекинг покрытия после `test-generator`
  - [x] verified & enriched
  - [x] выпущен в каталог (v1.5.0): 27-й скилл, showcase `docs/showcase/showcase-coverage-analyzer-lovii.md`
- [x] `api-contract-testing` — генерация тестов/проверок контракта из OpenAPI (после `api-doc-generator`)
  - [x] verified & enriched
  - [x] выпущен в каталог (v1.5.0): 28-й скилл

## 🧪 v1.6 — Skill Showcase (examples on real project)

> После завершения v1.x и перед v2.0 — подготовить рабочие примеры **каждого**
> скилла на реальном проекте (эталон: **lovii.ru** / `lovii_demo`,
> https://github.com/bestdeejay-design/lovii_demo). Требование закреплено в
> `CONTRIBUTING.md` (шаг 6 — showcase обязателен для нового скилла).

- [x] Showcase-шаблон: `docs/showcase-template.md` — каркас демо (вход/запуск/вывод/интерпретация)
- [ ] Showcase v1.0: `github-repo-hygiene`, `test-graphics`, `reddit-karma`, `presentation-maker`, `docs-system`
- [ ] Showcase v1.1: `commit-message-writer`, `changelog-generator`, `code-review`, `api-doc-generator`, `test-generator`, `plan-skill`, `systematic-debugger`
- [ ] Showcase v1.2: `diagram-maker`, `mermaid-to-image`, `pdf-report-builder`, `video-script-writer`
- [ ] Showcase v1.3: `sql-helper`, `csv-pro`, `web-scraper`, `data-analysis` (на данных/коде `lovii_demo`)
- [x] `docs/showcase/` — сборник showcase-демо (по файлу на скилл) + таблица в `README`/`README.ru` (web-scraper, diagram-maker, github-repo-hygiene, test-graphics, seo-toolkit)

## 🇬🇧 v1.7 — Catalog Language Policy (English-primary)

> Языковая политика закреплена в `CONTRIBUTING.md` (английский — основной язык
> скиллов, русский — по желанию). Текущий каталог написан в основном на русском —
> мигрируем все `SKILL.md`/`references`/`index.json` на английский язык.

- [x] `seo-toolkit` — импорт из skills.sh был на испанском: переведён на английский (SKILL.md, 13 команд, canonical-patterns, helper)
  - [x] выпущен в каталог (v1.7.0): 22-й скилл, 13 SEO-команд, helper `scripts/seo_toolkit.py`, canonical analogues (Lighthouse, Google Search Central, schema.org, Screaming Frog)
- [ ] Ревизия CONTRIBUTING.md — языковая политика описана явно (EN-primary, RU и другие языки по желанию)
- [ ] Перевод `SKILL.md` оставшихся 21 скиллов на английский
- [ ] Перевод `references/canonical-patterns.md` на английский (где ещё русский)
- [ ] `index.json` + README/README.ru — синхронизация описаний (EN-дефолт, RU-зеркала)

## 🌟 v2.0 — Ecosystem

- [ ] MCP adapter (load skills via Model Context Protocol)
- [ ] CLI installer (`npx install-skill <name>` / `pip install agent-skills-cli`)
- [ ] Skill templates repository (scaffold a new skill in one command)
- [ ] Community showcase (`SHOWCASE.md` — how people use the skills)
- [ ] `skills.sh.json` catalog — publish to the skills.sh registry (per `vercel-labs`)
- [ ] Multi-harness packaging — convert skills to `.claude-plugin`/`.codex-plugin`/`.cursor-plugin` (per `obra/superpowers`)
- [x] `skill-suggester` — auto-recommend a skill from task description
  - [x] verified & enriched
- [ ] `issue-to-plan`, `prompt-optimizer` — meta/agent skills

## 💡 Backlog (unordered)

- `diagram-svg-theming` — custom palettes/themes for Mermaid output
- `infra-diagram` — AWS/GCP topology renderer
- `pr-description-writer` — auto PR description from changeset (overlap: с `commit-message-writer`/`code-review`)
- `code-explainer` — walk through an unfamiliar module for onboarding
- `seo-basics` — On-page/GEO basics for new pages (per `coreyhaines31`, `AgriciDaniel`)
- `pkm-obsidian` — export notes to Obsidian-compatible markdown (per `kepano/obsidian-skills`)
- `career-builder` — resume/ATS optimization toolkit (per `Paramchoudhary/ResumeSkills`)
- `mock-data-synth` — synthetic test data beyond images (rows/JSON/API fixtures) (overlap: `test-generator`/`test-graphics`)

> Новые скиллы добавляются в ROADMAP сразу с двумя чекбоксами (см. шапку);
> «verified & enriched» закрывается после канонического пасса.

## 🤝 Contributing

Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md) and pick an unclaimed
item from this roadmap. Open an issue or PR with the skill proposal first.