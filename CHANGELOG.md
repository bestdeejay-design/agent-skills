# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This repository tracks the **skill collection** (`agent-skills`) as a whole,
not the internal version bumps of individual skills.

## [1.6.0] - 2026-08-09

### Added
- **`frontend-perfection`** — frontend audit & polish skill. Lighthouse ≥13
  runner `scripts/audit.js` uses chrome-launcher + the Lighthouse Node API
  (no Playwright internals, `.default` fallback, dependencies resolve local →
  `NODE_PATH` → `npm root -g`; mobile/desktop, `--threshold`, compact JSON
  with failed audit ids, exit 0/1/2). Static audit `scripts/meta_audit.py`
  (Python stdlib, offline): SEO meta layer (title/description/canonical/OG/
  Twitter/JSON-LD/robots/sitemap), WCAG contrast by computed luminance,
  heading order, design tokens (zero raw hex outside token block),
  fixed-header `scroll-padding-top`, breakpoint check. Crop-safe OG-image
  methodology (1200×630, ~640px central safe zone, rename-not-overwrite to
  bust social caches, forced reflow before capture). Every fix binds to an
  audit id. Plan: `docs/plans/frontend-perfection-plan.md`. Showcase:
  [`showcase-frontend-perfection-lovii.md`](docs/showcase/showcase-frontend-perfection-lovii.md)
  — lovii_demo Lighthouse mobile 94/96/100/91, desktop 72/96/100/91;
  meta audit 17 checks / 12 violations.
- Catalog (`index.json`) updated 28 → 29 entries, version `1.6.0`;
  ROADMAP v1.6 section released; README/README.ru skill tables, showcase
  tables and badges updated (Skills: 29).

## [1.5.0] - 2026-08-09

### Added
- **`version-bumper`** — deterministic semver bump from git history
  (`bumper.py`, stdlib-only): reads git tags (fallback `0.0.0`), counts
  feat/fix/breaking commits in range, suggests bump (major/minor/patch) and
  release tag. Offline, read-only. Showcase:
  [`showcase-version-bumper-lovii.md`](docs/showcase/showcase-version-bumper-lovii.md).
- **`commit-lint`** — Conventional Commits v1.0.0 validation (`commit_lint.py`,
  stdlib-only): reads `git log` or stdin, parses type/scope/subject, reports
  violations (missing/invalid type, type case, subject/header/body length,
  trailing dot), text/JSON report, exit 0/1/2. Offline, read-only. Showcase:
  [`showcase-commit-lint-lovii.md`](docs/showcase/showcase-commit-lint-lovii.md).
- **`coverage-analyzer`** — test coverage analysis (`coverage_analyzer.py`,
  stdlib-only): reads coverage.py XML/JSON reports, computes statement/line/
  branch coverage, flags files below threshold, summary + recommendations.
  Showcase: [`showcase-coverage-analyzer-lovii.md`](docs/showcase/showcase-coverage-analyzer-lovii.md).
- **`api-contract-testing`** — API contract validation against OpenAPI 3.x
  (`api_contract.py`, stdlib-only, built-in YAML subset parser, no PyYAML):
  enumerates paths + webhooks, checks internal consistency ($refs, duplicates),
  compares endpoint manifest offline, live mode probes HTTP statuses. JSON
  report, exit 0/1/2.

## [1.4.0] - 2026-08-09

### Added
- **`secret-scanner`** — static secret/token scanning for codebases and git
  repos (`secret_scanner.py`, stdlib-only): gitleaks v8.30.1 pattern table
  (19 rule families — AWS, GitHub, OpenAI, Anthropic, Stripe, Google, Slack,
  private keys, JWT, generic), Shannon-entropy gating, allowlist noise
  filters, JSON/Markdown/text reports, redaction, CI exit-code gate.
  Showcase: [`showcase-secret-scanner-lovii.md`](docs/showcase/showcase-secret-scanner-lovii.md).
- **`security-review`** — security review orchestrator (`security_review.py`,
  stdlib-only): lockfile/manifest inventory (npm/pnpm/yarn, pip/poetry, cargo,
  go, gem, maven/gradle, composer), exit-code classifier for 13 SCA/SAST tools
  (semgrep, bandit, gitleaks, osv-scanner, pip-audit, trufflehog, checkov,
  trivy, grype, npm audit, cargo audit, dependency-check) with verified
  semantics, JSON normalizers (osv-scanner, pip-audit, semgrep, gitleaks,
  bandit) to one unified finding schema, plain/markdown/JSON reports.
  Showcase: `docs/showcase/showcase-security-review-lovii.md`.

## [1.3.0] - 2026-08-08


### Added
- **`sql-helper`** — SQL generation from a text question + DDL schema
  (`sql_helper.py`): in-memory sqlite3 schema from DDL, intent templates
  (select/join/where/group/order/count/limit), candidate verification via
  `EXPLAIN`, human-readable plan with `--explain`.
- **`csv-pro`** — CSV profiling (`csv_pro.py`): column types, min/max/mean,
  missing counts, unique values, top-3 frequent; anomalies (zero variance,
  >95% empty, duplicate rows, >1000-char rows, ≥5×IQR outliers); markdown or
  JSON output; `;`/`,` delimiter detection, file or stdin.
- **`web-scraper`** — polite HTML scraping to Markdown/JSON (`scrape.py`):
  simple CSS selectors (tag/tag#id/tag.class), text/links/tables extraction,
  built-in legal guardrails — robots.txt check, honest User-Agent, request
  delay (default 1.0 s), 10 MB page limit.
- **`data-analysis`** — dataset profiling for CSV or JSON-array (`data_analyze.py`):
  field types, count/unique/missing, min/max/mean/std, mode + top-N, 5-bin
  histogram for numerics, top-3 Pearson correlations, anomalies and
  recommendations; markdown (default) or JSON report; CSV delimiter
  auto-detection (`;` preferred, then `,`).
- **Showcase process & real-project examples**: `CONTRIBUTING.md` — шаг 6
  (обязательный showcase на реальном проекте, эталон: lovii.ru / `lovii_demo`);
  `ROADMAP.md` — новая секция v1.6 Skill Showcase (примеры каждого скилла на
  lovii.ru до v2.0); `docs/showcase-template.md` — каркас демо;
  `docs/showcase/` — эталонные примеры: `web-scraper` на lovii.ru (White Paper
  → Markdown), `diagram-maker` на `lovii_demo/docs/ARCHITECTURE.md` (текстовая
  архитектура SPA → Mermaid flowchart); `README`/`README.ru` — таблица
  showcase-примеров. Валидатор 21/21.
- **v1.3 planned via bootstrap**: `docs/plans/v1.3-plan.md` passed
  `plan_validator.py`; catalog (`index.json`) updated 17 → 21 entries;
  README/README.ru skill tables and repo trees updated; `ROADMAP.md` v1.3
  marked released.
- **Canonical enrichment for v1.3 skills**: each of `sql-helper`, `csv-pro`,
  `web-scraper`, `data-analysis` gained `references/canonical-patterns.md`
  (analogues among canonical authors — Anthropic, sqlsure, Vanna.ai, Spider/
  BIRD, sqlite-utils, ydata-profiling, DuckDB, Scrapy, MCP fetch, D-Tale, etc. —
  with missing-technique analysis and citable CLI/API examples); `SKILL.md`
  updated with "Canonical analogues" sections; `ROADMAP.md` marks them
  `verified & enriched`; `CONTRIBUTING.md` now mandates canonical enrichment
  for every new skill.

## [1.2.0] - 2026-08-08

### Added
- **`mermaid-to-image`** — render `.mmd` diagrams to PNG/SVG
  (`mermaid_to_image.py`): local `mmdc` (mermaid-cli) preferred, `mermaid.ink`
  API fallback; `--engine auto/mmdc/ink`, `--bg`, `--scale`, file or stdin,
  output file or stdout. Discovered & fixed mermaid.ink API quirks (PNG via
  `/img/`, not `/png/`; 400 on `mermaid` payload for PNG; 400 on `scale` without
  `width`/`height` — `--scale` applies to mmdc only; trailing `\n` in `.mmd`
  breaks `/img/` for code with `{...}`/`|...|` — input is stripped).
- **`pdf-report-builder`** — markdown → PDF reports (`pdf_report_builder.py`):
  HTML via pandoc (or built-in converter), PDF via first available engine —
  Chrome/Chromium/Edge headless `--print-to-pdf`, weasyprint, or pandoc with a
  PDF engine (pdflatex/tectonic/typst); tables/code/quotes/links supported.
- **`video-script-writer`** — structured video scripts from a topic
  (`video_script_writer.py`): Hook → Body (5 scenes: Problem/Basics/Walkthrough/
  Pitfalls/Pro tip) → CTA, timecodes table, ru/en, custom CTA, full or outline.
- **v1.2 planned via bootstrap**: `docs/plans/v1.2-plan.md` passed
  `plan_validator.py`; catalog (`index.json`) updated 14 → 17 entries;
  README/README.ru skill tables and repo trees updated; `ROADMAP.md` v1.2
  marked released.

## [Unreleased]

### Added
- **`dsh-runner`** — autonomous agent runs via DeepSeek Harness
  (`scripts/dsh_task.py`): task → isolated one-off workspace → `harness.run()`
  → JSON report (`final_response`, `finish_reason`) + JSONL session log;
  headless single-run mode or Web UI (`npx @deepseek-ai/dsh web`),
  model-comparison mode; requires `DEEPSEEK_API_KEY` or an OpenAI-compatible
  endpoint (`DEEPSEEK_BASE_URL`); developer-preview pitfalls and workspace
  isolation rules in `references/runbook.md`. New `agents` category in the
  catalog; Catalog (`index.json`) updated 45 → 46 entries; README/README.ru
  skill tables, badges and repo trees updated.
- **`seo-toolkit`** — 13 SEO-команд для AI-агентов (импорт из открытого каталога
  skills.sh, переименование без привязки к вендорскому имени: `claude-seo` →
  `seo-toolkit`): технический аудит, Core Web Vitals, crawlability, schema.org,
  keywords, meta, content, images, отчёты со взвешенным скорингом, сравнение с
  конкурентами, автономные исправления (P1–P5, diff-before-apply). Два режима —
  URL (fetch сайтов) и файловый. Новый helper `scripts/seo_toolkit.py`
  (Python 3 stdlib): аудит meta/headings/img alt, плотность ключей, валидация
  JSON-LD. Канонические аналоги (Lighthouse, Google Search Central, schema.org,
  sitemaps.org, RFC 9309, Screaming Frog, Rich Results Test) — в
  `references/canonical-patterns.md`; showcase на lovii.ru —
  `docs/showcase/showcase-seo-toolkit-lovii.md`.
- Catalog (`index.json`) updated 21 → 22 entries; README/README.ru skill tables,
  showcase tables and repo trees updated.
- **`docs/SKILLS_CATALOG.md`** — ecosystem catalog: 11 domains, 15 benchmark
  vendor libraries, formats/standards, 8 trends, coverage gaps, 8 roadmap
  recommendations (from two research passes: ecosystem map + skills audit).
- `license: MIT`, `metadata` (author/version) and `compatibility` fields in
  the frontmatter of all 9 `SKILL.md` manifests.
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
- **`changelog-generator`** — Keep a Changelog section from git history
  (`changelog_gen.py`): parses `git log tag..HEAD` (NUL-separated fields),
  Conventional Commits type mapping (feat→Added, fix→Fixed, perf/refactor→Changed,
  breaking→own section), rendered Markdown with dates and commit links.
- **`api-doc-generator`** — REST API Markdown docs from an OpenAPI 3.x schema
  (`api_doc.py`): per-endpoint sections with method/path/params/request body/
  response codes; FastAPI via `app.openapi()`, Express via swagger-jsdoc.
- **`test-generator`** — pytest skeletons from a Python module AST (`test_gen.py`):
  ghostwriter-style arg heuristics (bool→True/False, int→0/-1/1, str→sample/empty,
  list/dict→empty, Optional→None), `@pytest.mark.parametrize`, private funcs skipped.
- **`plan-skill`** — implementation planning per superpowers v2
  (`plan_validator.py` + template + example): brainstorming→writing-plans→
  executing→verification, HARD-GATE, bite-sized steps, no placeholders.
- **`systematic-debugger`** — Iron Law debugging workflow (`debug_log.py`):
  4 phases (reproduce→hypotheses→isolate root cause→fix+regression), Red Flags,
  Rationalization Table; renders a structured phase report.
- **Bootstrap pipeline**: each new skill above was planned and validated with
  `plan-skill` (`docs/plans/*.md` passed `plan_validator.py`) before creation.
- Catalog (`index.json`) updated 9 → 14 entries; README/README.ru skill tables
  and repo trees updated; `ROADMAP.md` v1.1 marked released.

### Changed
- **Enriched all 9 skills** per the ecosystem audit: descriptions rewritten in
  imperative voice with "When to use / Do NOT use" sections (where relevant),
  internal paths switched to relative (`scripts/...`, `references/...`),
  emoji removed from `SKILL.md` prose. `presentation-maker` slimmed from 379 →
  253 lines by extracting `references/design-system.md` and
  `references/product-designer.md`; `test-graphics` now bundles
  `scripts/test-graphics.py` (declared via `requirements.script`).
- **Fixed metadata drift**: triggers and descriptions were inconsistent across
  `SKILL.md` ↔ `skill.json` ↔ `index.json` in 7 of 9 skills; synchronized all
  three sources to the `SKILL.md` frontmatter as the canonical definition
  (9/9 verified identical, validator green).
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

### Fixed
- **`seo-toolkit`** helper (`scripts/seo_toolkit.py`): keyword density now strips
  `<script>`/`<style>` content before counting (visible-text word count only;
  CSS/JS source previously inflated it ~2-3×); JSON-LD validator now supports
  `Organization` (requires `name` + `url`, consistent with Product/Article/FAQPage
  rules); CLI accepts a positional HTML path as a fallback for `--file`
  (`--meta <file>` no longer fails with `unrecognized arguments`).

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