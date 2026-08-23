# Mobile Checklist (детальный, по уровням)

Каждый пункт — бинарный ✅/❌. Уровень пройден, только если все пункты зелёные.
Скрипты запускаются в браузере (Playwright/Chromium) на нужном вьюпорте.

## Уровень 0 — Foundations

- [ ] `viewport` мета: `width=device-width, initial-scale=1, viewport-fit=cover`
- [ ] `:root` содержит токены (spacing/type/breakpoints/--header-h/safe-area)
- [ ] Все цвета и отступы — через переменные (нет «голых» hex в правилах, кроме transparent/currentColor)
- [ ] Якорные секции имеют `id`, задан `scroll-margin-top`

## Уровень 1 — Build

- [ ] Mobile-first: базовые стили мобильные, расширения через `min-width`
- [ ] Контейнер: `max-width` + боковой `padding` (--content-px), нет фикс. ширин блоков
- [ ] Картинки: `width:100%; height:auto; loading="lazy"; decoding="async"` (+srcset при наличии)
- [ ] Интерактивы ≥ 44px по меньшей стороне
- [ ] `font-display: swap` на всех шрифтах; body ≥ 16px

## Уровень 2 — Visual QA (320 / 360 / 390 / 414 / 768)

Для каждого вьюпорта:

- [ ] **Нет горизонтального скролла:**
  ```js
  const o = document.documentElement;
  return o.scrollWidth <= o.clientWidth;
  ```
- [ ] **Tap-target ≥ 44px** (все `<a>/<button>`):
  ```js
  [...document.querySelectorAll('a,button')].filter(el=>{
    const r = el.getBoundingClientRect();
    return r.width>0 && (r.width<44 || r.height<44);
  }).map(el=>el.outerHTML); // должен вернуть []
  ```
- [ ] **Шрифты загрузились:**
  ```js
  await document.fonts.ready; return document.fonts.status === 'loaded';
  ```
- [ ] **Safe-area:** нижний CTA/меню не перекрывается home-indicator
  (`getComputedStyle(el).paddingBottom` включает `env(safe-area-inset-bottom)`)
- [ ] **Якоря под шапкой:**
  ```js
  const h = document.querySelector('header'); const hb = h.getBoundingClientRect().bottom;
  const t = document.querySelector('#target'); t.scrollIntoView();
  return t.getBoundingClientRect().top >= hb - 1;
  ```
- [ ] Скриншот сохранён и визуально сверен (`/visual-qa`, `frontend-design-taste`)

## Уровень 3 — Nav & Menu (см. debug-menu-nav.md)

- [ ] Гамбургер переключает меню; `aria-expanded` синхронен
- [ ] Пункт меню ведёт на цель И закрывает меню
- [ ] Фокус-ловушка в открытом меню; `Esc` закрывает
- [ ] Якорные/глубокие ссылки скроллятся под шапку
- [ ] `Tab`-порядок логичен; `:focus-visible` видим
- [ ] `z-index`: меню выше контента/шапки, ниже модалок

## Уровень 4 — Perf (mobile Lighthouse через frontend-perfection)

- [ ] CLS < 0.1
- [ ] LCP < 2.5s
- [ ] INP < 200ms
- [ ] Нет блокирующего рендер CSS/JS

## Уровень 5 — Fix & re-verify

- [ ] Правки внесены по уровням (2→3→4)
- [ ] Затронутые уровни перепроверены → зелёные
- [ ] Sign-off по критериям из SKILL.md
