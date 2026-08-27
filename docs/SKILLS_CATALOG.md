# Каталог скиллов: обзор экосистемы AI Agent Skills

> **Версия:** 1.0 · **Дата:** август 2026
> **Источник:** два независимых ресерча экосистемы (GitHub API / gh CLI, официальные спецификации, каталоги и агрегаторы)
> **Цель:** справочник по направлениям экосистемы и ориентир для развития библиотеки `agent-skills` (9 скиллов).

---

## 1. Зачем этот документ

Экосистема AI agent skills растёт взрывными темпами: на GitHub уже ~4.85M файлов `SKILL.md`. Каталог — это карта того, что существует в индустрии: кто выпускает официальные скиллы, какие направления покрыты, какие форматы устоялись, где пробелы. Он используется для:

- планирования развития библиотеки `agent-skills` (что добавить следующим);
- позиционирования наших 9 скиллов относительно индустрии;
- быстрого ввода нового участника в контекст экосистемы.

---

## 2. Классификация по направлениям

### 2.1 Официальные библиотеки вендоров

Скиллы, выпущенные самими создателями агентных инструментов — эталон качества, формата и документации.

| Вендор / репозиторий | Звёзды | Что внутри |
|---|---|---|
| `anthropics/skills` | 167k⭐ (топик) | 17 скиллов: `algorithmic-art`, `brand-guidelines`, `canvas-design`, `claude-api`, `doc-coauthoring`, `docx`, `frontend-design`, `internal-comms`, `mcp-builder`, `pdf`, `pptx`, `skill-creator`, `slack-gif-creator`, `theme-factory`, `web-artifacts-builder`, `webapp-testing`, `xlsx` |
| `vercel-labs/agent-skills` | — | React/Next.js/Vercel: `vercel-react-best-practices`, `vercel-composition-patterns`, `vercel-react-view-transitions`, `vercel-react-native-skills`, `deploy-to-vercel`, `vercel-cli-with-tokens`, `vercel-optimize`, `web-design-guidelines`, `writing-guidelines` |
| `microsoft/azure-skills` | — | Скиллы по Azure + Azure MCP Server (200+ инструментов, 40+ сервисов) |
| `google/skills` | — | Скиллы Google Cloud (recipes/solutions), установка `npx skills add google/skills` |
| `expo/skills` | — | Скиллы React Native, каталог через `skills.sh.json` |
| `github/awesome-copilot` | 37.5k | Официальный каталог Copilot: agents, instructions, skills, hooks, workflows |

**Наша библиотека:** частично покрывает направление «офисные артефакты» (presentation-maker ↔ `pptx` у Anthropic, diagram-maker ↔ визуализация) и «работа с репозиторием» (github-repo-hygiene, code-review, commit-message-writer). Слайды и диаграммы — наша сильная сторона против `anthropics/pptx`.

### 2.2 Каталоги и агрегаторы (awesome-списки)

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `VoltAgent/awesome-agent-skills` | 29.8k | 1497+ скиллов от Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Netlify, Trail of Bits, Sentry, Expo, Hugging Face, Figma |
| `ComposioHQ/awesome-claude-skills` | 72k | Курируемый список скиллов Claude |
| `hesreallyhim/awesome-claude-code` | 51.9k | Каталог всего для Claude Code |
| `travisvn/awesome-claude-skills` | 14.5k | Курируемый список, регулярно обновляется |
| `sickn33/agentic-awesome-skills` | 44.6k | Агентные скиллы |
| `VoltAgent/awesome-openclaw-skills` | 51.8k | Скиллы для OpenClaw |
| `jeremylongshore/claude-code-plugins-plus-skills` | — | 471 плагин, 3179 скиллов, 347 агентов; tonsofskills.com |
| `wshobson/agents` | 38.6k | 94 плагина, 203 агента, 175 скиллов, 109 команд |

**Наша библиотека:** пока не представлена в этих каталогах. Публикация в `VoltAgent/awesome-agent-skills` (issue/PR) — быстрый путь к discoverability.

### 2.3 Методологии и рабочие процессы (workflow-скиллы)

**`obra/superpowers`** — 14 скиллов, ставших эталоном методки: `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills`.

**`addyosmani/agent-skills`** — production-grade инженерные скиллы: жизненный цикл DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP, 8 slash-команд: `/spec`, `/plan`, `/build`, `/test`, `/review`, `/webperf`, `/code-simplify`, `/ship`.

**`OthmanAdi/planning-with-files`** (26k⭐) — планирование через файлы.

**Наши:** code-review и skill-suggester пересекаются с этим направлением частично (code-review ≃ `requesting-code-review` / review-цикл). Проблематика и станет зоной роста: `plan-skill`, `systematic-debugger` (см. ROADMAP).

### 2.4 Безопасность

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `mukul975/Anthropic-Cybersecurity-Skills` | 27.4k | 817 скиллов, 6 фреймворков (включая MITRE ATT&CK) |
| `NVIDIA/SkillSpector` | 14.3k | Сканер уязвимостей скиллов |
| `zhaoxuya520/reverse-skill` | 20.9k | Реверс-инжиниринг |
| `trailofbits/skills` | 6.4k | Security-маркетплейс от Trail of Bits |
| `gadievron/raptor` | 3.5k | Security-скиллы |
| `SnailSploit/Claude-Red` | 2.8k | Red teaming |
| `ljagiello/ctf-skills` | 2.9k | CTF |

**Наши:** `code-review` включает security-чек-лист (S-категория), но полноценного security-скилла нет. Возможен `security-review` (зависимости, секреты) по образцу `trailofbits/skills`.

### 2.5 Наука и исследования

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `Imbad0202/academic-research-skills` | 41.3k | Академический ресёрч |
| `wanshuiyin/Auto-claude-code-research-in-sleep` | 14.4k | Автономный ресёрч |
| `K-Dense-AI/scientific-agent-skills` | 32.9k | 159 скиллов, 100+ научных БД, v2.62.0 |
| `Orchestra-Research/AI-Research-SKILLs` | 11.5k | Исследовательские скиллы |

**Наши:** нет покрытия. Низкий приоритет, если не развиваем научную нишу.

### 2.6 Маркетинг, SEO, контент

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `coreyhaines31/marketingskills` | 43.5k | CRO, copywriting, SEO, analytics, growth |
| `AgriciDaniel/claude-seo` | 13.6k | 25 суб-скиллов + 18 суб-агентов, технический SEO |
| `zubair-trabzada/geo-seo-claude` | 9.2k | GEO-first SEO (оптимизация под AI-поиск) |
| `aaron-he-zhu/aaron-marketing-skills` | 2.5k | 120 скиллов + 8 команд |
| `zubair-trabzada/ai-marketing-claude` | 2.2k | 15 скиллов с параллельными субагентами |

**Наши:** нет. Потенциальная ниша — см. ROADMAP (`seo-basics`).

### 2.7 Персональная продуктивность и PKM

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `kepano/obsidian-skills` | 44.4k | Скиллы для Obsidian (CLI, открытые форматы) |
| `axtonliu/axton-obsidian-visual-skills` | 3.2k | Canvas, Excalidraw, Mermaid |
| `bevibing/tutor-skills` | 1.1k | PDF/доки → Obsidian study vaults |
| `huytieu/COG-second-brain` | 809 | 33 скилла, 10 агентов, people CRM |

**Наши:** частично — `diagram-maker` (Mermaid) покрывает визуальную часть. Полноценного PKM-скилла нет (см. ROADMAP: `pkm-obsidian`).

### 2.8 Карьера и резюме

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `Paramchoudhary/ResumeSkills` | 1.4k | Оптимизация резюме, job applications |
| `andrew-shwetzer/career-ops-plugin` | 460 | 9 скиллов: оценка вакансий, ATS-оптимизация |
| `liyupi/yupi-skill` | 407 | Менторство, собеседования, резюме |
| `yanliudesign/offer-toolkit-skill` | 281 | Декодер JD + билдер резюме (11 шаблонов) |

**Наши:** нет. Ниша с активным спросом, небольшой барьер входа (см. ROADMAP: `career-builder`).

### 2.9 Юридические и финансовые

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `zubair-trabzada/ai-legal-claude` | 1.6k | Контракты, риски, NDA |
| `evolsb/claude-legal-skill` | 400 | CUAD risk detection, бенчмарки |
| `openaccountant/skills` | 49 | 44 финансовых скилла: P&L, бюджет, налоги, долги |
| `get-zeked/finance-super-skill` | 17 | 7 финансовых скиллов Perplexity |
| `j9o/cfo-expert` | 10 | US GAAP, финмоделирование |

**Наши:** нет.

### 2.10 Медиа и творчество

| Репозиторий | Звёзды | Что это |
|---|---|---|
| `zarazhangrui/frontend-slides` | 27.1k | Слайды/презентации |
| `chuspeeism/dashi-ppt-skill` | 4.8k | PPT |
| `htdt/godogen` | 5.5k | Автономная разработка игр (Godot, Bevy, Babylon.js) |
| `Vincentwei1021/video-shotcraft` | 4.1k | Видеомонтаж |
| `SamurAIGPT/Generative-Media-Skills` | 4k | Генеративные медиа |
| `WH-2099/mermaid-skill` | 206 | Mermaid-диаграммы |
| `csthink/dashmotion` | 150 | Анимированные диаграммы |
| `deusyu/translate-book` | 1k | Перевод книг (PDF/DOCX/EPUB) |

**Наши:** сильное покрытие — `presentation-maker` (слайды), `diagram-maker` (Mermaid), `test-graphics` (медиа-заполнение). Здесь мы уже конкурируем с `zarazhangrui/frontend-slides` и `WH-2099/mermaid-skill`.

### 2.11 Вертикальные домены со слабым покрытием (пробелы)

| Домен | Примеры | Оценка покрытия |
|---|---|---|
| Медицина/здравоохранение | `nickjlamb/redacta` (8⭐), `skills-il/health-services` (4⭐) | критически мало |
| Музыка/аудио | `lucaperret/tidal-cli` (9⭐) | критически мало |
| Email | `framix-team/skill-email-html-mjml` (62⭐), `rNLKJA/gmail-labeler` (5⭐) | мало |
| Перевод | `deusyu/translate-book` (1k⭐) | мало |
| E-commerce | `coral870921-source/Ozon-Profit-Skills` (16⭐) | мало |

---

## 3. Эталонные библиотеки: таблица сравнения

| Репозиторий | Кол-во | Форматы | Устройство каталога | Ценное |
|---|---|---|---|---|
| `anthropics/skills` | 17 | SKILL.md + frontmatter (name/description/license) | Плоская `skills/<name>/SKILL.md` | Эталон качества |
| `vercel-labs/agent-skills` | ~10 | SKILL.md + `skills.sh.json` | Groupings (React/Vercel/Design) | Пример каталога для skills.sh |
| `obra/superpowers` | 14 | SKILL.md + multi-harness | `skills/` → конвертация в .claude-plugin/.codex-plugin/.cursor-plugin/.kimi-plugin/.opencode/.pi | Методки, мульти-агентность |
| `wshobson/agents` | 175 | SKILL.md + plugin.json | Один source-of-truth → 5+ харнесов | Мульти-агентная экосистема |
| `VoltAgent/awesome-agent-skills` | 1497+ | Агрегатор ссылок | Категории по доменам | Крупнейший каталог |
| `addyosmani/agent-skills` | 8 команд | SKILL.md | `/spec /plan /build /test /review /webperf /code-simplify /ship` | Production-инженерные скиллы |
| `microsoft/azure-skills` | ~20 | SKILL.md + MCP | Azure skills + MCP Server | Интеграция скиллов с MCP |
| `K-Dense-AI/scientific-agent-skills` | 159 | SKILL.md | Категории по наукам | 100+ научных БД |
| `trailofbits/skills` | ~10 | SKILL.md | Security-маркетплейс | Безопасность |
| `github/awesome-copilot` | ~50 | AGENTS.md + skills | Категории по README | Официальный каталог Copilot |
| `expo/skills` | ~5 | SKILL.md + skills.sh.json | Groupings | React Native |
| `google/skills` | ~10 | SKILL.md | recipes/solutions | Google Cloud |
| `Jeffallan/claude-skills` | 67 | SKILL.md | 9 воркфлоу | Практичные скиллы |
| `alirezarezvani/claude-skills` | 362 | SKILL.md | 13 инструментов | Маркетинг (AEO), security, C-level |

---

## 4. Стандарты форматов

| Формат | Зачем | Ключевые поля / правила |
|---|---|---|
| **SKILL.md** (agentskills.io) | Де-факто стандарт скиллов | frontmatter: `name` (≤64, lowercase+hyphens, = имя папки), `description` (≤1024), `license`, `compatibility` (≤500), `metadata`, `allowed-tools`; тело <500 строк / <5000 токенов; скрипты — в `scripts/`, последние ссылки |
| **skills.sh.json** | Каталог для реестра skills.sh | `$schema`, `schema`, `notGrouped`, `groupings[].title/description/skills`; установка `npx skills add <owner/repo>`; ~525 файлов на GitHub |
| **.claude-plugin/plugin.json** | Плагины Claude Code | `name` — immutable slug; команды/скиллы/агенты/MCP |
| **marketplace.json** | Плагины Codex | Плагинные маркетплейсы |
| **AGENTS.md** | Codex / GitHub | Руководства для агентов (репо/проект) |
| **MCP** | Модель-контекст-протокол | modelcontextprotocol/servers, registry.modelcontextprotocol.io (~63 сервера) |

---

## 5. Тренды 2025–2026

1. **Мульти-харнессность** — один исходный Markdown → конвертация в форматы всех агентов (Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Copilot, Windsurf).
2. **Стандартизация формата** — `SKILL.md` становится де-факто стандартом; прогрессивное раскрытие (metadata ~100 токенов → полные инструкции <5k → ресурсы по требованию).
3. **Каталогизация через skills.sh** — `skills.sh.json`, `npx skills add`.
4. **Интеграция с MCP** — скиллы поставляются вместе с MCP-серверами (Azure, Foundry).
5. **Плагинные маркетплейсы** — `.claude-plugin`, `marketplace.json`, `marketplace.extended.json`.
6. **Вертикальные домены** — маркетинг/SEO, юриспруденция, финансы, наука, медиа — самые быстрорастущие ниши.
7. **Безопасность скиллов** — появление сканеров уязвимостей скиллов (NVIDIA/SkillSpector) — знак зрелости экосистемы.
8. **Взрывной рост** — ~4.85M SKILL.md на GitHub.

---

## 6. Пробелы экосистемы

| Область | Текущее состояние | Возможность |
|---|---|---|
| Здравоохранение | Критически мало (единичные мелкие репо) | Высокая ниша (с осторожностью к регуляторике) |
| Музыка/аудио | Критически мало | Высокая ниша |
| Email-маркетинг | Мало (MJML, gmail-labeler) | Средняя |
| Локализация/перевод | Есть, но мало | Средняя |
| Аналитика больших данных | Есть, но нет стандарта | Средняя (связь с data-скиллами) |
| Юридические | Есть, но не стандартизированы (CUAD, NDA) | Средняя |
| Финансы | Есть, но мало | Средняя |
| Образование/менторство | Есть, но не систематизировано | Средняя |

---

## 7. Что делать нашему репозиторию (рекомендации по приоритету)

| Приоритет | Действие | Тип |
|---|---|---|
| 1 | Добавить `skills.sh.json` для публикации в реестре skills.sh (как vercel-labs) | Quick win |
| 2 | Workflow-скиллы: `plan-skill`, `systematic-debugger`, `test-driven-development` (по образцу `obra/superpowers`) | Структурный |
| 3 | Мульти-харнессность: конвертер SKILL.md → `.claude-plugin`/`.codex-plugin`/`.cursor-plugin`/`.opencode` | Структурный |
| 4 | Security: `secret-scanner`, `dependency-audit` (по образцу `trailofbits/skills`) | Средний |
| 5 | SEO/маркетинг: `seo-basics`, `geo-optimizer` (по образцу `coreyhaines31`) | Мефунк |
| 6 | PKM/Obsidian: `pkm-obsidian` (по образцу `kepano`) | Средний |
| 7 | MCP-интеграции: поставлять скиллы вместе с легковесным MCP-сервером | Структурный |
| 8 | Публикация в агрегаторы: `VoltAgent/awesome-agent-skills`, `travisvn/awesome-claude-skills` | Quick win |

---

## 8. Ссылки

### Официальные
- https://github.com/anthropics/skills
- https://github.com/vercel-labs/agent-skills
- https://github.com/vercel-labs/skills (CLI)
- https://github.com/anthropics/claude-plugins-official
- https://github.com/modelcontextprotocol/servers
- https://github.com/microsoft/azure-skills
- https://github.com/google/skills
- https://github.com/github/awesome-copilot

### Каталоги и агрегаторы
- https://skills.sh — Open Agent Skills Directory
- https://github.com/VoltAgent/awesome-agent-skills
- https://github.com/travisvn/awesome-claude-skills
- https://github.com/ComposioHQ/awesome-claude-skills
- https://github.com/hesreallyhim/awesome-claude-code
- https://github.com/jeremylongshore/claude-code-plugins-plus-skills
- https://github.com/wshobson/agents

### Методки и workflow
- https://github.com/obra/superpowers
- https://github.com/addyosmani/agent-skills
- https://github.com/OthmanAdi/planning-with-files

### Тематические
- https://github.com/mukul975/Anthropic-Cybersecurity-Skills
- https://github.com/NVIDIA/SkillSpector
- https://github.com/coreyhaines31/marketingskills
- https://github.com/kepano/obsidian-skills
- https://github.com/Imbad0202/academic-research-skills
- https://github.com/K-Dense-AI/scientific-agent-skills
- https://github.com/trailofbits/skills
- https://github.com/zarazhangrui/frontend-slides
- https://github.com/htdt/godogen
- https://github.com/Paramchoudhary/ResumeSkills
- https://github.com/zubair-trabzada/ai-legal-claude
- https://github.com/openaccountant/skills

### Спецификации и форматы
- https://agentskills.io — спецификация SKILL.md
- https://skills.sh/schemas/skills.sh.schema.json — схема skills.sh.json
- https://developers.openai.com/codex/skills — формат Codex skills (plugin.json)
- https://registry.modelcontextprotocol.io — MCP Registry

---

## 9. Каталог скиллов библиотеки `agent-skills`

Структурированный обзор скиллов самой библиотеки, сгруппированный по категориям (полный список и триггеры — в `index.json`). Категория `code` охватывает инженерные скиллы: линтинг/коммиты, ревью, тесты, безопасность, планирование и долгосрочные рабочие процессы агента.

### 9.1 `code` — инженерные скиллы

| Скилл | Версия | Назначение |
|---|---|---|
| `api-contract-testing` | 1.0.0 | Валидация API-контракта против OpenAPI 3.x + манифест эндпоинтов |
| `code-review` | 1.1.0 | Структурированный code review по чек-листу (без правок) |
| `commit-lint` | 1.0.0 | Проверка commit-сообщений по Conventional Commits |
| `commit-message-writer` | 1.0.0 | Оформление staged-изменений в Conventional Commit |
| `coverage-analyzer` | 1.0.0 | Разбор coverage.xml в читаемый отчёт с порогом |
| `frontend-perfection` | 1.5.0 | Аудит и полировка фронтенда до проверяемого идеала: Lighthouse ≥13, офлайн мета/SEO/WCAG/токен-аудит, Security/Privacy/i18n + OG-изображения |
| `frontend-a11y` | 1.0.0 | Глубокий аудит доступности (95 правил Front-End-Checklist): офлайн Python + Playwright/axe-core + ручной скринридер |
| `frontend-performance` | 1.0.0 | Глубина производительности за Lighthouse: офлайн-анализ заголовков/ассетов + Core Web Vitals (LCP/FCP/INP/CLS) |
| `frontend-testing` | 1.0.0 | Фронтенд-тестировка для production (Playwright, jest-axe, Pact, CI perf-budget + coverage) |
| `mobile-frontend` | 1.0.1 | Качественный mobile-first фронтенд: правила, сборка, многоуровневая проверка |
| `skill-feedback` | 1.0.0 | Сбор фидбека по скиллам в feedback/<skill>/YYYY-MM-DD.jsonl |
| `long-running-agent-workflow` | 1.0.0 | LRA-протокол для многосессионных проектов: `.lra/` feature-list + прогресс-лог, чекпоинты и восстановление |
| `plan-skill` | 1.0.0 | Планирование реализации (superpowers v2) с валидацией плана |
| `secret-scanner` | 1.0.0 | Статический поиск утёк секретов/токенов (gitleaks + энтропия) |
| `security-review` | 1.0.0 | Оркестрация security-ревью зависимостей и исходников |
| `skill-suggester` | 1.1.0 | Подбор скилла из библиотеки по триггерам/описанию |
| `systematic-debugger` | 1.0.0 | Систематическая отладка по Iron Law (4 фазы) |
| `test-generator` | 1.0.0 | Генерация pytest-скелетов из Python-модуля по AST |
| `version-bumper` | 1.0.0 | Предложение следующей semver-версии из git-истории |

> Полный перечень скиллов всех категорий (`code`, `data`, `media`, `repository`, `social`) — в `index.json`; описание каждого скилла — в его `SKILL.md`.