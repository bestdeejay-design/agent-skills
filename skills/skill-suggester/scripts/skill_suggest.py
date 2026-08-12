#!/usr/bin/env python3
"""skill_suggest.py — подбор скиллов из библиотеки agent-skills по запросу.

Загружает index.json из мастер-каталога (по умолчанию ~/Projects/agent-skills/index.json или env AGENT_SKILLS_INDEX), читает у каждого скилла поля
triggers и description, нормализует запрос и скорит совпадения:
  - совпадение триггера (фраза или слово) → вес 3
  - совпадение слова из описания          → вес 1

Печатает топ-5: "rank. skill-name (score) — короткое обоснование".
Флаг --combo выводит цепочку из 2-3 скиллов для многоэтапной задачи.

Примеры:
  python3 skills/skill-suggester/scripts/skill_suggest.py "нужно описать репозиторий"
  python3 skills/skill-suggester/scripts/skill_suggest.py "сгенерируй презентацию" --combo
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
SCRIPT_DEFAULT = os.path.join(REPO_ROOT, "index.json")
MASTER_INDEX = os.path.expanduser("~/Projects/agent-skills/index.json")


def resolve_index() -> str:
    """Locate the master catalog index.json.

    Priority:
      1. env AGENT_SKILLS_INDEX (explicit override)
      2. ~/Projects/agent-skills/index.json (master repo, works when installed standalone)
      3. script-relative repo root (fallback for the agent-skills repo itself)
    """
    env = os.environ.get("AGENT_SKILLS_INDEX")
    if env and os.path.isfile(env):
        return env
    if os.path.isfile(MASTER_INDEX):
        return MASTER_INDEX
    return SCRIPT_DEFAULT

# Стоп-слова RU/EN — не несут смысла для скоринга.
STOPWORDS = {
    # русские
    "и", "в", "во", "на", "с", "со", "по", "для", "из", "за", "у", "об", "к",
    "ко", "до", "не", "ни", "но", "же", "я", "что", "как", "это", "тот", "эта",
    "эти", "все", "всё", "весь", "вся", "нужно", "надо", "хочу", "сделать",
    "сделай", "создать", "создай", "подскажи", "подсказать", "помоги", "помочь",
    "какой", "какая", "какие", "какое", "каких", "каким", "какую", "есть",
    "быть", "будет", "можно", "мой", "моя", "моё", "твой", "свой", "очень",
    "просто", "только", "также", "ещё", "уже", "при", "через", "теперь", "под",
    "над", "между", "после", "перед", "вместо", "чтобы", "если", "когда",
    # английские
    "a", "an", "the", "and", "or", "but", "for", "to", "of", "in", "on", "at",
    "with", "by", "from", "up", "down", "into", "over", "after", "before",
    "i", "you", "he", "she", "it", "we", "they", "me", "my", "your", "our",
    "this", "that", "these", "those", "is", "are", "was", "were", "be", "been",
    "do", "does", "did", "have", "has", "had", "will", "would", "can", "could",
    "should", "want", "make", "create", "help", "please", "how", "what",
    "where", "when", "why", "some", "any", "all", "each", "more", "most",
    "other", "such", "just", "very", "also", "now", "so", "if", "then", "not",
    "no", "need", "use", "using", "used",
}


def normalize(text: str) -> list[str]:
    """Нижний регистр, убрать пунктуацию, разбить на слова."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", " ", text, flags=re.UNICODE)
    return [w for w in text.split() if w]


def load_index(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Не удалось прочитать index.json ({path}): {e}", file=sys.stderr)
        sys.exit(1)


def score_skill(skill: dict, query_words: list[str], query_text: str) -> tuple[int, list[str]]:
    """Скорит скилл: триггеры (вес 3), слова описания (вес 1)."""
    score = 0
    reasons: list[str] = []

    for trig in skill.get("triggers", []):
        trig_words = normalize(trig)
        if not trig_words:
            continue
        phrase = " ".join(trig_words)
        if phrase in query_text:
            score += 3
            reasons.append(f"триггер «{trig}»")
        elif any(w in query_words for w in trig_words):
            score += 3
            reasons.append(f"триггер «{trig}»")

    desc_words = {w for w in normalize(skill.get("description", "")) if w not in STOPWORDS}
    for w in query_words:
        if w in desc_words:
            score += 1
            reasons.append(f"слово описания «{w}»")

    return score, reasons


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Подбор скиллов из библиотеки agent-skills по запросу."
    )
    parser.add_argument("query", nargs="?", default="",
                        help="описание задачи свободным текстом")
    parser.add_argument("--index", default=resolve_index(),
                        help="путь к index.json (по умолчанию мастер-каталог agent-skills)")
    parser.add_argument("--combo", action="store_true",
                        help="вывести цепочку из 2-3 скиллов для многоэтапной задачи")
    parser.add_argument("--top", type=int, default=5,
                        help="сколько скиллов вывести (по умолчанию 5)")
    args = parser.parse_args()

    query = args.query.strip()
    if not query:
        parser.print_help()
        sys.exit(1)

    index = load_index(args.index)
    skills = index.get("skills", [])
    if not skills:
        print("❌ В index.json нет ни одного скилла.", file=sys.stderr)
        sys.exit(1)

    query_all = normalize(query)
    query_text = " ".join(query_all)
    query_words = [w for w in query_all if w not in STOPWORDS]

    ranked = []
    for skill in skills:
        score, reasons = score_skill(skill, query_words, query_text)
        if score > 0:
            ranked.append((score, skill, reasons))

    ranked.sort(key=lambda x: (-x[0], x[1]["name"]))
    top = ranked[: args.top]

    if not top:
        print(f"😕 Ничего не нашлось по запросу «{query}». Попробуйте переформулировать.")
        print("Доступные скиллы библиотеки:")
        for s in sorted(skills, key=lambda x: x["name"]):
            print(f"  • {s['name']} — {s.get('description', '')[:90]}")
        sys.exit(0)

    print(f"Запрос: «{query}»")
    print(f"Найдено совпадений: {len(ranked)}. Топ-{len(top)}:\n")
    for i, (score, skill, reasons) in enumerate(top, start=1):
        why = "; ".join(dedupe(reasons)[:3]) if reasons else "совпадение по описанию"
        print(f"{i}. {skill['name']} ({score}) — {why}")

    index_dir = os.path.dirname(os.path.abspath(args.index))
    print("\n📄 Ad-hoc apply: если скилл не установлен — прочитай его SKILL.md из мастер-каталога:")
    for _, skill, _ in top:
        rel = skill.get("path", f"skills/{skill['name']}")
        p = os.path.join(index_dir, rel, "SKILL.md")
        print(f"   {skill['name']}: {p}")

    if args.combo and len(top) >= 2:
        chain = top[: min(3, len(top))]
        print("\n🔗 Комбо (цепочка для многоэтапной работы):")
        print("   " + " → ".join(s["name"] for _, s, _ in chain))
        for i, (_, s, _) in enumerate(chain, start=1):
            print(f"   {i}. {s['name']}: {s.get('description', '')[:100]}")


if __name__ == "__main__":
    main()