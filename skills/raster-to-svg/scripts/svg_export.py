#!/usr/bin/env python3
"""SVG -> DXF (AutoCAD R12 ASCII) and SVG -> EPS (PostScript Level 2) converters.

Pure Python 3 standard library. Consumes the SVG subset emitted by
``raster_to_svg.py`` (paths, rects, circles, polygons, polylines) and exports
it for laser cutters / CNC / vector editors (DXF) or print / Illustrator (EPS).

Public API:
    svg_to_dxf(svg_text) -> str
    svg_to_eps(svg_text) -> str
    svg_export_formats() -> ["dxf", "eps"]
    main(argv=None)
"""

import argparse
import math
import re
import sys


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

# Common CSS color names; unknown names fall back to black upstream. The exact
# color always travels through the layer name (hex) in DXF, so this is only a
# convenience for --bg CSS names.
_CSS_COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "lime": (0, 255, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "cyan": (0, 255, 255), "aqua": (0, 255, 255),
    "magenta": (255, 0, 255), "fuchsia": (255, 0, 255), "gray": (128, 128, 128),
    "grey": (128, 128, 128), "darkgray": (169, 169, 169),
    "darkgrey": (169, 169, 169), "lightgray": (211, 211, 211),
    "lightgrey": (211, 211, 211), "silver": (192, 192, 192),
    "maroon": (128, 0, 0), "olive": (128, 128, 0), "purple": (128, 0, 128),
    "teal": (0, 128, 128), "navy": (0, 0, 128), "orange": (255, 165, 0),
    "pink": (255, 192, 203), "brown": (165, 42, 42), "gold": (255, 215, 0),
    "crimson": (220, 20, 60), "indigo": (75, 0, 130), "violet": (238, 130, 238),
    "tomato": (255, 99, 71), "salmon": (250, 128, 114), "khaki": (240, 230, 140),
    "coral": (255, 127, 80), "turquoise": (64, 224, 208), "orchid": (218, 112, 214),
    "plum": (221, 160, 221), "tan": (210, 180, 140), "azure": (240, 255, 255),
    "beige": (245, 245, 220), "ivory": (255, 255, 240), "lavender": (230, 230, 250),
    "skyblue": (135, 206, 235), "steelblue": (70, 130, 180),
    "forestgreen": (34, 139, 34), "seagreen": (46, 139, 87),
    "royalblue": (65, 105, 225), "hotpink": (255, 105, 180),
    "deeppink": (255, 20, 147), "dodgerblue": (30, 144, 255),
    "springgreen": (0, 255, 127), "chartreuse": (127, 255, 0),
}


def _parse_color(s):
    """Return (r, g, b) or None for 'none'/transparent/unknown."""
    if s is None:
        return None
    s = s.strip().lower()
    if s in ("none", "transparent"):
        return None
    if s.startswith("#"):
        h = s[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            try:
                return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
            except ValueError:
                return None
        return None
    return _CSS_COLORS.get(s)


def _hex_of(rgb):
    if rgb is None:
        return None
    return "%02X%02X%02X" % rgb


# Standard AutoCAD color index (ACI) palette used to approximate arbitrary
# fills; the exact color always travels in the layer name (hex).
_STD_ACI = [
    (1, (255, 0, 0)), (2, (255, 255, 0)), (3, (0, 255, 0)),
    (4, (0, 255, 255)), (5, (0, 0, 255)), (6, (255, 0, 255)),
    (7, (255, 255, 255)), (8, (128, 128, 128)), (9, (192, 192, 192)),
]


def _aci_of(rgb):
    if rgb is None:
        return 7
    best, best_d = 7, None
    for aci, c in _STD_ACI:
        d = (rgb[0] - c[0]) ** 2 + (rgb[1] - c[1]) ** 2 + (rgb[2] - c[2]) ** 2
        if best_d is None or d < best_d:
            best_d, best = d, aci
    return best


# ---------------------------------------------------------------------------
# SVG path parsing
# ---------------------------------------------------------------------------

_CMD_SET = set("MmLlHhVvCcSsQqTtAaZz")
# A token is either a command letter or a number (int/float, optional sign,
# decimal, exponent). Commas/spaces are ignored as separators.
_TOKEN_RE = re.compile(
    r"[MmLlHhVvCcSsQqTtAaZz]"
    r"|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
)


def _quad_to_cubic(x0, y0, x1, y1, x, y):
    c1x = x0 + 2.0 / 3.0 * (x1 - x0)
    c1y = y0 + 2.0 / 3.0 * (y1 - y0)
    c2x = x + 2.0 / 3.0 * (x1 - x)
    c2y = y + 2.0 / 3.0 * (y1 - y)
    return ("C", c1x, c1y, c2x, c2y, x, y)


def _arc_points(x0, y0, rx, ry, phi_deg, large, sweep, x1, y1, n=24):
    """Sample an SVG arc into n line endpoints (excludes the start point)."""
    if rx == 0 or ry == 0:
        return [(x1, y1)]
    phi = math.radians(phi_deg)
    sinp, cosp = math.sin(phi), math.cos(phi)
    dx, dy = (x0 - x1) / 2.0, (y0 - y1) / 2.0
    x0p = cosp * dx + sinp * dy
    y0p = -sinp * dx + cosp * dy
    rx, ry = abs(rx), abs(ry)
    lam = (x0p * x0p) / (rx * rx) + (y0p * y0p) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y0p * y0p - ry * ry * x0p * x0p
    den = rx * rx * y0p * y0p + ry * ry * x0p * x0p
    co = 0.0 if den == 0 else math.sqrt(max(0.0, num / den))
    if large == sweep:
        co = -co
    cxp = co * (rx * y0p / ry)
    cyp = co * (-ry * x0p / rx)
    cx = cosp * x0p - sinp * cyp + (x0 + x1) / 2.0
    cy = sinp * x0p + cosp * cyp + (y0 + y1) / 2.0

    def _pt(ang):
        xx = rx * math.cos(ang)
        yy = ry * math.sin(ang)
        return (cosp * xx - sinp * yy + cx, sinp * xx + cosp * yy + cy)

    def _ang(u, v):
        return math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])

    u = ((x0p - cxp) / rx, (y0p - cyp) / ry)
    v = ((-x0p - cxp) / rx, (-y0p - cyp) / ry)
    theta1 = _ang((1.0, 0.0), u)
    dtheta = _ang(u, v) % (2 * math.pi)
    if sweep == 0 and dtheta > 0:
        dtheta -= 2 * math.pi
    if sweep == 1 and dtheta < 0:
        dtheta += 2 * math.pi
    return [_pt(theta1 + dtheta * k / n) for k in range(1, n + 1)]


def _parse_path(d):
    """Parse an SVG path 'd' into a list of subpaths.

    Each subpath is a list of canonical commands:
        ('M', x, y), ('L', x, y), ('C', x1, y1, x2, y2, x, y), ('Z',)
    Quadratic/smooth/arc commands are normalized to cubic/line segments so
    downstream converters only deal with M/L/C/Z (absolute or relative).
    """
    if not d:
        return []
    tokens = _TOKEN_RE.findall(d)
    groups = []
    cur = None
    for t in tokens:
        if t in _CMD_SET:
            cur = [t, []]
            groups.append(cur)
        elif cur is not None:
            cur[1].append(float(t))
    subpaths = []
    cur_sub = []
    cx = cy = sx = sy = 0.0
    px = py = None  # previous Bezier control point (for S/T smoothing)

    def new_subpath():
        if cur_sub:
            subpaths.append(cur_sub)
        return []

    for cmd, nums in groups:
        if cmd in ("Z", "z"):
            cur_sub.append(("Z",))
            cx, cy = sx, sy
            px = py = None
            continue
        if cmd == "M":
            cur_sub = new_subpath()
            x, y = nums[0], nums[1]
            cx, cy, sx, sy = x, y, x, y
            cur_sub.append(("M", x, y))
            for k in range(2, len(nums), 2):
                cx, cy = nums[k], nums[k + 1]
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "m":
            cur_sub = new_subpath()
            x, y = nums[0] + cx, nums[1] + cy
            cx, cy, sx, sy = x, y, x, y
            cur_sub.append(("M", x, y))
            for k in range(2, len(nums), 2):
                cx, cy = nums[k] + cx, nums[k + 1] + cy
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "L":
            for k in range(0, len(nums), 2):
                cx, cy = nums[k], nums[k + 1]
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "l":
            for k in range(0, len(nums), 2):
                cx, cy = nums[k] + cx, nums[k + 1] + cy
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "H":
            for v in nums:
                cx = v
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "h":
            for v in nums:
                cx += v
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "V":
            for v in nums:
                cy = v
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "v":
            for v in nums:
                cy += v
                cur_sub.append(("L", cx, cy))
            px = py = None
            continue
        if cmd == "C":
            for k in range(0, len(nums), 6):
                x1, y1, x2, y2, x, y = nums[k:k + 6]
                cur_sub.append(("C", x1, y1, x2, y2, x, y))
                px, py, cx, cy = x2, y2, x, y
            continue
        if cmd == "c":
            for k in range(0, len(nums), 6):
                x1, y1, x2, y2, x, y = (nums[k] + cx, nums[k + 1] + cy,
                                        nums[k + 2] + cx, nums[k + 3] + cy,
                                        nums[k + 4] + cx, nums[k + 5] + cy)
                cur_sub.append(("C", x1, y1, x2, y2, x, y))
                px, py, cx, cy = x2, y2, x, y
            continue
        if cmd == "S":
            for k in range(0, len(nums), 4):
                x2, y2, x, y = nums[k:k + 4]
                x1, y1 = (cx, cy) if px is None else (2 * cx - px, 2 * cy - py)
                cur_sub.append(("C", x1, y1, x2, y2, x, y))
                px, py, cx, cy = x2, y2, x, y
            continue
        if cmd == "s":
            for k in range(0, len(nums), 4):
                x2, y2, x, y = (nums[k] + cx, nums[k + 1] + cy,
                                nums[k + 2] + cx, nums[k + 3] + cy)
                x1, y1 = (cx, cy) if px is None else (2 * cx - px, 2 * cy - py)
                cur_sub.append(("C", x1, y1, x2, y2, x, y))
                px, py, cx, cy = x2, y2, x, y
            continue
        if cmd == "Q":
            for k in range(0, len(nums), 4):
                x1, y1, x, y = nums[k:k + 4]
                cur_sub.append(_quad_to_cubic(cx, cy, x1, y1, x, y))
                px, py, cx, cy = x1, y1, x, y
            continue
        if cmd == "q":
            for k in range(0, len(nums), 4):
                x1, y1, x, y = (nums[k] + cx, nums[k + 1] + cy,
                                nums[k + 2] + cx, nums[k + 3] + cy)
                cur_sub.append(_quad_to_cubic(cx, cy, x1, y1, x, y))
                px, py, cx, cy = x1, y1, x, y
            continue
        if cmd == "T":
            for k in range(0, len(nums), 2):
                x, y = nums[k:k + 2]
                x1, y1 = (cx, cy) if px is None else (2 * cx - px, 2 * cy - py)
                cur_sub.append(_quad_to_cubic(cx, cy, x1, y1, x, y))
                px, py, cx, cy = x1, y1, x, y
            continue
        if cmd == "t":
            for k in range(0, len(nums), 2):
                x, y = nums[k] + cx, nums[k + 1] + cy
                x1, y1 = (cx, cy) if px is None else (2 * cx - px, 2 * cy - py)
                cur_sub.append(_quad_to_cubic(cx, cy, x1, y1, x, y))
                px, py, cx, cy = x1, y1, x, y
            continue
        if cmd == "A":
            for k in range(0, len(nums), 7):
                rx, ry, xrot, large, sweep, x, y = nums[k:k + 7]
                for (ax, ay) in _arc_points(cx, cy, rx, ry, xrot, int(large), int(sweep), x, y):
                    cur_sub.append(("L", ax, ay))
                cx, cy = x, y
                px = py = None
            continue
        if cmd == "a":
            for k in range(0, len(nums), 7):
                rx, ry, xrot, large, sweep, dx, dy = nums[k:k + 7]
                x, y = cx + dx, cy + dy
                for (ax, ay) in _arc_points(cx, cy, rx, ry, xrot, int(large), int(sweep), x, y):
                    cur_sub.append(("L", ax, ay))
                cx, cy = x, y
                px = py = None
            continue
    if cur_sub:
        subpaths.append(cur_sub)
    return subpaths


# ---------------------------------------------------------------------------
# SVG document parsing + normalization
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)\b([^>]*)>", re.S)
_ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def _parse_points(s):
    vals = [v for v in re.split(r"[\s,]+\s*", s.strip()) if v != ""]
    pts = []
    for i in range(0, len(vals) - 1, 2):
        pts.append((float(vals[i]), float(vals[i + 1])))
    return pts


def _attrs(tag_body):
    return {m.group(1).lower(): m.group(2) for m in _ATTR_RE.finditer(tag_body)}


def _circle_subpaths(cx, cy, r, seg=32):
    pts = [(cx + r * math.cos(2 * math.pi * i / seg),
            cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    sub = [("M", pts[0][0], pts[0][1])]
    sub += [("L", p[0], p[1]) for p in pts[1:]]
    sub.append(("Z",))
    return [sub]


def _rect_subpaths(x, y, w, h):
    return [[("M", x, y), ("L", x + w, y), ("L", x + w, y + h),
             ("L", x, y + h), ("Z",)]]


def _poly_subpaths(points, closed):
    if not points:
        return []
    sub = [("M", points[0][0], points[0][1])]
    sub += [("L", p[0], p[1]) for p in points[1:]]
    if closed:
        sub.append(("Z",))
    return [sub]


def parse_svg(text):
    """Return (width, height, elements).

    ``elements`` is a list of dicts with keys: subpaths (list of canonical
    subpaths), fill (rgb or None), stroke (rgb or None), sw (stroke width),
    fill_rule (str or None).
    """
    width = height = None
    elements = []
    for m in _TAG_RE.finditer(text):
        name = m.group(1).lower()
        attrs = _attrs(m.group(2))
        if name == "svg":
            w = attrs.get("width")
            if w is not None:
                try:
                    width = float(re.sub(r"[^0-9.]", "", w))
                except ValueError:
                    width = None
            h = attrs.get("height")
            if h is not None:
                try:
                    height = float(re.sub(r"[^0-9.]", "", h))
                except ValueError:
                    height = None
            continue
        if name == "path":
            d = attrs.get("d")
            if not d:
                continue
            elements.append({
                "subpaths": _parse_path(d),
                "fill": _parse_color(attrs.get("fill")),
                "stroke": _parse_color(attrs.get("stroke")),
                "sw": float(attrs.get("stroke-width", "1") or "1"),
                "fill_rule": attrs.get("fill-rule"),
            })
        elif name == "rect":
            try:
                x = float(attrs["x"]); y = float(attrs["y"])
                w = float(attrs["width"]); h = float(attrs["height"])
            except (KeyError, ValueError):
                continue
            elements.append({
                "subpaths": _rect_subpaths(x, y, w, h),
                "fill": _parse_color(attrs.get("fill")),
                "stroke": _parse_color(attrs.get("stroke")),
                "sw": float(attrs.get("stroke-width", "1") or "1"),
                "fill_rule": None,
            })
        elif name == "circle":
            try:
                cx = float(attrs["cx"]); cy = float(attrs["cy"]); r = float(attrs["r"])
            except (KeyError, ValueError):
                continue
            elements.append({
                "subpaths": _circle_subpaths(cx, cy, r),
                "fill": _parse_color(attrs.get("fill")),
                "stroke": _parse_color(attrs.get("stroke")),
                "sw": float(attrs.get("stroke-width", "1") or "1"),
                "fill_rule": None,
            })
        elif name in ("polygon", "polyline"):
            pts = _parse_points(attrs.get("points", ""))
            if not pts:
                continue
            elements.append({
                "subpaths": _poly_subpaths(pts, name == "polygon"),
                "fill": _parse_color(attrs.get("fill")),
                "stroke": _parse_color(attrs.get("stroke")),
                "sw": float(attrs.get("stroke-width", "1") or "1"),
                "fill_rule": None,
            })
    if width is None or height is None:
        bx0 = bx1 = by0 = by1 = None
        for el in elements:
            for sub in el["subpaths"]:
                for c in sub:
                    if c[0] in ("M", "L"):
                        x, y = c[1], c[2]
                    elif c[0] == "C":
                        x, y = c[5], c[6]
                    else:
                        continue
                    bx0 = x if bx0 is None else min(bx0, x)
                    bx1 = x if bx1 is None else max(bx1, x)
                    by0 = y if by0 is None else min(by0, y)
                    by1 = y if by1 is None else max(by1, y)
        if width is None:
            width = bx1 if bx1 is not None else 0.0
        if height is None:
            height = by1 if by1 is not None else 0.0
    return width, height, elements


# ---------------------------------------------------------------------------
# DXF (AutoCAD R12 ASCII) export
# ---------------------------------------------------------------------------

def _fmt(v):
    s = "%.4f" % v
    if s == "-0.0000":
        s = "0.0000"
    return s


def _flatten_subpath(sub, seg=24):
    # Bezier curves are flattened to line segments; LWPOLYLINE carries the
    # resulting vertices (bulge 0) -- simplest robust choice for R12.
    pts = []
    closed = False
    cx = cy = 0.0
    for c in sub:
        if c[0] == "M":
            cx, cy = c[1], c[2]
            pts.append((cx, cy))
        elif c[0] == "L":
            cx, cy = c[1], c[2]
            pts.append((cx, cy))
        elif c[0] == "C":
            x1, y1, x2, y2, x, y = c[1], c[2], c[3], c[4], c[5], c[6]
            for k in range(1, seg + 1):
                t = k / seg
                mt = 1 - t
                bx = mt**3 * cx + 3 * mt * mt * t * x1 + 3 * mt * t * t * x2 + t**3 * x
                by = mt**3 * cy + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t**3 * y
                pts.append((bx, by))
            cx, cy = x, y
        elif c[0] == "Z":
            closed = True
    return pts, closed


def _dxf_lwpolyline(points, closed, layer, aci):
    out = ["0", "LWPOLYLINE", "8", layer, "62", str(aci), "66", "1"]
    for (x, y) in points:
        out += ["10", _fmt(x), "20", _fmt(y)]
    out += ["70", "1" if closed else "0"]
    return out


def svg_to_dxf(svg_text):
    """Convert SVG text to an AutoCAD R12 ASCII DXF string."""
    width, height, elements = parse_svg(svg_text)
    layers = {}
    for el in elements:
        for key in ("fill", "stroke"):
            rgb = el[key]
            if rgb is None:
                continue
            hexc = _hex_of(rgb)
            if hexc not in layers:
                layers[hexc] = _aci_of(rgb)
    if not layers:
        layers["0"] = 7
    ent = []
    for el in elements:
        fill_hex = _hex_of(el["fill"]) if el["fill"] else None
        stroke_hex = _hex_of(el["stroke"]) if el["stroke"] else None
        if fill_hex is None and stroke_hex is None:
            continue
        for sub in el["subpaths"]:
            pts, closed = _flatten_subpath(sub)
            if not pts:
                continue
            if fill_hex is not None:
                ent += _dxf_lwpolyline(pts, closed, fill_hex, layers[fill_hex])
            if stroke_hex is not None:
                ent += _dxf_lwpolyline(pts, False, stroke_hex, layers[stroke_hex])
    lines = []
    lines += ["0", "SECTION", "2", "HEADER", "0", "ENDSEC"]
    lines += ["0", "SECTION", "2", "TABLES"]
    lines += ["0", "TABLE", "2", "LTYPE", "70", "1"]
    lines += ["0", "LTYPE", "2", "CONTINUOUS", "70", "64", "3", "Solid line",
              "72", "65", "73", "0", "40", "0.0"]
    lines += ["0", "ENDTAB"]
    lines += ["0", "TABLE", "2", "LAYER", "70", str(len(layers))]
    for hexc in sorted(layers):
        lines += ["0", "LAYER", "2", hexc, "70", "64", "62", str(layers[hexc]),
                  "6", "CONTINUOUS"]
    lines += ["0", "ENDTAB"]
    lines += ["0", "ENDSEC"]
    lines += ["0", "SECTION", "2", "ENTITIES"]
    lines += ent
    lines += ["0", "ENDSEC"]
    lines += ["0", "EOF"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# EPS (PostScript Level 2) export
# ---------------------------------------------------------------------------

def _eps_fmt(v):
    s = "%.3f" % v
    if s == "-0.000":
        s = "0.000"
    return s


def svg_to_eps(svg_text):
    """Convert SVG text to an EPS (PostScript Level 2) string."""
    width, height, elements = parse_svg(svg_text)
    H = height if height else 0.0
    bx0 = bx1 = by0 = by1 = None

    def _track(x, y):
        nonlocal bx0, bx1, by0, by1
        fx, fy = x, H - y  # SVG y-down -> PS y-up
        bx0 = fx if bx0 is None else min(bx0, fx)
        bx1 = fx if bx1 is None else max(bx1, fx)
        by0 = fy if by0 is None else min(by0, fy)
        by1 = fy if by1 is None else max(by1, fy)

    # BoundingBox from actual (sampled) geometry so curves are not over-estimated
    # by their control polygon; matches the DXF flattening sampling.
    for el in elements:
        for sub in el["subpaths"]:
            for (x, y) in _flatten_subpath(sub)[0]:
                _track(x, y)
    if bx0 is None:
        bx0, bx1, by0, by1 = 0.0, width or 0.0, 0.0, H or 0.0

    out = []
    out.append("%!PS-Adobe-3.0 EPSF-3.0")
    out.append("%%%%BoundingBox: %s %s %s %s" % (
        _eps_fmt(bx0), _eps_fmt(by0), _eps_fmt(bx1), _eps_fmt(by1)))
    out.append("%%Pages: 1")
    out.append("%%EndComments")
    out.append("%%Page: 1 1")

    def _path_lines(sub):
        lines = []
        for c in sub:
            if c[0] == "M":
                lines.append("%s %s moveto" % (_eps_fmt(c[1]), _eps_fmt(H - c[2])))
            elif c[0] == "L":
                lines.append("%s %s lineto" % (_eps_fmt(c[1]), _eps_fmt(H - c[2])))
            elif c[0] == "C":
                lines.append("%s %s %s %s %s %s curveto" % (
                    _eps_fmt(c[1]), _eps_fmt(H - c[2]),
                    _eps_fmt(c[3]), _eps_fmt(H - c[4]),
                    _eps_fmt(c[5]), _eps_fmt(H - c[6])))
            elif c[0] == "Z":
                lines.append("closepath")
        return lines

    for el in elements:
        fill_rgb = el["fill"]
        stroke_rgb = el["stroke"]
        if fill_rgb is None and stroke_rgb is None:
            continue
        for sub in el["subpaths"]:
            if not sub:
                continue
            plines = _path_lines(sub)
            if fill_rgb is not None:
                out.extend(plines)
                r, g, b = fill_rgb
                out.append("%.4f %.4f %.4f setrgbcolor" % (r / 255, g / 255, b / 255))
                out.append("eofill" if el["fill_rule"] == "evenodd" else "fill")
            if stroke_rgb is not None:
                out.extend(plines)
                r, g, b = stroke_rgb
                out.append("%.4f %.4f %.4f setrgbcolor" % (r / 255, g / 255, b / 255))
                out.append("%.3f setlinewidth" % el["sw"])
                out.append("stroke")
    out.append("%%EOF")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def svg_export_formats():
    """Return the list of supported export formats."""
    return ["dxf", "eps"]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert an SVG (as emitted by raster_to_svg.py) to DXF or EPS.")
    parser.add_argument("input", nargs="?", help="input SVG file (ignored with --stdin)")
    parser.add_argument("--stdin", action="store_true", help="read SVG from stdin")
    parser.add_argument("--fmt", choices=svg_export_formats(), default="dxf",
                        help="output format (default: dxf)")
    parser.add_argument("-o", "--output", default=None, help="output file (default: stdout)")
    args = parser.parse_args(argv)
    if not args.stdin and not args.input:
        sys.stderr.write("svg_export: error: either an input file or --stdin is required\n")
        return 1
    try:
        if args.stdin:
            svg_text = sys.stdin.read()
        else:
            with open(args.input, "r", encoding="utf-8") as f:
                svg_text = f.read()
        if args.fmt == "dxf":
            out = svg_to_dxf(svg_text)
        else:
            out = svg_to_eps(svg_text)
    except Exception as exc:  # noqa: BLE001 - surface any parse/IO error as exit 1
        sys.stderr.write("svg_export: error: %s\n" % exc)
        return 1
    try:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out)
        else:
            sys.stdout.write(out)
    except OSError as exc:
        sys.stderr.write("svg_export: error writing output: %s\n" % exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
