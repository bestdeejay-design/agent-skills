# repo-community-files (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** создание и сопровождение легальных/community-файлов репозитория:
`LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`,
issue/PR-шаблонов, `FUNDING.yml`. Без скриптов — шаблонно.

**Зачем:** эти файлы закрывают чек-лист GitHub «Community Standards» (метрика
`health_percentage`). Отсутствие файлов снижает оценку и мешает контрибьюторам.

**Когда применять:** новый репозиторий; файл отсутствует/устарел; просят «license»,
«contributing», «security policy», «issue template».

**Не применять:** для README/визуального оформления — `repo-readme-assets`; для
описания/topics/Pages/аудита — `repo-metadata-health`; для social preview PNG —
`repo-social-preview`.

**Важно:** `LICENSE` нельзя класть в `.github/` — GitHub распознаёт её только в корне
или `docs/`. На уровне org поддерживаются default-файлы через спецрепозиторий `.github`,
но `LICENSE` не наследуется.
