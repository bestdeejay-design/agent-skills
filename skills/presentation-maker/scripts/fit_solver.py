#!/usr/bin/env python3
"""fit_solver — геометрическая гарантия до рендера (Слой 3).

Для каждого слайда с параметрами от composer.py измеряет реальную геометрию
текста в headless-Chromium (bbox-пересечения, заполненность, переносы) и либо
подтверждает fit, либо возвращает composer.py на повторный выбор с
исключённой опцией (детерминированный retry). Чистая геометрия, без LLM.

Использование (через build_html.py):
    fit, report = fit_solver.check_slide(html_fragment, slide_index, geometry)
"""
import json
import sys
from pathlib import Path

MIN_FILL = 0.15   # контент не может занимать < 15% площади (кроме dominant)
MAX_FILL = 0.85   # и > 85% (тесно)
MAX_ATTEMPTS = 5


def _render_and_measure(fragments: list[str], viewport=(1600, 900), base_css: str = "") -> list[dict]:
    """Отрендерить фрагменты в headless-Chromium и вернуть bbox ключевых блоков.

    base_css — реальный CSS деки (base.html + composition CSS + активный
    паттерн), передаётся вызывающей стороной (build_html.py). Без него
    измерение бессмысленно: карточки/сетки полагаются на .metrics-grid,
    .col-card и т.д., которые задаёт именно этот CSS, а не заглушка —
    на голых тегах все карточки схлопываются в одну точку и дают ложные
    "overlaps"/fill-провалы на КАЖДОМ слайде."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("fit_solver: playwright недоступен — проверка пропущена", file=sys.stderr)
        return []
    fallback_css = (
        ".slide{position:relative;width:1600px;height:900px;overflow:visible;"
        "display:flex;flex-direction:column;justify-content:center;align-items:center;}"
        "h1,h2{font-size:44px;}h2{font-size:44px;}"
        ".bullet-list li{font-size:18px;line-height:1.5;}"
        ".metric-card{font-size:20px;padding:20px;}"
    )
    style_block = base_css or fallback_css
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        for frag in fragments:
            page.set_content(
                f'<div id="deck">{frag}</div>'
                f"<style>{style_block}</style>"
            )
            page.wait_for_timeout(100)
            data = page.evaluate("""() => {
                const slide = document.getElementById('deck');
                const title = slide.querySelector('h1, h2');
                const content = slide.querySelector('.bullet-list, .metrics-grid, .spread-grid, '
                    + '.bars-block, .fact-grid, .menu-block, .ladder-block, .stats-block, '
                    + '.steps, .timeline, .table-wrap, .col-card');
                const boxes = [];
                const push = (el, name) => {
                    if (!el) return;
                    const r = el.getBoundingClientRect();
                    boxes.push({name, x: r.x, y: r.y, w: r.width, h: r.height});
                };
                push(title, 'title');
                push(content, 'content');
                // "карточки" — только повторяющиеся визуальные единицы верхнего
                // уровня (metric-card/col-card/...); голый <li> учитывается,
                // ТОЛЬКО если он не вложен внутрь уже выбранной карточки —
                // иначе li внутри .col-card «перекрывает» свой же контейнер
                // и даёт ложные overlaps на каждом comparison-слайде.
                const cardSel = '.metric-card, .col-card, .step-card, .tl-card';
                const cardEls = Array.from(slide.querySelectorAll(cardSel));
                cardEls.forEach((c, i) => push(c, 'card' + i));
                if (cardEls.length === 0) {
                    slide.querySelectorAll('li').forEach((c, i) => push(c, 'card' + i));
                }
                return boxes;
            }""")
            results.append(data)
        browser.close()
    return results


def _overlaps(a: dict, b: dict) -> bool:
    ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return ox > 4 and oy > 4


def _fails(measure: dict, geometry: dict, is_dominant: bool) -> list[str]:
    """Вернуть список нарушений fit для одного слайда."""
    issues = []
    title = next((b for b in measure if b["name"] == "title"), None)
    content = next((b for b in measure if b["name"] == "content"), None)
    cards = [b for b in measure if b["name"].startswith("card")]

    if title and content and _overlaps(title, content):
        issues.append("title overlaps content")
    # пересечения между карточками
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            if _overlaps(cards[i], cards[j]):
                issues.append(f"card{i} overlaps card{j}")
    # заполненность контента (кроме dominant/climax — там воздух часть брифа)
    if content and not is_dominant:
        area = content["w"] * content["h"]
        slide_area = 1600 * 900
        fill = area / slide_area
        if fill < MIN_FILL:
            issues.append(f"content fill {fill:.0%} < {MIN_FILL:.0%}")
        if fill > MAX_FILL:
            issues.append(f"content fill {fill:.0%} > {MAX_FILL:.0%}")
    # перенос заголовка: короткий заголовок не должен падать в 3+ строки
    if title and geometry.get("title_word_count", 99) < 8:
        if title["h"] > 200:
            issues.append("short title wraps to 3+ lines — title_scale too big")
    return issues


def check_slide(html_fragment: str, geometry: dict, is_dominant: bool = False,
                base_css: str = "") -> tuple[bool, list[str]]:
    """Проверить fit одного слайда. True = помещается.

    base_css — реальный CSS деки (см. _render_and_measure); без него
    результаты недостоверны."""
    # слайд без контента вовсе (bridge/statement — только заголовок) — не
    # применяем MIN_FILL, пустота тут осознанная (см. content_profile: role=bridge)
    is_empty_by_design = not any(geometry.get(k, 0) for k in
                                 ("bullet_count", "metric_count", "column_count", "step_count"))
    measured = _render_and_measure([html_fragment], base_css=base_css)
    if not measured:
        return True, []  # нет playwright — пропускаем (не блокируем)
    fails = _fails(measured[0], geometry, is_dominant or is_empty_by_design)
    return (not fails, fails)


if __name__ == "__main__":
    print("fit_solver: модуль измерения геометрии (вызывается из build_html.py)")
