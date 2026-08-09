<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <img src="assets/header.svg" alt="header" />
  </a>
</p>

# Agent Skills — AI Agent Skill Collection

> Autonomous skill instructions for AI agents: Sisyphus, opencode, and compatible. Each skill is a folder with `SKILL.md` (instructions) and `skill.json` (manifest for installation/discovery).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 29](https://img.shields.io/badge/Skills-29-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--09-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Skill Catalog

> 📚 Ecosystem map: see [**docs/SKILLS_CATALOG.md**](docs/SKILLS_CATALOG.md) — catalog of the AI agent skills ecosystem (official vendors, formats, standards, ~4.85M SKILL.md files tracked, gaps and recommendations).

| Skill | Category | Description | Triggers |
|-------|----------|-------------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene/SKILL.md) | `repository` | Validates and updates GitHub repo descriptive section: README (EN+RU) + visual header/footer as **local animated SVG** (`assets/header.svg` + `assets/footer.svg`, SMIL waves & gradient — no external services), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates, social preview, releases, description, topics, GitHub Pages, community health. | `github hygiene`, `setup repository`, `update readme`, `github page`, `repo description`, `search tags`, `topics`, `contributing`, `license`, `security policy`, `readme header`, `animated svg`, `waving banner` |
| [**test-graphics**](skills/test-graphics/SKILL.md) | `media` | Generates test images, photos, icons, placeholders via Python + free APIs (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `test pictures`, `icons for test`, `stubs`, `mock data images`, `generate photo` |
| [**reddit-karma**](skills/reddit-karma/SKILL.md) | `social` | Systematic Reddit karma building for your account: topic search, response drafting, tone detection, thank-you templates, routine runs. Configure your username, subreddits and target resource. | `reddit`, `karma`, `r/LocalLLaMA`, `build karma`, `reply to comments`, `reddit run`, `leave trace` |
| [**presentation-maker**](skills/presentation-maker/SKILL.md) | `media` | Presentation generator: Markdown outline, HTML 16:9 slides, .pptx via python-pptx. Auto-layouts, themes, design-system (tokens, mood), product-design module (narrative, data-viz, a11y, premium). | `make presentation`, `presentation`, `slides`, `pptx`, `make deck`, `generate slides` |
| [**docs-system**](skills/docs-system/SKILL.md) | `repository` | Guide for an AI agent: how to compose product and project documentation and its composition. Product branch (VISION/PRD/ROADMAP/FEATURES) + project branch (ARCHITECTURE/ADR/contracts/TEST_CASES/REFERENCE map), fill order (phases), templates, completeness checklist, levels L1/L2/L3 for large systems. | `documentation`, `docs catalog`, `documentation structure`, `docs for new project`, `documentation plan`, `документация`, `каталог документов` |
| [**commit-message-writer**](skills/commit-message-writer/SKILL.md) | `code` | Generates Conventional Commits messages from `git diff --staged`: type inferred from changed files, scope from paths, short summary, optional body. `suggest.py` (Python 3) only analyzes staged changes, never commits. | `commit message`, `write commit`, `git commit`, `conventional commit`, `[сообщение коммита]`, `[написать коммит]`, `[закоммитить]` |
| [**code-review**](skills/code-review/SKILL.md) | `code` | Structured code review: reads a git diff or path to repo/file, applies checklists by category (correctness, security, performance, style, tests, edge cases) and emits `[severity] file:line` findings with suggested fixes. Analysis only — makes no edits. | `code review`, `[ревью кода]`, `review PR`, `[проверь код]`, `pull request review`, `code quality`, `[найти баги]`, `review commit` |
| [**diagram-maker**](skills/diagram-maker/SKILL.md) | `data` | Generates diagrams from a text description: flowchart, sequence, architecture, ER — in Mermaid syntax. Input: natural language; output: Mermaid code + rendering recommendation (mermaid.live / mermaid-cli / MCP). | `diagram`, `mermaid`, `flowchart`, `[диаграмма]`, `sequence diagram`, `[архитектура]`, `[ER-схема]`, `draw a diagram` |
| [**mermaid-to-image**](skills/mermaid-to-image/SKILL.md) | `data` | Renders `.mmd` Mermaid diagrams to PNG/SVG: local `mmdc` (mermaid-cli) preferred, mermaid.ink API fallback; engine/background/scale options, file or stdin. | `mermaid в картинку`, `отрендерить диаграмму`, `render diagram`, `диаграмма в svg`, `mermaid to image` |
| [**pdf-report-builder**](skills/pdf-report-builder/SKILL.md) | `media` | Builds PDF reports from Markdown: HTML via pandoc (or built-in converter), PDF via first available engine — Chrome/Chromium headless, weasyprint, or pandoc+PDF engine. Tables/code/quotes supported. | `отчёт в pdf`, `markdown в pdf`, `собери отчёт`, `pdf report`, `document to pdf` |
| [**skill-suggester**](skills/skill-suggester/SKILL.md) | `code` | Recommends a skill from the library for a user task: reads `index.json`, scores triggers and descriptions, returns top-5 with relevance plus combos of up to 3 skills. | `which skill`, `[какой скилл использовать]`, `suggest skill`, `[подбор скилла]`, `[рекомендовать скилл]`, `[какой навык]` |
| [**api-doc-generator**](skills/api-doc-generator/SKILL.md) | `repository` | Renders REST API documentation from an OpenAPI 3.x schema (incl. 3.1.0) to Markdown: per-endpoint sections with method/path/params/request/response codes. FastAPI via `app.openapi()`; Express via swagger-jsdoc. | `api doc`, `openapi`, `swagger in markdown`, `api reference`, `document endpoints`, `описать API` |
| [**changelog-generator**](skills/changelog-generator/SKILL.md) | `repository` | Generates a Keep a Changelog section from git history (Conventional Commits): git log tag..HEAD, type mapping feat→Added/fix→Fixed/perf→Changed, breaking into its own section. Python 3 stdlib. | `changelog`, `generate changelog`, `release notes`, `история изменений`, `keep a changelog` |
| [**plan-skill**](skills/plan-skill/SKILL.md) | `code` | Implementation planning per `obra/superpowers` v2: brainstorming → writing-plans → executing → verification; HARD-GATE, bite-sized steps, no placeholders, Interfaces (Produces/Consumes). `plan_validator.py` checks the plan is execution-ready. | `спланируй`, `составь план`, `plan`, `разбей на шаги`, `roadmap`, `write a plan` |
| [**systematic-debugger**](skills/systematic-debugger/SKILL.md) | `code` | Hypothesis-driven debugging per Iron Law: reproduce → hypotheses → isolate root cause → minimal fix + regression test. Red Flags, Rationalization Table. `debug_log.py` renders a phase report. | `debug`, `отладить`, `почему не работает`, `баг`, `debugging`, `fix the bug` |
| [**test-generator**](skills/test-generator/SKILL.md) | `code` | Generates pytest skeletons from a Python module AST with ghostwriter-style arg heuristics (bool→True/False, int→0/-1/1, str→sample/empty, list/dict→empty, Optional→None). `@pytest.mark.parametrize` scaffolding; TS/Go references. | `generate tests`, `сгенерируй тесты`, `test skeleton`, `pytest скелет`, `покрытие тестами` |
| [**video-script-writer**](skills/video-script-writer/SKILL.md) | `media` | Generates structured video scripts from a topic: Hook → Body (5 scenes: Problem/Basics/Walkthrough/Pitfalls/Pro tip) → CTA, timecodes table, ru/en, custom CTA, full script or outline. | `сценарий видео`, `video script`, `напиши сценарий`, `план видео`, `video outline` |
| [**sql-helper**](skills/sql-helper/SKILL.md) | `data` | Generates SQL from a text question + DDL schema: in-memory sqlite3 schema from DDL, question words mapped to tables/columns, intent templates (select/join/where/group/order/count/limit), every candidate checked via EXPLAIN, readable plan with `--explain`. | `sql helper`, `sql генерация`, `сгенерируй sql`, `explain запроса`, `sql formatting` |
| [**csv-pro**](skills/csv-pro/SKILL.md) | `data` | Profiles CSV files: column types, min/max/mean, missing, unique, top-3 frequent; anomaly detection (zero variance, >95% empty, duplicate rows, >1000-char rows, ≥5×IQR outliers); markdown or JSON output; delimiter detection, file or stdin. | `csv profile`, `профиль csv`, `анализ csv`, `аномалии csv`, `csv anomalies` |
| [**web-scraper**](skills/web-scraper/SKILL.md) | `data` | Polite HTML scraping to Markdown/JSON: simple CSS selector (tag/tag#id/tag.class), text/links/tables extraction; legal guardrails — robots.txt check, honest User-Agent, request delay, 10 MB page limit. | `web scraping`, `скраппинг`, `скачать данные с сайта`, `парсинг сайта`, `scrape` |
| [**data-analysis**](skills/data-analysis/SKILL.md) | `data` | Profiles datasets (CSV or JSON array): field types, count/unique/missing, min/max/mean/std, mode + top-N, 5-bin histogram, top-3 Pearson correlations, anomalies, recommendations; markdown or JSON report. | `data analysis`, `анализ данных`, `профиль датасета`, `статистика данных`, `eda` |
| [**seo-toolkit**](skills/seo-toolkit/SKILL.md) | `media` | 13 SEO commands for AI agents: technical audit, Core Web Vitals, crawlability, schema.org, keywords, meta tags, content analysis, images, reports, competitor comparison, autonomous fixes. URL mode (fetch external sites) + file mode (local projects). Helper `seo_toolkit.py`: meta/headings/alt audit, keyword density, JSON-LD validation. | `seo audit`, `core web vitals`, `schema org`, `json-ld`, `keywords analysis`, `seo report`, `meta tags`, `crawlability` |
| [**secret-scanner**](skills/secret-scanner/SKILL.md) | `code` | Static secret/token scanning for codebases and git repos: AWS, GitHub, OpenAI, Anthropic, Stripe, Google, Slack, private keys, JWTs via gitleaks v8.30.1 pattern table + Shannon entropy gating + allowlist noise filters. Stdlib-only Python script, offline, JSON/Markdown/text reports, redaction, CI exit-code gate. | `secret scan`, `проверь секреты`, `leaked token`, `scan for keys`, `hardcoded credentials` |
| [**security-review**](skills/security-review/SKILL.md) | `code` | Security review orchestrator: lockfile inventory (npm/pip/cargo/go/gem/maven/gradle/composer), exit-code classifier for 13 sca tools (semgrep, bandit, gitleaks, osv-scanner, pip-audit, trufflehog, checkov, trivy, grype, npm audit, cargo audit, dependency-check), JSON normalizer to one unified finding schema, reports. Stdlib-only, offline, OWASP-aligned. | `security review`, `audit dependencies`, `lockfile audit`, `проверь зависимости`, `osv-scanner`, `уязвимости` |
| [**version-bumper**](skills/version-bumper/SKILL.md) | `code` | Deterministic semver bump from git history: reads git tags (fallback `0.0.0`), counts feat/fix/breaking in Conventional Commits range, suggests bump (major/minor/patch) + release tag, `-s` deterministic mode. Stdlib-only, offline, read-only. Closes the loop for `commit-message-writer`/`changelog-generator`. | `version bump`, `next version`, `semver`, `release tag`, `какая следующая версия`, `определи версию`, `next release version` |
| [**commit-lint**](skills/commit-lint/SKILL.md) | `code` | Conventional Commits v1.0.0 validation: reads `git log` (or stdin), parses type/scope/subject, reports violations (missing/invalid type, case, subject/header/body length, trailing dot), text/JSON report, exit 0/1/2. Stdlib-only, offline, read-only. Local commitlint analog. | `commit lint`, `lint commits`, `conventional commits`, `check commit messages`, `проверка коммитов`, `валидация коммитов`, `commit style check` |
| [**coverage-analyzer**](skills/coverage-analyzer/SKILL.md) | `code` | Test coverage analysis from coverage.py XML/JSON reports: statement/line/branch coverage, per-file breakdown with files below threshold, total percentage, actionable recommendations. Stdlib-only, offline. Pairs with `test-generator`. | `coverage`, `coverage analysis`, `coverage report`, `test coverage`, `покрытие кода`, `анализ покрытия`, `branch coverage` |
| [**api-contract-testing**](skills/api-contract-testing/SKILL.md) | `code` | API contract validation against OpenAPI 3.x spec (JSON/YAML, built-in YAML subset parser, no PyYAML): enumerates paths + webhooks, checks internal consistency ($refs, duplicates, missing responses), compares endpoint manifest offline, live mode probes HTTP statuses. JSON report, exit 0/1/2. Stdlib-only. Pairs with `api-doc-generator`. | `api contract testing`, `contract test`, `validate openapi spec`, `spec vs manifest`, `endpoint coverage`, `проверь контракт API`, `тест контракта` |
| [**frontend-perfection**](skills/frontend-perfection/SKILL.md) | `code` | Frontend audit & polish to verifiable perfection: real Chrome through chrome-launcher + Lighthouse ≥13 Node API (mobile+desktop, no Playwright internals, `.default` fallback, self-resolved deps, exit 0/1/2, compact JSON with failed audit ids); offline Python-stdlib static audit (SEO meta layer, WCAG contrast by computed luminance, heading order, design tokens — zero raw hex outside tokens, scroll-padding under fixed header, breakpoints); crop-safe OG-image generation (1200×630 with ~640px central safe zone, rename not overwrite to bust social caches, forced reflow before capture). Every fix binds to an audit id. | `frontend audit`, `lighthouse check`, `make it 100/100/100/100`, `perfect the layout`, `og image`, `contrast check`, `design tokens`, `проверь вёрстку`, `довести фронтенд до идеала` |

## 🎬 Showcase — real-project examples

> Live demonstrations of skills on **real** projects (not abstract examples).
> Reference project: **lovii.ru** (`lovii_demo`). Every new skill must ship a
> showcase. Template: [`docs/showcase-template.md`](docs/showcase-template.md).

| Skill | Project | What's demonstrated |
|---|---|---|
| [`web-scraper`](docs/showcase/showcase-web-scraper-lovii.md) | lovii.ru landing (White Paper) | Scraping the public page → Markdown summary (sections, metrics, contacts, table) |
| [`diagram-maker`](docs/showcase/showcase-diagram-maker-lovii.md) | lovii_demo `docs/ARCHITECTURE.md` | Textual SPA architecture → Mermaid flowchart of role-based screen structure |
| [`github-repo-hygiene`](docs/showcase/showcase-github-repo-hygiene-lovii.md) | lovii_demo repository | Community Health audit (0% → 100%): missing files, metadata, API checklists |
| [`test-graphics`](docs/showcase/showcase-test-graphics-lovii.md) | lovii_demo mock data + brand | Partner avatars, product placeholders, Lucide icons, batch for e2e |
| [`seo-toolkit`](docs/showcase/showcase-seo-toolkit-lovii.md) | lovii.ru landing (White Paper) | SEO-audit of the public page: meta/OG/headings/alt via helper + Core Web Vitals checklist, JSON-LD (0 blocks) |
| [`secret-scanner`](docs/showcase/showcase-secret-scanner-lovii.md) | lovii_demo repo | Secret scan of the repo: 1 Medium (generic-api-key, UUID false positive, `index.js:7`) — entropy + allowlist interpretation |
| [`security-review`](docs/showcase/showcase-security-review-lovii.md) | lovii_demo repo | Lockfile inventory (npm `package-lock.json` in `.opencode/`), exit-code classification (osv-scanner 129 = API error, semgrep 1 = findings) |
| [`version-bumper`](docs/showcase/showcase-version-bumper-lovii.md) | agent-skills + lovii_demo | Next semver from git history: agent-skills `v1.0.0` → `v1.1.0` (minor), lovii_demo fallback `0.0.0` → `v0.1.0` |
| [`commit-lint`](docs/showcase/showcase-commit-lint-lovii.md) | agent-skills + lovii_demo | Conventional Commits validation: 12/12 agent-skills (long subjects + `i18n` type), lovii_demo type-case + missing-type classes |
| [`coverage-analyzer`](docs/showcase/showcase-coverage-analyzer-lovii.md) | agent-skills | Coverage report from coverage.py XML: statements/line/branch, files below threshold, summary percentage |
| [`frontend-perfection`](docs/showcase/showcase-frontend-perfection-lovii.md) | lovii_demo | Real-Chrome Lighthouse across form factors (mobile 94/96/100/91, desktop 72/96/100/91) + offline meta audit (17 checks, 12 violations: meta layer, tokens, contrast, scroll-padding) |

---

## 🚀 Installation

### For opencode

Copy the desired skill folder to `~/.config/opencode/skills/`:

```bash
# Example: install presentation-maker
cp -r skills/presentation-maker ~/.config/opencode/skills/
```

Or load directly via skill tool pointing to `SKILL.md`:

```bash
# In opencode session
skill load path/to/skills/presentation-maker/SKILL.md
```

### For Sisyphus / other agents

Each skill contains:
- `SKILL.md` — full instruction (Markdown)
- `skill.json` — manifest with metadata (name, version, triggers, requirements, files)

Agent can parse `index.json` to discover skills by triggers/categories and load the needed one.

---

## 📁 Repository Structure

```
agent-skills/
├── index.json                 # Repository manifest (search/catalog)
├── README.md                  # This file (English)
├── README.ru.md               # Russian mirror
├── CHANGELOG.md               # Keep a Changelog
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # How to add/update skills
├── SECURITY.md                # Security policy
├── SUPPORT.md                 # Where to get help
├── CODE_OF_CONDUCT.md         # Contributor Covenant 2.1
├── FUNDING.yml                # Sponsor button
├── og-image.png               # Social preview (1280x640)
├── docs/
│   └── SKILLS_CATALOG.md      # Ecosystem catalog (vendors, formats, gaps)
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml     # Issue form (bug)
│   │   └── feature_request.yml # Issue form (feature)
│   ├── pull_request_template.md
│   ├── release.yml            # Auto-generated release notes config
│   └── workflows/
│       └── validate-skills.yml # CI: JSON schema, cross-check, Python syntax
└── skills/
    ├── github-repo-hygiene/
    │   ├── SKILL.md
    │   └── skill.json
    ├── test-graphics/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/test-graphics.py
    ├── reddit-karma/
    │   ├── SKILL.md
    │   └── skill.json
    ├── presentation-maker/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── references/
    │   │   ├── design-system.md
    │   │   └── product-designer.md
    │   ├── scripts/
    │   │   ├── build_html.py
    │   │   ├── build_pptx.py
    │   │   └── verify_slides.py
    │   ├── templates/
    │   │   ├── slides.html
    │   │   ├── themes/*.json
    │   │   └── icons/*.svg
    └── docs-system/
        ├── SKILL.md
        ├── skill.json
        ├── ROADMAP.md
        ├── references/
        │   ├── product-docs.md
        │   ├── project-docs.md
        │   ├── order.md
        │   ├── completeness.md
        │   └── levels.md
        ├── templates/
        │   ├── product/   (VISION.tmpl, PRD.tmpl, ROADMAP.tmpl)
        │   └── project/   (14 *.tmpl)
        └── examples/example-monorepo/README.md
    ├── commit-message-writer/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/suggest.py
    ├── code-review/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── scripts/
    │   │   ├── review.py
    │   │   └── checklists.py
    │   ├── templates/review-template.md
    │   └── examples/example-pr.md
    ├── diagram-maker/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── scripts/mermaid_to_markdown.py
    │   ├── templates/ (flowchart.mmd, sequence.mmd, architecture.mmd, er.mmd)
    │   └── examples/ (example-cart-flow.mmd, example-billing-seq.mmd)
    ├── mermaid-to-image/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/mermaid_to_image.py
    ├── pdf-report-builder/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/pdf_report_builder.py
    ├── skill-suggester/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/skill_suggest.py
    ├── video-script-writer/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/video_script_writer.py
    ├── api-doc-generator/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/api_doc.py
    ├── changelog-generator/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/changelog_gen.py
    ├── plan-skill/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── scripts/plan_validator.py
    │   ├── templates/implementation-plan.md
    │   └── examples/implementation-plan-example.md
    ├── systematic-debugger/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/debug_log.py
    ├── test-generator/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/test_gen.py
    ├── sql-helper/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/sql_helper.py
    ├── csv-pro/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/csv_pro.py
    ├── data-analysis/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/data_analyze.py
    ├── web-scraper/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/scrape.py
    ├── seo-toolkit/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── references/canonical-patterns.md
    │   ├── scripts/seo_toolkit.py
    │   └── commands/ (13 × seo-*.md)
    └── frontend-perfection/
        ├── SKILL.md
        ├── skill.json
        ├── references/canonical-patterns.md
        ├── scripts/audit.js
        └── scripts/meta_audit.py
```

---

## 🔍 Skill Discovery

Use `index.json` — it contains a `skills` array with fields:
- `name`, `version`, `category`, `description`, `path`, `triggers`, `updated`

Example filtering by trigger (Python):
```python
import json
with open('index.json') as f:
    data = json.load(f)
# Find skills matching trigger "presentation"
matches = [s for s in data['skills'] if 'presentation' in ' '.join(s['triggers'])]
```

---

## 🛠 Adding a New Skill

1. Create folder in `skills/<name>/`
2. Add two required files:
   - `SKILL.md` — full agent instruction (English primary; Russian optional, with YAML frontmatter `name`, `description`)
   - `skill.json` — manifest (see schema below)
3. Optionally add scripts/templates in subfolders (`scripts/`, `templates/`, `icons/`)
4. Update `index.json` (add entry to `skills[]`)
5. Open PR

### `skill.json` Schema (required fields)

```json
{
  "name": "kebab-case-name",
  "version": "1.0.0",
  "description": "Brief description (1-2 sentences)",
  "author": "github-username",
  "license": "MIT",
  "keywords": ["tag1", "tag2"],
  "triggers": ["trigger phrase 1", "trigger на русском"],
  "category": "repository|media|social|code|data",
  "entrypoint": "SKILL.md",
  "files": ["SKILL.md", "scripts/*.py"],
  "requirements": {
    "tools": ["python3", "gh"],
    "permissions": ["repo:read"]
  },
  "updated": "YYYY-MM-DD"
}
```

**Categories**: `repository`, `media`, `social`, `code`, `data`

**Triggers**: phrases that cause the agent to load the skill. Provide English; Russian optional.

### `SKILL.md` Requirements

- Language: **English** (primary, instructions for agent); Russian optional
- Required YAML frontmatter:
  ```yaml
  ---
  name: skill-name
  description: "Description for catalog/search"
  ---
  ```
- Structure: intro → parameters/steps → examples → constraints/know-how
- No emojis as icons (SVG only)
- Concrete commands, paths, invocation examples

### Pre-PR Checklist

```bash
# Validate JSON
python3 -m json.tool index.json >/dev/null
python3 -m json.tool skills/<name>/skill.json >/dev/null

# Check required files exist
ls skills/<name>/SKILL.md skills/<name>/skill.json
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🔒 Security

See [SECURITY.md](SECURITY.md).

---

## 📜 Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1).

---

<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <img src="assets/footer.svg" alt="footer" />
  </a>
</p>