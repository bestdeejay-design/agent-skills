"""Composer — детерминированный синтез композиции каждого слайда.

Каждая презентация уникальна: композиция слайда НЕ выбирается из готовых
паттернов, а генерируется заново из seed (название деки + дата + индекс
слайда) внутри параметрического пространства. Паттерны в templates/patterns/
остаются как референс-рецепты (из них берутся идеи), но значения параметров
синтезируются под конкретную деку.

Инварианты качества (не нарушаются генератором):
- заголовок не пересекается с контентом (title_pos + content смещены);
- не более 3 колонок контента при text-heavy плотности;
- акцент один на слайд (word | underline | icons), никогда два;
- акцент не ложится на акцентный фон (accent только на светлом);
- декор не перекрывает текст (z-index текста выше).
"""
import hashlib

# Параметрическое пространство
TITLE_POSITIONS = ("left", "center", "vertical", "bottom-left")
TITLE_SCALES = (44, 50, 56, 62, 70)          # кегль заголовка (h2/h1)
CONTENT_LAYOUTS = ("cards", "columns", "plain", "split")
GRID_COLS = (1, 2, 3)
ACCENT_MODES = ("word", "underline", "icons")
ACCENT_LEVELS = (0.35, 0.5, 0.65, 0.8)       # интенсивность акцента
DECORS = ("none", "ovals", "dots", "grid", "beams", "diagonal", "duotone")
RADII = (10, 14, 18, 24, 30)                  # скругление карточек
SHADOWS = ("soft", "medium", "strong")



# Паттерн-рецепты: стиль элементов (характер карточек/списков), не layout.
# Каждый рецепт применяется к типам контента из PATTERN_FITS.
PATTERN_FITS = {
    "hero-left": ["bullets", "feature", "title", "quote"],
    "editorial-asym": ["title", "divider", "closing", "quote"],
    "swiss-grid": ["bullets", "metrics", "comparison", "table", "process", "timeline", "feature"],
    "z-pattern": ["bullets", "metrics", "comparison", "table"],
    "split-diagonal": ["title", "divider", "comparison", "closing"],
    "big-type": ["metrics", "big_number", "quote", "title", "closing"],
    "card-dashboard": ["metrics", "table", "process", "timeline", "feature", "bullets"],
    "vertical-rail": ["bullets", "feature", "quote", "table"],
    "split-frame": ["title", "divider", "feature", "closing", "image_showcase"],
    "sparkline-metric": ["metrics", "big_number", "kpi_row"],
    "before-after": ["comparison", "feature", "divider"],
    "vertical-stepper": ["process", "timeline"],
    "zigzag-timeline": ["timeline", "process"],
    "quote-hero": ["quote", "title", "divider"],
    "recap-grid": ["closing", "metrics", "bullets"],
    "soft-shapes": ["title", "divider", "closing", "image_showcase"],
    "data-story": ["chart", "metrics", "kpi_row", "table"],
    "cyclic-process": ["process", "timeline"],
}


def _h(seed: str, salt: str) -> int:
    return int(hashlib.sha256(f"{seed}::{salt}".encode()).hexdigest(), 16)


def _pick(seed: str, salt: str, options) -> any:
    return options[_h(seed, salt) % len(options)]


# Варианты компонентов (атомы слайда) — независимые, комбинируются.
TITLE_VARIANTS = ("line", "number", "caps", "rail", "bgword", "vertical")
MARKER_VARIANTS = ("dot", "square", "icon", "number", "dash", "none")
CARD_VARIANTS = ("glass", "border", "shadow", "edge", "gradient", "flat")
METRIC_VARIANTS = ("tile", "big", "inline", "delta", "spark")

# Структурные шаблоны по типу контента: разные HTML-разметки, не только стили.
STRUCTURES = {
    "bullets": ("list", "columns", "bars", "grid"),
    "metrics": ("grid", "menu", "ladder", "stats"),
    "big_number": ("grid", "menu", "ladder"),
    "kpi_row": ("stats", "grid"),
    "comparison": ("split", "table", "cards"),
    "process": ("stepper", "conveyor", "cycle", "list"),
    "timeline": ("zigzag", "conveyor", "list"),
    "feature": ("grid", "list", "columns"),
    "table": ("table", "cards"),
    "quote": ("center", "left", "full"),
    "title": ("poster", "split", "center"),
    "divider": ("center", "editorial"),
    "closing": ("center", "recap", "split"),
    "chart": ("bars", "line", "donut"),
}


def _pick_structure(seed: str, salt: str, layout: str) -> str:
    opts = STRUCTURES.get(layout, ("list",))
    return _pick(seed, salt + ":st", opts)


def _geometry(spec_slide: dict) -> dict:
    """Извлечь реальную геометрию текста слайда из спеки."""
    title = str(spec_slide.get("title", ""))
    bullets = spec_slide.get("bullets", []) or []
    metrics = spec_slide.get("metrics", []) or []
    columns = spec_slide.get("columns", []) or []
    steps = spec_slide.get("steps", []) or spec_slide.get("items", []) or []
    return {
        "title_word_count": len(title.split()),
        "title_char_count": len(title),
        "bullet_count": len(bullets),
        "max_bullet_len": max((len(str(b)) for b in bullets), default=0),
        "metric_count": len(metrics),
        "max_label_len": max((len(str(m.get("label", ""))) for m in metrics), default=0),
        "column_count": len(columns),
        "max_points_per_column": max((len(c.get("points", [])) for c in columns), default=0),
        "step_count": len(steps),
        "max_step_len": max((len(str(s.get("title", s))) for s in steps), default=0),
    }


def allowed_title_variants(geometry: dict) -> tuple:
    """Убрать варианты заголовка, физически несовместимые с длиной текста."""
    variants = list(TITLE_VARIANTS)
    wc = geometry.get("title_word_count", 0)
    if wc > 6:
        variants = [v for v in variants if v not in ("vertical", "bgword")]
    if wc > 10:
        variants = [v for v in variants if v not in ("caps",)]
    return tuple(variants) or ("line",)


def allowed_title_scale(geometry: dict, cols: int) -> tuple:
    """Крупный кегль запрещён, если заголовку нужно делить ширину с контентом."""
    scales = list(TITLE_SCALES)
    heavy = geometry.get("metric_count", 0) >= 4 or geometry.get("bullet_count", 0) >= 5
    if heavy or cols >= 3:
        scales = [s for s in scales if s <= 50]
    if geometry.get("title_word_count", 0) > 12:
        scales = [s for s in scales if s <= 44]
    return tuple(scales) or (44,)


def allowed_title_pos(geometry: dict, layout: str) -> tuple:
    """side-by-side позиции запрещены при длинном заголовке + тяжёлом контенте."""
    if layout in ("title", "divider", "closing", "quote"):
        positions = list(("center", "bottom-left"))
    elif layout in ("table", "chart"):
        positions = list(("center",))
    else:
        positions = list(("left", "center"))
    heavy = geometry.get("metric_count", 0) >= 4 or geometry.get("bullet_count", 0) >= 5
    if geometry.get("title_word_count", 0) > 8 and heavy:
        positions = [p for p in positions if p != "left"]
    return tuple(positions) or ("center",)


def compose_slide(seed: str, layout: str, index: int, density: str = "standard",
                  content_len: int = 3, is_dark: bool = False,
                  geometry: dict | None = None) -> dict:
    """Синтезировать композицию для одного слайда.

    seed   — строка деки (название+дата); layout — тип слайда (bullets/metrics/...);
    index  — номер слайда (для разнообразия); density — concise|standard|text-heavy;
    content_len — число элементов контента; is_dark — тёмный фон;
    geometry — реальные метрики текста (Слой 1), ограничивают выбор параметров.
    Возвращает словарь параметров композиции.
    """
    salt = f"{layout}:{index}:{density}:{content_len}"
    geo = geometry or {}
    # сетка: text-heavy → меньше колонок
    max_cols = 1 if density == "text-heavy" else 3
    cols = _pick(seed, salt + ":cols", [c for c in GRID_COLS if c <= max_cols])
    # позиция и масштаб заголовка — ограничены геометрией текста (фильтры Слоя 3)
    title_pos = _pick(seed, salt + ":tp", allowed_title_pos(geo, layout))
    title_scale = _pick(seed, salt + ":ts", allowed_title_scale(geo, cols))
    # layout контента: карточки для списков/метрик, колонки для сравнений
    if layout in ("comparison",):
        content_layout = _pick(seed, salt + ":cl", ("columns", "split"))
    elif layout in ("metrics", "big_number", "kpi_row"):
        content_layout = _pick(seed, salt + ":cl", ("cards", "plain"))
    else:
        content_layout = _pick(seed, salt + ":cl", CONTENT_LAYOUTS)
    # акцент: один, интенсивность зависит от density (concise → ярче)
    accent_mode = _pick(seed, salt + ":am", ACCENT_MODES)
    accent_level = _pick(seed, salt + ":al", ACCENT_LEVELS)
    if density == "concise":
        accent_level = max(accent_level, 0.5)
    # декор: на тёмных слайдах мягче
    decor = _pick(seed, salt + ":dc", DECORS)
    if is_dark and decor == "beams":
        decor = "ovals"
    radius = _pick(seed, salt + ":rd", RADII)
    shadow = _pick(seed, salt + ":sh", SHADOWS)
    # паттерн-рецепт: стиль элементов (не layout) — даёт характер карточкам/спискам
    recipe_cands = [pid for pid, fits in PATTERN_FITS.items() if layout in fits]
    recipe = _pick(seed, salt + ":rc", recipe_cands) if recipe_cands else "swiss-grid"
    # структура: какой HTML-шаблон собрать (список/меню/лестница/полосы/разворот/дашборд)
    structure = _pick_structure(seed, salt, layout)
    # варианты компонентов — независимые атомы, комбинация даёт разнообразие
    title_variant = _pick(seed, salt + ":tv", allowed_title_variants(geo))
    marker_variant = _pick(seed, salt + ":mv", MARKER_VARIANTS)
    card_variant = _pick(seed, salt + ":cv", CARD_VARIANTS)
    metric_variant = _pick(seed, salt + ":mv2", METRIC_VARIANTS)
    return {
        "title_pos": title_pos,
        "title_variant": title_variant,
        "structure": structure,
        "marker_variant": marker_variant,
        "card_variant": card_variant,
        "metric_variant": metric_variant,
        "title_scale": title_scale,
        "cols": cols,
        "content_layout": content_layout,
        "accent_mode": accent_mode,
        "accent_level": accent_level,
        "decor": decor,
        "radius": radius,
        "shadow": shadow,
        "recipe": recipe,
    }


def deck_seed(title: str, date: str = "") -> str:
    """Seed деки: название + дата → воспроизводимый, но уникальный."""
    return f"{title.strip().lower()}::{date.strip()}"
