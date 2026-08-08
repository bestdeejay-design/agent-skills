# Showcase: `github-repo-hygiene` on lovii_demo

> Демонстрация работы скилла на **реальном** репозитории проекта **lovii.ru** —
> `https://github.com/bestdeejay-design/lovii_demo` (пред-MVP, public).
> Цель: показать, как скилл аутгенит текущее состояние (0% community health)
> и подготавливает план приведения к 100% по Community Standards.

---

## 1. Вход (Input)

| Что | Где |
|---|---|
| Репозиторий | `bestdeejay-design/lovii_demo` (public) |
| Ветка | `master` |
| Текущий `description` | *(пусто)* |
| `homepageUrl` | *(пусто)* — должен быть `https://lovii.ru/` |
| `repositoryTopics` | *(пусто)* — нужно добавить |
| `licenseInfo` | `null` — лицензия отсутствует |
| `.github/` | отсутствует — нужен каталог с health-файлами |
| `README.md` | есть (`index.html` — это SPA, но нет классического README) |

---

## 2. Запуск (Run)

```bash
# Полный аудит community health (самый информативный чек)
gh api repos/bestdeejay-design/lovii_demo/community/profile

# Проверка метаданных
gh repo view --json description,homepageUrl,repositoryTopics,licenseInfo,hasDiscussionsEnabled

# Проверка Pages (если включён)
gh api repos/bestdeejay-design/lovii_demo/pages
```

---

## 3. Текущее состояние (Output)

```json
{
  "health_percentage": 0,
  "description": null,
  "documentation": "https://lovii.mobiap.com/",
  "files": {
    "code_of_conduct": null,
    "contributing": null,
    "issue_template": null,
    "pull_request_template": null,
    "license": null,
    "readme": null
  },
  "updated_at": null
}
```

**Интерпретация**: репозиторий не проходит **ни одного** критерия Community Standards.
- Нет `README.md` (SPA без классического README)
- Нет `LICENSE`
- Нет `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1)
- Нет `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`
- Нет `.github/` каталога (issue/PR templates, workflows)
- Нет топиков, description, homepage
- Discussions отключены

---

## 4. План действий скилла (Action Plan)

Скилл подготовит следующие изменения для приведения к **100% Community Health**:

### A. Файлы (приоритет: критичные)

| # | Файл | Действие | Пример/шаблон |
|---|------|----------|---------------|
| 1 | `README.md` | Создать на базе White Paper (lovii.ru) + структура SPA | шаблон из SKILL.md §51–62 |
| 2 | `README.ru.md` | Зеркало англ. версии | правило 1:1 заголовков |
| 3 | `LICENSE` | Добавить MIT (owner: ООО «Аксиома», year: 2026) | стандарт MIT header |
| 4 | `CODE_OF_CONDUCT.md` | Полный текст Contributor Covenant 2.1 + контакт | `key: contributor_covenant` в community profile |
| 4 | `CONTRIBUTING.md` | Инструкция для контрибьюторов (PR/Issue process) | базовый шаблон |
| 5 | `SECURITY.md` | Политика отвечающего раскрытия (Responsible Disclosure) | шаблон из SKILL.md |
| 5 | `SUPPORT.md` | Имя **строго в верхнем регистре**; ссылки на каналы поддержки | redirect на Telegram/Email |
| 6 | `.github/ISSUE_TEMPLATE/` | `bug_report.yml`, `feature_request.yml` + `config.yml` | формы YAML с `name`+`description` |
| 6 | `.github/pull_request_template.md` | PR-шаблон с чек-листом | `name`+`about` frontmatter |
| 6 | `.github/workflows/ci.yml` | Базовый CI (lint, typecheck, tests) | GitHub Actions |
| 6 | `.github/release.yml` | Конфиг авто-riliz-notes | категории: features/docs/bugfix |
| 7 | `FUNDING.yml` | Опц.: кнопка Sponsor (OpenCollective/GitHub Sponsors) | `.github/FUNDING.yml` |

### B. Метаданные GitHub (через `gh` CLI)

| # | Параметр | Значение | Команда |
|---|----------|----------|---------|
| 1 | `description` | "White-label SaaS platform for local marketplaces — launch a neighborhood marketplace in 5 min" | `gh repo edit --description "..."` |
| 2 | `topics` | `["white-label","marketplace","saas","local-commerce","fintech","typescript","spa","lovii"]` | `gh api .../topics -X PUT -f 'names[]=...'` |
| 2 | `homepage` | `https://lovii.ru/` | `gh repo edit --homepage https://lovii.ru/` |
| 3 | `Discussions` | включить | `gh repo edit --enable-discussions` |
| 3 | `Security` | включить secret scanning / dependabot | `gh repo edit --enable-secret-scanning --enable-secret-scanning-push-protection` |

### C. Community Profile — цель: 100%

```bash
# После внесения изменений — проверка
gh api repos/bestdeejay-design/lovii_demo/community/profile
# Ожидаемый результат:
# health_percentage: 100
# files: {code_of_conduct: "contributor_covenant", contributing: "...", issue_template: "...", pull_request_template: "...", license: "mit", readme: "..."}
```

### D. Дополнительно (по канонам)

| Пункт | Статус | Примечание |
|-------|--------|------------|
| Social preview (og:image) | ☐ | Загрузить 1280×640 PNG < 1MB через Settings UI (API нет) |
| GitHub Pages | ☐ | `gh api repos/.../pages` (source: `gh-pages` / `docs`) + health check |
| `.github/release.yml` | ☐ | Авто-ноты по лейблам (features/docs/bugfix) |
| `.github/CODEOWNERS` | ☐ | Канон `github/docs` |
| `.github/dependabot.yml` | ☐ | Паттерн `github/docs` |
| `.github/ISSUE_TEMPLATE/config.yml` | ☐ | Валидация форм (`name`+`description`) для community profile |
| Social preview (og:image) | ☐ | 1280×640 PNG < 1MB — только через Settings UI (API нет) |
| Custom Properties | ☐ | `ownership-name`, `deployable` (паттерн `github/docs`) |

---

## 5. Интерпретация (Interpretation)

- **lovii_demo** — публичный репозиторий пред-MVP продукта (White Paper на lovii.ru).
- Текущее `health_percentage: 0` — типично для ранних проектов, фокусированных на коде, а не на гигиене репозитория.
- Скилл `github-repo-hygiene` даёт **перечень конкретных действий** (файлы + `gh` команды + проверки) для приведения к **100% Community Standards** за 1–2 PR.
- **Ключевые канонические паттерны**, которые скилл применит:
  - `health_percentage: 100` через Community Profile API (эталон `github/docs`)
  - Contributor Covenant 2.1 (`key: contributor_covenant`) — распознаётся GitHub автоматически
  - Issue-формы YAML с `name`+`description` — чтобы `files.issue_template` не было `null`
  - `description` ≤ 350 символов + topics ≤ 20 (lowercase) — для поиска
  - Social preview только через UI (API нет), 1280×640 PNG < 1MB
  - Pages: `gh-pages` branch или `/docs`, health check DNS

---

> **Чек-лист готовности showcase:**
> - [x] Вход — реальный публичный репозиторий (`bestdeejay-design/lovii_demo`)
> - [x] Команда `gh api .../community/profile` воспроизводима
> - [x] Вывод — реальный JSON с `health_percentage: 0`
> - [x] План действий покрывает все критерии Community Standards до 100%