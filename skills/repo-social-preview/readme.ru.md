# repo-social-preview (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** генерация кастомного social preview (og:image) репозитория — PNG
1280×640 с хедер-композицией и волнами. GitHub генерирует превью автоматически, но
кастомное даёт брендированную картинку для соцсетей.

**Скрипт:** `generate_social_preview.py` (требует `pip install pillow`).

**Требования GitHub:** файл в корне / `docs/` / default-ветке; PNG/JPG/GIF; < 1 МБ;
≥ 640×320, рекомендовано 1280×640. Установка — только через UI: Settings → Social
preview → Edit → Upload (API нет). Прозрачность поддерживается, но сплошной фон
рекомендуется.

**Когда применять:** нужен брендированный social preview; просят «social preview»,
«og image», «repo preview png».

**Не применять:** для README/визуального оформления — `repo-readme-assets`; для
легальных/community-файлов — `repo-community-files`; для метаданных/health —
`repo-metadata-health`.
