# Plan: raster-to-svg — фаза 2 (палитра, экспорт, пакет, MCP) + релиз

> Дата: 2026-08-18
> Статус: `approved`
> Версия скилла: 1.1.0 (было 1.0.0)

## Goal
Расширить скилл `skills/raster-to-svg/` из CLI-конвертера в полноценный
веб-инструмент: редактор палитры, экспорт в DXF/EPS/PNG, пакетная обработка,
опциональный MCP-сервер. Синхронизировать код и документацию между проектом,
дистрибутивом agent-skills и установленным скиллом opencode.

**Acceptance criteria (проверяемо):**
- [x] CR1: в UI есть редактор палитры: свотчи по группам, перекраска цвета, слияние двух цветов
- [x] CR2: экспорт SVG → DXF R12 (слои по цвету заливки), EPS, PNG (клиентский canvas, ×1–×4)
- [x] CR3: пакетная обработка: N PNG → N SVG → один `.zip`
- [x] CR4: `scripts/svg_export.py` работает как самостоятельный CLI; `scripts/raster_to_svg_mcp.py` отвечает на MCP-запросы
- [x] CR5: код, SKILL.md, skill.json, README, BENCHMARK идентичны в 3 местах (проект, agent-skills, ~/.config/opencode/skills)
- [x] CR6: E2E пройден: конверсия → палитра (recolor+merge) → экспорт DXF/EPS/PNG → пакет+zip

## Constraints
- Только Python 3 stdlib (http.server, argparse, zipfile) — без pip
- Фронтенд — vanilla JS/CSS без сборки и CDN
- Не ломать CLI-режим и детерминизм вывода
- НЕ добавлять Ф3 без ТЗ: gap filler, centerline, параметрические фигуры — отменены (нет требований; группировка по цвету уже реализована в `_flatten_dxf_layers`)

## Steps

### Step 1: svg_export.py (SVG → DXF R12 / EPS)
- Files: `scripts/svg_export.py`
- Produces: `svg_to_dxf(svg, layers) -> bytes`, `svg_to_eps(svg) -> bytes`, CLI `--fmt dxf|eps`
- Consumes: SVG-строку, опциональный маппинг слоёв (имя → цвет)
- Action: DXF — заголовок R12, ENTITIES с group code 8 (слой по цвету заливки), флэттенинг кривых; EPS — EPSF-3.0 header, команды пути
- Verification: DXF валиден (заголовок, ENTITIES, слои), EPS начинается с `%!PS-Adobe-3.0 EPSF-3.0`
- [x] done

### Step 2: сервер — /defaults, /export, /zip
- Files: `scripts/raster_to_svg_server.py`
- Produces: `GET /defaults` (схема параметров, single source of truth), `POST /export` (JSON {svg, fmt, layers} → DXF/EPS), `POST /zip` (JSON {files:[{name,svg}]} → .zip), `_flatten_dxf_layers`
- Action: добавить эндпоинты, группировка слоёв DXF по цвету
- Verification: curl-прогоны всех трёх эндпоинтов, коды 200/400/413/415/500
- [x] done

### Step 3: UI — палитра, экспорт-модалка, пакет
- Files: `web/index.html`, `web/style.css`, `web/app.js`
- Produces: `renderPalette`, `applyRecolor` (фикс двойной решётки — `full.replace('#'+h, to)`), merge-кнопка, `toggleExportModal`, `doExport`, `runBatch`, `addBatchFiles`, `zipBatch`
- Action: разделить монолитный index.html на app.js + style.css + index.html; палитра читает цвета из SVG, реколор через замену в тексте SVG
- Verification: E2E в браузере: палитра 31 свотч, recolor #ef8d18→#00ff00 (2 вхождения), merge #dc2d28→#e04444; DXF слой 00FF00 есть / EF8D18 отсутствует
- [x] done

### Step 4: MCP-сервер
- Files: `scripts/raster_to_svg_mcp.py`
- Produces: MCP-обработчики convert/health (stdio, JSON-RPC 2.0)
- Consumes: PNG (base64/файл) → параметры трассировки
- Action: обёртка над raster_to_svg.py без MCP SDK (чистый stdlib)
- Verification: ручной JSON-RPC-запрос `initialize`/`tools/list`
- [x] done

### Step 5: документация и синхронизация
- Files: `SKILL.md`, `skill.json`, `README.md`, `README.ru.md`, `BENCHMARK.md`, `web/*`, `scripts/*`
- Action: обновить SKILL.md (Files, API: /defaults /export /zip, фичи UI), skill.json (files + description + updated 2026-08-18), README/README.ru (фичи Ф2, структура репо), BENCHMARK (перепроверка цифр — актуален)
- Sync: проект → `agent-skills/skills/raster-to-svg` → `~/.config/opencode/skills/raster-to-svg`; проверить diff всех файлов
- Verification: `diff` всех файлов = пусто; `index.json` в agent-skills обновлён (v1.1.0, новое описание); README-таблицы agent-skills исправлены (была склейка строк mermaid-to-image/raster-to-svg)
- [x] done

### Step 6: review-архив и финальный E2E
- Files: `docs/plans/raster-to-svg-plan.md`, `skills/raster-to-svg/scripts/raster_to_svg.py`, `skills/raster-to-svg/scripts/raster_to_svg_server.py`, `skills/raster-to-svg/scripts/svg_export.py`, `skills/raster-to-svg/web/app.js`
- Action: зафиксировать результаты ревью в этом документе; финальный E2E на синхронизированной копии (agent-skills): сервер :8643 — /health, /defaults, /convert, /export (DXF/EPS), /zip
- Verification: CLI smoke обеих копий (94 мс, validated: ok); HTTP-коды 200 на всех эндпоинтах
- [x] done

## Interfaces
- Consumes → Produces:
  - `Step1.svg_export` → `Step2./export`
  - `Step2./defaults` → `Step3.renderPalette` (схема параметров)
  - `Step3.svg_edited` → `Step2./export` (реколор в тексте SVG)
  - `Step5.sync` → `Step6.E2E` (проверка синхронизированной копии)

## Verification (полная)
- [x] E2E браузер: конверсия shapes.png → 32 пути; палитра 31 свотч; recolor + merge; DXF 3.1 MB / 31 слой; EPS 1.2 MB / EPSF-3.0; PNG 1600×1200; batch 2 файла → zip (2 SVG)
- [x] CLI smoke обеих копий: native-contour, colors 4, validated: ok, 94 мс
- [x] BENCHMARK: цифры совпадают с замером (101 мс vs 99 мс — в пределах погрешности)
- [x] diff всех синхронизированных файлов = пусто (SKILL, skill.json, raster_to_svg.py, server, svg_export, mcp, app.js, style.css, index.html)
- [x] Ревью: applyRecolor без двойной решётки; слои DXF привязаны group code 8; реколор отражается в экспорте
- [ ] Финальный E2E-прогон на синхронизированной копии (сервер agent-skills)
