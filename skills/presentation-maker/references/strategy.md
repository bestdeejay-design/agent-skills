# Strategy — выбор стратегии презентации по цели

Справочник для агента-автора: как по цели (`goal`) подобрать нарративную дугу
(`arc`), эстетический режим (`mood`), плотность (`density`) и набор лейаутов.
Логика реализована в `scripts/strategy.py` (`select_strategy`) и автоматически
применяется `scripts/deck_md.py`, когда соответствующие поля не заданы во
frontmatter файла `deck.md`.

Рациональность опирается на `deck-html/references/product-designer.md`
(модуль «Продакт-дизайнер», раздел A — нарратив/ИА) и
`deck-html/references/design-system.md` (раздел 5.4 — эстетические режимы).

## Быстрая таблица

| goal | arc | mood | density | тема (palette) | лейауты |
|---|---|---|---|---|---|
| `pitch` | problem-solution-proof-cta | `glass` | concise | swift | title, bullets, metrics, comparison, closing |
| `consulting` | problem-solution-proof-cta (пирамида Minto/SCQA) | `swiss` | text-heavy | executive | table, chart, metrics, bullets |
| `keynote` | sparkline (или star-moment) | `editorial` | concise | standard | big_number, quote, divider |
| `report` | problem-solution-proof-cta | `swiss` | standard | standard | table, chart, process |
| `edu` | star (STAR-кейс) | `flat` | standard | modern | bullets, process, feature |

> Примечание: имена `swift / executive / standard / modern` в ТЗ — это **имена
> файлов тем** (`deck-html/templates/themes/*.json`), а не mood. Валидные mood
> (поле `theme.mood` в `deck.json`): `swiss`, `editorial`, `flat`, `glass`,
> `dark`. Сопоставление mood → тема в `DEFAULT_THEMES`:
> `swiss→executive`, `editorial→standard`, `flat→modern`, `glass→swift`,
> `dark→dynamic`.

## По целям (best practices для темы)

### pitch — инвесторам / на раунд
- **Дуга:** Problem→Solution→Proof→CTA. Аудитория ещё не знакома с проблемой:
  боль → решение → доказательства (тракция/метрики) → один призыв (CTA).
- **Mood:** `glass` (Apple-стиль, blur/glow) — премиум tech-продукт, keynote-вид.
- **Density:** `concise` (~20 слов/слайд). Питч = 10 минут, метрики бьют в цель.
- **Лейауты:** `title` (хук) → `bullets` (проблема) → `metrics` (тракция) →
  `comparison` (мы vs альтернативы) → `closing` (CTA).
- **Практика:** заголовки — assertion («Рост выручки ускорился до 40% в Q3»);
  одна идея на слайд; метрики крупно, с дельтой.

### consulting — стратегия / отчёт для совета директоров
- **Дуга:** Problem→Solution→Proof→CTA, построенная как **пирамида Minto**
  (тезис сверху, ≤3 MECE-опоры, каждая с фактами) + SCQA.
- **Mood:** `swiss` (строгая сетка, волосяные линии) — бизнес/аналитика.
- **Density:** `text-heavy` — аудитория читает сама, плотные данные, таблицы.
- **Лейауты:** `table` (точные значения) → `chart` (тренды/ранжиры) →
  `metrics` (итоговые карточки) → `bullets` (выводы).
- **Практика:** assertion-заголовки обязательны; таблицы ≤7 колонок/≤12 строк,
  подсвети ответ (highlight_col); числа с единицами, ≤2 знаков.

### keynote — выступление / конференция
- **Дуга:** **Sparkline** (Duarte) — чередование «что есть» ↔ «что могло бы быть»
  на протяжении деки; или `star-moment` (один шокирующий поворот).
- **Mood:** `editorial` (журнальная типографика, serif-display) или `dark`
  (ночной режим, консольная строгость).
- **Density:** `concise` — минимум текста, эмоциональная дуга.
- **Лейауты:** `big_number` (герой-цифра) → `quote` (манифест) →
  `divider` (главы/повороты).
- **Практика:** один S.T.A.R. момент на всю деку; крупная иерархия; воздух.

### report — регулярный отчёт / квартал
- **Дуга:** Problem→Solution→Proof→CTA (структура отчёта: что случилось →
  почему → что сделали → план).
- **Mood:** `swiss` (строго, отчётно) — ближе к executive, чем к playful.
- **Density:** `standard` (~40 слов/слайд).
- **Лейауты:** `table` (детали) → `chart` (динамика) → `process` (шаги плана).
- **Практика:** подпись-вывод у каждой таблицы/графика; ось Y с 0; сортировка
  баров по убыванию.

### edu — обучение / курс / лекция
- **Дуга:** **STAR** (Situation→Task→Action→Result) — один слайд = один кейс,
  доказывающий компетенцию.
- **Mood:** `flat` (ровные карточки, крупные радиусы, бенто) — современная
  лаконичность, дружелюбно к обучению.
- **Density:** `standard`.
- **Лейауты:** `bullets` (тезисы) → `process` (алгоритм/шаги) →
  `feature` (набор понятий: иконка+заголовок+описание).
- **Практика:** концепты — через `feature` (иконки из `templates/icons/`, не
  эмодзи); процессы — через `process`; одна идея на слайд.

## Эстетические режимы (mood) — кратко

| mood | характер | когда |
|---|---|---|
| `swiss` | минимализм, строгая сетка, волосяные линии | бизнес, стратегия, аналитика |
| `editorial` | журнальная типографика, serif-display, дуо-градиенты | бренды, креатив, премиум |
| `flat` | ровные карточки, крупные радиусы, без теней | стартапы, продукт, обучение |
| `glass` | полупрозрачные карточки, blur, glow | tech-продукт, keynote |
| `dark` | тёмный блок, моноширинная индексация | тех, код, data, ночной режим |

Правило: не смешивай 2+ режима в одной деке; mood согласуется со смыслом
(не ставь светлый мягкий mood для тёмной палитры).

## Использование

```bash
# Только стратегия (JSON в stdout)
python3 scripts/strategy.py --goal keynote
python3 scripts/strategy.py --audience "инвесторы SaaS" --topic "раунд A"

# Полный пайплайн (deck.md -> deck.json)
python3 scripts/deck_md.py deck.md --out deck.json
```

`select_strategy(goal, audience=None, topic=None, language=None)` возвращает
`{goal, arc, mood, density, palette_name, layouts}`. Если `goal` не задан/неизвестен,
цель выводится по ключевым словам в `audience`/`topic`, иначе дефолт `pitch`.
