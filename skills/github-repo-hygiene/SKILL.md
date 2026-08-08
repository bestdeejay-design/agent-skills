---
name: github-repo-hygiene
description: "Проверка и обновление описательной части GitHub-репозитория при мажорных изменениях: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR-шаблоны, social preview, релизы, description, topics, ссылки на GitHub Pages, community health. Триггеры: 'github hygiene', 'оформить репозиторий', 'обновить readme', 'github page', 'описание репозитория', 'теги для поиска', 'topics', 'contributing', 'license', 'security policy', 'полностью оформить гитхаб', 'репозиторий готов к публикации', 'repo polish', 'github repo docs', 'community health', 'issue template', 'pr template', 'social preview', 'релиз', 'release notes'."
license: MIT
metadata:
  author: best
  version: "1.1.0"
compatibility: "Requires gh CLI and network access to api.github.com"
---

# GitHub Repo Hygiene — оформление и поддержание описательной части репозитория

Загружай этот скилл, когда нужно **оформить или проверить соответствие** описательной
части GitHub-страницы репозитория: README, лицензия, community-файлы, issue/PR-шаблоны,
social preview, теги поиска, релизы, ссылка на GitHub Pages, community health.

## Цель

Чтобы страница репозитория на GitHub всегда отражала **актуальное состояние** проекта:
не отставала после мажорных изменений (новые сервисы, фичи, саги, смена стека) и была
полноценной (Чек-лист GitHub «Community Standards» закрыт на 100%).

## Do not use

- Не используй этот скилл, когда README и описательная часть уже актуальны, а
  пользователь не просил изменений — не «улучшай» без запроса.
- Для одного точечного фикса (например, только обновить один бейдж) скилл не нужен —
  делай правку напрямую, без загрузки скилла.

## Обязательные / желательные файлы репозитория

| Файл | Назначение | Когда обновлять |
|------|-----------|-----------------|
| `README.md` | Англ. версия, главная страница (лимит отображения ~500 KiB) | при любых мажорных изменениях |
| `README.<lang>.md` (напр. `README.ru.md`) | Локализованные версии, зеркала англ. | синхронизировать с англ. |
| `LICENSE` | MIT-лицензия (owner/year) | при создании, смене владельца |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 (полный текст с контактом) | редко |
| `CONTRIBUTING.md` | Инструкция контрибьюторам | при смене процессов/конвенций |
| `SECURITY.md` | Политика безопасности | при смене контактов/политики |
| `SUPPORT.md` | Строго **верхний регистр имени файла**; ссылка «Support» в хелпере при создании issue | редко |
| `.github/ISSUE_TEMPLATE/*.yml` | Issue-формы (bug_report, feature_request) — дают галочку в Community Health | при смене процессов |
| `.github/pull_request_template.md` | PR-шаблон (корень/`docs/`/`.github/`, формат `.md`/`.txt`) | при смене процессов |
| `.github/workflows/ci.yml` | CI | при изменении проверок |
| `.github/release.yml` | Конфиг автогенерируемых release-notes | при создании первой релизии |
| `FUNDING.yml` | Опц: кнопка «Sponsor» | редко |
| `CHANGELOG.md` | Опц: формат Keep a Changelog | при каждой релизии |

> `LICENSE` нельзя выносить в `.github/` — GitHub распознаёт её только в корне/`docs/`
> репозитория (default-файлы в `.github/` для лицензии НЕ сканируются).

## README — обязательные элементы

1. **Шапка**: название, однострочное описание проекта, живые значок-линки (badges: 3–6, единый стиль).
2. **Статус-блок**: актуальные цифры проверок (typecheck/contract/integration).
3. **Быстрый старт**: установка, инфраструктура, запуск.
4. **Структура репозитория**: полное дерево (включая новые каталоги/сервисы).
5. **Разделы про стек/события/проверки** — синхронизировать с реальным кодом.
6. **Ссылка на GitHub Pages** (если включён): `https://<user>.github.io/<repo>/` + homepage в About.
7. **Языковая шапка-переключатель**: `**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](…)`.
8. **Хэштеги/ключевые слова** — для поиска (описание + topics).
9. Рекомендуется использовать **относительные** ссылки на файлы репо (абсолютные ломаются в клонах).
10. GitHub автогенерирует TOC — ручной оглавление не требуется.

## Правило двух версий (анти-дрейф)

- `README.md` — **всегда на английском** (международный стандарт GitHub).
- `README.<lang>.md` — русская версия, **зеркало**: при изменении англ. версии
  переносить правки в русскую (структуру заголовков 1:1, цифры, статусы).
- Расхождение локализованных версий — типичный антипаттерн; перед релизом делать
  программную сверку заголовков обоих файлов.
- Избегать «AI-slop» формулировок: «seamless», «unleash», «empower», перегруз эмодзи.

## Теги поиска (topics) и описание

Устанавливать через `gh api`:

```bash
# Описание репозитория (лимит UI ~350 символов) — перечислять ВСЕ ключевые компоненты
gh repo edit --description "<полное описание с ключевыми словами>"

# Теги (массив через -f 'names[]=...')
gh api -X PUT repos/<owner>/<repo>/topics \
  -f 'names[]=python' -f 'names[]=markdown' -f 'names[]=documentation' \
  -f 'names[]=agents' -f 'names[]=skills' -f 'names[]=opencode'
```

Рекомендации по тегам:
- максимум **20 тегов** на репозиторий (лимит GitHub)
- каждый тег: **≤ 50 символов**, только lowercase-буквы/цифры/дефисы
- язык/фреймворк/БД/брокер (ключевые), архитектурные паттерны, тип проекта
- **все значимые компоненты** должны быть отражены и в description, и в topics

## GitHub Pages

Евл. Pages включён (`gh api repos/<owner>/<repo>/pages`):
- в README обязательна ссылка `https://<owner>.github.io/<repo>/` — проверять, что рабочая
- в About поле «Website» = URL Pages (`gh repo edit --homepage https://…`)

## Social preview (og:image)

- Файл в корне/`docs/`/default-ветки, формат PNG/JPG/GIF, **< 1 MB**, **≥ 640×320**,
  рекомендовано **1280×640**.
- Устанавливается в Settings → Social preview → Edit → Upload (только через UI).
- Прозрачность поддерживается, но сплошной фон рекомендуется.

## Релизы

- Публичные релизы с **semver-тегами** (`v1.0.0`, `v1.1.0`).
- `.github/release.yml` — автонотсы из merged PR по лейблам (features/docs/bugfix).
- Тег создаётся на main; GitHub сам назначает badge «latest» по semver.

## Чек-лист проверки при мажорном изменении

Запускать при: новый сервис/фича/сага, смена стека, смена портов/схем, изменение
контрактов, изменение процессов (CI/коммиты), любой релиз/гейт, delivery gate.

### A. Файлы — на месте и распознаны GitHub

1. [ ] `README.md` отражает новое состояние (структура, сервисы, цифры тестов, статус).
2. [ ] `README.<lang>.md` синхронизирован с англ. версией (заголовки 1:1).
3. [ ] `LICENSE` на месте, owner/year корректны, GitHub **распознаёт** лицензию (`spdx_id`).
4. [ ] `CODE_OF_CONDUCT.md` — полный текст Contributor Covenant 2.1 с контактом;
      GitHub **распознаёт** как Covenant (`key: contributor_covenant`, **не** `other`).
5. [ ] `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md` (имя строго в upper-case).
6. [ ] `.github/ISSUE_TEMPLATE/` (bug_report + feature_request, forms yml) и
      `.github/pull_request_template.md` на месте с валидным frontmatter
      (`name`+`about` для `.md`, `name`+`description` для `.yml`).

### B. Метаданные GitHub

7. [ ] `gh repo edit --description` актуально, перечисляет ВСЕ компоненты (≤350 символов на UI).
8. [ ] topics (`gh api .../topics`) актуальны, ≤ 20, lowercase, ≤ 50 символов каждый.
9. [ ] Homepage (`gh repo edit --homepage https://<user>.github.io/<repo>/`) — при Pages; рабочая ссылка.
10. [ ] Social preview задан (1280×640, < 1 MB) — если есть Settings.
11. [ ] CI-бейдж/статус в README соответствует реальному состоянию (не stale).

### C. Community Health

12. [ ] `gh api repos/<owner>/<repo>/community/profile` → `health_percentage >= 100`,
      `files.issue_template` и `files.pull_request_template` не `null`.
13. [ ] `has_discussions` желательно `true` (Discussions включены) для вопросов.

### D. Релизы

14. [ ] Существует релиз с semver-тегом (последний «latest»), `.github/release.yml` настроен.
15. [ ] `CHANGELOG.md` (Keep a Changelog) обновлён под новый релиз.

### E. Финальная

16. [ ] Коммит/пуш сделан, изменения видны на GitHub; CI зелёный.

## Команды проверки

```bash
# Файлы на месте
ls LICENSE CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md SUPPORT.md README.md README.ru.md

# Описание + homepage + темы
gh repo view --json description,homepageUrl,repositoryTopics

# Теги
gh api repos/<owner>/<repo>/topics

# Pages
gh api repos/<owner>/<repo>/pages

# Community health (!!) — самый информативный чек
gh api repos/<owner>/<repo>/community/profile

# Распознавание лицензии и CoC (ключи)
gh api repos/<owner>/<repo>/community-enabled   # или /community/get
```

Замена отображения в WEB-интерфейсе (бейджи, community health %) занимает
1–5 минут после пуша — проверять не сразу после коммита, а с небольшой паузой.

## Примечания

- README.ru.md — специфика этого проекта; в других проектах русской версии может не быть —
  проверять наличие перед синхронизацией.
- Не менять `README.md` без явной просьбы, если он уже актуален — скилл для
  проверки/обновления, а не для «улучшательств».
- После изменения README: `git add README.md README.ru.md && git commit && git push`
  (только по запросу пользователя).
- Антипаттерны: битые бейджи (хуже отсутствующих), ASCII-арт, «AI-slop»-формулировки,
  расхождение локализованных README, отсутствие лицензии у публичного репо, отсутствие
  SECURITY.md при приёме контрибьюций.

## Canonical analogues

Полный разбор — в `references/canonical-patterns.md`. Ключевые каноны:

- **GitHub Docs: Community Profile API** (`GET /repos/{owner}/{repo}/community/profile`) — эталонный аудит с метрикой `health_percentage` (эталон `github/docs` = 100%), готовый чеклист файлов.
- **GitHub Docs: Default community health files** — org-level `.github` репозиторий, приоритет поиска файлов, правило «LICENSE не наследуется», полный список health-файлов (включая `FUNDING.yml`, `GOVERNANCE.md`).
- **GitHub CLI (`gh repo edit`, `gh release create`)** — полный набор флагов: add/remove-topic, template, default-branch, enable-* (advanced-security, secret-scanning), draft-then-publish flow для релизов, immutable releases.
- **GitHub REST API** (Repositories / Pages / Licenses / Custom Properties) — PATCH /repos (все поля), PUT /repos/topics (только так), Pages API (cname, health check, build_type workflow), Custom Properties API, security_and_analysis, archival/transfer, SPDX License API.
- **github/docs** — эталон 100% community health: CODEOWNERS, dependabot.yml, issue-формы YAML + config.yml, custom properties (ownership/deployable/CodeQL-Block).
- **facebook/react, kubernetes/kubernetes, vercel/next.js, microsoft/vscode** — SUPPORT.md (редирект), SECURITY_CONTACTS, AGENTS.md/CLAUDE.md (AI-instructions), CODENOTIFY/OWNERS.
- **Contributor Covenant v2.1** — канонический текст CoC (key `contributor_covenant` в community profile).
- **SPDX License List** — канонические SPDX-идентификаторы, на них опирается GitHub Licenses API.