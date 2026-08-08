---
name: mermaid-to-image
description: "Рендер Mermaid-диаграмм (.mmd) в PNG/SVG. Скрипт mermaid_to_image.py читает .mmd (файл или stdin) и отдаёт изображение: приоритет локальному mmdc (mermaid-cli), fallback на публичный API mermaid.ink. Поддерживает выбор формата (svg/png), фоновый цвет, масштаб PNG, движок рендера (auto/mmdc/ink), вывод в файл или stdout. Триггеры: 'mermaid в картинку', 'отрендерить диаграмму', '.mmd в png', 'mermaid to image', 'render diagram', 'диаграмма в svg', 'схема в картинку'."
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib; optional: mermaid-cli (mmdc) для офлайн-рендера"
---

# Mermaid To Image

> Рендер Mermaid-диаграмм из текста `.mmd` в файлы PNG/SVG.

Загружай этот скилл когда нужно **превратить Mermaid-диаграмму в картинку**:
для README, документации, презентаций, бейджей или вложений в отчёты.

## 🎯 When to use

Use this skill when:
- Есть `.mmd`-файл или текст Mermaid и нужен PNG/SVG-файл
- Нужно вставить диаграмму в README/вики/презентацию (у рендер-плагинов GitHub нет PNG)
- Просят «отрендерить диаграмму», «mermaid в png», «схему в картинку»
- Нужна статичная картинка для экспорта (не интерактивная mermaid.live)

Do NOT use when:
- Диаграмма нужна только в Markdown-исходнике — GitHub рендерит Mermaid сам
- Нужны диаграммы из текстового описания без Mermaid-кода — это `diagram-maker`
- Нужны диаграммы архитектуры AWS/GCP — отдельный рендер в roadmap

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/mermaid_to_image.py` — рендерер .mmd → PNG/SVG (Python 3 stdlib)

## 🧰 Usage

```bash
# Файл → SVG (по умолчанию):
python3 skills/mermaid-to-image/scripts/mermaid_to_image.py -i diagram.mmd -o diagram.svg

# Файл → PNG:
python3 skills/mermaid-to-image/scripts/mermaid_to_image.py -i diagram.mmd -o diagram.png

# Из stdin (текст прямо в пайплайне):
cat diagram.mmd | python3 mermaid_to_image.py --stdin -o out.svg

# С фоном и масштабом:
python3 mermaid_to_image.py -i d.mmd -o d.png --bg white --scale 3

# В stdout (для программного использования):
python3 mermaid_to_image.py -i d.mmd --stdout > d.svg
```

## 🧭 Движки рендера

| Движок | Как включить | Когда выбирать |
|--------|-------------|----------------|
| `mmdc` (mermaid-cli) | `--engine mmdc` (npm i -g @mermaid-js/mermaid-cli) | офлайн, приватные схемы, большие диаграммы, точный контроль |
| `ink` (mermaid.ink) | `--engine ink` | без установки, быстрый старт; PNG отдаётся как JPEG-образ |

По умолчанию `--engine auto`: используется `mmdc`, если он установлен, иначе `ink`.

## 🔬 Проверка результата

- SVG: файл начинается с `<svg`, валиден для вставки в Markdown/HTML.
- PNG: `file out.png` показывает «JPEG image data» — это нормально для mermaid.ink
  (API отдаёт JPEG-кодированный образ); визуально проверьте открытием.
- При ошибке сети/API скрипт пишет причину в stderr и завершается с кодом 2.
