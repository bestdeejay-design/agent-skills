<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
      <img src="assets/header.svg" alt="Agent Skills — header" />
    </picture>
  </a>
</p>

# Agent Skills — AI Agent Skill Collection

> Autonomous skill instructions for AI agents: Sisyphus, opencode, and compatible. Each skill is a folder with `SKILL.md` (instructions) and `skill.json` (manifest for installation/discovery).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 51](https://img.shields.io/badge/Skills-51-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--19-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)
[![code: 15](https://img.shields.io/badge/code-15-2F81F7.svg)](README.md#cat-code) [![data: 7](https://img.shields.io/badge/data-7-E3B341.svg)](README.md#cat-data) [![media: 12](https://img.shields.io/badge/media-12-A371F7.svg)](README.md#cat-media) [![repository: 10](https://img.shields.io/badge/repository-10-3FB950.svg)](README.md#cat-repository) [![agents: 1](https://img.shields.io/badge/agents-1-FFD166.svg)](README.md#cat-agents) [![social: 1](https://img.shields.io/badge/social-1-F85149.svg)](README.md#cat-social)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

<details>
<summary><b>📑 Table of Contents</b></summary>

- [📦 Skill Catalog](#sec-catalog) — 51 skills · 6 categories
- [🎬 Showcase](#sec-showcase) — real-project examples
- [🚀 Installation](#sec-installation)
- [📁 Repository Structure](#sec-structure)
- [🔍 Skill Discovery](#sec-discovery)
- [🛠 Adding a New Skill](#sec-adding)
- [📄 Project Info](#sec-project-info) — license · contributing · security · code of conduct

</details>

---

<a id="sec-catalog"></a>

## 📦 Skill Catalog

> 📚 Ecosystem map: see [**docs/SKILLS_CATALOG.md**](docs/SKILLS_CATALOG.md) — catalog of the AI agent skills ecosystem (official vendors, formats, standards, ~4.85M SKILL.md files tracked, gaps and recommendations).

**51 skills · 6 categories.** Pick a category below; triggers and full metadata live in [`index.json`](index.json).

| Category | Skills | What's inside |
|----------|:------:|---------------|
| 💻 [Development & Code](#cat-code) | 20 | commits, review, debugging, tests, coverage, security, planning, frontend, skill authoring |
| 🤖 [Agents](#cat-agents) | 1 | autonomous agent runs (DeepSeek Harness) |
| 📊 [Data & Diagrams](#cat-data) | 7 | profiling, SQL, diagrams, scraping |
| 🎬 [Content & Media](#cat-media) | 13 | slides, video, PDF reports, SEO, test graphics |
| 🏗️ [Repository & Docs](#cat-repository) | 10 | README, community files, metadata, documentation, API docs |
| 💬 [Social](#cat-social) | 1 | Reddit |

<a id="cat-code"></a>

### 💻 Development & Code · `code` · 20

| Skill | Purpose |
|-------|---------|
| [**commit-message-writer**](skills/commit-message-writer/SKILL.md) | Conventional Commits message from `git diff --staged`: type/scope inferred, summary + optional body. |
| [**commit-lint**](skills/commit-lint/SKILL.md) | Validates commit messages against Conventional Commits v1.0.0 (type, scope, lengths, capitalization); text/JSON report, exit 0/1/2. |
| [**version-bumper**](skills/version-bumper/SKILL.md) | Deterministic next semver + release tag from git history (feat/fix/breaking); `-s` mode, read-only. |
| [**code-review**](skills/code-review/SKILL.md) | Structured review of a diff/repo: checklists by category (correctness, security, performance, style, tests, edge cases), `[severity] file:line` findings. Analysis only — no edits. |
| [**systematic-debugger**](skills/systematic-debugger/SKILL.md) | Hypothesis-driven debugging (Iron Law): reproduce → hypotheses → root cause → minimal fix + regression test; Red Flags, phase report. |
| [**test-generator**](skills/test-generator/SKILL.md) | pytest skeletons from a Python module AST with ghostwriter arg heuristics; parametrize scaffolding, TS/Go references. |
| [**coverage-analyzer**](skills/coverage-analyzer/SKILL.md) | Coverage analysis from coverage.py XML: total line/branch %, zero-coverage files, worst-10, delta vs baseline, PASS/FAIL gate. |
| [**secret-scanner**](skills/secret-scanner/SKILL.md) | Static secret scan (AWS, GitHub, OpenAI, Anthropic, Stripe, Google, Slack, keys, JWTs): gitleaks patterns + Shannon entropy + allowlists; offline, redaction, CI exit-code. |
| [**security-review**](skills/security-review/SKILL.md) | Security review orchestrator: lockfile inventory + exit-code classifier for 13 scanners (semgrep, bandit, gitleaks, osv-scanner, trivy, grype…) into one finding schema; OWASP-aligned. |
| [**plan-skill**](skills/plan-skill/SKILL.md) | Implementation planning (superpowers v2): brainstorm → plan → execute → verify; HARD-GATE, bite-sized steps, no placeholders; validator script. |
| [**skill-suggester**](skills/skill-suggester/SKILL.md) | Recommends the right skill from this library for a task: scores `index.json` triggers/descriptions, top-5 + combos of up to 3. |
| [**skill-forge**](skills/skill-forge/SKILL.md) | Meta-skill and design compass for creating new skills and upgrading existing ones: maximally technological, creative, aesthetically disciplined; anti-templated gate. |
| [**api-contract-testing**](skills/api-contract-testing/SKILL.md) | Validates an API contract against OpenAPI 3.x (offline manifest check + live HTTP probes); JSON report, exit 0/1/2. |
| [**frontend-perfection**](skills/frontend-perfection/SKILL.md) | Frontend audit & polish to verifiable perfection: real-Chrome Lighthouse ≥13 (mobile+desktop), offline meta/SEO/WCAG/token audit, Security/Privacy/i18n audit, OG-image generation. |
| [**frontend-a11y**](skills/frontend-a11y/SKILL.md) | Deep accessibility audit (95 Front-End-Checklist a11y rules): offline Python static checks (structure, ARIA, headings, landmarks, tables, forms, media, lists, CSS) plus a Playwright + axe-core runtime runner (contrast, focus order, live regions, modal traps, reflow) and manual screen-reader checks. |
| [**frontend-performance**](skills/frontend-performance/SKILL.md) | Performance depth beyond Lighthouse: offline header/asset analysis (HTTP/2-3, compression, caching, HSTS, TTFB, page weight, bundle size, duplicates, resource hints, SW, speculation, streaming, virtualization) + Lighthouse Core Web Vitals runner (LCP/FCP/INP/CLS). Maps 43 Front-End-Checklist Performance rules. |
| [**frontend-testing**](skills/frontend-testing/SKILL.md) | Frontend testing for production readiness (13 Front-End-Checklist Testing rules): testing pyramid + copy-paste Playwright, jest-axe, Pact contract tests, and a GitHub Actions perf-budget + coverage CI. Scaffolds & advises; does not run user CI. |
| [**mobile-frontend**](skills/mobile-frontend/SKILL.md) | Quality mobile-first frontend: codified rules (spacing, type scale, anchors, safe-area, tap-targets), build, and multi-level verification with per-element menu/nav debugging; routes deep a11y/perf/testing to dedicated skills. |
| [**skill-feedback**](skills/skill-feedback/SKILL.md) | Capture and aggregate usage feedback for Agent Skills (wrong trigger, near-miss, broken output, manual correction) into `feedback/<skill>/YYYY-MM-DD.jsonl`; summarizes for the skill-forge optimization loop. |

<a id="cat-agents"></a>

### 🤖 Agents · `agents` · 1

| Skill | Purpose |
|-------|---------|
| [**dsh-runner**](skills/dsh-runner/SKILL.md) | Runs autonomous agent tasks via DeepSeek Harness (dsh): isolated one-off workspaces, JSONL session logs, headless `dsh_task.py` or Web UI, model comparison; requires DEEPSEEK_API_KEY / OpenAI-compatible endpoint. |

<a id="cat-data"></a>
| [**long-running-agent-workflow**](skills/long-running-agent-workflow/SKILL.md) | Protocol for AI agents working across many context windows: a `.lra/` directory with an atomic feature list (id/priority/acceptance criteria/status) and session progress checkpoints. |

### 📊 Data & Diagrams · `data` · 7

| Skill | Purpose |
|-------|---------|
| [**csv-pro**](skills/csv-pro/SKILL.md) | CSV profiling: column types, statistics, anomalies (empty/duplicates/outliers), delimiter auto-detect; markdown/JSON. |
| [**data-analysis**](skills/data-analysis/SKILL.md) | Dataset profiling (CSV/JSON): field stats, modes, histograms, top Pearson correlations, anomalies + recommendations. |
| [**sql-helper**](skills/sql-helper/SKILL.md) | SQL from a text question + DDL: in-memory sqlite schema, intent templates, every candidate verified via EXPLAIN. |
| [**diagram-maker**](skills/diagram-maker/SKILL.md) | Diagrams from a text description in Mermaid syntax: flowchart, sequence, architecture, ER + rendering advice. |
| [**mermaid-to-image**](skills/mermaid-to-image/SKILL.md) | Renders `.mmd` to PNG/SVG: local mermaid-cli preferred, mermaid.ink fallback; format/scale/background options. |
| [**raster-to-svg**](skills/raster-to-svg/SKILL.md) | PNG → vector SVG: vtracer-cli when installed, built-in stdlib tracer otherwise (contour with Bezier curves / mosaic of primitives); deterministic, XML-validated; web UI with color palette editor (recolor/merge), export DXF R12 (layers by color)/EPS/PNG, batch → .zip, optional MCP server. |
| [**web-scraper**](skills/web-scraper/SKILL.md) | Polite HTML scraping to Markdown/JSON: CSS selectors, text/links/tables; legal guardrails — robots.txt, honest UA, rate limit. |

<a id="cat-media"></a>

### 🎬 Content & Media · `media` · 13

| Skill | Purpose |
|-------|---------|
| [**video-script-writer**](skills/video-script-writer/SKILL.md) | Structured video script: Hook → Body (5 timed scenes) → CTA; timecodes, ru/en, full script or outline. |
| [**pdf-report-builder**](skills/pdf-report-builder/SKILL.md) | Markdown → PDF report: HTML via pandoc/built-in converter, PDF via Chrome headless / weasyprint / pandoc; tables, code, quotes. |
| [**test-graphics**](skills/test-graphics/SKILL.md) | Test images, placeholders, icons, avatars for mocks/staging/e2e: Python + free APIs (loremflickr, placehold.co, picsum, Lucide). |
| [**frontend-design-taste**](skills/frontend-design-taste/SKILL.md) | Distinctive visual direction that doesn't read as templated AI: subject grounding, token system, uniqueness gate, user-side copy. |
| [**seo-audit**](skills/seo-audit/SKILL.md) | Technical SEO audit: meta/headings/alt/links/sitemap/robots, Core Web Vitals, scored report (7 dimensions), autonomous P1–P5 fixes. |
| [**seo-schema**](skills/seo-schema/SKILL.md) | Structured data & meta: JSON-LD schema.org (Product/Article/Organization/Breadcrumb/FAQ) + title/description/OG/Twitter. |
| [**seo-content**](skills/seo-content/SKILL.md) | On-page content: thin/duplicates, readability, E-E-A-T, keywords (density, cannibalization, LSI, long-tail), heading hierarchy, image SEO. |
| [**seo-crawl**](skills/seo-crawl/SKILL.md) | Crawlability: robots.txt, noindex, canonical, redirects, sitemap, internal linking, click depth, orphan pages, competitor comparison. |
| [**seo-toolkit**](skills/seo-toolkit/SKILL.md) | ⚠️ **Deprecated router** → use [seo-audit](skills/seo-audit/SKILL.md) / [seo-schema](skills/seo-schema/SKILL.md) / [seo-content](skills/seo-content/SKILL.md) / [seo-crawl](skills/seo-crawl/SKILL.md). |
| [**presentation-maker**](skills/presentation-maker/SKILL.md) | End-to-end decks from a topic: outline -> JSON spec -> 16:9 HTML slides (with mandatory Playwright check) and real `.pptx`; strategy presets, PDF export, deck-quality audit. One command per stage. |
| [**presentation-craft**](skills/presentation-craft/SKILL.md) | Router for high-quality decks: orchestrates docs-product → frontend-design-taste → presentation-maker → frontend-perfection per stage (narrative, visual direction, build, audit). |
| [**presentation-engineering**](skills/presentation-engineering/SKILL.md) | Story engineering: turning ideas into world-changing presentations — narrative engineering, visual language, and performance design (not a slide generator). |

<a id="cat-repository"></a>

### 🏗️ Repository & Docs · `repository` · 10

| Skill | Purpose |
|-------|---------|
| [**repo-readme-assets**](skills/repo-readme-assets/SKILL.md) | README.md (EN) + localized mirror + local animated SVG header/footer (4 presets), zero external services. |
| [**repo-community-files**](skills/repo-community-files/SKILL.md) | Community/legal files: LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates, FUNDING; drives Community Health. |
| [**repo-metadata-health**](skills/repo-metadata-health/SKILL.md) | Repo metadata & health: description, topics (≤20), Pages link, Community Health % via gh API + 16-point checklist. |
| [**repo-social-preview**](skills/repo-social-preview/SKILL.md) | GitHub social preview (og:image) PNG 1280×640: header + waves, <1 MB, solid background recommended. |
| [**api-doc-generator**](skills/api-doc-generator/SKILL.md) | REST API docs in Markdown from OpenAPI 3.x: per-endpoint sections (method, params, request/response); FastAPI/Express references. |
| [**changelog-generator**](skills/changelog-generator/SKILL.md) | Keep a Changelog section from git history (Conventional Commits): tag..HEAD, type mapping, dates, commit links. |
| [**docs-system**](skills/docs-system/SKILL.md) | Meta-guide + router for documentation: product branch (why/what) vs project branch (how), phases, L1–L3 levels, completeness checklist. |
| [**docs-product**](skills/docs-product/SKILL.md) | Product docs branch — «why» and «what»: VISION → PRD → ROADMAP → FEATURES, from an idea forward; templates + checklist. |
| [**docs-project**](skills/docs-project/SKILL.md) | Engineering docs branch — «how»: README, ENTRY, ARCHITECTURE, ADR, contracts (OpenAPI/AsyncAPI), tests, REFERENCE map; templates + checklist. |
| [**github-repo-hygiene**](skills/github-repo-hygiene/SKILL.md) | ⚠️ **Deprecated router** → use [repo-readme-assets](skills/repo-readme-assets/SKILL.md) / [repo-community-files](skills/repo-community-files/SKILL.md) / [repo-metadata-health](skills/repo-metadata-health/SKILL.md) / [repo-social-preview](skills/repo-social-preview/SKILL.md). |

<a id="cat-social"></a>

### 💬 Social · `social` · 1

| Skill | Purpose |
|-------|---------|
| [**reddit-karma**](skills/reddit-karma/SKILL.md) | Systematic Reddit karma building: topic search, tone-aware replies, thank-you templates, routine runs; configurable for your account. |

<a id="sec-showcase"></a>

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

<a id="sec-installation"></a>

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

<a id="sec-structure"></a>

## 📁 Repository Structure

```
agent-skills/
├── index.json                 # Master catalog: name, version, category, description, triggers
├── README.md · README.ru.md   # This document (EN / RU mirror)
├── CHANGELOG.md · LICENSE · CONTRIBUTING.md · SECURITY.md · SUPPORT.md · CODE_OF_CONDUCT.md · FUNDING.yml
├── og-image.png               # Social preview 1280×640
├── assets/                    # README header/footer SVG
├── docs/
│   ├── SKILLS_CATALOG.md      # AI agent skills ecosystem catalog
│   ├── showcase/              # Real-project demonstrations (+ template)
│   └── plans/                 # Planning documents
├── .github/
│   ├── ISSUE_TEMPLATE/ · pull_request_template.md · release.yml
│   └── workflows/validate-skills.yml   # CI: manifest validation
└── skills/                    # 51 skills, one folder each
    └── <skill-name>/
        ├── SKILL.md           # Agent instruction (required)
        ├── skill.json         # Manifest: name, version, triggers, files (required)
        ├── scripts/           # Executable helpers (Python/JS)
        ├── templates/         # Reusable templates
        └── references/        # Deep-dive materials
```

**Skill folder anatomy** (example — `code-review`):

```
skills/code-review/
├── SKILL.md              # Agent instruction: intro → steps → examples → constraints
├── skill.json            # Manifest: name, version, category, triggers, files
├── scripts/              # review.py, checklists.py
├── templates/            # review-template.md
└── examples/             # example-pr.md
```

> Only `SKILL.md` and `skill.json` are required — everything else is optional and depends on the skill.

---

<a id="sec-discovery"></a>

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

<a id="sec-adding"></a>

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

<a id="sec-project-info"></a>

## 📄 Project Info

| | |
|---|---|
| **License** | [MIT](LICENSE) |
| **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Security** | [SECURITY.md](SECURITY.md) |
| **Code of Conduct** | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Contributor Covenant 2.1 |

---

<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <img src="assets/footer.svg" alt="footer" />
  </a>
</p>
