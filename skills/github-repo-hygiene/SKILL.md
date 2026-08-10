---
name: github-repo-hygiene
description: "Проверка и обновление описательной части GitHub-репозитория при мажорных изменениях: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR-шаблоны, social preview, релизы, description, topics, ссылки на GitHub Pages, community health + визуальное оформление header/footer локальными анимированными SVG (4 пресета: default/minimal/dark-first/monochrome). Триггеры: 'github hygiene', 'оформить репозиторий', 'обновить readme', 'github page', 'описание репозитория', 'теги для поиска', 'topics', 'contributing', 'license', 'security policy', 'полностью оформить гитхаб', 'репозиторий готов к публикации', 'repo polish', 'github repo docs', 'community health', 'issue template', 'pr template', 'social preview', 'релиз', 'release notes', 'шапка readme', 'readme header', 'анимированный svg', 'визуальное оформление', 'waving svg', 'пресеты оформления', 'extract context'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.5.0"
compatibility: "Requires gh CLI and network access to api.github.com for metadata checks; pure-Python scripts (python3, stdlib only) for generation/validation"
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

## Инструменты скилла (scripts/)

Скилл поставляется с тремя скриптами (pure Python 3 stdlib) — используй их вместо
ручной работы, где возможно:

| Скрипт | Назначение | Вызов |
|---|---|---|
| `scripts/generate_assets.py` | Детерминированная генерация `assets/header.svg` + `assets/footer.svg` (пресеты: `--preset default\|minimal\|dark-first\|monochrome`) | `python3 scripts/generate_assets.py --name X --desc Y --user Z --cold #HEX --warm #HEX [--preset default]` |
| `scripts/extract_context.py` | Авто-детект контекста генерации: name/desc/стек/topic/цвета COLD/WARM/user из git remote | `python3 scripts/extract_context.py [--path DIR] [--gh-repo owner/repo] [--text]` |
| `scripts/validate_svg.py` | Валидация SVG по правилам скилла (SMIL, маска, морфинг) | `python3 scripts/validate_svg.py assets/` |
| `scripts/validate_repo.py` | Прогон 16-пунктового чек-листа (gh API + filesystem) | `python3 scripts/validate_repo.py [owner/repo]` |

Детали каждого — в его docstring; отчёты в JSON, exit code 0/1 (пригодны для CI).

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

- `README.md` — **всегда на английском** (международный стандарт GitHub).
- `README.<lang>.md` — локализованная версия, **зеркало**: при изменении англ. версии
  переносить правки (структуру заголовков 1:1, цифры, статусы).
- Расхождение локализованных версий — типичный антипаттерн; перед релизом делать
  программную сверку заголовков обоих файлов (есть в `scripts/validate_repo.py`).
- Избегать «AI-slop» формулировок: «seamless», «unleash», «empower», перегруз эмодзи.

## Визуальное оформление README — локальные анимированные SVG

По умолчанию каждый репозиторий, проходящий через скилл, получает **header** (начало
README) и **footer** (конец README) — **локальные анимированные SVG** в `assets/`
(`assets/header.svg`, `assets/footer.svg`), обязательны в обеих языковых версиях.

**Принцип: ноль внешних сервисов.** Никаких `capsule-render`, `shields`-генераторов
и URL-баннеров. Анимация — только **SMIL** (`<animate>`, `<animateTransform>`):
работает в `<img>` на GitHub без скриптов и внешних запросов.

Ключевые приёмы: эффект «фон наплывает» (чёрная волна в `<mask>` вырезает цвет →
виден фон страницы), морфинг `d`-path 4 кадрами (гребни `Q`+`T`, одинаковая
последовательность команд во всех кадрах), рассинхрон волн 30%, блик-проход раз
в ~16s, twinkling-ник в footer.

**Полная спецификация + шаблоны header/footer → `references/svg-animation.md`**
**Определение значений (USERNAME/PROJECT_NAME/PROJECT_DESC/COLD/WARM) → `references/color-tokens.md`**
**Пресеты оформления (default/minimal/dark-first/monochrome) → `references/svg-presets.md`**

Выбор пресета: по умолчанию `default` (анимированный градиент). `minimal` — для
документации/стабильных инструментов (статичный градиент, без волн);
`dark-first` — глубокая тёмная подложка (тёмная тема GitHub по умолчанию);
`monochrome` — книги/печать/спеки (ч/б, без SMIL). Проси пользователя указать
пресет, либо бери `default`.

### Как генерировать (рекомендуемый путь)

**Скриптом** (детерминированно, затем валидация):

```bash
python3 scripts/generate_assets.py \
  --name "Project Name" --desc "Short description" --user "username" \
  --cold "#0ABAB5" --warm "#F64A8A"
python3 scripts/validate_svg.py assets/        # должно быть: all passed
```

**Вручную** (когда скрипт недоступен): прочитай `references/svg-animation.md`,
подставь `COLD`, `WARM`, `PROJECT_NAME`, `PROJECT_DESC`, `FONTCOLOR`, `USERNAME`
в шаблоны, создай `assets/`, добавь ссылки (см. «Вставка в README.md» в reference).

### Безопасность генерации

- Не генерировать без подтверждения `USERNAME`, если он неочевиден.
- Не перезаписывать существующие `.svg` без явного запроса.
- Не трогать контент README между header и footer.
- Не добавлять header/footer, если они уже есть (только по запросу).
- SVG: без `<script>`, без base64, только SMIL; маска с белым `<rect>` на весь холст.

## Теги поиска (topics) и описание

Устанавливать через `gh api`:

```bash
# Описание репозитория (лимит UI ~350 символов) — перечислять ВСЕ ключевые компоненты
gh repo edit --description "<полное описание с ключевыми словами>"

# Теги (массив через -f 'names[]=...') — только PUT, полная замена списка
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

Если Pages включён (`gh api repos/<owner>/<repo>/pages`):
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

16-пунктовый чек-лист (файлы → метаданные → community health → релизы → финал) с
командами проверки: **`references/community-checklist.md`**.

Автоматизированный прогон:

```bash
python3 scripts/validate_repo.py            # авто-детект из git remote
python3 scripts/validate_repo.py owner/repo # явный репозиторий
```

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
- **GitHub Docs: Default community health files** — org-level `.github` репозиторий, приоритет поиска файлов, правило «LICENSE не наследуется», полный список health-файлов.
- **GitHub CLI (`gh repo edit`, `gh release create`)** — полный набор флагов, draft-then-publish flow для релизов, immutable releases.
- **GitHub REST API** — PATCH /repos, PUT /repos/topics (только так), Pages API, Custom Properties API, security_and_analysis, SPDX License API.
- **github/docs** — эталон 100% community health: CODEOWNERS, dependabot.yml, issue-формы YAML + config.yml.
- **facebook/react, kubernetes/kubernetes, vercel/next.js, microsoft/vscode** — SUPPORT.md, SECURITY_CONTACTS, AGENTS.md/CLAUDE.md.
- **Contributor Covenant v2.1** — канонический текст CoC (key `contributor_covenant` в community profile).
- **SPDX License List** — канонические идентификаторы, на них опирается GitHub Licenses API.