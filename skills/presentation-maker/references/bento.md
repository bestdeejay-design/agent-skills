# Bento JSON sidecar — формат и валидация

Спецификация JSON-боковой панели (`doc.json`), встраиваемой в `.bento.html` через
`<script type="application/bento+json" id="bento-doc">`. Формат описан в
[nyblnet/bento](https://github.com/nyblnet/bento) (MIT). Этот документ — справочник
по структуре, ограничениям и кодам проверок.

---

## Файл и извлечение

`.bento.html` — самодостаточный HTML-файл. Внутри него ровно один блок
`<script type="application/bento+json" id="bento-doc">` содержит JSON-объект
документа. Валидатор (`qa_bento.py`) принимает оба формата:

* **`.bento.html`** — извлекает JSON из `#bento-doc` блока.
* **`.doc.json`** — читает JSON напрямую (если файл начинается с `{`).

Валидатор — browser-free, stdlib-only (argparse, json, re, html, pathlib).

---

## Корневой объект

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `format` | строка | да | Всегда `"bento/slides"` |
| `version` | число | да | Всегда `1` |
| `docId` | строка | да | Уникальный идентификатор документа |
| `title` | строка | да | Название презентации |
| `size` | объект | да | `{width, height}` — размер слайда в px |
| `theme` | объект | да | Тема (палитра, шрифты) |
| `slides` | массив | да | Массив слайдов |
| `modified` | строка | да | ISO-дата последнего изменения |
| `meta` | объект | нет | Мета: author, company, subject, event, keywords |
| `present` | объект | нет | Настройки презентации |
| `assets` | объект | нет | Документ-уровневые ассеты (ключ → тип/данные) |
| `blobs` | объект | нет | BLOB-данные |
| `fonts` | массив | нет | Встроенные шрифты (`[{family, asset}]`) |
| `layouts` | объект | нет | Переиспользуемые шаблоны слайдов |
| `collab` | объект | нет | Ключи совместного редактирования |
| `template` | строка | нет | Шаблон |
| `readonly` | булево | нет | Режим «только чтение» |

### size

```json
{"width": 1280, "height": 720}
```

`width` и `height` — положительные числа. По умолчанию 1280×720 (16:9).

### theme

| Поле | Описание |
|------|----------|
| `background` | Цвет фона слайда |
| `color` | Цвет текста по умолчанию |
| `accent` | Акцентный цвет |
| `fontFamily` | Шрифт основного текста |
| `headingFamily` | Шрифт заголовков |
| `palette` | Объект палитры (bg2, tx2, accent2–6, hlink, folHlink) |
| `chartPalette` | Палитра для графиков |
| `table` | Настройки таблиц |

### present

| Поле | Описание |
|------|----------|
| `numberHidden` | Скрыть нумерацию |
| `slideNumber` | Показать номер слайда |
| `controls` | Показать элементы управления |
| `progress` | Показать прогресс-бар |
| `morphSeconds` | Длительность morph-перехода |

---

## Слайд

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `id` | строка | да | Уникальный id слайда |
| `background` | строка/объект | да | Фон слайда |
| `transition` | строка | да | Переход: `none`, `fade`, `slide`, `zoom`, `morph` |
| `elements` | массив | да | Массив элементов |
| `notes` | строка | да | Заметки спикера (пустая строка — missing-notes info) |
| `name` | строка | нет | Человекочитаемое имя |
| `stateOf` | строка | нет | Id родительского слайда (state-машинка) |
| `hidden` | булево | нет | Скрытый слайд |
| `hover` | объект | нет | Hover-поведение (`{type, dim, default}`) |
| `comments` | массив | нет | Комментарии |
| `themeRefs` | объект | нет | Переопределения темы для слайда |

### transition

Допустимые значения: `none`, `fade`, `slide`, `zoom`, `morph`.

Morph — фирменный переход Bento. Деки с ≥3 слайдами без ни одного
`morph`-перехода получают warning `no-morph-anywhere`.

### state-машинка

Слайды с `stateOf` — это «состояния» другого слайда. Правила:

* `stateOf` должен указывать на существующий слайд.
* State-слайд должен стоять **сразу после** родителя (смежность).
* State/hidden-слайды без входящих ссылок — `unreachable-hidden-slide` (info).

---

## Элемент

Каждый элемент имеет **базовые поля** (общие для всех типов) и **типовые поля**
(зависят от `type`).

### Базовые поля

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `type` | строка | да | Тип элемента |
| `id` | строка | да | Уникальный id на слайде |
| `x` | число | да | X-координата (px) |
| `y` | число | да | Y-координата (px) |
| `w` | число | да | Ширина (px), > 0 |
| `h` | число | да | Высота (px), > 0 |
| `rotation` | число | да | Вращение (градусы) |
| `opacity` | число | да | Прозрачность 0..1 |
| `morphId` | строка | нет | Ключ для morph-связки между слайдами |
| `shadow` | объект/массив | нет | Тень (`{x, y, blur, color}`) |
| `blur` | число | нет | Размытие |
| `blend` | строка | нет | Режим смешивания |
| `backdropFilter` | строка | нет | CSS backdrop-filter |
| `fx` | объект | нет | Анимации и эффекты |
| `link` | строка | нет | Ссылка на другой слайд (id) |
| `group` | строка | нет | Имя группы |
| `groupId` | строка | нет | Id группы |
| `showOnHover` | строка | нет | Показать при наведении на элемент |
| `role` | строка | нет | Роль: `title`, `subtitle`, `body`, `kicker` |
| `themeRefs` | объект | нет | Переопределения темы для элемента |

### Типы элементов

#### text

| Поле | Описание |
|------|----------|
| `html` | HTML-содержимое (ограниченный набор тегов) |
| `fontSize` | Размер шрифта (px) |
| `fontFamily` | Семейство шрифта |
| `fontWeight` | Толщина шрифта |
| `color` | Цвет текста |
| `colorGradient` | Градиент `{angle, stops}` |
| `align` | Горизонтальное выравнивание: `left`, `center`, `right` |
| `valign` | Вертикальное выравнивание: `top`, `middle`, `bottom` |
| `lineHeight` | Межстрочный интервал |
| `letterSpacing` | Межбуквенное расстояние |
| `textStroke` | Обводка текста |
| `placeholder` | Заглушка |

**Ограничения HTML:** допустимые теги — `b`, `i`, `u`, `s`, `code`, `br`, `span`,
`p`, `div`, `ul`, `ol`, `li`, `h1`–`h6`. Атрибуты запрещены. Эмодзи — warning
(`emoji-in-text`): Bento-деки используют SVG/shape-иконки, не эмодзи.

**fontSize:** порог 15px (caption floor) — ниже warning `text-too-small`.
Chrome/decor-элементы (id начинается с `chrome-`, `decor`, `ghost`) исключены.

#### shape

| Поле | Описание |
|------|----------|
| `shape` | Тип: `rect`, `ellipse`, `triangle`, `arrow`, `line`, `path` |
| `fill` | Цвет заливки |
| `fillGradient` | Градиент заливки `{angle, stops}` |
| `stroke` | Цвет обводки |
| `strokeWidth` | Толщина обводки |
| `radius` | Радиус скругления |
| `strokeDash` | Пунктир обводки |
| `strokeStyle` | Стиль обводки: `solid`, `dashed`, `dotted` |
| `lineStart` | Начало линии: `none`, `arrow`, `dot`, `bar` |
| `lineEnd` | Конец линии: `none`, `arrow`, `dot`, `bar` |
| `d` | Path data (для shape=path) |
| `pathBox` | Bounding box для path |
| `from` | Начало коннектора `{el}` |
| `to` | Конец коннектора `{el}` |

#### image

| Поле | Описание |
|------|----------|
| `src` | Источник изображения (обязательно) |
| `fit` | Режим масштабирования: `contain`, `cover`, `fill` |
| `radius` | Радиус скругления |

#### svg

| Поле | Описание |
|------|----------|
| `asset` | Ключ в `doc.assets` |
| `markup` | Inline SVG-разметка |
| `css` | CSS для SVG |

Нужен хотя бы `asset` или `markup` (иначе `missing-asset`).

#### chart

| Поле | Описание |
|------|----------|
| `preset` | Тип: `bar`, `line`, `pie`, `scatter` |
| `option` | ECharts-подобный объект опций |
| `source` | Источник данных |

**Важно:** Bento использует `charts-lite`, а **не** полный ECharts.
Особенности:
* Bar/line/scatter: данные — **плоские числа**. `{name,value}` объекты → 0
  (`chart-nonnumeric-data`, error).
* Label работает только на pie (`chart-label-ignored`).
* Formatter — строковый шаблон (`{b}`, `{c}`, `{d}`), не функция
  (`chart-function-formatter`, error).
* Деки с bar/line/scatter должны иметь `xAxis` + `yAxis`
  (`chart-missing-axis`, warning).

#### table

| Поле | Описание |
|------|----------|
| `columns` | Массив колонок `[{w}]` |
| `rows` | Массив строк `[{cells: [{html, align, color, bg, bold}]}]` |
| `header` | Заголовочная строка |
| `style` | Стилизация `{headerBg, headerColor, zebra, borderColor, ...}` |

`columns[].w` — положительное число. Количество `cells` в строке должно
совпадать с числом колонок (`table-ragged-rows`).

#### media

| Поле | Описание |
|------|----------|
| `kind` | Тип медиа (`video`, `audio`) |
| `src` | Источник |
| `poster` | Обложка (для video) |
| `fit` | Режим масштабирования |
| `radius` | Радиус скругления |
| `autoplay` | Автозапуск |
| `loop` | Зацикливание |
| `muted` | Без звука |
| `controls` | Показать контролы |

#### code

| Поле | Описание |
|------|----------|
| `content` | Код |
| `fontSize` | Размер шрифта |
| `fontFamily` | Моноширинный шрифт |
| `align` | Выравнивание |
| `valign` | Вертикальное выравнивание |
| `lineHeight` | Межстрочный интервал |
| `color` | Цвет текста |
| `grammarAssetId` | Id ассета подсветки грамматики |
| `grammarName` | Имя грамматики |
| `themeAssetId` | Id ассета темы |
| `themeName` | Имя темы |

---

## fx — анимации и эффекты

| Поле | Описание |
|------|----------|
| `enter` | Входная анимация: `fade-up`, `fade`, `fade-down`, `slide-left`, `slide-right`, `slide-up`, `slide-down` |
| `enterDur` | Длительность входа |
| `order` | Порядок появления |
| `countUp` | Анимация счётчика |
| `ambient` | Фоновая анимация (ken-burns и т.п.) |
| `ken` | Ken-burns: `{dir, scale, duration}` — dir: `drift`, `out`, `in` |
| `loop` | Циклическая анимация |

### loop

| Поле | Описание |
|------|----------|
| `type` | Тип: `dash-march`, `motion-path` и др. |
| `distance` | Дистанция |
| `duration` | Длительность (сек) |
| `path` | SVG path для motion-path |
| `delay` | Задержка |
| `ease` | Функция сглаживания |
| `speeds` | Массив скоростей |

**dash-march:** требует `strokeStyle: "dashed"` или `"dotted"` — иначе
`dash-march-no-dash` (warning).

**motion-path:** требует `path`. Несовместим с `fx.enter` (оба борются за
CSS transform) → `entrance-on-motion-path` (warning).

### Морф-конфликты

Если элемент **приходит через morph** (его `morphId` есть на предыдущем слайде
с `transition: "morph"`):

* `fx.enter` → `overridden-enter-fx` (warning) — Bento пропускает вход.
* `fx.countUp` → `inert-countup` (info) — пропускается по дизайну.

---

## Коннекторы

Элементы типа `shape` могут быть коннекторами между другими элементами:

```json
{"from": {"el": "element-id"}, "to": {"el": "element-id"}}
```

Если `from.el` или `to.el` ссылается на элемент, которого нет на текущем
слайде → `dangling-connector` (warning).

---

## Границы и поля

| Правило | Порог | Код |
|---------|-------|-----|
| Canvas bounds | Элемент не должен выступать за пределы `size.width × size.height` | `out-of-canvas` (warning) |
| Content margin | Текст/таблица: x ≥ 96, x+w ≤ 1184, y+h ≤ 624 | `past-margin` (info) |
| Positive size | w > 0, h > 0 | `zero-size` (error) |
| Opacity | 0 ≤ opacity ≤ 1 | `bad-opacity` (warning) |

Chrome/decor-элементы (id: `chrome-*`, `decor*`, `ghost*`) **исключены** из
проверки canvas bounds.

---

## Дизайн-проверки

| Код | Уровень | Описание |
|-----|---------|----------|
| `no-morph-anywhere` | warning | ≥3 слайдов, ни одного `transition: "morph"` |
| `no-motion-moment` | warning | Ни один элемент не использует `countUp`, `ambient` или `loop` |
| `static-chrome` | info | Chrome-id не идентичны между слайдами (поп вместо morph) |
| `numbers-as-text` | info | Числовая серия отрисована как текстовые буллеты (нужен chart) |
| `font-not-embedded` | info | fontFamily не встроена и не системная |

---

## CLI: qa_bento.py

```bash
python3 qa_bento.py deck.bento.html
python3 qa_bento.py deck.bento.html.doc.json --strict
python3 qa_bento.py deck.bento.html --json report.json --codes
```

| Флаг | Описание |
|------|----------|
| `--json FILE` | Записать JSON-отчёт |
| `--strict` | FAIL при warnings тоже |
| `--max-warnings N` | FAIL при превышении N warnings |
| `--codes` | Вывести только уникальные коды finding'ов |
| `--quiet` | Только строка вердикта |

**Exit codes:** 0 = PASS (без ошибок), 1 = FAIL, 2 = ошибка ввода.

### JSON-отчёт

```json
{
  "deck": "deck.bento.html",
  "format": "bento/slides",
  "version": 1,
  "slides": 19,
  "elements": 200,
  "measured": false,
  "findings": [
    {
      "code": "out-of-canvas",
      "severity": "warning",
      "message": "element extends outside the 1280x720 canvas ...",
      "slide": 2,
      "element": "b1-card"
    }
  ],
  "counts": {"errors": 0, "warnings": 1, "infos": 0, "total": 1},
  "verdict": "PASS"
}
```

`measured` всегда `false` — проверка text-overflow требует реального DOM
(Playwright), этот гейт browser-free.

---

## Коды проверок

### Ошибки (error → exit 1)

| Код | Семейство | Описание |
|-----|-----------|----------|
| `bad-format` | document | format ≠ `"bento/slides"` |
| `bad-version` | document | version ≠ `1` |
| `missing-required` | document/slide | Отсутствует обязательное поле |
| `missing-asset` | document/element | Ассет не найден в `doc.assets` |
| `unescaped-lt` | document | Сырой `<` внутри `#bento-doc` блока |
| `zero-size` | element | w ≤ 0 или h ≤ 0 |
| `duplicate-slide-id` | slide | Дублирующийся id слайда |
| `duplicate-id` | element | Два элемента на одном слайде с одним id |
| `morph-key-collision` | element | Два элемента на одном слайде с одним morph key |
| `missing-element-field` | element | Нет обязательного базового поля |
| `broken-link` | element | Ссылка на несуществующий слайд |
| `missing-asset` | element | SVG/image без src/asset |
| `chart-nonnumeric-data` | chart | Bar/line/scatter данные не числа |
| `chart-function-formatter` | chart | Formatter — функция, а не строка |
| `bad-enum` | various | Значение не из допустимого набора (format, transition, align, ...) |

### Предупреждения (warning → exit 1 при --strict)

| Код | Семейство | Описание |
|-----|-----------|----------|
| `unknown-key` | various | Неизвестное поле (Bento игнорирует молча) |
| `out-of-canvas` | element | Элемент за пределами canvas |
| `text-too-small` | element | fontSize < 15px |
| `emoji-in-text` | element | Эмодзи в тексте |
| `disallowed-html-tag` | element | Тег вне подмножества Bento |
| `dash-march-no-dash` | element | dash-march без пунктира |
| `entrance-on-motion-path` | element | enter + motion-path конфликт |
| `overridden-enter-fx` | element | enter на morph-приходящем элементе |
| `state-not-adjacent` | slide | State-слайд не сразу после родителя |
| `missing-transition` | slide | Переход не из допустимого набора |
| `table-ragged-rows` | table | Разное число cells в строках |
| `table-bad-weight` | table | Отрицательный/нулевой вес колонки |
| `chart-empty-series` | chart | Пустой массив данных |
| `chart-label-ignored` | chart | Label на не-pie графике |
| `chart-missing-axis` | chart | Cartesian без xAxis/yAxis |
| `no-morph-anywhere` | design | Нет morph-перехода в деке |
| `no-motion-moment` | design | Ни одного动态-эффекта |
| `dangling-connector` | element | Коннектор ссылается на отсутствующий элемент |
| `bad-opacity` | element | opacity вне 0..1 |
| `bad-enum` | various | Невалидное значение перечисления |

### Информационные (info → не влияют на exit)

| Код | Семейство | Описание |
|-----|-----------|----------|
| `past-margin` | element | Контент за пределами 96px margin |
| `missing-notes` | slide | Пустые заметки спикера |
| `unreachable-hidden-slide` | slide | Hidden/state слайд без входящих ссылок |
| `font-not-embedded` | element | Шрифт не встроен и не системный |
| `collab-secrets-present` | document | writerPriv в collab (не для публикации) |
| `inert-countup` | element | countUp на morph-приходящем элементе |
| `static-chrome` | design | Chrome-id не идентичны |
| `numbers-as-text` | design | Числовая серия как буллеты |
