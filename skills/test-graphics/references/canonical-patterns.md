# Canonical patterns: test-graphics

> Эталонные источники и пробелы текущего скилла относительно канонов.
> Обработка результатов librarian-исследования (август 2026).

---

## (a) Named analogues

| # | Name | Owner | URL | Type |
|---|------|-------|-----|------|
| 1 | DiceBear | dicebear | https://github.com/dicebear/dicebear | OSS библиотека + HTTP API + CLI |
| 2 | Playwright Test | microsoft | https://github.com/microsoft/playwright | Официальный e2e-фреймворк |
| 3 | SVGO | svg | https://github.com/svg/svgo | Официальная CLI + библиотека оптимизации SVG |
| 4 | Lucide | lucide-icons | https://github.com/lucide-icons/lucide | SVG-библиотека иконок с tree-shaking |
| 5 | Cypress | cypress-io | https://docs.cypress.io/api/commands/fixture | Официальная документация e2e-фреймворка |
| 6 | Storybook | storybookjs | https://storybook.js.org/docs/configure | Официальные docs (v10.5) |

---

## (b) Techniques the script is MISSING

| # | Technique / Source | What is missing in current skill |
|---|--------------------|----------------------------------|
| 1 | **Детерминированный seed → PRNG** (DiceBear `Fnv1a` → `Mulberry32`) | Сейчас генерация случайная; для e2e и визуальных диффов нужны воспроизводимые картинки. Канон: `Fnv1a` hash → `Mulberry32` PRNG: [Fnv1a.ts#L8-L16](https://github.com/dicebear/dicebear/blob/5f152c12b87f26f106adeb5b3f160c15e32ecc69/src/js/core/src/Prng/Fnv1a.ts#L8-L16) |
| 2 | **HTTP API с версионированием и rate limits** (DiceBear) | Нет обработки 429 (50 rps SVG / 10 rps растр), нет явного указания версии API (`10.x`), нет таблицы статусов сервисов (source.unsplash.com мёртв 503, loremflickr пережил блокировку, dummyimage жив). |
| 3 | **SVG-first подход + оптимизация** (SVGO `preset-default`) | Скилл генерирует SVG (placehold.co, DiceBear, Lucide), но не оптимизирует. Канон: `multipass`, `preset-default` (~30 плагинов), CLI `svgo -rf dir -o out`, datauri: [svgo-node.js#L83-L98](https://github.com/svg/svgo/blob/66d1495a22c01640acc593ca36e25d43e22d807f/lib/svgo-node.js#L83-L98) |
| 4 | **Tree-shaking иконок** (Lucide `createLucideIcon`) | Lucide использует фабрику компонентов + отдельные файлы на иконку → tree-shaking: [createLucideIcon.ts#L12-L31](https://github.com/lucide-icons/lucide/blob/113a3b1a3bda9a31d30f4b056cd434ce9462828e/packages/lucide-react/src/createLucideIcon.ts#L12-L31). Дефолтные атрибуты `stroke="currentColor"`, `fill="none"`, `strokeWidth=2`: [defaultAttributes.ts#L6-L10](https://github.com/lucide-icons/lucide/blob/113a3b1a3bda9a31d30f4b056cd434ce9462828e/packages/lucide-react/src/defaultAttributes.ts#L6-L10) |
| 5 | **Playwright fixtures + скриншот-сравнение** | Нет паттерна `test.extend({ scope: 'worker', auto: true })` для генерации placeholder-набора один раз на воркер; нет `toHaveScreenshot` с `maxDiffPixelRatio` (валидация 0..1): [toMatchSnapshot.ts#L260-L277](https://github.com/microsoft/playwright/blob/c973356ee9e3906260f60da5e3e04442e069a0d4/packages/playwright/src/matchers/toMatchSnapshot.ts#L260-L277), [валидация maxDiffPixelRatio #L138-L139](https://github.com/microsoft/playwright/blob/c973356ee9e3906260f60da5e3e04442e069a0d4/packages/playwright/src/matchers/toMatchSnapshot.ts#L138-L139). Нет `testInfo.attach` / `testInfo.outputPath()` для прикрепления артефактов. |
| 6 | **Cypress fixture-паттерн** | Нет: `cy.fixture('img.png')` → base64 по умолчанию, `cy.fixture('img.png', null)` → Buffer; `cy.intercept({fixture})` для перехвата изображений; кодировки и лимит ~100 MB через WebSocket. Docs: https://docs.cypress.io/api/commands/fixture |
| 7 | **Storybook staticDirs** | Нет паттерна `staticDirs: ['../public']` — placeholder-картинки как локальные статические ассеты вместо внешних URL (детерминированность, офлайн, без rate limits): https://storybook.js.org/docs/configure/integration/images-and-assets |
| 8 | **SVG-first подход** | SVG без лимитов и с CORS `*` у всех сервисов (проверено); скилл не отдаёт SVG как приоритетный формат. |
| 9 | **CLI для пакетной генерации** (DiceBear CLI) | Нет: `dicebear lorelei ./avatars --count 100 --format png --size 256 --json --exif`, `--optimize`/`--optimize-check` для CI. |
| 10 | **CORS/кэш/статус сервисов** | Нет таблицы: placehold.co (1209600s), picsum (no CORS header, no-cache), loremflickr (no-store, пережил блокировку Flickr 2024-12..2025-05), dicebear (31919000s, 50/10 rps), dummyimage (7776000s). source.unsplash.com мёртв (503) — замена Unsplash API. |
| 11 | **GitHub Actions upload-artifact** | Нет интеграции с CI: хранение скриншотов/артефактов через `actions/upload-artifact@v4`, `download-artifact@v5`, `retention-days`. Docs: https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/storing-and-sharing-data-from-a-workflow |
| 12 | **Percy / Chromatic** | Нет упоминания скриншот-сравнения как сервиса (Percy — BrowserStack, Chromatic — авторы Storybook). |

---

## (c) Citable CLI/API examples

```bash
# 1) DiceBear — детерминированный аватар через seed (API)
curl "https://api.dicebear.com/10.x/lorelei/svg?seed=user-42&size=256&backgroundType=solid&backgroundColor=fff" -o avatar.svg

# 2) DiceBear CLI — пакетная генерация
dicebear lorelei ./avatars --count 20 --format png --size 256 --json --exif

# 3) DiceBear — optimise check для CI
dicebear lorelei ./avatars --count 10 --format svg --optimize-check

# 4) picsum — конкретная картинка по seed
curl "https://picsum.photos/seed/abc123/800/600.jpg" -o photo.jpg

# 5) loremflickr — стабильный выбор через lock
curl "https://loremflickr.com/800/600/tech?lock=42" -o flickr.jpg

# 6) placehold.co — SVG с текстом и retina
curl "https://placehold.co/400x300@2x/svg?text=Test+Image&font=inter" -o ph.svg

# 7) Lucide — tree-shaking импорт (React)
# import { Home } from 'lucide-react';  // только Home попадёт в бандл

# 8) SVGO — оптимизация SVG
svgo -rf ./input-svgs -o ./optimised --multipass --config=svgo.config.mjs
# data:uri base64
svgo -i icon.svg --datauri=base64

# 9) Playwright — fixture для генерации placeholder (worker scope)
# test.extend({
#   placeholders: async ({}, use) => {
#     const images = await generatePlaceholders(); // один раз на воркер
#     await use(images);
#   },
#   { scope: 'worker', auto: true }
# });

# 10) Playwright — визуальное сравнение с threshold
# await expect(page).toHaveScreenshot('expected.png', { maxDiffPixelRatio: 0.01 });

# 11) Playwright — прикрепление артефакта к отчёту
# await testInfo.attach('generated-avatar', { path: 'avatar.svg', contentType: 'image/svg+xml' });

# 12) Cypress — fixture как base64 или Buffer
# cy.fixture('images/logo.png').then(base64 => ...)        # base64
# cy.fixture('images/logo.png', null).then(buf => ...)      # Buffer
# cy.intercept('/api/avatar', { fixture: 'avatar.png' })    # мокап ответа с картинкой

# 13) GitHub Actions — загрузка артефактов тестов
# - uses: actions/upload-artifact@v4
#   with:
#     name: test-screenshots
#     path: test-results/screenshots/
#     retention-days: 30
#     digest: sha256
```

---

## (d) Adopted already

1. **LoremFlickr / placehold.co / picsum / DiceBear / Lucide** — сервисы уже интегрированы в CLI (`--provider`, `--style`, `--size`).
2. **SVG output** — placehold.co и DiceBear отдают SVG по умолчанию.
3. **CLI** — `--input`, `--stdin`, `--output`, `--format` (markdown/JSON).
4. **Аватары** — простой паттерн инициал/хеш (DiceBear-style).

---

## (e) Canonical analogue details (for deep enrichment)

### 1. DiceBear
- **Repo**: https://github.com/dicebear/dicebear (SHA `5f152c12b87f26f106adeb5b3f160c15e32ecc69`)
- **Docs**: https://dicebear.com/how-to-use/http-api/ | https://dicebear.com/how-to-use/cli/
- **Паттерны**: seed → `Fnv1a` → `Mulberry32` PRNG; версионирование API (`10.x`); rate limits 50/10 rps; CLI пачка; `--optimize-check` для CI; 5.x–8.x EOL 30.04.2028.

### 2. Playwright Test
- **Repo**: https://github.com/microsoft/playwright (SHA `c973356ee9e3906260f60da5e3e04442e069a0d4`)
- **Docs**: https://playwright.dev/docs/test-fixtures | https://playwright.dev/docs/test-snapshots
- **Паттерны**: `test.extend` с `scope: 'worker'`; `toHaveScreenshot` / `toMatchSnapshot` с `maxDiffPixelRatio`; `testInfo.attach` / `outputPath()`.

### 3. SVGO
- **Repo**: https://github.com/svg/svgo (SHA `66d1495a22c01640acc593ca36e25d43e22d807f`)
- **Паттерны**: `optimize()` + `multipass` + `preset-default` (~30 плагинов); CLI `svgo -rf dir -o out --datauri=base64`.

### 4. Lucide
- **Repo**: https://github.com/lucide-icons/lucide (SHA `113a3b1a3bda9a31d30f4b056cd434ce9462828e`)
- **Паттерны**: `createLucideIcon` фабрика; tree-shaking; дефолтные атрибуты `stroke="currentColor"`, `fill="none"`; `dynamicIconImports`.

### 5. Cypress
- **Docs**: https://docs.cypress.io/api/commands/fixture
- **Паттерны**: `cy.fixture('img.png')` → base64; `cy.fixture('img.png', null)` → Buffer; `cy.intercept({fixture})`; лимит ~100 MB.

### 6. Storybook
- **Docs**: https://storybook.js.org/docs/configure/integration/images-and-assets
- **Паттерны**: `staticDirs: ['../public']` — локальные статические ассеты вместо внешних URL.

---

> **Сводка**: текущий скилл покрывает ~4 из 12+ канонических паттернов. Главные пробелы: детерминизм (seed/PRNG), SVG-оптимизация (SVGO), tree-shaking иконок (Lucide), тест-интеграции (Playwright fixtures, Cypress fixtures, GitHub Actions artifacts), визуальные диффы (`maxDiffPixelRatio`), таблица статусов/лимитов сервисов.