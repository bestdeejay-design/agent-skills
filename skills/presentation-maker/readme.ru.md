# presentation-maker (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Презентации «под ключ» из темы.** Единый конвейер из маленьких скриптов — по
одной команде на этап:

```
тема / outline.md
      │  strategy.py            (дуга + mood + плотность + лейауты)
      ▼
   deck.md  ──(deck_md.py)──▶  deck.json
      │                          ├──(build_html.py)──▶ slides.html
      │                          │                        └──(verify_slides.py)──▶ PASS/FAIL  [обязательный гейт Playwright]
      │                          ├──(build_pptx.py)──▶ deck.pptx
      │                          ├──(build_pdf.py)──▶  deck.pdf
      │                          └──(deck_audit.py)──▶  отчёт о качестве (JSON)
```

## Команды

```bash
# 1. Стратегия (опционально)
python3 skills/presentation-maker/scripts/strategy.py --goal keynote
python3 skills/presentation-maker/scripts/strategy.py --list
python3 skills/presentation-maker/scripts/strategy.py --show pitch

# 2. Аутлайн → спецификация
python3 skills/presentation-maker/scripts/deck_md.py outline.md -o deck.json
python3 skills/presentation-maker/scripts/deck_md.py outline.md -o deck.json \
    --goal keynote --audience "инвесторы" --lang ru --palette swift --tone confident

# 3. HTML-слайды 16:9
python3 skills/presentation-maker/scripts/build_html.py deck.json slides.html

# 4. Верификация (ОБЯЗАТЕЛЬНО, Playwright)
python3 skills/presentation-maker/scripts/verify_slides.py slides.html --spec deck.json

# 5. PowerPoint
python3 skills/presentation-maker/scripts/build_pptx.py deck.json deck.pptx

# 6. PDF (из slides.html, Playwright)
python3 skills/presentation-maker/scripts/build_pdf.py slides.html deck.pdf

# 7. Аудит качества
python3 skills/presentation-maker/scripts/deck_audit.py deck.json --html slides.html
```

## Что внутри

- `scripts/` — `deck_md.py` (md→json), `strategy.py` (пресеты), `build_html.py`
  (HTML 16:9), `verify_slides.py` (гейт Playwright), `build_pptx.py` (реальный
  `.pptx`), `build_pdf.py` (PDF из HTML), `deck_audit.py` (эстетический гейт).
- `templates/` — `slides.html`, `themes/*.json` (general/modern/executive/momentum/
  swift/standard/dynamic), `icons/*.svg`.
- `references/` — `strategy.md`, `design-system.md`, `product-designer.md`, `pdf.md`,
  `audit.md`.

## Зависимости

- `python3` (stdlib для `deck_md.py`, `strategy.py`, `deck_audit.py`).
- `pip install python-pptx` — для `build_pptx.py`.
- `pip install playwright && playwright install chromium` — для `verify_slides.py`
  и `build_pdf.py`.
