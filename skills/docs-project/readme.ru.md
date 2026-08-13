# docs-project (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** проектная (инженерная) ветка документации — «как»: README,
ENTRY, ранбуки AGENT/DELIVERY, `docs/` (карта REFERENCE, ARCHITECTURE, ADR,
SAGA, TEST_CASES, DEV_GUIDE, IMPROVEMENTS, TROUBLESHOOTING, BACKLOG, REVIEW,
STATUS) и `contracts/` (OpenAPI/AsyncAPI — «machine truth before code»,
контракты пишутся ДО кода).

**Правило карты:** у каждого документа есть карточка в `REFERENCE.md`
(назначение → структура → факты → ссылки); пишется последним, обновляется при
каждом изменении.

**Когда применять:** просят «проектную/инженерную документацию», «архитектуру»,
«adr», «контракты openapi».

**Не применять:** для продуктовой ветки — `docs-product`; для мета-гайда
(фазы/уровни/полнота) — `docs-system`.

**Шаблоны:** `templates/project/*.tmpl` (14 шт). Каталог и чек-лист —
`references/project-docs.md`.
