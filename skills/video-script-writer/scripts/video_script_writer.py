#!/usr/bin/env python3
"""video_script_writer.py — генерация структурированного сценария видео.

Строит markdown-сценарий из темы: HOOK (захват, первые секунды), BODY
(сцены с тайм-слотами), CTA (призыв к действию). Вывод полный или outline.

Примеры:
  python3 video_script_writer.py --topic "Как собрать презентацию за 20 минут"
  python3 video_script_writer.py --topic "MCP for agents" --duration 90 --lang en
  python3 video_script_writer.py --topic "Отчёт в PDF" --format outline
"""

import argparse
import sys

HOOK_POOL = {
    "ru": [
        "Смотри, как {topic} делается за минуту — без лишней теории.",
        "Главная ошибка новичков при теме {topic} — начинают не с того конца.",
        "Хочешь, чтобы про {topic} досмотрели до конца? Начни с захватывающих трёх секунд.",
    ],
    "en": [
        "Here's how {topic} works in 60 seconds — skip the theory.",
        "Most people get {topic} wrong right at the start. Avoid it.",
        "Want a video on {topic} people actually finish? Nail the first 3 seconds.",
    ],
}

BODY_BEATS = {
    "ru": [
        ("Проблема", "почему это сложно и где болит"),
        ("Основы", "ключевые термины и минимум базы"),
        ("Разбор", "пошаговый пример с экраном"),
        ("Ошибки", "две-три типичные ошибки и как их избежать"),
        ("Совет", "одна техника, которая сразу усиливает результат"),
    ],
    "en": [
        ("Problem", "why this hurts and why it feels hard"),
        ("Basics", "core terms and the minimal foundation"),
        ("Walkthrough", "step-by-step example, screen capture"),
        ("Pitfalls", "2–3 common mistakes and how to avoid them"),
        ("Pro tip", "one technique that multiplies the result"),
    ],
}


def _fmt(seconds: int) -> str:
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def build(topic: str, duration: int, lang: str, cta: str, scenes: int) -> str:
    hook_len = max(5, duration // 10)
    cta_len = max(5, duration // 8)
    body_start = hook_len
    body_end = duration - cta_len
    titles = BODY_BEATS[lang]
    seg = max(10, (body_end - body_start) // scenes)

    lines = [
        f"# 🎬 Сценарий: {topic}",
        "",
        f"- Язык: {lang} · Хронометраж: {duration}с ({_fmt(duration)}) · Сцен: {scenes}",
        "",
        "## 🪝 Hook (HOOK)",
        f"{_fmt(0)}–{_fmt(hook_len)} — захват внимания",
        HOOK_POOL[lang][scenes % len(HOOK_POOL[lang])].format(topic=topic),
        "",
        "## 🧩 Тело (BODY)",
    ]

    cursor = body_start
    for i in range(scenes):
        name, desc = titles[i % len(titles)]
        end = min(body_end, cursor + seg)
        lines.append(f"### Сцена {i + 1}: {name} — {_fmt(cursor)}–{_fmt(end)}")
        lines.append(f"- {desc}")
        lines.append(f"- Пример/демо: конкретный шаг, который зритель может повторить")
        lines.append("")
        cursor = end
    if cursor < body_end:
        lines.append(f"### Финальное резюме — {_fmt(cursor)}–{_fmt(body_end)}")
        lines.append("- Сжать ключевое из всех сцен в 2–3 предложения")
        lines.append("")

    lines.append(f"## 🎯 CTA (призыв) — {_fmt(body_end)}–{_fmt(duration)}")
    lines.append(cta)
    lines.append("")
    lines.append("## ⏱ Сводка таймкодов")
    lines.append("| Часть | Интервал |")
    lines.append("|-------|----------|")
    lines.append(f"| Hook | {_fmt(0)}–{_fmt(hook_len)} |")
    lines.append(f"| Body | {_fmt(body_start)}–{_fmt(body_end)} |")
    lines.append(f"| CTA | {_fmt(body_end)}–{_fmt(duration)} |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a structured video script")
    ap.add_argument("--topic", required=True, help="video topic")
    ap.add_argument("--duration", type=int, default=60, help="target duration in seconds")
    ap.add_argument("--lang", default="ru", choices=("ru", "en"))
    ap.add_argument("--cta", default=None, help="call-to-action phrase")
    ap.add_argument("--scene", type=int, default=5, help="number of body scenes (max 5)")
    ap.add_argument("--format", choices=("full", "outline"), default="full")
    ap.add_argument("-o", "--out", default=None, help="output file (default stdout)")
    args = ap.parse_args()

    scenes = max(1, min(5, args.scene))
    cta = args.cta or ("Подпишись и поставь лайк — следующее видео уже в работе."
                       if args.lang == "ru" else "Subscribe and like. Another video is in the works.")
    script = build(args.topic, max(30, args.duration), args.lang, cta, scenes)

    if args.format == "outline":
        keep = [l for l in script.splitlines() if l.startswith("## ") or l.startswith("### ")]
        if not keep:
            keep = ["## 🎝 Hook (HOOK)", "## 🧩 Тело (BODY)", "## 🎯 CTA"]
        script = f"# Outline: {args.topic}\n\n" + "\n".join(keep) + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"OK: {args.out}")
    else:
        sys.stdout.write(script + "\n")


if __name__ == "__main__":
    main()