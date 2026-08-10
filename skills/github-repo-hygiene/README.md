# github-repo-hygiene

> Проверка и обновление описательной части GitHub-репозитория + визуальное
> оформление README локальными анимированными SVG. Скилл для AI-агентов
> (opencode и аналогичные), поставляется с пакетом скриптов для CI-гейтов.

**Ключевое:** ноль внешних сервисов. Шапка и футер README — это
`assets/header.svg` / `assets/footer.svg` **в вашем репозитории**: анимация на
SMIL (`<animate>`), работает в `<img>` на GitHub без скриптов и внешних запросов.

## Возможности

- **Чек-лист Community Standards → 100%**: README (EN) + зеркало `README.<lang>.md`,
  распознаваемые LICENSE (`spdx_id`) и CODE_OF_CONDUCT (Contributor Covenant 2.1),
  CONTRIBUTING/SECURITY/SUPPORT, issue-формы YAML + PR-шаблон, CI,
  `community/profile` → `health_percentage`.
- **Метаданные**: description, topics (≤20, lowercase), homepage (Pages),
  social preview, релизы semver + `release.yml`, CHANGELOG.
- **Локальные анимированные SVG**: эффект «фон наплывает» (маска-вырез),
  морфинг волн (4 кадра, `Q`+`T`), рассинхрон 30%, блик-проход, twinkling.
  4 пресета: `default` / `minimal` / `dark-first` / `monochrome`.
- **Скрипты** (pure Python 3 stdlib, exit 0/1 — годятся для CI):
  - `scripts/generate_assets.py` — генерация header/footer (пресеты)
  - `scripts/extract_context.py` — авто-определение name/desc/стека/цветов
  - `scripts/validate_svg.py` — валидация SVG по правилам
  - `scripts/validate_repo.py` — 16-пунктовый чек-лист (gh API + filesystem)
- **CI-интеграция**: пример `examples/repo-hygiene.yml` — валидаторы как
  pre-merge check (read-only).

## Установка

Скопируйте директорию скилла в библиотеку скиллов агента
(например `~/.config/opencode/skills/github-repo-hygiene`).
Требования: `python3` (stdlib only). Для проверок метаданных — `gh` CLI
с авторизацией (`gh auth login`), это опционально.

## Быстрый старт

```bash
# 1. Авто-детект контекста репозитория (в корне клона)
python3 scripts/extract_context.py --gh-repo owner/repo

# 2. Генерация шапки/футера
python3 scripts/generate_assets.py \
  --name "Project Name" --desc "Short description" --user "owner" \
  --cold "#0ABAB5" --warm "#F64A8A" --preset default

# 3. Проверка SVG (для CI-гейта)
python3 scripts/validate_svg.py assets/

# 4. Полный чек-лист (локально или через API, --clone для remote)
python3 scripts/validate_repo.py owner/repo --clone
```

Вставьте в начало README.md:

```html
<p align="center">
  <a href="https://github.com/owner" target="_blank">
    <img src="assets/header.svg" alt="header" />
  </a>
</p>
```

(в конец — то же с `assets/footer.svg`; ссылки относительные — работают
в клонах и форках).

## Состав

| Файл | Назначение |
|---|---|
| `SKILL.md` | инструкция-воркфлоу для агента (точка входа) |
| `skill.json` | манифест (requirements, inputs/outputs) |
| `references/svg-animation.md` | полная спецификация SVG + шаблоны |
| `references/color-tokens.md` | decision tree: name/desc/цвета |
| `references/community-checklist.md` | 16 пунктов + команды проверки |
| `references/svg-presets.md` | пресеты оформления |
| `references/canonical-patterns.md` | каноны: GitHub Docs/API/github-docs/SPDX |
| `scripts/` | 4 скрипта генерации/валидации |
| `examples/repo-hygiene.yml` | CI-воркфлоу-пример |
| `showcase.md` | «до/после» для каталогов |

## Эксплуатация

- После мажорных изменений (новые сервисы, смена стека, релиз) прогоняйте
  `validate_repo.py` — отчёт JSON, exit 0/1.
- Расхождение локализованных README ловится автоматически (сверка структуры
  заголовков).
- Web-интерфейс GitHub (бейджи, health %) обновляется 1–5 минут после пуша.

## Лицензия

MIT. Автор: [bestdeejay-design](https://github.com/bestdeejay-design).