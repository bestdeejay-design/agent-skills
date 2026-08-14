"""Память скилла: сохранение удачных сборок как case для будущих пользователей.

После сборки презентация может быть сохранена как case: deck.json + выбранные
паттерны + стилевые решения. Следующие сборки могут сослаться на case как
референс (--pattern-from-case) или скилл накапливает проверенные композиции —
каждая дека может стать шаблоном для следующих.
"""
import json
import shutil
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CASES_DIR = SKILL_DIR / "examples" / "cases"


def save_case(name: str, deck_spec: dict, pattern_map: dict, source_html: Path | None = None) -> Path:
    """Сохранить deck.json + выбранные паттерны как case.

    name — короткое имя (например 'lovii-pitch'); deck_spec — deck.json;
    pattern_map — {slide_index: pattern_id}; source_html — опционально slides.html.
    Возвращает путь к сохранённому case.
    """
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in name.lower())
    case_dir = CASES_DIR / safe
    case_dir.mkdir(exist_ok=True)

    case = {
        "name": name,
        "saved": date.today().isoformat(),
        "title": deck_spec.get("title", ""),
        "style": deck_spec.get("style", {}),
        "theme": deck_spec.get("theme", {}).get("name", ""),
        "patterns": pattern_map,
        "slides": len(deck_spec.get("slides", [])),
    }
    (case_dir / "case.json").write_text(
        json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
    (case_dir / "deck.json").write_text(
        json.dumps(deck_spec, ensure_ascii=False, indent=2), encoding="utf-8")
    if source_html and source_html.exists():
        shutil.copy(source_html, case_dir / "slides.html")
    return case_dir


def list_cases() -> list:
    """Список сохранённых case (имя + заголовок + дата)."""
    if not CASES_DIR.is_dir():
        return []
    out = []
    for d in sorted(CASES_DIR.iterdir()):
        if d.is_dir() and (d / "case.json").exists():
            try:
                c = json.loads((d / "case.json").read_text(encoding="utf-8"))
                out.append({"name": c.get("name"), "title": c.get("title", ""),
                            "saved": c.get("saved", ""), "patterns": len(c.get("patterns", {}))})
            except Exception:
                continue
    return out
