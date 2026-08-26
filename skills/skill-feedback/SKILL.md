---
name: skill-feedback
description: "Capture and aggregate usage feedback for Agent Skills so the Skill Quality Gate loop can improve them over time. Use when a skill triggered wrongly, failed to trigger on a relevant request (near-miss), produced a wrong or broken output, or the user manually corrected its result. Writes structured entries to feedback/<skill>/YYYY-MM-DD.jsonl and can summarize them into a report that feeds skill-forge's Optimize-description step."
when_to_use: "Use when: a skill fired but was wrong; a request should have triggered a skill but did not (near-miss); the user edited or corrected a skill's output; you want to review accumulated skill feedback. Examples: 'запомни: запрос X должен был вызвать скилл Y', 'добавь фидбек по skill-forge', 'покажи накопленный фидбек по скиллам', 'этот вывод скилла неверный — запиши'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib only; no third-party packages"
---

# Skill Feedback — capture the fuel for skill improvement

This skill closes the loop opened by `docs/SKILL_QUALITY_GATE.md`. The Quality
Gate tells you *whether* a skill is good; this skill tells you *how to make it
better next time* by recording what happened in real usage and turning it into
a feed for `skill-forge`.

Without a feedback capture, improvement is guesswork. With it, every near-miss
trigger and every manual correction becomes a concrete edit to a skill's
`description` / `when_to_use` / body.

## When to use

- A skill **should have triggered** but did not (near-miss): the user's request
  was in-scope but the auto-load missed it.
- A skill **triggered wrongly**: the wrong skill loaded for the request.
- A skill produced a **wrong / broken / low-quality** output.
- The user **manually corrected** the skill's output (edited the result, or
  told you "no, do it differently").
- You want to **review** what has piled up before running `skill-forge`.

## DO NOT USE FOR

- General chat feedback, venting, or notes unrelated to a specific skill —
  those belong in memory or the session log, not the skill feedback store.
- Capturing secrets or personal data — never log credentials or PII in entries.

## Auto-capture (make it automatic)

For the loop to run without manual nudging, the agent should capture feedback
proactively. Installers: append the rule from `AGENTS_FRAGMENT.md` (repo root) to
your opencode `AGENTS.md`. Then any near-miss / manual correction is logged
automatically — no explicit "remember this" needed. Each consumer grows their own
skills locally; see `docs/SKILL_QUALITY_GATE.md` Layer C.

## How feedback is stored

Each entry is one JSON object on its own line in:

```
feedback/<skill-name>/YYYY-MM-DD.jsonl
```

Entry schema:

```json
{
  "ts": "2026-08-26T14:03:00",
  "skill": "api-contract-testing",
  "type": "near_miss_trigger",
  "request": "проверь, что эндпоинты совпадают со спецификацией",
  "detail": "skill did not auto-load; user had to invoke it manually",
  "suggested_fix": "add casual-phrasing trigger 'проверь эндпоинты' to when_to_use",
  "source": "user"
}
```

`type` is one of: `near_miss_trigger`, `wrong_trigger`, `output_issue`,
`manual_correction`, `description_gap`.

## The script

`scripts/feedback.py` — pure Python 3 stdlib.

| Command | Effect |
|---|---|
| `python3 feedback.py add --skill NAME --type TYPE --request "..." --detail "..." [--fix "..."]` | append one entry |
| `python3 feedback.py report [--skill NAME]` | aggregate counts by skill+type, list recent near-miss `request` strings (the exact fuel for trigger optimization) |
| `python3 feedback.py export [--skill NAME]` | emit a prompt-ready digest for the `skill-forge` Improve / Optimize-description steps |

## How it feeds the loop

1. During/after a session, capture near-misses and corrections via `add` (or ask
   the user "should I log this as skill feedback?").
2. Before improving a skill, run `report` to see its accumulated issues.
3. Feed the near-miss `request` strings into `skill-forge`'s *Optimize
   description* (they become the missing trigger queries); feed
   `manual_correction` `suggested_fix` into the *Improve* step.
4. Re-run the Layer A/B audit (the `docs/skill-quality-audit.md` generator) to confirm
   the edit moved the needle.
5. Commit the skill change — and optionally the feedback store — so the loop is
   reproducible.

## Privacy & hygiene

- The store lives in the repo under `feedback/`. Commit it only if you want the
  history shared; otherwise gitignore it.
- Never put secrets, tokens, or personal data in `request` / `detail`.
- Keep entries factual and short; one issue per entry.
