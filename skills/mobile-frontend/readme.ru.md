# mobile-frontend

Композитный скилл для качественной мобильной вёрстки: правила (отступы, шрифты,
якоря, токены) → сборка → многоуровневая проверка с отладкой каждого элемента,
включая меню и навигацию → финальный аудит перед сдачей.

## Что внутри

- `SKILL.md` — воркфлоу из 6 уровней (Foundations → Build → Visual QA → Nav/Menu →
  Perf → Fix & re-verify) и критерии сдачи.
- `references/tokens.md` — мобильные токены: spacing 4/8-сетка, type-scale на
  `clamp()`, breakpoints, якоря (`scroll-margin-top`), safe-area, tap-target 44px.
- `references/mobile-checklist.md` — детальный чек-лист с JS-сниппетами для
  Playwright/Chromium (нет горизонтального скролла, tap-target, якоря, шрифты).
- `references/debug-menu-nav.md` — проигрыш отладки меню/навигации (9 типовых багов
  с симптомом → причиной → фиксом).

## Маршрутизация

Эстетика → `frontend-design-taste`; Lighthouse/контраст/a11y/токены →
`frontend-perfection`; скриншот-сверка → `/visual-qa`; общая оркестрация → `/frontend`.

## Быстрый старт

1. Заведите токены из `references/tokens.md` в `:root`.
2. Соберите mobile-first, прогоните уровни 0→4.
3. Отладьте меню/навигацию по `references/debug-menu-nav.md`.
4. Исправьте → перепроверьте → sign-off по критериям из `SKILL.md`.
