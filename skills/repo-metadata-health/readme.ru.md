# repo-metadata-health (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** аудит и обновление метаданных и community-здоровья репозитория на
GitHub: description, topics, ссылка на GitHub Pages + homepage в About, процент
«Community Health» (Community Profile API), а также прогон 16-пунктового чек-листа.

**Скрипт:** `validate_repo.py` — 16-пунктовый чек-лист через `gh api` + filesystem,
с авто-детектом репозитория из git remote.

**Когда применять:** устарели description/topics после мажорного изменения; нужен аудит
community health; нужно завести ссылку на GitHub Pages; просят «repo description»,
«topics», «github pages», «community health», «repo audit».

**Ключевое:**
- description — до ~350 символов, перечислять ВСЕ значимые компоненты;
- topics — максимум 20, ≤50 символов, только lowercase/цифры/дефисы, замена списка
  только через PUT;
- Pages включён → ссылка в README + homepage в About.

**Не применять:** для README/визуального оформления — `repo-readme-assets`; для
легальных/community-файлов — `repo-community-files`; для social preview PNG —
`repo-social-preview`.
