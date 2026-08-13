# deck-pptx (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** сборка настоящего PowerPoint (`.pptx`) из JSON-спеки презентации,
которую готовит `deck-outline`. Один фокус: спека → PowerPoint.

**Скрипт:** `build_pptx.py` рисует лейауты через python-pptx: textbox для
заголовков/буллетов, `TrueTable` для таблиц, `CategoryChartData` для графиков,
фоны по палитре из спеки.

**Когда применять:** просят «pptx», «powerpoint», «сделай pptx».

**Не применять:** для структуры — `deck-outline`; для HTML-слайдов — `deck-html`.

**Зависимость:** python-pptx в venv проекта (`.venv/bin/pip install python-pptx`).
