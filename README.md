# Agent Skills — AI Agent Skill Collection

> Autonomous skill instructions for AI agents: Sisyphus, opencode, and compatible. Each skill is a folder with `SKILL.md` (instructions) and `skill.json` (manifest for installation/discovery).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 5](https://img.shields.io/badge/Skills-5-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Updated](https://img.shields.io/badge/Updated-2026--08--07-green.svg)](index.json)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Skill Catalog

| Skill | Category | Description | Triggers |
|-------|----------|-------------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene) | `repository` | Validates and updates GitHub repo descriptive section: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, description, topics, GitHub Pages. | `github hygiene`, `setup repository`, `update readme`, `github page`, `repo description`, `search tags`, `topics`, `contributing`, `license`, `security policy` |
| [**test-graphics**](skills/test-graphics) | `media` | Generates test images, photos, icons, placeholders via Python + free APIs (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `test pictures`, `icons for test`, `stubs`, `mock data images`, `generate photo` |
| [**reddit-karma**](skills/reddit-karma) | `social` | Systematic Reddit karma building for account InterviewDesigner777: topic search, response drafting, tone detection, thank-you templates, routine runs. | `reddit`, `karma`, `r/LocalLLaMA`, `build karma`, `reply to comments`, `reddit run`, `leave trace` |
| [**presentation-maker**](skills/presentation-maker) | `media` | Presentation generator: Markdown outline, HTML 16:9 slides, .pptx via python-pptx. Auto-layouts, themes, design-system (tokens, mood), product-design module (narrative, data-viz, a11y, premium). | `make presentation`, `presentation`, `slides`, `pptx`, `make deck`, `generate slides` |
| [**docs-system**](skills/docs-system) | `repository` | Guide for an AI agent: how to compose product and project documentation and its composition. Product branch (VISION/PRD/ROADMAP/FEATURES) + project branch (ARCHITECTURE/ADR/contracts/TEST_CASES/REFERENCE map), fill order (phases), templates, completeness checklist, levels L1/L2/L3 for large systems. | `documentation`, `docs catalog`, `documentation structure`, `docs for new project`, `documentation plan`, `документация`, `каталог документов` |

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
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # How to add/update skills
├── SECURITY.md                # Security policy
├── CODE_OF_CONDUCT.md         # Contributor Covenant 2.1
├── .github/
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
        └── examples/pmos/README.md
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