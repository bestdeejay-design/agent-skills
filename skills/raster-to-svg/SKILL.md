---
name: raster-to-svg
description: "Конвертер PNG в векторный SVG. Скрипт raster_to_svg.py читает PNG (файл или stdin) и отдаёт SVG: при установленном vtracer-cli используется он (качественная цветная трассировка), иначе встроенный нативный трассировщик на чистом Python 3 stdlib (свой декодер PNG через zlib, без pip-зависимостей). Два режима: contour (квантование median-cut, контурная трассировка, квадратичные Bezier, fill-rule evenodd, дырки) и mosaic (сетка примитивов rect/circle/triangle/diamond с детерминированным миксом по --seed). SVG всегда валидируется (round-trip через XML-парсер) перед записью, вывод детерминирован. Триггеры: 'png в svg', 'картинка в svg', 'растровое в векторное', 'векторизация', 'конвертнуть в svg', 'trace image', 'convert png to svg', 'vectorize', 'изображение в вектор', 'трассировка изображения'."
license: MIT
metadata:
  author: best
  version: 1.1.0
  compatibility: "Requires Python 3 stdlib; optional: vtracer-cli (cargo install vtracer-cli) для качественной цветной трассировки"
when_to_use: "Use when converting a raster image (PNG/logo/icon) to scalable vector SVG: 'png to svg', 'vectorize image', 'trace image', 'convert png to svg', 'картинка в svg', 'векторизация', 'трассировка изображения'. Example: 'turn this logo.png into an SVG' or 'convert png to svg'."
---

# Raster To SVG

> Превращает растровую PNG-картинку в масштабируемый векторный SVG.

Загружай этот скилл когда нужно **перевести растровое изображение в вектор**:
для логотипов, иконок, схем, README-ассетов или любого PNG, который должен
масштабироваться без потери качества.

## 🎯 When to use

Use this skill when:
- Есть PNG-файл (логотип, иконка, схема) и нужен SVG для вставки в веб/документацию
- Просят «векторизировать картинку», «png в svg», «trace image», «convert png to svg»
- Нужна детерминированная трассировка без внешних зависимостей (только Python 3)
- Хочется стилизованный результат: контурную обводку или мозаику из примитивов

Do NOT use when:
- Исходник уже в векторе (SVG/PDF/EPS) — трассировка растра не нужна
- Нужна фотореалистичная векторизация сложных фото — лучше специализированный редактор
- Формат не PNG — CLI принимает только PNG на входе (в веб-интерфейсе JPG/JPEG/WEBP конвертируются автоматически в браузере)

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/raster_to_svg.py` — конвертер PNG → SVG (Python 3 stdlib, без pip)
- `scripts/raster_to_svg_server.py` — локальный веб-сервер с UI (стандартный `http.server`)
- `scripts/svg_export.py` — конвертеры SVG → DXF R12 / EPS (слои по цвету заливки)
- `scripts/raster_to_svg_mcp.py` — опциональный MCP-сервер для AI-агентов
- `examples/web/` — фронтенд (`index.html` + `style.css` + `app.js`): drag & drop (PNG/JPG/WEBP с локальной перекодировкой), sticky-превью с лупой ×4 на результате, 12 быстрых пресетов (плоский стиль, минимал, лайн-арт, иконка, логотип, фото-плоский, фото, дуотон, винтаж, чб, мозаика-постер, мозаика-круги) с меткой «ручные настройки» при ручном изменении, скрытие неактуальных групп настроек движка (vtracer/native/мозаика), подготовка фото (сглаживание + ступени цвета в браузере), прогресс-бар, код SVG, скачивание

## 🧰 Usage

```bash
# Базово: PNG → SVG с белым фоном:
python3 skills/raster-to-svg/scripts/raster_to_svg.py -i logo.png -o logo.svg --bg white

# Меньше цветов (нативный contour):
python3 raster_to_svg.py -i logo.png -o logo.svg --colors 4

# Мозаичный постер из примитивов:
python3 raster_to_svg.py -i icon.png -o icon.svg -m mosaic --cell 8 --shape auto

# Пайплайн stdin → stdout:
cat icon.png | python3 raster_to_svg.py -i - -o -

# Машиночитаемый отчёт:
python3 raster_to_svg.py -i logo.png -o logo.svg --json

# Принудительно нативный движок (без vtracer):
python3 raster_to_svg.py -i logo.png -o logo.svg --engine native
```

## 🌐 Веб-интерфейс

Запуск локального веб-сервера с UI (drag & drop, превью, код, скачивание, копирование):

```bash
python3 skills/raster-to-svg/scripts/raster_to_svg_server.py
# → http://127.0.0.1:8642/ (откроется в браузере автоматически)
```

Опции: `--port N`, `--host`, `--no-browser`, `--max-mb N` (лимит входного файла, по умолчанию 20 МБ).

- Конвертация полностью локальная — картинка никуда не отправляется.
- API: `GET /` — UI, `GET /health` — статус, `GET /defaults` — схема параметров (single source of truth), `POST /convert?<параметры>` с телом = raw PNG → `{"svg", "report"}`, `POST /export` (JSON `{"svg","fmt","layers"}`) → DXF/EPS, `POST /zip` (JSON `{"files":[{"name","svg"}]}`) → `.zip` для пакетной обработки.
- UI-фичи: редактор палитры (свотчи, перекраска, слияние цветов), экспорт DXF/EPS/PNG, пакетная обработка (очередь PNG → один .zip).
- Ошибки: `400` неверный параметр, `413` превышен лимит, `415` не-PNG, `500` сбой движка.

## 🧭 Движки и режимы

| Движок | Как включить | Когда выбирать |
|--------|-------------|----------------|
| `vtracer` (бинарь `vtracer` из пакета `vtracer-cli`) | `--engine vtracer` (cargo install vtracer-cli) | качественная цветная трассировка, лучше детали, в 2–4× быстрее на фото |
| `native` (встроенный) | `--engine native` | без установки, офлайн, детерминированный результат |

По умолчанию `--engine auto`: берётся `vtracer`, если он установлен, иначе `native`.

Режимы (`-m`):
- `contour` (по умолчанию): квантование цветов → контуры → квадратичные Bezier, поддерживает дырки (`fill-rule="evenodd"`). Тюнинг: `--colors`, `--smooth`, `--corner`, `--seam`, `--bg`.
- `mosaic`: сетка ячеек из примитивов (`--shape rect|circle|triangle|auto`), детерминированный микс по `--seed`, зазор `--gap`. Тюнинг: `--cell`, `--shape`, `--gap`, `--seed`.

vtracer-параметры: `--vtracer-preset bw|poster|photo`, `--vtracer-mode spline|polygon`, `--vtracer-color-precision`, `--vtracer-filter-speckle`.

## ⚡ Производительность движков (эмпирика, aug 2026)

Замер: contour, 8 цветов, macOS arm64. Фото = портрет 1024×1024.

| Картинка | native | vtracer |
|----------|--------|---------|
| лого/иконка 200×150 | 4–99 мс, mce 0.0 | 8–11 мс, файл меньше |
| градиент | 60 мс, 8 путей, mce 5.24 | 17 мс, 20 путей (плавнее) |
| фото 512×512 | 2.46 с, 490 KB, 8 путей | 0.44 с, 312 KB, 642 пути |
| фото 1024×1024 | 9.1 с, 1.2 MB, 8 путей | 2.0 с, 842 KB, 2014 путей |

Итог: для фото `vtracer` в 2–4× быстрее, легче и детальнее; `native` — выбор для простых изображений (логотипы, пиксель-арт, иконки): mce 0.0, один путь на цвет, полный офлайн. `auto` сам выбирает vtracer при наличии.

## 🔬 Проверка результата

- SVG всегда проходит XML-валидацию (round-trip через парсер) перед записью — файл корректен для вставки в HTML/Markdown.
- Детерминизм: один и тот же вход даёт байт-идентичный SVG при повторном запуске.
- Коды выхода: `0` — успех, `1` — ошибка ввода/использования, `2` — сбой движка. При ошибке причина пишется в stderr.
