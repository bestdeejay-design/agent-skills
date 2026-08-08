# Agent Skills — AI Agent Skill Collection

> Autonomous skill instructions for AI agents: Sisyphus, opencode, and compatible. Each skill is a folder with `SKILL.md` (instructions) and `skill.json` (manifest for installation/discovery).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 9](https://img.shields.io/badge/Skills-9-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--08-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Skill Catalog

| Skill | Category | Description | Triggers |
|-------|----------|-------------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene) | `repository` | Validates and updates GitHub repo descriptive section: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates, social preview, releases, description, topics, GitHub Pages, community health. | `github hygiene`, `setup repository`, `update readme`, `github page`, `repo description`, `search tags`, `topics`, `contributing`, `license`, `security policy` |
| [**test-graphics**](skills/test-graphics) | `media` | Generates test images, photos, icons, placeholders via Python + free APIs (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `test pictures`, `icons for test`, `stubs`, `mock data images`, `generate photo` |
| [**reddit-karma**](skills/reddit-karma) | `social` | Systematic Reddit karma building for your account: topic search, response drafting, tone detection, thank-you templates, routine runs. Configure your username, subreddits and target resource. | `reddit`, `karma`, `r/LocalLLaMA`, `build karma`, `reply to comments`, `reddit run`, `leave trace` |
| [**presentation-maker**](skills/presentation-maker) | `media` | Presentation generator: Markdown outline, HTML 16:9 slides, .pptx via python-pptx. Auto-layouts, themes, design-system (tokens, mood), product-design module (narrative, data-viz, a11y, premium). | `make presentation`, `presentation`, `slides`, `pptx`, `make deck`, `generate slides` |
| [**docs-system**](skills/docs-system) | `repository` | Guide for an AI agent: how to compose product and project documentation and its composition. Product branch (VISION/PRD/ROADMAP/FEATURES) + project branch (ARCHITECTURE/ADR/contracts/TEST_CASES/REFERENCE map), fill order (phases), templates, completeness checklist, levels L1/L2/L3 for large systems. | `documentation`, `docs catalog`, `documentation structure`, `docs for new project`, `documentation plan`, `документация`, `каталог документов` |
| [**commit-message-writer**](skills/commit-message-writer) | `code` | Generates Conventional Commits messages from `git diff --staged`: type inferred from changed files, scope from paths, short summary, optional body. `suggest.py` (Python 3) only analyzes staged changes, never commits. | `commit message`, `write commit`, `git commit`, `conventional commit`, `[сообщение коммита]`, `[написать коммит]`, `[закоммитить]` |
| [**code-review**](skills/code-review) | `code` | Structured code review: reads a git diff or path to repo/file, applies checklists by category (correctness, security, performance, style, tests, edge cases) and emits `[severity] file:line` findings with suggested fixes. Analysis only — makes no edits. | `code review`, `[ревью кода]`, `review PR`, `[проверь код]`, `pull request review`, `code quality`, `[найти баги]`, `review commit` |
| [**diagram-maker**](skills/diagram-maker) | `data` | Generates diagrams from a text description: flowchart, sequence, architecture, ER — in Mermaid syntax. Input: natural language; output: Mermaid code + rendering recommendation (mermaid.live / mermaid-cli / MCP). | `diagram`, `mermaid`, `flowchart`, `[диаграмма]`, `sequence diagram`, `[архитектура]`, `[ER-схема]`, `draw a diagram` |
| [**skill-suggester**](skills/skill-suggester) | `code` | Recommends a skill from the library for a user task: reads `index.json`, scores triggers and descriptions, returns top-5 with relevance plus combos of up to 3 skills. | `which skill`, `[какой скилл использовать]`, `suggest skill`, `[подбор скилла]`, `[рекомендовать скилл]`, `[какой навык]` |

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
    │   └── skill.json
    ├── reddit-karma/
    │   ├── SKILL.md
    │   └── skill.json
    ├── presentation-maker/
    │   ├── SKILL.md
    │   ├── skill.json
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
    └── skill-suggester/
        ├── SKILL.md
        ├── skill.json
        └── scripts/skill_suggest.py
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