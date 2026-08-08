# Agent Skills — AI Agent Skill Collection

> Autonomous skill instructions for AI agents: Sisyphus, opencode, and compatible. Each skill is a folder with `SKILL.md` (instructions) and `skill.json` (manifest for installation/discovery).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 21](https://img.shields.io/badge/Skills-21-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--08-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Skill Catalog

> 📚 Ecosystem map: see [**docs/SKILLS_CATALOG.md**](docs/SKILLS_CATALOG.md) — catalog of the AI agent skills ecosystem (official vendors, formats, standards, ~4.85M SKILL.md files tracked, gaps and recommendations).

| Skill | Category | Description | Triggers |
|-------|----------|-------------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene/SKILL.md) | `repository` | Validates and updates GitHub repo descriptive section: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates, social preview, releases, description, topics, GitHub Pages, community health. | `github hygiene`, `setup repository`, `update readme`, `github page`, `repo description`, `search tags`, `topics`, `contributing`, `license`, `security policy` |
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

## 🎬 Showcase — real-project examples

> Live demonstrations of skills on **real** projects (not abstract examples).
> Reference project: **lovii.ru** (`lovii_demo`). Every new skill must ship a
> showcase. Template: [`docs/showcase-template.md`](docs/showcase-template.md).

| Skill | Project | What's demonstrated |
|---|---|---|
| [`web-scraper`](docs/showcase/showcase-web-scraper-lovii.md) | lovii.ru landing (White Paper) | Scraping the public page → Markdown summary (sections, metrics, contacts, table) |
| [`diagram-maker`](docs/showcase/showcase-diagram-maker-lovii.md) | lovii_demo `docs/ARCHITECTURE.md` | Textual SPA architecture → Mermaid flowchart of role-based screen structure |

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
    └── web-scraper/
        ├── SKILL.md
        ├── skill.json
        └── scripts/scrape.py
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