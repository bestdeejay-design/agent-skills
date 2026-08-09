# Showcase: seo-toolkit на lovii.ru

> Демонстрация `seo-toolkit` (13 SEO-команд + helper `seo_toolkit.py`)
> на реальном проекте — лендинг **lovii.ru** (White Paper, `lovii_demo`),
> по процессу `CONTRIBUTING.md` (шаг 6).

## Вход

```
Скилл:  seo-toolkit
Проект: https://lovii.ru/ (публичная страница White Paper LOVII)
Режим:  URL mode → fetch страницы, затем helper по сохранённому HTML

$ curl -sL https://lovii.ru/ -o /tmp/lovii_home.html   # HTTP 200, 36 462 bytes
$ python3 scripts/seo_toolkit.py --meta --file /tmp/lovii_home.html
$ python3 scripts/seo_toolkit.py --density --file /tmp/lovii_home.html --keyword marketplace
$ python3 scripts/seo_toolkit.py --jsonld --file /tmp/lovii_home.html
```

## Вывод

### 1. Meta/заголовки/картинки (`--meta`)

| Параметр | Значение |
|---|---|
| `<title>` | `LOVII — White Paper` (19 символов — **короткий**, канон 50–60) |
| `description` | 178 символов (канон 120–160 — чуть длиннее) |
| `canonical` | **отсутствует** |
| `og:image` | `https://lovii.ru/og-image.svg` (**svg** — OG требует PNG/JPG ≥ 600×315) |
| `twitter:card` | `summary_large_image` |
| `H1` | 1 шт: «LOVII — от района к Федерации» ✅ |
| H2/H3/H4 | 28 заголовков, иерархия 1→2→3→4 без пропусков ✅ |
| Изображения | 2 шт., **все с alt** ✅ |

### 2. Плотность ключей (`--density --keyword marketplace`)

```
words_total: 2823
keyword_hits: 0
density: 0.00%
```

Контент про «локальные маркетплейсы», но точный ключ `marketplace` не встречается —
сигнал к доработке контент-описания под семантическое ядро.

### 3. JSON-LD (`--jsonld`)

```
json_ld_blocks: 0
```

Структурных данных (schema.org) на странице **нет** — упущение для rich results.

## Интерпретация (что показал бы супервайзер)

1. **нет canonical** (самодостаточный лендинг) — риск дублей при размещении на зеркалах
   (GGH Pages + отдельный домен).
2. **нет JSON-LD** — opportunity: добавить `Organization` + `WebSite` + `Article`
   (white paper) для rich results.
3. `<title>` и description вне канонических длин — метрика CTR.
4. `og:image` в SVG — ок графика соцфолки требует PNG/JPG.
5. H1/H2 иерархия и alt-атрибуты — **в порядке** (прочий позитив аудита).
6. По канонам `references/canonical-patterns.md`: подключить Lighthouse/PSI для
   Core Web Vitals и Rich Results Test для валидации разметки.

Это типичный пример «аудит лендинга»: быстрое считывание метаданных + структуры
страницы и точные исправления по чек-листу SEO.