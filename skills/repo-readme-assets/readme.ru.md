# repo-readme-assets (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** создание и обновление `README.md` (английская версия) + локализованного
зеркала (например `README.ru.md`) + локальных анимированных SVG-шапки и подвала
репозитория (`assets/header.svg`, `assets/footer.svg`).

**Принцип: ноль внешних сервисов.** Никаких `capsule-render`, `shields`-генераторов и
URL-баннеров. Анимация — только SMIL (`<animate>`, `<animateTransform>`), работает в
`<img>` на GitHub без скриптов и сети.

**Скрипты:**
- `generate_assets.py` — детерминированная генерация header/footer (4 пресета: default / minimal / dark-first / monochrome).
- `extract_context.py` — авто-детект имени/описания/стека/цветов/username из git remote.
- `validate_svg.py` — валидация SVG по правилам скилла (SMIL, маска, морфинг d-path).

**Когда применять:** нужен README с шапкой/подвалом; мажорное изменение и README надо
актуализировать; просят «анимированный svg», «шапка readme», «waving svg».

**Не применять:** README уже актуален и правок не просили; нужен точечный фикс бейджа;
нужны легальные файлы (LICENSE/CONTRIBUTING/SECURITY) — это `repo-community-files`;
нужно описание/topics/Pages/community health — это `repo-metadata-health`; нужен social
preview PNG — это `repo-social-preview`.
