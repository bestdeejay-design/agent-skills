# Community Health — чек-лист проверки

> Вынесено из SKILL.md. Запускать при: новый сервис/фича/сага, смена стека,
> смена портов/схем, изменение контрактов, изменение процессов (CI/коммиты),
> любой релиз/гейт, delivery gate.

## A. Файлы — на месте и распознаны GitHub

1. [ ] `README.md` отражает новое состояние (структура, сервисы, цифры тестов, статус).
2. [ ] `README.<lang>.md` синхронизирован с англ. версией (заголовки 1:1).
3. [ ] `LICENSE` на месте, owner/year корректны, GitHub **распознаёт** лицензию (`spdx_id`).
4. [ ] `CODE_OF_CONDUCT.md` — полный текст Contributor Covenant 2.1 с контактом;
      GitHub **распознаёт** как Covenant (`key: contributor_covenant`, **не** `other`).
5. [ ] `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md` (имя строго в upper-case).
6. [ ] `.github/ISSUE_TEMPLATE/` (bug_report + feature_request, forms yml) и
      `.github/pull_request_template.md` на месте с валидным frontmatter
      (`name`+`about` для `.md`, `name`+`description` для `.yml`).

## B. Метаданные GitHub

7. [ ] `gh repo edit --description` актуально, перечисляет ВСЕ компоненты (≤350 символов на UI).
8. [ ] topics (`gh api .../topics`) актуальны, ≤ 20, lowercase, ≤ 50 символов каждый.
9. [ ] Homepage (`gh repo edit --homepage https://<user>.github.io/<repo>/`) — при Pages; рабочая ссылка.
10. [ ] Social preview задан (1280×640, < 1 MB) — если есть Settings.
11. [ ] CI-бейдж/статус в README соответствует реальному состоянию (не stale).

## C. Community Health

12. [ ] `gh api repos/<owner>/<repo>/community/profile` → `health_percentage >= 100`,
      `files.issue_template` и `files.pull_request_template` не `null`.
13. [ ] `has_discussions` желательно `true` (Discussions включены) для вопросов.

## D. Релизы

14. [ ] Существует релиз с semver-тегом (последний «latest»), `.github/release.yml` настроен.
15. [ ] `CHANGELOG.md` (Keep a Changelog) обновлён под новый релиз.

## E. Финальная

16. [ ] Коммит/пуш сделан, изменения видны на GitHub; CI зелёный.

## Автопроверка

Автоматизированная версия пунктов — `python3 scripts/validate_repo.py` (JSON-отчёт,
exit 0/1). Скрипт покрывает все пункты, которые можно проверить без UI; пункты
10 (social preview) и 11 (CI-бейдж) — только предупреждения.

## Команды проверки

```bash
# Файлы на месте
ls LICENSE CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md SUPPORT.md README.md README.ru.md

# Описание + homepage + темы
gh repo view --json description,homepageUrl,repositoryTopics

# Теги
gh api repos/<owner>/<repo>/topics

# Pages
gh api repos/<owner>/<repo>/pages

# Community health (!!) — самый информативный чек
gh api repos/<owner>/<repo>/community/profile

# Распознавание лицензии и CoC (ключи)
gh api repos/<owner>/<repo>/community-enabled   # или /community/get
```

Замена отображения в WEB-интерфейсе (бейджи, community health %) занимает
1–5 минут после пуша — проверять не сразу после коммита, а с небольшой паузой.