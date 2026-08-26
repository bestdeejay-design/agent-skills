---
name: pdf-report-builder
description: "Сборка PDF-отчётов из Markdown без обязательных зависимостей. Скрипт pdf_report_builder.py конвертирует markdown (файл или stdin) в HTML (pandoc или встроенный конвертер) и далее в PDF первым доступным движком: Chromium/Chrome headless --print-to-pdf, weasyprint или pandoc с PDF-движком (pdflatex/tectonic/typst). Поддержка заголовков, списков, таблиц, кода, цитат, ссылок, кастомный заголовок документа. Триггеры: 'отчёт в pdf', 'markdown в pdf', 'собери отчёт', 'pdf report', 'markdown to pdf', 'отчёт для клиента', 'document to pdf'."
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib; PDF-движок опционально (Chrome/weasyprint/pandoc)"
when_to_use: "Build a PDF document from Markdown (report, README, spec, client deliverable). Triggers: 'markdown to pdf', 'pdf report', 'отчёт в pdf', 'markdown в pdf', 'собери отчёт', 'отчёт для клиента', 'document to pdf'. Example: 'Convert my report.md into a PDF for the client.'"
---

# PDF Report Builder

> Сборка PDF-отчёта из Markdown-файла: заголовки, таблицы, код, цитаты —
> в аккуратный одностраничный PDF.

Загружай этот скилл когда нужно **сделать PDF-документ из Markdown**: отчёт
по проекту, README в PDF, спецификацию, чек-лист для клиента, экспорт
документации вне GitHub.

## 🎯 When to use

Use this skill when:
- Есть `.md`-файл и нужен PDF (отчёт, README, спецификация, сопроводительное письмо)
- Нужно отправить документ клиенту/коллеге в печатном формате
- Просят «сделай отчёт в pdf», «markdown в pdf», «собери документ»

Do NOT use when:
- Достаточно HTML — проще отдать `.md` или github-rendered страницу
- Нужна презентация — это `presentation-maker`
- Нужна диаграмма — это `diagram-maker` / `mermaid-to-image`

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/pdf_report_builder.py` — конвертер markdown → PDF (Python 3 stdlib)

## 🧰 Usage

```bash
# Из файла:
python3 skills/pdf-report-builder/scripts/pdf_report_builder.py -i report.md -o report.pdf --title "Project Report"

# Из stdin (пайплайн):
cat notes.md | python3 pdf_report_builder.py --stdin -o notes.pdf --title "Notes"

# Прямо из плана v1.2 и пр.
```

## 🧭 Движки (по приоритету)

1. **Chrome/Chromium/Edge headless** — `--headless --print-to-pdf` (обычно стоит на macOS)
2. **weasyprint** — `python3 -m pip install weasyprint`
3. **pandoc + PDF-движок** — `pdflatex`/`tectonic`/`typst`/`context`

Если ни одного нет — скрипт печатает подсказку по установке и завершается с кодом 1.
Разметка отрисовывается через `pandoc` (если установлен) или встроенный конвертер
(заголовки, списки, таблицы, код, цитаты, ссылки).

## 🔬 Проверка результата

- `file out.pdf` → «PDF document, version 1.4»
- Открыть в просмотрщике и проверить: заголовки, таблицы, код-блоки не обрезаны.
- Для кириллицы: шрифт по умолчанию без проблем (системный), размер страницы A4 по умолчанию.