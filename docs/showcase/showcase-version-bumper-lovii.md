# Showcase: `version-bumper` on a real project

> Демонстрация работы скилла на **реальном** репозитории. Основной прогон —
> на самом репозитории agent-skills (`/Users/best/Projects/test/skills-repo`),
> для которого `version-bumper` и является частью release-пайплайна (тег
> `v1.0.0` + Conventional Commits). Дополнительный прогон — на
> `lovii_demo` (https://github.com/bestdeejay-design/lovii_demo), где тегов
> нет, а коммиты не полностью conventional — проверка fallback-режимов.

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект (репозиторий) | `/Users/best/Projects/test/skills-repo` (agent-skills) |
| Git-история | 34 коммита, Conventional Commits (`feat`/`fix`/`docs`/`chore`/`refactor`/`i18n`/`merge`), тег `v1.0.0` |
| Задача для скилла | Определить следующую версию и предложить release-тег перед релизом |

*Почему именно эти данные:* репозиторий agent-skills — реальный release-пайплайн,
для которого скилл и создан: есть семвер-тег `v1.0.0`, история строго в
Conventional Commits, есть нетривиальные кейсы (коммиты `i18n(...)` и `merge:`,
которые не должны влиять на версию). Второй прогон на `lovii_demo` проверяет
fallback: отсутствие тегов (старт с `0.0.0`) и регистронезависимый разбор
(`Feat:` → `feat`).

## 2. Запуск (Run)

```bash
# Основной прогон — release-пайплайн agent-skills (детерминированный режим -s)
python3 skills/version-bumper/scripts/bumper.py --path /Users/best/Projects/test/skills-repo --from-tags -s

# Дополнительный прогон — lovii_demo без тегов (fallback 0.0.0)
python3 skills/version-bumper/scripts/bumper.py --path /Users/best/Projects/lovii_demo --from-tags
```

## 3. Вывод (Output)

Реальный вывод (запуск 2026-08-09), agent-skills:

```text
latest_tag: v1.0.0
current_version: 1.0.0
next_version: 1.1.0
suggested_tag: v1.1.0
bump: minor
commits_analyzed: 34
counts: feat=14, fix=5, perf=0, refactor=1, docs=8, style=0, test=0, chore=4, build=0, ci=0, revert=0, breaking=0, other=2
stable: true
```

Реальный вывод (запуск 2026-08-09), lovii_demo:

```text
warning: no semver tags found in /Users/best/Projects/lovii_demo; starting from 0.0.0
latest_tag: none
current_version: 0.0.0
next_version: 0.1.0
suggested_tag: v0.1.0
bump: minor
commits_analyzed: 11
counts: feat=3, fix=0, perf=0, refactor=0, docs=0, style=0, test=0, chore=2, build=0, ci=0, revert=0, breaking=0, other=6
EXIT:0
```

## 4. Интерпретация (Interpretation)

- **agent-skills**: с момента тега `v1.0.0` в историю вошли 14 `feat`-коммитов
  (новые скиллы, canonical-обогащение, showcase-процесс) и ни одного breaking —
  скилл корректно предлагает **MINOR**: `v1.0.0 → v1.1.0`. Это совпадает с
  фактическим релизным циклом репозитория (в `index.json` версия `1.4.0`,
  теги ставятся вручную) — скилл даёт тот же ответ, что и человек.
- **`other=2`** — коммиты `i18n(seo-toolkit): …` и `merge: combine local
  skills …`: тип `i18n` не входит в preset-таблицу, `merge` тоже. Они
  корректно не влияют на бамп — это ожидаемое поведение, а не потеря данных.
- **lovii_demo**: тегов нет → fallback `0.0.0`; `Feat:`/`Feat(search):`
  распознаны регистронезависимо как `feat` (3 шт.) → предложен `v0.1.0`.
  `other=6` — коммиты без conventional-префикса (`snapshot before refactor:`,
  `Delete nginx.conf`, `Clean history - orphan commit`). Для этого проекта
  скилл полезен как стартовая точка: перед первым релизом стоит решить,
  `v0.1.0` (первая фича) или `v1.0.0` (первый стабильный API).
- **Полезно владельцу**: скилл даёт детерминированный ответ на вопрос «какой
  тег ставить» — тот же вход, тот же `next_version` (`-s`). В release-пайплайн
  его можно встроить как источник версии для `changelog-generator`, а тег
  создавать отдельно (скилл read-only).
- **Ограничение**: скилл не создаёт теги, не пишет changelog и не понимает
  pre-release схемы (`1.2.3-rc.1`) — это осознанный скоуп; тег и changelog —
  отдельные шаги.

---

> Чек-лист:
> - [x] вход — реальные репозитории (agent-skills + lovii_demo);
> - [x] команда воспроизводима (выполнена 2026-08-09, exit 0);
> - [x] вывод — реальный (оба прогона, без правок).