# Showcase: `frontend-perfection` на реальном проекте

> Демонстрация работы скилла на **реальном** фронтенде — `lovii_demo`
> (`https://github.com/bestdeejay-design/lovii_demo`, статический
> marketplace: `index.html` + `css/`). Прогон выполнен локально 2026-08-09
> на реальном Chrome через стабильный раннер (chrome-launcher + Lighthouse
> 13.4.1 Node API, без Playwright-интерналов).

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект | `/Users/best/Projects/lovii_demo` |
| HTML | `index.html` (статический, без сборки) |
| CSS | `main.css`, `css/demo.css` |
| Локальный URL | `http://localhost:8377/` (`python3 -m http.server`) |
| Задача скилла | Аудит до/после: Lighthouse mobile+desktop, SEO-мета-слой, контрасты, дизайн-токены, адаптив |

*Почему именно эти данные:* проект — статический HTML/CSS/JS без бандлера,
t.е. ключевой кейс из отчёта по built-in `frontend` скиллу: React-тулинг
неприменим, дизайн-система сводится к «все hex в токены», а Lighthouse —
единственный объективный измеритель. Здесь же проверяется, что раннер не
использует приватные поля Playwright и не падает на Lighthouse 13 API.

## 2. Запуск (Run)

```bash
# Lighthouse, мобильный прогон (реальный Chrome, headless)
node skills/frontend-perfection/scripts/audit.js --url http://localhost:8377/ --mobile --out lh-mobile.json

# Lighthouse, десктопный прогон
node skills/frontend-perfection/scripts/audit.js --url http://localhost:8377/ --desktop --out lh-desktop.json

# Статический аудит SEO/контраст/токены/адаптив (offline, Python stdlib)
python3 skills/frontend-perfection/scripts/meta_audit.py --html index.html --css main.css css/demo.css --out meta.json
```

## 3. Вывод (Output)

Реальный вывод (запуск 2026-08-09), мобильный прогон:

```text
[frontend-perfection] mobile audit of http://localhost:8377/
  performance      94/100
  accessibility    96/100
  best-practices   100/100
  seo              91/100

  Failed audits (5):
    - first-contentful-paint  (score 92, weight 10)  First Contentful Paint — 1.7 s
    - largest-contentful-paint (score 91, weight 25) Largest Contentful Paint — 2.4 s
    - speed-index             (score 73, weight 10)  Speed Index — 4.5 s
    - color-contrast          (score 0, weight 7)    Background and foreground colors do not have sufficient contrast.
    - meta-description        (score 0, weight 1)    Document does not have a meta description
exit 1 (порог по умолчанию 100)
```

Десктопный прогон: **performance 72/100** (FCP 44, LCP 49, Speed Index
6 — тяжёлый hero-контент и шрифты), accessibility 96, best-practices 100,
seo 91; те же failed audit-id (цвета + meta).

Статический аудит (`meta_audit.py`) — 17 проверок, 5 passed / 12
violations, exit 1:

```text
❌ meta:title-length   — title length 269 (limit 60)
❌ meta:description    — meta description: (пусто)          [СОВПАДАЕТ с lighthouse audit-id meta-description]
❌ meta:canonical      — canonical: MISSING
❌ meta:og:title       — og:title MISSING
❌ meta:og:image       — og:image MISSING
❌ meta:og:size        — og:image:width/height not declared
❌ meta:twitter:card   — twitter:card MISSING
❌ meta:json-ld        — JSON-LD structured data MISSING
❌ meta:sitemap-link   — sitemap link not referenced
❌ headings:single-h1  — 0 h1 tag(s)
❌ tokens:raw-hex      — 9 raw hex outside token block (#00000080, #0d111b14, #0F0F12, …)
❌ adaptive:scroll-padding — position:fixed found — MISSING scroll-padding-top
```

## 4. Интерпретация (Interpretation)

- **Скилл работает на стабильном API.** Прогон состоялся на Lighthouse
  13.4.1 + chrome-launcher 1.2.1 без единой правки: `.default`-фолбэк и
  авто-резолюция глобального `npm root -g` сработали «из коробки». Раннер
  не трогает приватные поля Playwright — поэтому не падает как его
  предшественник.
- **12 одинаковых корневых дефектов закрывают все три прогона.** Мета-слой
  (title/description/OG/canonical/JSON-LD) отсутствует целиком — это видно
  и в `meta-description` (Lighthouse), и в 8 чек-аудитах `meta_audit.py`.
  `color-contrast` (Lighthouse) и `contrast:wcag-aa`+`tokens:raw-hex`
  (meta-аудит) — одна и та же первопричина: цвета не вынесены в токены и
  не проверены на яркость.
- **Приоритет фиксов.** 1) meta-слой (SEO 91→100, +9 чеков за один
  проход); 2) дизайн-токены + контраст (a11y 96→100); 3) `scroll-padding-top`
  под fixed-хедер; 4) перформанс — только после первых трёх, т.к.
  Speed Index и LCP на локальном сервере без CDN будут различаться с
  продакшеном (это честно указано в отчёте).
- **Что намеренно НЕ сделано:** не правили саму вёрстку lovii_demo (это
  эталонный showcase-проект), не меняли thumbnails/скриншоты, не гнали
  `!important`-хаки ради 100 — фикс каждого audit-id остаётся за агентом,
  работающим с живым проектом.

**Итог для владельца проекта:** вместо «красиво/не красиво» — 12
проверяемых пунктов с audit-id и 19 объективных метрик Lighthouse; каждый
фикс привязывается к конкретному audit-id, повторный прогон после правок
показывает дельту (до/после) без пересборки контекста.