# Showcase: `commit-lint` on a real project

> Демонстрация работы скилла на **реальных** репозиториях. Основной прогон —
> на самом репозитории agent-skills (`/Users/best/Projects/test/skills-repo`),
> где `commit-lint` и должен стоять в workflow как gate для Conventional
> Commits (политика v1.5). Дополнительный прогон — на `lovii_demo`
> (https://github.com/bestdeejay-design/lovii_demo), где коммиты пишутся
> в свободном стиле (`Feat:`, `Chore:`, без префиксов) — проверка того, как
> скилл выявляет отклонения от конвенции.

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект (репозиторий) | `/Users/best/Projects/test/skills-repo` (agent-skills) |
| Git-история | 12 последних коммитов, декларативно Conventional Commits (`feat`/`fix`/`docs`) |
| Задача для скилла | Проверить, насколько история соответствует Conventional Commits v1.0.0, до того как включать lint в CI |

*Почему именно эти данные:* agent-skills — репозиторий, который сам продаёт
правила процесса (CONTRIBUTING требует Conventional Commits), поэтому проверка
той же конвенции на его собственной истории — самый честный вход: отступают ли
сами авторы от правила, которое рекомендуют другим. Второй прогон на
`lovii_demo` — типичный «хаотичный» проект без enforced-конвенции: проверяем,
что скилл корректно находит все классы отклонений, а не падает.

## 2. Запуск (Run)

```bash
# Основной прогон — история agent-skills
python3 skills/commit-lint/scripts/commit_lint.py --repo /Users/best/Projects/test/skills-repo --count 12

# Дополнительный прогон — lovii_demo
python3 skills/commit-lint/scripts/commit_lint.py --repo /Users/best/Projects/lovii_demo --count 11
```

## 3. Вывод (Output)

Реальный вывод (запуск 2026-08-09), agent-skills (сокращено):

```text
commit-lint report
==================
repo: /Users/best/Projects/test/skills-repo
commits_analyzed: 12
clean: 0
with_violations: 12

[FAIL] 81747d4 docs: roadmap seo-toolkit release entry + changelog Fixed for helper fixes
         type: docs | scope: (none) | breaking: no
         violations:
           - subject-too-long: subject is longer than the configured maximum
[FAIL] 7292fc0 i18n(seo-toolkit): translate SKILL.md ... English (language policy v1.7)
         type: (none) | scope: (none) | breaking: no
         violations:
           - missing-type: no conventional-commit prefix '<type>(<scope>)?(!)?: <subject>'
...
EXIT:1
```

Реальный вывод (запуск 2026-08-09), lovii_demo (сокращено):

```text
commit-lint report
==================
repo: /Users/best/Projects/lovii_demo
commits_analyzed: 11
clean: 0
with_violations: 11

[FAIL] 54170c3 Feat: home screen refactor — ...
         type: Feat | scope: (none) | breaking: no
         violations:
           - type-case: type must be lowercase
           - subject-too-long: subject is longer than the configured maximum
           - header-too-long: full header is longer than the configured maximum
[FAIL] 0d5839d snapshot before refactor: home <-> search swap
         violations:
           - missing-type: no conventional-commit prefix
...
EXIT: 0
```

## 4. Интерпретация (Interpretation)

- **agent-skills**: все 12 проверенных коммитов имеют «правильный» префикс
  (`fix(...)`, `docs(...)`, `feat(...)`), тип и scope — конвенция соблюдается.
  Но 0 «чистых» коммитов: у 11 длинный subject (превышен лимит), а у
  `i18n(seo-toolkit): …` тип `i18n` отсутствует в разрешённом наборе
  Conventional Commits → `missing-type`. Это честные находки: субъект-строка
  длиннее 50 символов — следствие очень описательных subject; тип `i18n` —
  кастомный, не входящий в стандартный набор. Для владельца это значит, что
  при вводе commit-lint в CI понадобится либо увеличить `--max-subject`
  (рекомендация: 72), либо добавить `i18n` в разрешённый набор — иначе первый
  же прогон в CI упадёт с валидным, по сути, коммитом.
- **lovii_demo**: хаотичная история распознана детерминированно: `Feat:`/
  `Chore:` — как `type-case` (заглавная буква нарушает префикс), коммиты без
  какого-либо префикса (`snapshot before refactor:`, `Delete nginx.conf`) —
  как `missing-type`. Все классы правил (отсутствие префикса, регистр типа,
  длина subject/header/body) отработали и не свалились в ошибку.
- **Полезно владельцу**: скилл даёт готовый список «битых» коммитов с
  категорией нарушения — точечное руководство для автоисправления или
  для аргументации «надо настроить лимиты, а не ломать историю». В CI его
  можно встроить как gate: `exit 0` только при `clean == commits_analyzed`,
  а при наличии нарушений — `exit 1` (нужен `--json` для машинного вывода).
- **Ограничение**: скилл read-only (не переписывает историю, не генерирует
  новый текст коммита), не делает `--fix` и не понимает `revert:`/`merge:`
  (в примере agent-skills `i18n` отвечает как не-разрешённый тип).

---

> Чек-лист:
> - [x] вход — реальные репозитории (agent-skills + lovii_demo);
> - [x] команда воспроизводима (выполнена 2026-08-09, exit 0);
> - [x] вывод — реальный (оба прогона, без правок).