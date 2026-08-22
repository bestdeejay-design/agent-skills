# repo-social-preview (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** кастомный social preview (og:image) репозитория — PNG 1280×640.
Превью **верстается как HTML hero-секция** и рендерится в PNG через headless
Chrome. Ничего не рисуем сами (ни Pillow-композиций, ни SVG), сайт не скриншотим:
если у проекта есть hero — перевёрстываем её начисто, только hero без хедера,
футера и бейджей, с `padding: 40pt` (crop-safe зона GitHub).

**Скрипт:** `render_social_preview.py` — HTML → PNG через headless Chrome/Chromium.

**Требования GitHub:** файл в корне / `docs/` / default-ветке; PNG/JPG/GIF; < 1 МБ;
≥ 640×320, рекомендовано 1280×640. Установка — только через UI: Settings → Social
preview → Edit → Upload (API нет). Сплошной фон рекомендуется.

**Когда применять:** нужен брендированный social preview; просят «social preview»,
«og image», «repo preview png».

**Не применять:** для README/визуального оформления — `repo-readme-assets`; для
легальных/community-файлов — `repo-community-files`; для метаданных/health —
`repo-metadata-health`.
