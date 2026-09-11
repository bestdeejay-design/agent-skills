# 📣 Промо-кит agent-skills

> Готовые тексты для публикации. Дата: 2026-09-11 · 59 скиллов · 6 категорий · MIT.
> Правило: везде одна и та же фактура — 59 skills, CI-validated, offline-first, SKILL.md + skill.json.
> После каждого релиза обновляйте цифру «59» в текстах (см. `index.json`).

---

## 1. Позиционирование (база для всех каналов)

**One-liner (EN):** 59 production-ready skills that make AI agents actually ship — frontend audits (Lighthouse, a11y, perf), security review, presentations, SEO, docs integrity, data & diagrams.

**One-liner (RU):** 59 боевых скиллов для AI-агентов: аудит фронтенда (Lighthouse/a11y/перформанс), security-ревью, презентации, SEO, целостность документации, данные и диаграммы.

**Чем отличается от anthropics/skills (важно для комментариев):**
- глубина production-аудитов: не «сделай слайды», а «Lighthouse ≥13 пунктов + WCAG + Core Web Vitals с отчётом и exit-code для CI»;
- офлайн-first: скрипты на stdlib Python, работают без сети и без API-ключей;
- двойной манифест: `SKILL.md` (инструкция) + `skill.json` (установка/дискавери) + `index.json` с триггерами и `skill-suggester` для автоподбора;
- CI-пайплайн валидации всех скиллов (JSON, манифесты, кросс-чек index ↔ папки);
- мульти-агентность: Sisyphus, opencode, Claude Code и совместимые.

**Ключевые скиллы для демонстрации (по одному предложению):**
| Скилл | Хук |
|---|---|
| `frontend-perfection` | Доводит фронтенд до проверяемого идеала: реальный Chrome + Lighthouse ≥13 проверок, WCAG, OG-картинки |
| `security-review` | Оркестрирует 13 сканеров (semgrep, bandit, gitleaks, osv-scanner, trivy…) в один отчёт, OWASP-aligned |
| `presentation-maker` | От темы до настоящего .pptx: HTML-слайды 16:9 + обязательная Playwright-верификация |
| `secret-scanner` | Ищет утечки секретов офлайн: паттерны gitleaks + энтропия Шеннона, allowlists, exit-code для CI |
| `seo-audit/content/crawl/schema` | Полный SEO-конвейер: техаудит, контент, краулинг, JSON-LD — без платных инструментов |
| `chronos` (5 агентов) | Пантеон из 5 AI-агентов держит документацию целой: дубли, битые ссылки, сироты, устаревания |
| `raster-to-svg` | PNG→вектор офлайн: vtracer или собственный трассировщик, web-UI с перекраской палитры, DXF/EPS |
| `prd-to-app` | Из PRD и макетов — full-stack приложение за 8 фаз, с визуальной верификацией Playwright |

---

## 2. Готовые посты

### 2.1 X / Twitter (EN, тред)

**Твит 1:**
> I got tired of AI agents that talk instead of shipping. So I built 59 production-ready skills for them 🔧
>
> Frontend audits with real Lighthouse. Security review across 13 scanners. Presentations as real .pptx. SEO suite. Docs integrity.
>
> All offline-first, CI-validated, MIT. 🧵

**Твит 2:**
> What's inside 👇
> • frontend-perfection — Lighthouse ≥13 checks + WCAG + OG images
> • security-review — semgrep, bandit, gitleaks, osv-scanner, trivy… in one report
> • presentation-maker — topic → HTML slides → real .pptx, Playwright-verified
> • 4-skill SEO pipeline: audit → content → crawl → schema

**Твит 3:**
> Every skill = SKILL.md (instructions) + skill.json (manifest) + scripts on Python stdlib. No API keys, works offline. A CI pipeline validates all 59 on every push.
>
> Browse the catalog: https://github.com/bestdeejay-design/agent-skills
> ⭐ if useful!

### 2.2 Reddit — r/ClaudeAI (EN, пост)

**Заголовок:** I open-sourced 59 production-ready agent skills (frontend audits, security review, presentations, SEO) — offline-first, CI-validated

**Тело:**
> Like many of you I kept writing the same mega-prompts for every project. I turned them into a structured skill library: each skill is a folder with SKILL.md (instructions) + skill.json (manifest), and a CI pipeline validates all of them on every push.
>
> Highlights:
> - **frontend-perfection** — audit & polish to verifiable perfection: real-Chrome Lighthouse (mobile+desktop), WCAG a11y, security/privacy/i18n, OG-image generation
> - **security-review** — orchestrates 13 scanners (semgrep, bandit, gitleaks, osv-scanner, trivy, grype…) into one OWASP-aligned finding schema
> - **presentation-maker** — topic → outline → 16:9 HTML slides with mandatory Playwright verification → real .pptx
> - **SEO suite** — technical audit, content/on-page, crawlability, JSON-LD schema (4 skills + deprecated meta-router)
> - **chronos** — 5 doc-integrity agents: duplicates, broken links, orphans, stale dates
>
> Everything runs offline on Python stdlib wherever possible — no API keys. MIT. Works with Claude Code / opencode / Sisyphus-compatible agents.
>
> Repo: https://github.com/bestdeejay-design/agent-skills
>
> Happy to answer questions — and PRs welcome (CONTRIBUTING.md has a skill template + quality gate).

*(Правила сабреддитов проверь перед постом: где-то нужен «Show» префикс или запрет саморекламы в определенные дни. Резервные сабы: r/ChatGPTCoding, r/AI_Agents, r/opencode — переименуй первую строку под аудиторию.)*

### 2.3 LinkedIn (EN)

> AI agents are great at demos and unreliable at production. The gap is almost always the same: no checklist, no verification, no CI.
>
> I've been open-sourcing my answer to that: agent-skills — a library of 59 skills that turn an AI agent into a disciplined engineer.
>
> A few examples of the bar I aimed for:
> ▪️ Frontend audit skill that runs real Chrome + Lighthouse across 13 checks and refuses to pass until thresholds are met
> ▪️ Security review that orchestrates 13 scanners into a single OWASP-aligned report
> ▪️ Presentation skill that ships an actual .pptx — verified screenshot-by-screenshot by Playwright
> ▪️ A documentation-integrity pantheon: 5 agents hunting duplicates, broken links and stale docs
>
> All 59 skills are offline-first (Python stdlib), CI-validated on every push, and MIT-licensed.
>
> → https://github.com/bestdeejay-design/agent-skills
> Feedback and PRs welcome. #ai #opensource #softwareengineering #aiagents

### 2.4 Telegram (RU, для своего канала/чата)

> 🔧 Выложил в опенсорс: **agent-skills** — 59 скиллов, превращающих AI-агента в дисциплинированного инженера.
>
> Что внутри:
> • `frontend-perfection` — аудит фронтенда реальным Chrome + Lighthouse ≥13 проверок, WCAG, OG-картинки
> • `security-review` — 13 сканеров (semgrep, bandit, gitleaks, trivy…) в одном отчёте
> • `presentation-maker` — от темы до настоящего .pptx с Playwright-верификацией слайдов
> • SEO-конвейер из 4 скиллов: техаудит → контент → краулинг → JSON-LD
> • `chronos` — 5 агентов для целостности документации
>
> Всё офлайн-first (Python stdlib, без API-ключей), каждый пуш гоняет CI-валидацию. MIT.
>
> 👉 https://github.com/bestdeejay-design/agent-skills
> Звезда репо — лучшая поддержка 🙌

*(Для чатов — сократить до первых 3 пунктов + ссылка.)*

### 2.5 Show HN (EN)

**Заголовок:** Show HN: Agent-skills – 59 production-ready skills for AI agents (offline-first, CI-validated)

**Тело:**
> Hi HN! I've been building a library of "skills" for AI coding agents: self-contained folders of instructions + manifests + Python scripts that turn general-purpose agents into disciplined specialists.
>
> The thesis: agents fail in production not because the model is weak but because there's no verification loop. So every skill encodes a checklist *and* a way to prove the work: Lighthouse thresholds that must pass, a Playwright screenshot pass for every slide, exit codes for CI.
>
> Examples:
> - frontend-perfection: audit/polish a frontend to verifiable perfection (real Chrome Lighthouse, WCAG, security/privacy/i18n, OG images)
> - security-review: orchestrate 13 scanners (semgrep, bandit, gitleaks, osv-scanner, trivy…) into one OWASP-aligned schema
> - presentation-maker: topic → outline → 16:9 HTML slides → real .pptx, each slide Playwright-verified
> - secret-scanner: offline secret detection (gitleaks patterns + Shannon entropy), CI exit codes
>
> Design constraints: everything runs offline on Python stdlib where possible (no API keys), each skill is SKILL.md + skill.json, a CI pipeline validates the whole collection on every push, and a meta-skill (skill-suggester) routes a task to the right skill from index.json.
>
> Format is compatible with Claude Code / opencode / Sisyphus-style harnesses.
>
> Repo: https://github.com/bestdeejay-design/agent-skills
>
> Happy to answer questions about the skill format, the quality gate, or the verification loops.

### 2.6 dev.to / Хабр (план статьи)

1. Проблема: агент без чек-листа и верификации — это генератор правок, а не инженер.
2. Формат скилла: SKILL.md + skill.json + scripts; index.json как дискавери.
3. Анатомия одного скилла изнутри (разобрать `frontend-perfection` или `security-review`).
4. Верификация как контракт: exit-code, Playwright-проходы, пороги Lighthouse.
5. CI для самой библиотеки (validate_skills.py, security-scan).
6. Как добавить свой скилл (CONTRIBUTING + quality gate).
7. Дорожная карта (мульти-харнессность, MCP).
CTA: звезда + issue с идеей скилла.

---

## 3. Заявки в каталоги/агрегаторы (готовые строки)

### 3.1 `VoltAgent/awesome-agent-skills` (PR в README, раздел «repositories»/каталогов)

```markdown
| [bestdeejay-design/agent-skills](https://github.com/bestdeejay-design/agent-skills) | 59 production-ready skills for AI agents: frontend audits (Lighthouse/a11y/perf), security review (13 scanners), presentations (HTML→PPTX), 4-skill SEO pipeline, docs-integrity agents, data & diagrams. Offline-first, CI-validated. |
```

### 3.2 `travisvn/awesome-claude-skills` и `ComposioHQ/awesome-claude-skills`

```markdown
- [agent-skills](https://github.com/bestdeejay-design/agent-skills) — 59 CI-validated skills: frontend/perf/a11y audits, security review & secret scanning, presentations (.pptx), SEO suite, docs integrity, data tools. Offline-first, MIT.
```

### 3.3 `skills.sh`
Файл `skills.sh.json` уже в репо (6 группировок, 59 скиллов) — реестр индексирует репозитории автоматически; после индексации проверить страницу репо на skills.sh и установить через `npx skills add bestdeejay-design/agent-skills`.

### 3.4 GitHub About (готовый текст — вставить вручную)

> Description:
> ```
> 59 production-ready skills for AI agents (Claude Code, Sisyphus, opencode): frontend audits (Lighthouse/a11y/perf), security review & secret scanning, presentations (HTML→PPTX), SEO suite, docs integrity, data & diagrams, repo hygiene. SKILL.md + skill.json, CI-validated.
> ```
> Topics (заменить `github-repo-hygiene` → `claude-code`, добавить `seo-tools`):
> `ai-agents, automation, opencode, presentation-generator, productivity, python, sisyphus, claude-code, documentation, markdown, agent-framework, agent-skills, ai-tools, claude-skills, llm-agents, llm-tools, mcp, model-context-protocol, prompt-engineering, skill-catalog, seo-tools`

*(Токен интеграции без admin-прав, поэтому About меняется вручную: Repo → ⚙️ About → Description/Topics.)*

---

## 4. Чек-лист публикации (порядок и каналы)

**День 0 (сейчас):**
- [ ] GitHub About: вставить description + topics (см. 3.4)
- [ ] X/Twitter — тред (2.1)
- [ ] Telegram — свой канал + 2–3 чата (2.4)

**День 1–2:**
- [ ] Reddit r/ClaudeAI (2.2), через 2–3 дня — r/ChatGPTCoding или r/AI_Agents
- [ ] LinkedIn (2.3)
- [ ] PR в VoltAgent/awesome-agent-skills (3.1)
- [ ] PR в travisvn/awesome-claude-skills (3.2)

**День 3–7:**
- [ ] Show HN во вторник–четверг утром по CET (2.5)
- [ ] Статья на dev.to (2.6), кросс-пост в Hashnode
- [ ] Хабр (RU-версия статьи 2.6)
- [ ] Проверить индексацию skills.sh

**Постоянно:**
- [ ] Отвечать на issues в течение 24ч в неделю промо
- [ ] Каждые 2 недели — пост-апдейт (новый скилл = новый пост)
- [ ] После PR в awesome-списки — проверить, что приняли; если нет, вежливо уточнить

**Метрика успеха на месяц:** 50+ звёзд, листинг в 2+ агрегаторах, 1+ внешний PR/issue от чужих людей.
