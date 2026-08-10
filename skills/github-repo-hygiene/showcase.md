# Showcase: github-repo-hygiene до / после

> Материал для каталогов и README библиотеки. Показывает, что скилл меняет
> в репозитории на практике.

## «До» — типичный репозиторий без скилла

```
README.md (153 строки устаревшего текста, без визуала)
LICENSE
(и всё)

Community Standards:  ►●○○○○  ~40%
- description: пусто
- topics: none
- social preview: нет
- issue/PR шаблонов: нет
- поиск Google → capsule-render URL-баннер → сервис закрылся → битая картинка
```

## «После» — репозиторий, прошедший скилл

```
README.md (актуальный, EN) + README.ru.md (зеркало заголовков 1:1)
assets/header.svg + assets/footer.svg   ← локальные анимированные SVG
LICENSE (MIT, распознаётся: spdx_id=mit)
CODE_OF_CONDUCT.md (Contributor Covenant 2.1, key=contributor_covenant)
CONTRIBUTING.md · SECURITY.md · SUPPORT.md
.github/ISSUE_TEMPLATE/*.yml + pull_request_template.md
.github/workflows/ci.yml + release.yml
CHANGELOG.md (Keep a Changelog)
description ≤ 350 симв., topics ≤ 20, homepage = GitHub Pages
social preview 1280×640, < 1 MB
релиз v1.0.0 + generate-notes

Community Standards:  ●●●●●●  100%
```

## Как выглядит «шапка»

Баннер генерируется в репозитории — **ноль внешних сервисов**:

```html
<p align="center">
  <a href="https://github.com/USERNAME" target="_blank">
    <img src="assets/header.svg" alt="header" />
  </a>
</p>
```

Локальный SVG (примерно так, в пикселях реального файла):

```
┌──────────────────────────────────────────────────────────────┐
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  ~290px
│  ░░ PROJECT_NAME                               ░░        │  градиент
│  ░░ Short description of the project           ░░        │  COLD→WARM
│  ══≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈   │  волны
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │  «фон
└──────────────────────────────────────────────────────────────┘    наплывает»
```

Анимация (SMIL, работает в `<img>` на GitHub): переливающийся градиент,
«текущие» волны (морфинг d-path), блик-проход раз в ~16 секунд, плавное
появление текста. Футер — инверсия по вертикали, 60px, с мерцающим `@username`.

## Автоматика повторных прогонов

| Команда | Что даёт |
|---|---|
| `python3 scripts/generate_assets.py --name … --desc … --user … --cold #HEX --warm #HEX` | пере-генерация шапки/футера |
| `python3 scripts/extract_context.py` | авто-определение name/desc/стека/цветов для генератора |
| `python3 scripts/validate_svg.py assets/` | проверка SVG по правилам (CI-гейт) |
| `python3 scripts/validate_repo.py` | 16-пунктовый чек-лист, exit 0/1 (CI-гейт) |

Пример в `.github/workflows/repo-hygiene.yml` (в скилле: `examples/repo-hygiene.yml`)
превращает валидаторы в pre-merge check.

## Пресеты визуала

| Пресет | Когда |
|---|---|
| `default` | большинство проектов: анимированный градиент с волнами |
| `minimal` | документация, стабильные инструменты: статичный градиент |
| `dark-first` | тёмная тема GitHub по умолчанию: глубокий тёмный баннер |
| `monochrome` | книги/печать/спеки: ч/б без анимации |

Все пресеты — локальные файлы, без внешних зависимостей. Удалить баннер —
просто удалить `<p>`-обёртку из README.