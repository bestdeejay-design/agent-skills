#!/usr/bin/env python3
"""
test-graphics.py — генерация тестовых изображений для проектов.

Использование:
  test-graphics.py photo [width] [height] [output]
  test-graphics.py placeholder <width> <height> [color] [text] [output]
  test-graphics.py icon <name> [color] [size] [output]
  test-graphics.py batch-photos <count> [output_dir]
  test-graphics.py batch-icons <count> [output_dir]
  test-graphics.py download-icons <names> [output_dir]
  test-graphics.py lucide <name> [output_dir]
  test-graphics.py list-icons

Зависимости: python3, Pillow, requests (предустановлены).
"""

import os
import sys
import random
import string
import xml.dom.minidom as minidom

W = 800
H = 600

# ─────────────────────── SVG ICONS ───────────────────────

ICONS = {
    "star": (
        '<polygon points="32,4 40,24 62,24 44,38 50,60 32,48 14,60 20,38 2,24 24,24" '
        'fill="{color}" stroke="{stroke}" stroke-width="2"/>'
    ),
    "circle": (
        '<circle cx="32" cy="32" r="28" fill="{color}" stroke="{stroke}" stroke-width="2"/>'
    ),
    "square": (
        '<rect x="6" y="6" width="52" height="52" rx="4" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
    ),
    "triangle": (
        '<polygon points="32,4 60,56 4,56" fill="{color}" stroke="{stroke}" stroke-width="2"/>'
    ),
    "heart": (
        '<path d="M32,56 C12,40 4,28 4,18 C4,8 14,4 20,8 C26,12 30,18 32,22 '
        'C34,18 38,12 44,8 C50,4 60,8 60,18 C60,28 52,40 32,56Z" '
        'fill="{color}" stroke="{stroke}" stroke-width="2"/>'
    ),
    "home": (
        '<path d="M8,32 L32,8 L56,32 L56,56 L38,56 L38,38 L26,38 L26,56 L8,56Z" '
        'fill="{color}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
    ),
    "user": (
        '<circle cx="32" cy="22" r="12" fill="{color}" stroke="{stroke}" stroke-width="2"/>'
        '<path d="M8,58 C8,44 20,34 32,34 C44,34 56,44 56,58" '
        'fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>'
    ),
    "mail": (
        '<rect x="4" y="12" width="56" height="40" rx="4" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<path d="M4,16 L32,36 L60,16" fill="none" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "settings": (
        '<circle cx="32" cy="32" r="10" fill="none" stroke="{stroke}" stroke-width="2"/>'
        '<path d="M32,6 L32,14 M32,50 L32,58 M6,32 L14,32 M50,32 L58,32 '
        'M12,12 L18,18 M46,46 L52,52 M12,52 L18,46 M46,18 L52,12" '
        'stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>'
    ),
    "search": (
        '<circle cx="26" cy="26" r="18" fill="none" stroke="{stroke}" stroke-width="3"/>'
        '<line x1="40" y1="40" x2="58" y2="58" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "arrow-right": (
        '<line x1="8" y1="32" x2="52" y2="32" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<polyline points="40,18 54,32 40,46" fill="none" stroke="{stroke}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "arrow-left": (
        '<line x1="56" y1="32" x2="12" y2="32" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<polyline points="24,18 10,32 24,46" fill="none" stroke="{stroke}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "arrow-up": (
        '<line x1="32" y1="56" x2="32" y2="12" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<polyline points="18,24 32,10 46,24" fill="none" stroke="{stroke}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "arrow-down": (
        '<line x1="32" y1="8" x2="32" y2="52" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<polyline points="18,40 32,54 46,40" fill="none" stroke="{stroke}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "check": (
        '<polyline points="8,34 26,50 56,14" fill="none" stroke="{stroke}" '
        'stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "cross": (
        '<line x1="12" y1="12" x2="52" y2="52" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<line x1="52" y1="12" x2="12" y2="52" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "plus": (
        '<line x1="32" y1="10" x2="32" y2="54" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<line x1="10" y1="32" x2="54" y2="32" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "minus": (
        '<line x1="10" y1="32" x2="54" y2="32" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "info": (
        '<circle cx="32" cy="32" r="26" fill="none" stroke="{stroke}" stroke-width="2"/>'
        '<line x1="32" y1="28" x2="32" y2="46" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<circle cx="32" cy="18" r="2" fill="{stroke}"/>'
    ),
    "warning": (
        '<polygon points="32,6 58,52 6,52" fill="none" stroke="{stroke}" stroke-width="2" '
        'stroke-linejoin="round"/>'
        '<line x1="32" y1="24" x2="32" y2="38" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<circle cx="32" cy="44" r="2" fill="{stroke}"/>'
    ),
    "download": (
        '<line x1="32" y1="8" x2="32" y2="44" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<polyline points="16,30 32,48 48,30" fill="none" stroke="{stroke}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="8" y1="52" x2="56" y2="52" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "upload": (
        '<line x1="32" y1="52" x2="32" y2="16" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<polyline points="16,30 32,12 48,30" fill="none" stroke="{stroke}" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="8" y1="52" x2="56" y2="52" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "folder": (
        '<path d="M4,48 L4,16 C4,12 8,8 12,8 L26,8 L32,16 L52,16 '
        'C56,16 60,20 60,24 L60,48 C60,52 56,56 52,56 L12,56 '
        'C8,56 4,52 4,48Z" '
        'fill="{color}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
    ),
    "file": (
        '<path d="M16,6 L40,6 L56,22 L56,54 C56,58 52,60 48,60 L16,60 '
        'C12,60 8,58 8,54 L8,12 C8,8 12,6 16,6Z" '
        'fill="{color}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
        '<line x1="38" y1="6" x2="38" y2="22" stroke="{stroke}" stroke-width="2"/>'
        '<line x1="38" y1="22" x2="56" y2="22" stroke="{stroke}" stroke-width="2"/>'
    ),
    "image": (
        '<rect x="6" y="10" width="52" height="44" rx="4" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<circle cx="22" cy="24" r="6" fill="none" stroke="{stroke}" stroke-width="2"/>'
        '<path d="M6,50 L22,34 L32,44 L42,30 L58,50" fill="none" ' 
        'stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "calendar": (
        '<rect x="6" y="14" width="52" height="44" rx="4" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<line x1="6" y1="26" x2="58" y2="26" stroke="{stroke}" stroke-width="2"/>'
        '<line x1="20" y1="6" x2="20" y2="18" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<line x1="44" y1="6" x2="44" y2="18" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<line x1="20" y1="36" x2="44" y2="36" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<line x1="20" y1="46" x2="36" y2="46" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
    ),
    "clock": (
        '<circle cx="32" cy="32" r="26" fill="none" stroke="{stroke}" stroke-width="2"/>'
        '<line x1="32" y1="32" x2="32" y2="18" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<line x1="32" y1="32" x2="44" y2="38" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
    ),
    "location": (
        '<path d="M32,56 C20,44 12,34 12,24 C12,12 20,6 32,6 '
        'C44,6 52,12 52,24 C52,34 44,44 32,56Z" '
        'fill="{color}" stroke="{stroke}" stroke-width="2"/>'
        '<circle cx="32" cy="22" r="8" fill="none" stroke="{stroke}" stroke-width="2"/>'
    ),
    "tag": (
        '<path d="M12,8 L36,8 L56,28 L32,52 L8,32Z" '
        'fill="{color}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
        '<circle cx="26" cy="22" r="3" fill="{stroke}"/>'
    ),
    "cart": (
        '<path d="M8,10 L14,10 L20,38 L48,38 L56,16 L22,16" '
        'fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round"/>'
        '<circle cx="24" cy="50" r="4" fill="{stroke}"/>'
        '<circle cx="46" cy="50" r="4" fill="{stroke}"/>'
    ),
    "eye": (
        '<path d="M4,32 C12,16 52,16 60,32 C52,48 12,48 4,32Z" '
        'fill="none" stroke="{stroke}" stroke-width="2"/>'
        '<circle cx="32" cy="32" r="8" fill="none" stroke="{stroke}" stroke-width="2"/>'
    ),
    "lock": (
        '<rect x="16" y="32" width="32" height="24" rx="4" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<path d="M20,32 L20,22 C20,14 26,8 32,8 C38,8 44,14 44,22 L44,32" '
        'fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>'
    ),
    "phone": (
        '<rect x="16" y="4" width="32" height="56" rx="6" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<line x1="24" y1="48" x2="40" y2="48" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<circle cx="32" cy="12" r="2" fill="{stroke}"/>'
    ),
    "chart": (
        '<line x1="8" y1="52" x2="56" y2="52" stroke="{stroke}" stroke-width="2" '
        'stroke-linecap="round"/>'
        '<line x1="20" y1="52" x2="20" y2="24" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<line x1="32" y1="52" x2="32" y2="12" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
        '<line x1="44" y1="52" x2="44" y2="34" stroke="{stroke}" stroke-width="3" '
        'stroke-linecap="round"/>'
    ),
    "gift": (
        '<rect x="8" y="30" width="48" height="26" rx="2" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<path d="M8,30 L56,30 L56,38 L8,38Z" fill="{color}" '
        'stroke="{stroke}" stroke-width="2"/>'
        '<line x1="32" y1="30" x2="32" y2="56" stroke="{stroke}" stroke-width="2"/>'
        '<path d="M16,16 C16,8 24,8 28,14 L32,22 L36,14 C40,8 48,8 48,16 '
        'C48,24 40,26 32,26 L24,26 C18,26 16,22 16,16Z" '
        'fill="none" stroke="{stroke}" stroke-width="2"/>'
    ),
}

SVG_VIEWBOX = '0 0 64 64'
COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
    "#F0B27A", "#82E0AA", "#F1948A", "#85929E", "#73C6B6",
    "#E59866", "#7FB3D8", "#C39BD3", "#76D7C4", "#F8C471",
]


# ─────────────────────── HELPERS ───────────────────────

def _random_color():
    return random.choice(COLORS)


def _outpath(pattern, ext, w, h, label=""):
    label = label or pattern
    safe = label.lower().replace(" ", "-")
    ts = _ts()
    return f"{safe}-{w}x{h}-{ts}.{ext}"


def _ts():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def _slug(name):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())


# ─────────────────────── PHOTO (picsum.dev + fallbacks) ───────────────────────

_request_counter = 0

def _download(url, outpath, stream=False, quiet=False):
    import requests
    if not quiet:
        print(f"  ↓ {url}")
    r = requests.get(url, timeout=30, stream=stream,
                     headers={"User-Agent": "test-graphics.py/1.0"})
    r.raise_for_status()
    with open(outpath, "wb") as f:
        if stream:
            for chunk in r.iter_content(1024 * 64):
                f.write(chunk)
        else:
            f.write(r.content)
    size = os.path.getsize(outpath)
    if not quiet:
        print(f"  ✓ Saved {outpath}  ({size} bytes)")
    return outpath


# ─────────────────────── THEMED PHOTO (picsum.dev AI генерация) ───────────────────────

PICSUM_CATEGORIES = {
    "nature": "🌿 Nature",
    "animals": "🦊 Animals",
    "food": "🍽️ Food",
    "architecture": "🏛️ Architecture",
    "technology": "💻 Technology",
    "business": "💼 Business",
    "travel": "✈️ Travel",
    "abstract": "🎨 Abstract",
    "people": "🧑 People",
    "fashion": "👗 Fashion",
    "sports": "⚽ Sports",
    "space": "🚀 Space",
    "art": "🖌️ Art",
}

_PICSUM_SESSION = None


def _picsum_session():
    global _PICSUM_SESSION
    if _PICSUM_SESSION is None:
        import requests as req
        s = req.Session()
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })
        _PICSUM_SESSION = s
    return _PICSUM_SESSION


def _picsum_csrf(session):
    import re
    r = session.get("https://picsum.dev/gallery?category=food", timeout=15)
    m = re.search(r'csrf-token"\s+content="([^"]+)"', r.text)
    if not m:
        raise RuntimeError("Cannot fetch CSRF token from picsum.dev")
    return m.group(1)


def _picsum_generate(session, category, prompt, timeout=60):
    csrf = _picsum_csrf(session)
    r = session.post(
        "https://picsum.dev/gallery/generate",
        json={"category": category, "prompt": prompt},
        headers={"X-CSRF-TOKEN": csrf, "Accept": "application/json"},
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Generation failed"))
    return data  # { success, id, url, detail, category, prompt, width, height }


def _picsum_download_resize(session, url, outpath, width=None, height=None, size=None, img_id=None):
    """Скачать сгенерированное фото и привести к нужному размеру.

    Приоритеты:
    1. width/height + img_id: серверный ресайз https://picsum.dev/i/{id}/{w}/{h};
    2. локальный cover-кроп + ресайз из оригинала (fallback, без искажений);
    3. size: квадрат size×size;
    4. ничего: оригинал как есть (1024×1024).
    Формат файла — по расширению outpath (.jpg/.jpeg/.webp/.png), иначе WEBP.
    """
    from PIL import Image
    from io import BytesIO
    ext = os.path.splitext(outpath)[1].lower().lstrip(".") or "webp"
    fmt = {"jpg": "JPEG", "jpeg": "JPEG", "webp": "WEBP", "png": "PNG"}.get(ext, "WEBP")

    if width and height and img_id:
        try:
            r = session.get(f"https://picsum.dev/i/{img_id}/{width}/{height}", timeout=30)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            if (img.width, img.height) == (width, height):
                img.save(outpath, fmt, quality=85)
                return outpath
        except Exception:
            pass  # не серверный ресайз — локальный fallback ниже

    r = session.get(url, timeout=30)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGB")

    if width and height:
        target = width / height
        cur = img.width / img.height
        if cur > target:  # шире цели -> обрезать по ширине
            nw = int(img.height * target)
            x0 = (img.width - nw) // 2
            img = img.crop((x0, 0, x0 + nw, img.height))
        else:             # выше цели -> обрезать по высоте
            nh = int(img.width / target)
            y0 = (img.height - nh) // 2
            img = img.crop((0, y0, img.width, y0 + nh))
        img = img.resize((width, height), Image.LANCZOS)
    elif size:
        img = img.resize((size, size), Image.LANCZOS)

    img.save(outpath, fmt, quality=85)
    return outpath


def cmd_themed(args):
    """test-graphics.py themed <category> <prompt> [output] [width] [height]

    AI-генерация изображения по промту через picsum.dev.
    Категории: nature, animals, food, architecture, technology, business,
               travel, abstract, people, fashion, sports, space, art

    Генератор отдаёт оригинал 1024x1024. При указании width/height запрашивается
    серверный ресайз picsum.dev/i/{id}/{w}/{h}; если он недоступен — локальный
    cover-кроп + ресайз (без искажений).
    Лимит: 10 запросов/мин, генерация 5-20 сек.
    """
    category = args[0] if args else "food"
    prompt = args[1] if len(args) > 1 else category
    ow = int(args[3]) if len(args) > 3 else None
    oh = int(args[4]) if len(args) > 4 else None
    out = args[2] if len(args) > 2 else _outpath(prompt, "webp", ow or 1024, oh or 1024)
    _ensure_dir(os.path.dirname(out)) if os.path.dirname(out) else None

    if category not in PICSUM_CATEGORIES:
        cats = ", ".join(sorted(PICSUM_CATEGORIES.keys()))
        print(f"  ✗ Unknown category '{category}'. Available: {cats}")
        sys.exit(1)

    session = _picsum_session()
    print(f"  → Generating: category={category}, prompt={prompt!r}")
    try:
        data = _picsum_generate(session, category, prompt)
        print(f"  ✓ Generated: {data['url']}")
        print(f"  ✓ Gallery: {data.get('detail')}")
        _picsum_download_resize(session, data["url"], out, width=ow, height=oh, img_id=data.get("id"))
        size = os.path.getsize(out)
        dims = f"{ow}x{oh}" if ow and oh else "1024x1024"
        print(f"  ✓ Saved {out}  ({dims}, {size} bytes)")
        return out
    except Exception as e:
        print(f"  ✗ Generation failed: {e}")
        # Fallback: placehold.co
        try:
            c = COLORS[hash(category) % len(COLORS)].lstrip("#")
            pw, ph = (ow or 512), (oh or 512)
            url = f"https://placehold.co/{pw}x{ph}/{c}/FFFFFF/webp?text={prompt[:30]}"
            return _download(url, out, stream=True)
        except Exception:
            pass
        # Fallback: Pillow gradient
        from PIL import Image, ImageDraw
        c1, c2 = COLORS[hash(category) % len(COLORS)], COLORS[(hash(category) + 1) % len(COLORS)]
        pw, ph = (ow or 1024), (oh or 1024)
        img = Image.new("RGB", (pw, ph))
        for y in range(ph):
            t = y / ph
            color = (
                int(_r(c1, c2, t, 0)),
                int(_r(c1, c2, t, 1)),
                int(_r(c1, c2, t, 2)),
            )
            ImageDraw.Draw(img).line([(0, y), (pw, y)], fill=color)
        img.save(out, "WEBP", quality=70)
        print(f"  ✓ Generated fallback {out}  ({pw}x{ph})")
        return out


# ─────────────────────── BATCH THEMED ───────────────────────

def cmd_batch_themed(args):
    """test-graphics.py batch-themed <category> <prompt> <count> [output_dir] [width] [height]

    Пачка AI-изображений через picsum.dev.
    Каждое изображение получает тот же промпт, но генерируется свой вариант.
    При указании width/height все изображения приводятся к этому размеру.
    """
    category = args[0] if args else "food"
    prompt = args[1] if len(args) > 1 else category
    count = int(args[2]) if len(args) > 2 else 5
    outdir = args[3] if len(args) > 3 else "."
    ow = int(args[4]) if len(args) > 4 else None
    oh = int(args[5]) if len(args) > 5 else None
    _ensure_dir(outdir + "/")

    results = []
    for i in range(count):
        dims = f"{ow}x{oh}" if ow and oh else "1024x1024"
        fname = f"{_slug(prompt)}-{i+1}-{dims}.webp"
        out = os.path.join(outdir, fname)
        try:
            cmd_themed([category, prompt, out] + ([ow, oh] if ow and oh else []))
            results.append(out)
        except Exception as e:
            print(f"  ✗ Failed {i+1}: {e}")

    print(f"\n  ✔ Batch done: {len(results)}/{count} in {outdir}/")
    return results


# ─────────────────────── PHOTO (picsum.dev + fallbacks) ───────────────────────

def cmd_photo(args):
    w = int(args[0]) if len(args) > 0 else W
    h = int(args[1]) if len(args) > 1 else H
    out = args[2] if len(args) > 2 else _outpath("photo", "jpg", w, h)
    _ensure_dir(out)

    import requests
    global _request_counter
    _request_counter += 1

    # 1) picsum.dev — настоящие фото, без ключа
    for url in [
        f"https://picsum.dev/{w}/{h}?random={_request_counter}",
    ]:
        try:
            return _download(url, out, stream=True)
        except requests.RequestException:
            continue

    # 2) loremflickr
    for url in [
        f"https://loremflickr.com/{w}/{h}",
        f"https://loremflickr.com/{w}/{h}/all",
    ]:
        try:
            return _download(url, out, stream=True)
        except requests.RequestException:
            continue

    # 3) placehold.co — цветной блок
    try:
        color = random.choice(COLORS).lstrip("#")
        url = f"https://placehold.co/{w}x{h}/{color}/FFFFFF/png?text={w}%C3%97{h}"
        return _download(url, out.replace(".jpg", ".png"), stream=True)
    except requests.RequestException:
        pass

    # 4) полный fallback — Pillow gradient
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h))
    c1, c2 = random.choice(COLORS), random.choice(COLORS)
    for y in range(h):
        color = (
            int(_r(c1, c2, y / h, 0)),
            int(_r(c1, c2, y / h, 1)),
            int(_r(c1, c2, y / h, 2)),
        )
        ImageDraw.Draw(img).line([(0, y), (w, y)], fill=color)
    img.save(out, "JPEG", quality=70)
    print(f"  ✓ Generated fallback {out}  ({w}×{h})")
    return out


def _r(c1, c2, t, i):
    h1 = int(c1.lstrip("#")[i*2:(i+1)*2], 16)
    h2 = int(c2.lstrip("#")[i*2:(i+1)*2], 16)
    return h1 + int((h2 - h1) * t)


# ─────────────────────── PLACEHOLDER (Pillow) ───────────────────────

def cmd_placeholder(args):
    from PIL import Image, ImageDraw, ImageFont

    w = int(args[0]) if len(args) > 0 else W
    h = int(args[1]) if len(args) > 1 else H
    color = args[2] if len(args) > 2 else random.choice(COLORS)
    text = args[3] if len(args) > 3 else f"{w}×{h}"
    out = args[4] if len(args) > 4 else _outpath("placeholder", "png", w, h, text)
    _ensure_dir(out)

    img = Image.new("RGB", (w, h), color)
    draw = ImageDraw.Draw(img)

    # пытаемся найти шрифт
    font = None
    for fp in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, max(12, min(w, h) // 8))
            except Exception:
                pass
            break

    # текст по центру
    bbox = draw.textbbox((0, 0), text, font=font) if font else draw.textbbox((0, 0), text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = (h - th) // 2
    draw.text((x, y), text, fill="white" if _brightness(color) < 128 else "#333", font=font)

    img.save(out, "PNG")
    print(f"  ✓ Saved {out}  ({w}×{h}, {color})")
    return out


def _brightness(hex_color):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return 128
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000


# ─────────────────────── SVG ICON ───────────────────────

def cmd_icon(args):
    name = args[0].lower()
    color = args[1] if len(args) > 1 else None
    size = int(args[2]) if len(args) > 2 else 64
    out = args[3] if len(args) > 3 else _outpath(f"icon-{name}", "svg", size, size)

    if name not in ICONS:
        available = ", ".join(sorted(ICONS.keys()))
        print(f"  ✗ Unknown icon '{name}'. Available: {available}")
        sys.exit(1)

    if color is None:
        color = _random_color()

    _ensure_dir(out)
    body = ICONS[name].format(color=color, stroke=color)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="{SVG_VIEWBOX}">\n'
        f'  {body}\n'
        f'</svg>'
    )

    # pretty-print
    dom = minidom.parseString(svg)
    pretty = dom.toprettyxml(indent="  ", encoding=None)
    # убираем <?xml?>
    lines = pretty.splitlines()
    lines = [l for l in lines if not l.startswith("<?xml")]
    content = "\n".join(lines).strip()

    with open(out, "w") as f:
        f.write(content)
    print(f"  ✓ Saved {out}  ({size}×{size}, {color})")
    return out


# ─────────────────────── BATCH PHOTOS ───────────────────────

def cmd_batch_photos(args):
    count = int(args[0]) if args else 5
    outdir = args[1] if len(args) > 1 else "."
    _ensure_dir(outdir + "/")

    sizes = [(800, 600), (1920, 1080), (400, 300), (640, 480), (1200, 800),
             (300, 400), (200, 200), (100, 100), (600, 400), (800, 800)]
    results = []
    for i in range(count):
        w, h = random.choice(sizes)
        fname = f"photo-{i+1}-{w}x{h}-{_ts()}.jpg"
        out = os.path.join(outdir, fname)
        try:
            cmd_photo([str(w), str(h), out])
            results.append(out)
        except Exception as e:
            print(f"  ✗ Failed photo {i+1}: {e}")
    print(f"\n  ✔ Batch done: {len(results)}/{count} photos in {outdir}/")
    return results


# ─────────────────────── BATCH ICONS ───────────────────────

def cmd_batch_icons(args):
    count = int(args[0]) if args else 5
    outdir = args[1] if len(args) > 1 else "."
    _ensure_dir(outdir + "/")

    names = list(ICONS.keys())
    results = []
    for i in range(count):
        name = random.choice(names)
        color = _random_color()
        size = random.choice([32, 48, 64, 96])
        fname = f"icon-{name}-{size}x{size}-{_ts()}.svg"
        out = os.path.join(outdir, fname)
        try:
            cmd_icon([name, color, str(size), out])
            results.append(out)
        except Exception as e:
            print(f"  ✗ Failed icon {i+1}: {e}")
    print(f"\n  ✔ Batch done: {len(results)}/{count} icons in {outdir}/")
    return results


# ─────────────────────── DOWNLOAD ICONS (lucide.dev) ───────────────────────

def cmd_download_icons(args):
    names_str = args[0] if args else "star,heart,home"
    outdir = args[1] if len(args) > 1 else "."
    _ensure_dir(outdir + "/")

    names = [n.strip().lower() for n in names_str.split(",") if n.strip()]
    import requests

    results = []
    for name in names:
        url = f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg"
        out = os.path.join(outdir, f"{name}.svg")
        try:
            print(f"  ↓ {url}")
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(out, "w") as f:
                    f.write(r.text)
                print(f"  ✓ Saved {out}")
                results.append(out)
            else:
                print(f"  ✗ {name}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    print(f"\n  ✔ Downloaded {len(results)}/{len(names)} icons to {outdir}/")
    return results


# ─────────────────────── LUCIDE SINGLE ───────────────────────

def cmd_lucide(args):
    name = args[0].lower() if args else "star"
    outdir = args[1] if len(args) > 1 else "."
    _ensure_dir(outdir + "/")

    import requests
    url = f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg"
    out = os.path.join(outdir, f"{name}.svg")
    print(f"  ↓ {url}")
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        with open(out, "w") as f:
            f.write(r.text)
        print(f"  ✓ Saved {out}")
    else:
        print(f"  ✗ HTTP {r.status_code} — icon '{name}' not found")
        sys.exit(1)


# ─────────────────────── LIST ICONS ───────────────────────

def cmd_list_icons(_=None):
    print(f"Available icons ({len(ICONS)}):")
    for name in sorted(ICONS.keys()):
        print(f"  • {name}")


# ─────────────────────── AVATAR (ui-avatars.com) ───────────────────────

def cmd_avatar(args):
    name = args[0] if args else "User"
    out = None
    params = {"name": name}

    i = 1
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            key = a[2:]
            i += 1
            if i < len(args):
                params[key] = args[i]
        else:
            out = a
            break
        i += 1

    params.setdefault("size", "64")
    params.setdefault("background", "random")
    params.setdefault("color", "fff")
    params.setdefault("uppercase", "true")

    if out is None:
        slug = _slug(name)
        sz = params["size"]
        ext = "svg" if params.get("format") == "svg" else "png"
        out = _outpath(f"avatar-{slug}", ext, sz, sz)

    _ensure_dir(out)
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v)
    url = f"https://ui-avatars.com/api/?{qs}"
    return _download(url, out, stream=True)


# ─────────────────────── MAIN ───────────────────────

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]
    rest = args[1:]

    commands = {
        "photo": cmd_photo,
    "placeholder": cmd_placeholder,
    "icon": cmd_icon,
    "themed": cmd_themed,
    "batch-photos": cmd_batch_photos,
    "batch-themed": cmd_batch_themed,
    "batch-icons": cmd_batch_icons,
    "download-icons": cmd_download_icons,
    "lucide": cmd_lucide,
        "avatar": cmd_avatar,
        "list-icons": cmd_list_icons,
        "help": lambda _: print(__doc__),
    }

    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        print("Available: photo, placeholder, icon, avatar, themed, batch-photos, batch-icons, batch-themed, download-icons, lucide, list-icons")
        sys.exit(1)

    commands[cmd](rest)


if __name__ == "__main__":
    main()
