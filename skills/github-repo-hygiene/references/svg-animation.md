# SVG-анимация header/footer — полная спецификация

> Вынесено из SKILL.md для прогрессивного раскрытия. Читать этот файл,
> когда нужно **сгенерировать** или **поправить** `assets/header.svg` /
> `assets/footer.svg`. Для верхнеуровневого workflow — см. SKILL.md.

---

## Принцип: ноль внешних сервисов

Никаких `capsule-render`, `shields`-генераторов и прочих URL-баннеров.
AI создаёт файлы `assets/header.svg` и `assets/footer.svg` прямо в репозитории,
README ссылается на них относительными путями. Анимация реализуется
**SMIL-атрибутами `<animate>`** — она работает в GitHub (и любом браузере)
в теге `<img>` без скриптов и без внешних запросов. Пользователи скилла
не зависят ни от одного внешнего сервиса при оформлении.

## Структура файлов

```
assets/
  ├── header.svg
  └── footer.svg
README.md
```

## Эффект «фон наплывает» (главный паттерн)

Баннер — это **не просто градиент с волнами поверх**, а градиент с **вырезом**:
нижняя волна задаётся в `<mask>` **чёрным** цветом и **полностью убирает цвет
баннера** в своей области (дыра), сквозь которую виден фон страницы (белый фон
README). Визуально фон страницы «наплывает» на баннер волнистой линией снизу
(header) или сверху (footer). Полупрозрачные белые волны (`0.25`, `0.5`) лежат
ПОВЕРХ градиента внутри группы с маской и не вырезают — они только подсвечивают
слои.

## Что умеет анимация (лучше, чем у внешних сервисов)

- **Переливающийся градиент** — цвета плавно перетекают друг в друга (8s);
  оба цвета видны одновременно по горизонтали.
- **Блик-проход (средний цвет)** — раз в ~16s по баннеру от края до края
  проскальзывает приглушённый светлый блик: узкий мягкий ореол (`opacity 0.25`,
  края растушёваны), первый проход сразу после загрузки, затем редкий цикл.
- **Морфинг волн** — форма каждой волны (и выреза в маске) плавно
  **деформируется**: `animate attributeName="d"` с **4 кадрами**
  (`keyTimes="0;0.333;0.667;1"`), гребни `Q`+`T` (smooth quadratic) реально
  «текут» — это настоящее море, а не покачивание полосы. Слои **в рассинхроне
  30%**: при `dur="6s"` задержки `0s` / `-1.8s` / `-3.6s`.
- **Фон наплывает** — чёрная волна в маске вырезает цвет → виден фон страницы.
- **Плавное появление** — название и описание появляются с лёгким подъёмом (fade + slide).
- **Twinkling в footer** — ник владельца мерцает (пульсирует яркостью).
- Анимация держится только на SMIL `<animate>`/`<animateTransform>` — работает
  в `<img>` на GitHub без скриптов и без внешних сервисов.

## Шаблон header.svg

Подставить: `COLD`, `WARM` (с `#`), `PROJECT_NAME`, `PROJECT_DESC`, `FONTCOLOR`.
Ключевые правила: чёрная волна в маске `wave` вырезает низ баннера (фон
наплывает); волны анимируются **морфингом `d`-path** (4 кадра, гребни `Q`+`T` —
во всех кадрах **одинаковая последовательность команд**, иначе морфинг ломается);
задержки `begin` смещены на 30% (`0s` / `-1.8s` / `-3.6s` при `dur="6s"`);
патчи уходят за нижний край (`L…,290`) — при движении вниз не открывается
полоска; у текста тёмный дубль-тень под основным (читаемость на любом градиенте).

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="290" viewBox="0 0 1200 290" role="img" aria-label="PROJECT_NAME — PROJECT_DESC">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="COLD">
        <animate attributeName="stop-color" values="COLD;WARM;COLD" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="WARM">
        <animate attributeName="stop-color" values="WARM;COLD;WARM" dur="8s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <!-- Маска: чёрная волна морфится и вырезает цвет баннера снизу (фон «наплывает») -->
    <mask id="wave">
      <rect width="1200" height="290" fill="#FFFFFF"/>
      <path fill="#000000" d="M0,290 L0,245 Q150,222 400,245 T800,245 T1200,245 L1200,290 Z">
        <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-3.6s"
          keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
          values="M0,290 L0,245 Q150,222 400,245 T800,245 T1200,245 L1200,290 Z;M0,290 L0,250 Q150,230 400,250 T800,250 T1200,250 L1200,290 Z;M0,290 L0,240 Q150,214 400,240 T800,240 T1200,240 L1200,290 Z;M0,290 L0,245 Q150,222 400,245 T800,245 T1200,245 L1200,290 Z"/>
      </path>
    </mask>
    <!-- Блик среднего цвета: статичный градиент (узкий мягкий ореол), движется сам rect -->
    <linearGradient id="flash" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="35%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="44%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="48%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.25"/>
      <stop offset="52%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="56%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="65%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <g mask="url(#wave)">
    <rect width="1200" height="290" fill="url(#bg)"/>

    <!-- Блик: первый проход сразу, затем раз в 16s; от края до края; гаснет и телепортируется невидимым -->
    <rect width="1200" height="290" fill="url(#flash)">
      <animateTransform attributeName="transform" type="translate" values="-600,0;-600,0;600,0;600,0" keyTimes="0;0.05;0.28;1" dur="16s" calcMode="linear" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0;1;1;1;0;0" keyTimes="0;0.03;0.05;0.28;0.35;1" dur="16s" repeatCount="indefinite"/>
    </rect>

    <!-- Средняя волна (0.25), морфинг d, сдвиг 30% (-1.8s) -->
    <path fill="#FFFFFF" opacity="0.25" d="M0,290 L0,232 Q200,210 500,232 T1000,232 T1200,232 L1200,290 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-1.8s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,290 L0,232 Q200,210 500,232 T1000,232 T1200,232 L1200,290 Z;M0,290 L0,238 Q200,220 500,238 T1000,238 T1200,238 L1200,290 Z;M0,290 L0,226 Q200,200 500,226 T1000,226 T1200,226 L1200,290 Z;M0,290 L0,232 Q200,210 500,232 T1000,232 T1200,232 L1200,290 Z"/>
    </path>
    <!-- Верхняя волна (0.5), морфинг d, сдвиг 0s -->
    <path fill="#FFFFFF" opacity="0.5" d="M0,290 L0,220 Q150,198 300,220 T600,220 T900,220 T1200,220 L1200,290 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="0s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,290 L0,220 Q150,198 300,220 T600,220 T900,220 T1200,220 L1200,290 Z;M0,290 L0,228 Q150,210 300,228 T600,228 T900,228 T1200,228 L1200,290 Z;M0,290 L0,212 Q150,186 300,212 T600,212 T900,212 T1200,212 L1200,290 Z;M0,290 L0,220 Q150,198 300,220 T600,220 T900,220 T1200,220 L1200,290 Z"/>
    </path>

    <g>
      <animate attributeName="opacity" values="0;1" dur="1.5s" fill="freeze"/>
      <text x="602" y="105" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="48" font-weight="bold" fill="#000000" opacity="0.28" text-anchor="middle">PROJECT_NAME</text>
      <text x="600" y="103" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="48" font-weight="bold" fill="FONTCOLOR" text-anchor="middle">PROJECT_NAME</text>
    </g>

    <g>
      <animate attributeName="opacity" values="0;1" dur="1.5s" begin="0.5s" fill="freeze"/>
      <text x="602" y="162" font-family="'Helvetica Neue',Arial,sans-serif" font-size="26" fill="#000000" opacity="0.30" text-anchor="middle">PROJECT_DESC</text>
      <text x="600" y="160" font-family="'Helvetica Neue',Arial,sans-serif" font-size="26" fill="FONTCOLOR" opacity="0.95" text-anchor="middle">PROJECT_DESC</text>
    </g>
  </g>
</svg>
```

## Шаблон footer.svg

Подставить: `COLD`, `WARM` (с `#`), `USERNAME`.
Footer — **зеркало header по вертикали**: дыра (чёрная волна в маске) вырезает
цвет баннера **сверху** — фон страницы наплывает на футер сверху, текст снизу.
Высота **60px** (компактный — высокий футер выглядит как «дыра после контента»).
Волны — **морфинг `d`-path** с 4 кадрами (гребни `Q`+`T`). Все патчи начинаются
**выше холста** (`y=-12` / `y=-16`) — запас больше размаха морфинга, иначе сверху
открывается градиентная полоска.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="60" viewBox="0 0 1200 60" role="img" aria-label="@USERNAME">
  <defs>
    <linearGradient id="fg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="WARM">
        <animate attributeName="stop-color" values="WARM;COLD;WARM" dur="6s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="COLD">
        <animate attributeName="stop-color" values="COLD;WARM;COLD" dur="6s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <!-- Маска: чёрная волна морфится и вырезает цвет баннера сверху (фон наплывает на футер) -->
    <mask id="wave">
      <rect width="1200" height="60" fill="#FFFFFF"/>
      <path fill="#000000" d="M0,-12 L0,21 Q200,29 400,21 T800,21 T1200,21 L1200,-12 Z">
        <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-3.6s"
          keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
          values="M0,-12 L0,21 Q200,29 400,21 T800,21 T1200,21 L1200,-12 Z;M0,-12 L0,23 Q200,32 400,23 T800,23 T1200,23 L1200,-12 Z;M0,-12 L0,19 Q200,26 400,19 T800,19 T1200,19 L1200,-12 Z;M0,-12 L0,21 Q200,29 400,21 T800,21 T1200,21 L1200,-12 Z"/>
      </path>
    </mask>
    <!-- Блик среднего цвета: статичный градиент (узкий мягкий ореол), движется сам rect -->
    <linearGradient id="flash" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="35%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="44%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="48%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.25"/>
      <stop offset="52%" stop-color="#FFFFFF" stop-opacity="0.20"/>
      <stop offset="56%" stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="65%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <g mask="url(#wave)">
    <rect width="1200" height="60" fill="url(#fg)"/>

    <!-- Блик: первый проход сразу, затем раз в 16s; от края до края; гаснет и телепортируется невидимым -->
    <rect width="1200" height="60" fill="url(#flash)">
      <animateTransform attributeName="transform" type="translate" values="-600,0;-600,0;600,0;600,0" keyTimes="0;0.05;0.28;1" dur="16s" calcMode="linear" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0;1;1;1;0;0" keyTimes="0;0.03;0.05;0.28;0.35;1" dur="16s" repeatCount="indefinite"/>
    </rect>

    <!-- Средняя волна (0.25), морфинг d, сдвиг 30% (-1.8s), запас -12 -->
    <path fill="#FFFFFF" opacity="0.25" d="M0,-12 L0,27 Q150,35 300,27 T600,27 T900,27 T1200,27 L1200,-12 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="-1.8s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,-12 L0,27 Q150,35 300,27 T600,27 T900,27 T1200,27 L1200,-12 Z;M0,-12 L0,29 Q150,38 300,29 T600,29 T900,29 T1200,29 L1200,-12 Z;M0,-12 L0,25 Q150,32 300,25 T600,25 T900,25 T1200,25 L1200,-12 Z;M0,-12 L0,27 Q150,35 300,27 T600,27 T900,27 T1200,27 L1200,-12 Z"/>
    </path>
    <!-- Верхняя волна (0.5), морфинг d, сдвиг 0s, запас -16 -->
    <path fill="#FFFFFF" opacity="0.5" d="M0,-16 L0,35 Q120,44 240,35 T480,35 T720,35 T960,35 T1200,35 L1200,-16 Z">
      <animate attributeName="d" dur="6s" repeatCount="indefinite" begin="0s"
        keyTimes="0;0.333;0.667;1" calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"
        values="M0,-16 L0,35 Q120,44 240,35 T480,35 T720,35 T960,35 T1200,35 L1200,-16 Z;M0,-16 L0,38 Q120,48 240,38 T480,38 T720,38 T960,38 T1200,38 L1200,-16 Z;M0,-16 L0,32 Q120,40 240,32 T480,32 T720,32 T960,32 T1200,32 L1200,-16 Z;M0,-16 L0,35 Q120,44 240,35 T480,35 T720,35 T960,35 T1200,35 L1200,-16 Z"/>
    </path>

    <text x="602" y="51" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="bold" fill="#000000" opacity="0.30" text-anchor="middle">@USERNAME</text>
    <text x="600" y="49" font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="bold" fill="#FFFFFF" text-anchor="middle">
      @USERNAME
      <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
    </text>
  </g>
</svg>
```

## Вставка в README.md

В **начало** README.md:

```html
<p align="center">
  <a href="https://github.com/USERNAME" target="_blank">
    <img src="assets/header.svg" alt="header" />
  </a>
</p>
```

В **конец** README.md:

```html
<p align="center">
  <a href="https://github.com/USERNAME" target="_blank">
    <img src="assets/footer.svg" alt="footer" />
  </a>
</p>
```

- Ссылки **относительные** (`assets/header.svg`) — работают в клонах и форках;
  GitHub сам масштабирует SVG (1200×290 / 1200×60) под ширину контейнера.
- Кликабельность (переход на профиль владельца) обеспечивает обёртка `<a>` —
  внутри самого `<img>` SVG ссылки не срабатывают.

## Правила безопасности (SVG)

- Не использовать `<script>` в SVG — GitHub блокирует скрипты; только SMIL `<animate>`.
- Не использовать base64 — обычные файлы в `assets/`.
- Вырез цвета делает **только чёрная волна в `<mask>`**; полупрозрачные волны
  (`#FFFFFF` с `opacity`) не вырезают — они подсвечивают слои поверх градиента.
- В маске обязательно белый `<rect>` на весь холст (видимость) + чёрные патчи-вырезы;
  без белого rect маска «погасит» весь баннер.
- Footer всегда **зеркало** header по вертикали: дыра сверху — у header снизу.

## Кодировка текста в SVG

- Пробелы остаются пробелами (это SVG, не URL — URL-encoding не нужен).
- Спецсимволы — HTML entities при необходимости (`&amp;` для `&`).
- Если `PROJECT_NAME` длиннее 20 символов — уменьшить `font-size` до 36.
- Если длиннее 30 символов — уменьшить до 28.
- Если длиннее 40 — перенести часть в `PROJECT_DESC`.

## Параметры анимации (настраиваемые)

- `dur="8s"` (header) / `dur="6s"` (footer) — скорость перетекания градиента (можно 4–10s).
- `dur="6s"` — период морфинга волн (можно 4–8s).
- **Блик-проход** — `dur="16s"` (редкий, «раз в ~16 секунд»; можно 8–30s):
  - `values="-600,0;-600,0;600,0;600,0"` с `keyTimes="0;0.05;0.28;1"` —
    стоит у левого края (центр x=0), проезжает весь холст до правого края
    (центр x=1200) за ~23% периода, затем держится за холстом (невидим).
  - opacity `values="0;0;1;1;1;0;0"` с `keyTimes="0;0.03;0.05;0.28;0.35;1"` —
    блик видим ровно в окно прохода, гаснет до телепорта обратно
    (телепорт происходит при opacity=0 — незаметен).
  - Яркость: пик `stop-opacity="0.25"` (можно 0.15–0.4 — «еле уловимый»),
    стопы-хвосты `0.10/0.20` — мягкий размытый ореол, а не резкая полоса.
  - **Важно**: анимируется НЕ `gradientTransform` (ненадёжно в Safari),
    а `transform` самого `rect`; градиент блика статичен.
- **Рассинхрон 30%**: задержки волн считаются как `begin = -dur * 0.3 * n`
  для `n = 0, 1, 2`. При `dur="6s"`: `0s` (верхняя), `-1.8s` (средняя),
  `-3.6s` (вырез). Слои никогда не совпадают по фазе.
- **Морфинг `d`-path**: `animate attributeName="d"` с **4 кадрами** —
  `keyTimes="0;0.333;0.667;1"`, `calcMode="spline"`,
  `keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"`, 4-й кадр = 1-й
  (замкнутый цикл).
- **Критично для морфинга**: во ВСЕХ кадрах `values` — **одинаковая
  последовательность команд** (`M L Q T T L Z`), меняются только координаты.
  Иначе анимация `d` ломается. Разные слои могут иметь разное число гребней
  (вырез 2–3, верхняя волна 4–5) — внутри одного элемента оно одинаково.
- Гребни — **`Q`+`T`** (smooth quadratic): `T` автоматически зеркалит
  контрольную точку предыдущей `Q` → идеально гладкая периодическая волна
  без ручных расчётов.
- Пики волн в `d`-path **не должны совпадать по фазе** между слоями
  (разные `Q`-точки, разное число гребней) — иначе слои сливаются в одну волну.
- **Запас патча**: любой патч, упирающийся в край холста, должен выходить
  за него минимум на свой размах морфинга (footer: верх патчей `y=-12` / `y=-16`
  при размахе 4/6), иначе при анимации с края открывается полоска градиента.
- `dur="1.5s"` — скорость появления текста (можно 1–2s), `begin="0.5s"` —
  задержка появления desc.
- `dur="2s"` — скорость мерцания footer (можно 1.5–3s).