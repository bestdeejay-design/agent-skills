---
name: github-repo-hygiene
description: "Проверка и обновление описательной части GitHub-репозитория при мажорных изменениях: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR-шаблоны, social preview, релизы, description, topics, ссылки на GitHub Pages, community health. Триггеры: 'github hygiene', 'оформить репозиторий', 'обновить readme', 'github page', 'описание репозитория', 'теги для поиска', 'topics', 'contributing', 'license', 'security policy', 'полностью оформить гитхаб', 'репозиторий готов к публикации', 'repo polish', 'github repo docs', 'community health', 'issue template', 'pr template', 'social preview', 'релиз', 'release notes'."
license: MIT
metadata:
  author: best
  version: "1.3.0"
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

## Визуальное оформление README (header/footer) — локальные анимированные SVG

Применять по умолчанию к каждому репозиторию, который проходит через скилл:
README получает **header** (начало файла) и **footer** (конец файла) в виде
**локальных анимированных SVG-файлов** в репозитории. Оба элемента обязательны
в **обеих языковых версиях** (`README.md` + `README.<lang>.md`), когда локальная
версия существует.

**Принцип: ноль внешних сервисов.** Никаких `capsule-render`, `shields`-генераторов
и прочих URL-баннеров. AI создаёт файлы `assets/header.svg` и `assets/footer.svg`
прямо в репозитории, README ссылается на них относительными путями. Анимация
реализуется **SMIL-атрибутами `<animate>`** — она работает в GitHub (и любом
браузере) в теге `<img>` без скриптов и без внешних запросов. Пользователи скилла
не зависят ни от одного внешнего сервиса при оформлении.

### Структура файлов

В корне репозитория:

```
assets/
  ├── header.svg
  └── footer.svg
README.md
```

### Определение владельца (USERNAME)

- `USERNAME` = сегмент после `github.com/` в URL репозитория.
- Пример: `github.com/bestdeejay-design/repo` → `USERNAME = "bestdeejay-design"`.
- Если владелец неочевиден — подтвердить у пользователя до генерации.

### Определение названия проекта (PROJECT_NAME)

Приоритет (от высокого к низкому):
1. Поле `name` в `package.json`
2. Поле `name` в `pyproject.toml` / `setup.py` / `Cargo.toml`
3. Поле `name` в `composer.json` / `pubspec.yaml`
4. Название репозитория (без префикса владельца)
5. Заголовок первого `#` в существующем README

### Определение описания (PROJECT_DESC)

Приоритет:
1. Поле `description` в `package.json` / `pyproject.toml`
2. Поле `description` репозитория на GitHub
3. Анализ технологий → автогенерация (см. таблицу ниже)
4. По типу репозитория (см. таблицу)
5. Fallback: `Open Source Project`

#### Таблица автогенерации desc

| Технология/Тип | desc |
|---|---|
| React/Vue/Svelte/Next.js | `Frontend Developer` |
| Node.js/Express/Fastify | `Backend Engineer` |
| Python/Django/Flask | `Backend Developer` |
| TypeScript | `Type-Safe Code` |
| Rust | `Systems Programming` |
| Go | `Backend Tool` |
| Telegram/Discord/Slack bot | `Automation Tool` |
| CLI/terminal | `Developer Utility` |
| Mobile (React Native/Flutter/Swift) | `Mobile App` |
| UI library/design system | `UI Components` |
| Portfolio | `Creative Developer` |
| Documentation | `Knowledge Base` |
| API | `API Service` |
| Database/ORM | `Data Layer` |
| AI/ML/PyTorch/TensorFlow | `AI / Machine Learning` |
| DevOps/Docker/K8s | `DevOps Tool` |
| Game/Unity/Godot | `Game Development` |
| Chrome/Firefox extension | `Browser Extension` |
| VS Code extension | `IDE Plugin` |
| Web App (без конкретного стека) | `Web Application` |
| Library (общее) | `Developer Library` |

### Определение цветовой схемы (COLD + WARM)

Приоритет:
1. Явно указанные цвета проекта (брендинг, design tokens, бейджи README, `og-image`)
2. Цвета из настроек VSCode / темы (если присутствуют в репо)
3. AI подбирает по тематике (см. таблицу)
4. Fallback: `#0ABAB5` + `#F64A8A`

#### Таблица подбора цветов

| Тематика | Цвет 1 | Цвет 2 |
|---|---|---|
| Дизайн / UI / Frontend | `#0ABAB5` | `#F64A8A` |
| Backend / API / Инфра | `#1E3A8A` | `#F59E0B` |
| AI / ML / Data | `#7C3AED` | `#06B6D4` |
| DevOps / Cloud | `#0EA5E9` | `#10B981` |
| Mobile | `#8B5CF6` | `#EC4899` |
| Боты / Automation | `#9B4DCA` | `#00D4FF` |
| Игры | `#DC2626` | `#7C3AED` |
| Финансы / Крипто | `#1E293B` | `#FBBF24` |
| Безопасность | `#18181B` | `#EF4444` |
| Образование | `#2563EB` | `#F97316` |
| Open source общее | `#6366F1` | `#EC4899` |
| Fallback | `#0ABAB5` | `#F64A8A` |

Из таблицы: **Цвет 1 → COLD**, **Цвет 2 → WARM** (или наоборот — AI выбирает
направление так, чтобы градиент был контрастным; оба варианта допустимы, главное —
единообразие в рамках проекта).

### Правила для градиента

- **HEADER**: слева `COLD` → справа `WARM`.
- **FOOTER**: слева `WARM` → справа `COLD` (**инверсия header**).
- Запрещено использовать белый (`#FFFFFF`) в середине градиента — сольётся с текстом.
- `FONTCOLOR`: `#FFFFFF` (или `#1A1A2E`, если градиент светлый).

### Что умеет анимация (лучше, чем у внешних сервисов)

- **Переливающийся градиент** — цвета плавно перетекают друг в друга (8s).
- **Дрейфующие волны** — 2 полупрозрачные волны бесшовно плывут по фону с разной
  скоростью (движущееся «море»).
- **Плавное появление** — название и описание появляются с лёгким подъёмом (fade + slide).
- **Twinkling в footer** — ник владельца мерцает (пульсирует яркостью).
- Анимация держится только на SMIL `<animate>`/`<animateTransform>` — работает
  в `<img>` на GitHub без скриптов.

### Шаблон header.svg

Подставить: `COLD`, `WARM` (цвета без `#`-риска — с `#`), `PROJECT_NAME`, `PROJECT_DESC`, `FONTCOLOR`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="290" viewBox="0 0 1200 290" role="img" aria-label="PROJECT_NAME — PROJECT_DESC">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="COLD">
        <animate attributeName="stop-color" values="COLD;WARM;COLD" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="WARM">
        <animate attributeName="stop-color" values="WARM;COLD;WARM" dur="8s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
  </defs>

  <rect width="1200" height="290" fill="url(#bg)"/>

  <!-- Дрейфующая волна 1 (период 300, бесшовный сдвиг) -->
  <path fill="#FFFFFF" opacity="0.14"
        d="M-300,270 Q-225,230 -150,270 Q-75,310 0,270 Q75,230 150,270 Q225,310 300,270 Q375,230 450,270 Q525,310 600,270 Q675,230 750,270 Q825,310 900,270 Q975,230 1050,270 Q1125,310 1200,270 Q1275,230 1350,270 Q1425,310 1500,270 L1500,290 L-300,290 Z">
    <animateTransform attributeName="transform" type="translate" values="0,0;-300,0;0,0" dur="9s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.14;0.22;0.14" dur="6s" repeatCount="indefinite"/>
  </path>

  <!-- Дрейфующая волна 2 (период 450, другая скорость) -->
  <path fill="#FFFFFF" opacity="0.10"
        d="M-450,275 Q-337.5,260 -225,275 Q-112.5,290 0,275 Q112.5,260 225,275 Q337.5,290 450,275 Q562.5,260 675,275 Q787.5,290 900,275 Q1012.5,260 1125,275 Q1237.5,290 1350,275 L1350,290 L-450,290 Z">
    <animateTransform attributeName="transform" type="translate" values="0,0;-450,0;0,0" dur="14s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.10;0.16;0.10" dur="7s" repeatCount="indefinite"/>
  </path>

  <g>
    <animate attributeName="opacity" values="0;1" dur="1.5s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" values="0,16;0,0" dur="1.5s" fill="freeze"/>
    <text x="600" y="140" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="48" font-weight="bold" fill="FONTCOLOR" text-anchor="middle">PROJECT_NAME</text>
  </g>

  <g>
    <animate attributeName="opacity" values="0;1" dur="1.5s" begin="0.5s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" values="0,12;0,0" dur="1.5s" begin="0.5s" fill="freeze"/>
    <text x="600" y="196" font-family="'Helvetica Neue',Arial,sans-serif" font-size="26" fill="FONTCOLOR" opacity="0.92" text-anchor="middle">PROJECT_DESC</text>
  </g>
</svg>
```

### Шаблон footer.svg

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="80" viewBox="0 0 1200 80" role="img" aria-label="@USERNAME">
  <defs>
    <linearGradient id="fg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="WARM">
        <animate attributeName="stop-color" values="WARM;COLD;WARM" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="COLD">
        <animate attributeName="stop-color" values="COLD;WARM;COLD" dur="8s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
  </defs>

  <rect width="1200" height="80" fill="url(#fg)"/>

  <path fill="#FFFFFF" opacity="0.15"
        d="M-300,70 Q-225,55 -150,70 Q-75,85 0,70 Q75,55 150,70 Q225,85 300,70 Q375,55 450,70 Q525,85 600,70 Q675,55 750,70 Q825,85 900,70 Q975,55 1050,70 Q1125,85 1200,70 Q1275,55 1350,70 Q1425,85 1500,70 L1500,80 L-300,80 Z">
    <animateTransform attributeName="transform" type="translate" values="0,0;-300,0;0,0" dur="11s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.15;0.25;0.15" dur="5s" repeatCount="indefinite"/>
  </path>

  <text x="600" y="52" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="bold" fill="#FFFFFF" text-anchor="middle">
    @USERNAME
    <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
  </text>
</svg>
```

### Вставка в README.md

В **начало** README.md:

```html
<p align="center">
  <a href="https://github.com/USERNAME" target="_blank">
    <img src="assets/header.svg" alt="header" />
  </a>
</p>
```

В **конец** README.md:

```html
<p align="center">
  <a href="https://github.com/USERNAME" target="_blank">
    <img src="assets/footer.svg" alt="footer" />
  </a>
</p>
```

- Ссылки **относительные** (`assets/header.svg`) — работают в клонах и форках;
  GitHub сам масштабирует SVG (1200×290 / 1200×80) под ширину контейнера.
- Кликабельность (переход на профиль владельца) обеспечивает обёртка `<a>` —
  внутри самого `<img>` SVG ссылки не срабатывают.

### Алгоритм работы AI

1. Определи `USERNAME` из URL репозитория (подтвердить, если неочевиден).
2. Определи `PROJECT_NAME` по приоритетам выше.
3. Определи `PROJECT_DESC` по приоритетам / таблице.
4. Определи `COLD` и `WARM` по приоритетам / таблице цветов.
5. Определи `FONTCOLOR` (`#FFFFFF` по умолчанию).
6. Создай `assets/` (если нет) и сгенерируй `assets/header.svg` по шаблону.
7. Сгенерируй `assets/footer.svg` по шаблону.
8. Добавь ссылки в начало и конец README.md (и в `README.<lang>.md`, если есть).
9. Если `assets/header.svg` / `assets/footer.svg` уже существуют — спросить:
   перезаписать?

### Правила безопасности

- Не генерировать без подтверждения `USERNAME`, если он неочевиден.
- Не перезаписывать существующие `.svg` без явного запроса.
- Не трогать контент README между header и footer.
- Не добавлять header/footer, если они уже есть (только по запросу).
- Не использовать `<script>` в SVG — GitHub блокирует скрипты; только SMIL `<animate>`.
- Не использовать base64 — обычные файлы в `assets/`.

### Кодировка текста в SVG

- Пробелы остаются пробелами (это SVG, не URL — URL-encoding не нужен).
- Спецсимволы — HTML entities при необходимости (`&amp;` для `&`).
- Если `PROJECT_NAME` длиннее 20 символов — уменьшить `font-size` до 36.
- Если длиннее 30 символов — уменьшить до 28.
- Если длиннее 40 — перенести часть в `PROJECT_DESC`.

### Параметры анимации (настраиваемые)

- `dur="8s"` — скорость перетекания градиента (можно 4–10s).
- `dur="9s"/"14s"` — скорость дрейфа волн 1/2 (можно 6–18s; разные периоды
  создают глубину).
- `dur="1.5s"` — скорость появления текста (можно 1–2s), `begin="0.5s"` —
  задержка появления desc.
- `dur="2s"` — скорость мерцания footer (можно 1.5–3s).
- Периоды волн в `d`-path должны быть **кратны сдвигу** в `animateTransform`
  (например, период 300 ↔ сдвиг -300), иначе сдвиг не будет бесшовным.

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