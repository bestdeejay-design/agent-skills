---
name: presentation-craft
description: "Router for high-quality presentations. Orchestrates specialist sub-skills per stage: narrative (docs-product + seo-content) -> visual direction (frontend-design-taste) -> build (presentation-maker) -> UI/UX audit (frontend-perfection + deck_audit) -> export (presentation-maker pptx/pdf). Encodes a research-backed quality contract (assertion headlines, <=6 bullets, design tokens, WCAG contrast, uniqueness gate, layout rhythm). Use when a deck must be more than a template."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.1.0"
---

# presentation-craft

Router, не генератор. Он не рисует слайды сам — он ведёт многоэтапный сценарий и
на **каждом этапе подключает нужный скилл** (загрузкой его SKILL.md). Это прямой
перенос проверенного паттерна «тонкий entry -> quality -> reviewer»
(majiayu000/claude-skill-registry) и полного цикла guizang-ppt-skill на наш каталог.

> Внешние базы, на которых выстроен роутер: op7418/guizang-ppt-skill (полный цикл
> 0->7, заблокированные темы, Node-валидаторы); Mathews-Tom/armory skills/marp-slides
> (ленивая подгрузка references, роутинг); majiayu000/claude-skill-registry
> (marp-authoring + marp-slide-quality + marp-slide-reviewer); anthropics/skills
> skills/pptx (fidelity-экспорт, validate.py, Visual QA); wanshuiyin/.../slides-polish
> (постраничный ревьюер против reference-визуала, версионирование).

## Когда использовать
- Нужна презентация, которая не выглядит «шаблонной AI»: есть смысл, стиль,
  корректный UI/UX и проверка.
- Триггеры: «качественная презентация», «сделай стильную презентацию»,
  «презентация с дизайн-системой», «не шаблонные слайды», «presentation craft».

## Когда НЕ использовать
- Быстрый одностраничный набросок — бери сразу `presentation-maker`.
- Только верстка HTML-страницы — `frontend-perfection`.

## Канонический пайплайн (6 этапов)
Порядок и гейты — консенсус из anthropics/skills (pptx, frontend-design, theme-factory),
guizang-ppt-skill, armory/marp-slides, majiayu000 trio, wanshuiyin/slides-polish.

### Этап 0 — Intake (кларификация)
Сними неопределённость ДО генерации (guizang «7 вопросов» / armory «один запрос + дефолты»):
- Аудитория, цель (pitch / отчёт / обучение / имидж);
- Длительность -> число слайдов (~1 слайд/мин; для 10-мин доклада ≈ 8–12);
- Материалы (сайт, бриф, тексты) — если есть лендинг, сними контент через `web-scraper`;
- Стиль/бренд (если задан) или вольная на Этапе 2.
Не переходи дальше без аудитории + цели + объёма.

### Этап 1 — Narrative / смысл  -> скилл `docs-product` + `seo-content`
- `docs-product`: из материалов вытащи VISION/позиционирование/ценности -> структуру
  «зачем / что / доказательство» (дуга Hook -> Context -> Core -> Shift -> Takeaway).
- `seo-content`: читабельность (Flesch-KincoW), уберил воду, E-E-A-T.
- Результат: `outline.md` (формат `presentation-maker`) с assertion-заголовками
  (полное предложение с глаголом + точка), одна идея/слайд, ≤6 буллетов.
**Гейт**: заголовки — выводы, не темы; нет повторов; консистентность цифр между слайдами.

### Этап 2 — Visual direction / стиль  -> скилл `frontend-design-taste`
- Палитра 4–6 имён, типографика (display + body + utility), ОДИН signature-элемент.
- Прогони uniqueness gate против 3 AI-дефолтов (cream+serif+terracotta; near-black+acid;
  broadsheet). Если часть читается как дефолт — пересмотри и зафиксируй, что изменил.
- Зафиксируй токены: доминанта 60–70%, один accent, единый motif, без decorative
  полос/градиентов/теней в Swiss-режиме.
- Результат: token-спека (hex, шрифты, radius, mood) -> ляжет в `theme` presentation-maker
  (через `templates/themes/*.json` или `frontmatter theme:`).
**Гейт**: uniqueness пройден ДО сборки; палитра «содержательна», не дефолтна.

### Этап 3 — Build  -> скилл `presentation-maker`
- `deck_md.py outline.md -o deck.json --goal <pitch|consulting|keynote|report|edu> --theme <имя из Этапа 2> --lang ru`
- `build_html.py deck.json slides.html` (16:9; токены из Этапа 2 инжектятся в :root).
- Правь `deck.json` и пересобирай при необходимости (контракт единый).
**Гейт**: deck.json валиден; слайдов столько же, сколько в outline; layout-разнообразие
(≥6 разных типов на 8–12 слайдов, нет 3 одинаковых подряд).

### Этап 4 — UI/UX correctness + audit  -> скилл `frontend-perfection` + `deck_audit`
- `frontend-perfection` -> `meta_audit.py --html slides.html --css <css>`: WCAG-контраст
  (вычисляемый luminance ≥4.5:1), **zero raw hex вне токенов**, порядок заголовков,
  a11y (alt, focus, landmark). При наличии Node — `audit.js` (Lighthouse ≥13) на локальном сервере.
- `deck_audit.py deck.json --html slides.html`: assertion-заголовки, words/slide budget,
  единый mood, контраст.
- Итеративно правь до зелёного на обоих.
**Гейт**: contrast PASS; tokens:raw-hex = 0; headings в порядке; deck_audit без failed (warn допустимы).

### Этап 5 — Export + Visual QA + Deliver  -> скилл `presentation-maker`
- `verify_slides.py slides.html --spec deck.json` (обязательный Playwright-гейт:
  переполнения, наложения, навигация) — должен быть PASS.
- `build_pdf.py slides.html deck.pdf` (PDF 1:1 с HTML, тот же рендер).
- `build_pptx.py deck.json deck.pptx` — полная дизайн-система (14 типов слайдов,
  1600×900, токены из Этапа 2 в `theme`). Геометрия проверяется гейтами:
  - `qa_pptx.py deck.pptx --render` — geometric gate (bounds/overlap/tables) + JPEG-рендеры
    для визуального просмотра; дизайн-элементы `ghost*`/`decor*`/`chrome-*` исключены.
  - `qa_intern.py deck.pptx --skip-token-rules` — extern-линтер `intern` (alignment,
    DOUBLE_SPACE, margins); фильтрует ложные срабатывания дизайн-системы по имени фигуры.
- Визуальный финал: открыть slides.html, пролистать, сверить с чек-листом дефектов
  (overflow, overlaps, <0.3″ gaps, low-contrast icons). По JPEG из `qa_pptx.py --render`
  сверить ghost/decor-элементы, выходящие за холст (их геометрия не проверяется).
**Гейт**: verify_slides PASS; qa_pptx PASS; qa_intern 0 ошибок; PDF собран; pptx — финальный.

## Контракт качества (acceptance criteria)
Итоговая дека проходит, если:
- [ ] Нарратив: заголовки — assertion (вывод), одна идея/слайд, ≤6 буллетов, консистентность данных.
- [ ] Стиль: пройден uniqueness gate; палитра «содержательна»; один accent; доминанта 60–70%; signature-элемент есть.
- [ ] Токены: все цвета — через `:root`/theme, **ноль raw hex вне токенов**.
- [ ] Контраст: WCAG ≥4.5:1 (текст), ≥3:1 (иконки/границы) — вычисляемый luminance.
- [ ] Ритм: ≥6 разных layout-ов на 8–12 слайдов; нет 3 одинаковых подряд; hero/divider-чередование.
- [ ] UI/UX: a11y (alt, focus, reduced-motion), нет переполнений/наложений (verify_slides PASS).
- [ ] Экспорт: HTML + PDF 1:1; pptx — дизайн-система с геометрией (qa_pptx PASS, qa_intern 0).

## Команды (быстрая сводка)
Относительно репо-рута, скрипты `presentation-maker`:
```
python3 skills/presentation-maker/scripts/deck_md.py outline.md -o deck.json --theme <name> --lang ru
python3 skills/presentation-maker/scripts/build_html.py deck.json slides.html
python3 skills/presentation-maker/scripts/verify_slides.py slides.html --spec deck.json
python3 skills/presentation-maker/scripts/build_pdf.py slides.html deck.pdf
python3 skills/presentation-maker/scripts/build_pptx.py deck.json deck.pptx
python3 skills/presentation-maker/scripts/deck_audit.py deck.json --html slides.html
# UI/UX аудит (frontend-perfection, офлайн, без Node):
python3 skills/frontend-perfection/scripts/meta_audit.py --html slides.html --css <css>
```

## Закрытые гэпы и следующие шаги
- pptx (Этап 5) — полная дизайн-система: 14 типов слайдов, геометрический гейт
  (`qa_pptx.py`) и extern-линтер `intern` (`qa_intern.py`), PDF/PPTX из единого deck.json.
- Скоринг-движок (как SlideGauge) и XSD-валидация pptx (как anthropics validate.py) —
  кандидаты на отдельный суб-скилл аудита для ещё более жёстких гейтов.
