#!/usr/bin/env python3
"""raster_to_svg.py — convert a PNG image into a vector SVG.

Engines:
  * vtracer-cli  — high-quality color tracing (used when installed)
  * native       — built-in stdlib tracer: median-cut quantization +
                   contour tracing with quadratic Bezier fitting, or
                   a geometric mosaic mode.

Pure Python 3 stdlib (zlib, struct, subprocess, xml.etree). No pip deps.
Exit codes: 0 = ok, 1 = input/usage error, 2 = engine failure.
"""

import argparse
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from collections import defaultdict
from xml.etree import ElementTree

PROG = "raster_to_svg"
VERSION = "1.0.0"

PNG_SIG = b"\x89PNG\r\n\x1a\n"
ALPHA_MIN = 128  # pixels with alpha below this are treated as transparent

# Adam7 interlace passes: (x_start, y_start, x_step, y_step)
ADAM7 = [
    (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8),
    (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2),
]

CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


class PNGError(Exception):
    """Malformed or unsupported PNG input."""


# ---------------------------------------------------------------------------
# PNG decoder (stdlib only)
# ---------------------------------------------------------------------------

def _unfilter(raw, stride, height, bpp):
    """Reverse the per-scanline filters (0 None, 1 Sub, 2 Up, 3 Avg, 4 Paeth)."""
    out = bytearray()
    prev = bytearray(stride)
    pos = 0
    for _ in range(height):
        f = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out += line
        prev = line
    return bytes(out)


def _parse_scanline(line, w, bd, ct, ch, pal, trns):
    """Convert one decoded scanline into RGBA bytes."""
    out = bytearray()
    if bd == 8:
        for i in range(w):
            base = i * ch
            if ct == 0:
                v = line[base]
                out += bytes((v, v, v, 255))
            elif ct == 2:
                out += bytes(line[base:base + 3] + b"\xff")
            elif ct == 3:
                idx = line[base]
                r, g, b = pal[idx]
                a = trns[idx] if trns else 255
                out += bytes((r, g, b, a))
            elif ct == 4:
                v, a = line[base], line[base + 1]
                out += bytes((v, v, v, a))
            else:  # ct == 6
                out += bytes(line[base:base + 4])
    elif bd in (1, 2, 4):
        maxv = (1 << bd) - 1
        for i in range(w):
            bitpos = i * bd
            byte_idx = bitpos >> 3
            shift = 8 - bd - (bitpos & 7)
            val = (line[byte_idx] >> shift) & maxv
            if ct == 0:
                v = val * 255 // maxv
                out += bytes((v, v, v, 255))
            else:
                r, g, b = pal[val]
                a = trns[val] if trns else 255
                out += bytes((r, g, b, a))
    else:  # bd == 16: keep the high byte (lossy but pragmatic)
        for i in range(w):
            base = i * ch * 2
            if ct == 0:
                v = line[base]
                out += bytes((v, v, v, 255))
            elif ct == 2:
                out += bytes((line[base], line[base + 2], line[base + 4], 255))
            elif ct == 4:
                out += bytes((line[base], line[base], line[base], line[base + 2]))
            else:
                out += bytes((line[base], line[base + 2], line[base + 4], line[base + 6]))
    return bytes(out)


def decode_png(data):
    """Decode PNG bytes into (width, height, rgba bytearray w*h*4)."""
    if not data.startswith(PNG_SIG):
        raise PNGError("not a PNG file (bad signature)")
    pos = 8
    idat = []
    w = h = bd = ct = interlace = None
    pal = None
    trns = None
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            if length < 13:
                raise PNGError("truncated IHDR")
            w, h, bd, ct, comp, filt, interlace = struct.unpack(">IIBBBBB", chunk[:13])
            if comp != 0 or filt != 0:
                raise PNGError("unsupported compression/filter method")
            if bd not in (1, 2, 4, 8, 16):
                raise PNGError(f"unsupported bit depth {bd}")
            if ct not in CHANNELS:
                raise PNGError(f"unsupported color type {ct}")
            if bd < 8 and ct not in (0, 3):
                raise PNGError("bit depth < 8 only valid for gray/palette")
        elif ctype == b"PLTE":
            pal = [(chunk[i], chunk[i + 1], chunk[i + 2]) for i in range(0, len(chunk) - 2, 3)]
        elif ctype == b"tRNS":
            if ct == 3:
                trns = list(chunk)
            elif ct == 0 and len(chunk) >= 2:
                trns = struct.unpack(">H", chunk[:2])[0]
            elif ct == 2 and len(chunk) >= 6:
                trns = struct.unpack(">HHH", chunk[:6])
        elif ctype == b"IDAT":
            idat.append(chunk)
        elif ctype == b"IEND":
            break
    if None in (w, h, bd, ct, interlace):
        raise PNGError("missing IHDR")
    if ct == 3 and not pal:
        raise PNGError("palette image without PLTE")
    if not idat:
        raise PNGError("missing IDAT")
    try:
        raw = zlib.decompress(b"".join(idat))
    except zlib.error as exc:
        raise PNGError(f"corrupt IDAT stream: {exc}") from exc

    ch = CHANNELS[ct]
    bpp = (bd * ch + 7) // 8  # bytes per pixel used by filters
    rgba = bytearray(w * h * 4)

    def fill_line(line, x0, y0, step):
        """Parse one scanline and write RGBA pixels at (x0 + i*step, y0)."""
        line_rgba = _parse_scanline(line, w, bd, ct, ch, pal, trns) if False else None
        # _parse_scanline works on the full width; for interlace we parse the
        # sub-width, so rebuild a width-aware parser inline:
        return line_rgba

    def parse_sub(scanline, sw):
        return _parse_scanline(scanline, sw, bd, ct, ch, pal, trns)

    if interlace == 0:
        stride = (w * bd * ch + 7) // 8
        lines = _unfilter(raw, stride, h, bpp)
        for y in range(h):
            row = parse_sub(lines[y * stride:(y + 1) * stride], w)
            rgba[y * w * 4:(y + 1) * w * 4] = row
    else:
        pos = 0
        for x0, y0, dx, dy in ADAM7:
            sw = (w - x0 + dx - 1) // dx if w > x0 else 0
            sh = (h - y0 + dy - 1) // dy if h > y0 else 0
            if sw == 0 or sh == 0:
                continue
            stride = (sw * bd * ch + 7) // 8
            sub_raw = _unfilter(raw[pos:pos + sh * (stride + 1)], stride, sh, bpp)
            pos += sh * (stride + 1)
            for j in range(sh):
                row = parse_sub(sub_raw[j * stride:(j + 1) * stride], sw)
                yy = y0 + j * dy
                for i in range(sw):
                    xx = x0 + i * dx
                    dst = (yy * w + xx) * 4
                    rgba[dst:dst + 4] = row[i * 4:(i + 1) * 4]
    return w, h, rgba


# ---------------------------------------------------------------------------
# Quantization (median cut over the color histogram)
# ---------------------------------------------------------------------------

def build_histogram(rgba, w, h):
    hist = {}
    n = w * h
    for i in range(n):
        base = i * 4
        if rgba[base + 3] < ALPHA_MIN:
            continue
        key = (rgba[base], rgba[base + 1], rgba[base + 2])
        hist[key] = hist.get(key, 0) + 1
    return hist


def median_cut(hist, n_colors):
    """Return a palette of up to n_colors (r,g,b) tuples, deterministic."""
    if len(hist) <= n_colors:
        return [c for c, _ in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0]))]
    boxes = [list(hist.items())]
    while len(boxes) < n_colors:
        best = None
        best_score = -1.0
        for box in boxes:
            if len(box) < 2:
                continue
            total = sum(cnt for _, cnt in box)
            for axis in range(3):
                lo = min(p[axis] for p, _ in box)
                hi = max(p[axis] for p, _ in box)
                score = (hi - lo) * total
                if score > best_score:
                    best_score, best = score, box
        if best is None:
            break
        axis = max(range(3), key=lambda a: (
            max(p[a] for p, _ in best) - min(p[a] for p, _ in best)))
        best.sort(key=lambda kv: kv[0][axis])
        total = sum(cnt for _, cnt in best)
        acc = 0
        split = 0
        for i, (_, cnt) in enumerate(best):
            acc += cnt
            if acc * 2 >= total:
                split = i + 1
                break
        if split == 0 or split >= len(best):
            split = len(best) // 2 or 1
        boxes.remove(best)
        boxes.append(best[:split])
        boxes.append(best[split:])
    palette = []
    for box in boxes:
        tot = sum(cnt for _, cnt in box) or 1
        r = sum(p[0] * cnt for p, cnt in box) // tot
        g = sum(p[1] * cnt for p, cnt in box) // tot
        b = sum(p[2] * cnt for p, cnt in box) // tot
        palette.append((r, g, b))
    return palette


def assign_colors(rgba, w, h, palette):
    """Map every pixel to a palette index; 255 marks transparent pixels."""
    labels = bytearray(w * h)
    n = w * h
    for i in range(n):
        base = i * 4
        if rgba[base + 3] < ALPHA_MIN:
            labels[i] = 255
            continue
        r, g, b = rgba[base], rgba[base + 1], rgba[base + 2]
        best = 0
        best_d = 1 << 62
        for j, (pr, pg, pb) in enumerate(palette):
            d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if d < best_d:
                best_d = d
                best = j
        labels[i] = best
    return labels


def mean_color_error(rgba, w, h, labels, palette):
    """Average RGB distance between original and quantized color (opaque px)."""
    total = 0
    count = 0
    n = w * h
    for i in range(n):
        if labels[i] == 255:
            continue
        base = i * 4
        pr, pg, pb = palette[labels[i]]
        total += (abs(rgba[base] - pr) + abs(rgba[base + 1] - pg)
                  + abs(rgba[base + 2] - pb))
        count += 1
    return (total / (3 * count)) if count else 0.0


# ---------------------------------------------------------------------------
# Contour tracing (native engine)
# ---------------------------------------------------------------------------

def extract_edges(mask, w, h):
    """Return the set of boundary edges of the mask, as ((x1,y1),(x2,y2))."""
    edges = set()
    for y in range(h):
        row = y * w
        for x in range(w):
            if not mask[row + x]:
                continue
            if x == 0 or not mask[row + x - 1]:
                edges.add(((x, y), (x, y + 1)))
            if x == w - 1 or not mask[row + x + 1]:
                edges.add(((x + 1, y), (x + 1, y + 1)))
            if y == 0 or not mask[row - w + x]:
                edges.add(((x, y), (x + 1, y)))
            if y == h - 1 or not mask[row + w + x]:
                edges.add(((x, y + 1), (x + 1, y + 1)))
    return edges


def build_adjacency(edges):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    for v in adj:
        adj[v].sort()  # deterministic traversal order
    return adj


def choose_next(cur, prev, adj, used):
    cands = [v for v in adj[cur]
             if v != prev and frozenset((cur, v)) not in used]
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0]
    if prev is None:
        return cands[0]
    dx = cur[0] - prev[0]
    dy = cur[1] - prev[1]
    # priority: straight > left turn > right turn (grid-aligned edges)
    for target in ((cur[0] + dx, cur[1] + dy),
                   (cur[0] - dy, cur[1] + dx),
                   (cur[0] + dy, cur[1] - dx)):
        if target in cands:
            return target
    return cands[0]


def trace_mask_cycles(mask, w, h):
    """Extract closed vertex cycles along the mask boundary."""
    edges = extract_edges(mask, w, h)
    if not edges:
        return []
    adj = build_adjacency(edges)
    used = set()
    cycles = []
    # deterministic start: smallest vertex (y, then x) among remaining edges
    while edges:
        start = min((a for e in edges for a in e),
                    key=lambda p: (p[1], p[0]))
        cycle = [start]
        prev = None
        cur = start
        while True:
            nxt = choose_next(cur, prev, adj, used)
            if nxt is None:
                break
            edge = frozenset((cur, nxt))
            used.add(edge)
            edges.discard(tuple(sorted(edge, key=lambda p: (p[1], p[0]))))
            cycle.append(nxt)
            if nxt == start:
                break
            prev, cur = cur, nxt
        if len(cycle) > 3:
            cycles.append(cycle[:-1])  # drop the duplicated start point
    return cycles


def dp_simplify(points, eps):
    """Douglas-Peucker polyline simplification (recursive)."""
    if len(points) <= 2:
        return points
    eps = max(eps, 0.01)

    def dist(p, a, b):
        ax, ay = a
        bx, by = b
        px, py = p
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        cx, cy = ax + t * dx, ay + t * dy
        return math.hypot(px - cx, py - cy)

    def rec(pts):
        if len(pts) <= 2:
            return pts
        dmax = 0.0
        idx = 0
        for i in range(1, len(pts) - 1):
            d = dist(pts[i], pts[0], pts[-1])
            if d > dmax:
                dmax, idx = d, i
        if dmax > eps:
            left = rec(pts[:idx + 1])
            right = rec(pts[idx:])
            return left[:-1] + right
        return [pts[0], pts[-1]]

    return rec(points)


def split_corners(points, corner_deg):
    """Split a polyline into segments at sharp turns (corner detection)."""
    if len(points) < 4:
        return [points]
    segs = []
    cur = [points[0], points[1]]
    threshold = 180.0 - corner_deg
    for i in range(2, len(points) - 1):
        v1x = points[i][0] - points[i - 1][0]
        v1y = points[i][1] - points[i - 1][1]
        v2x = points[i + 1][0] - points[i][0]
        v2y = points[i + 1][1] - points[i][1]
        l1 = math.hypot(v1x, v1y)
        l2 = math.hypot(v2x, v2y)
        if l1 < 1e-9 or l2 < 1e-9:
            cur.append(points[i])
            continue
        cos_a = (v1x * v2x + v1y * v2y) / (l1 * l2)
        cos_a = max(-1.0, min(1.0, cos_a))
        angle = math.degrees(math.acos(cos_a))
        if angle < threshold:
            cur.append(points[i])
            segs.append(cur)
            cur = [points[i]]
        else:
            cur.append(points[i])
    cur.append(points[-1])
    segs.append(cur)
    return segs


def fit_quad(points):
    """Least-squares quadratic Bezier control point for a point segment."""
    p0, pn = points[0], points[-1]
    n = len(points) - 1
    if n < 2:
        return None
    num_x = num_y = 0.0
    den = 0
    for i in range(1, n):
        t = i / n
        w = 2.0 * t * (1.0 - t)
        if w < 1e-9:
            continue
        inv = 1.0 - t
        num_x += (points[i][0] - inv * inv * p0[0] - t * t * pn[0]) / w
        num_y += (points[i][1] - inv * inv * p0[1] - t * t * pn[1]) / w
        den += 1
    if den == 0:
        return None
    return (num_x / den, num_y / den)


def fmt_num(v):
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".") or "0"


def polygon_to_path(points, corner_deg, eps):
    """Convert a closed polygon to an SVG path 'd' string with Bezier curves."""
    pts = dp_simplify(points, eps)
    if len(pts) < 3:
        return None
    segs = split_corners(pts, corner_deg)
    parts = [f"M {fmt_num(pts[0][0])} {fmt_num(pts[0][1])}"]
    for seg in segs:
        if len(seg) < 2:
            continue
        if len(seg) == 2:
            parts.append(f"L {fmt_num(seg[1][0])} {fmt_num(seg[1][1])}")
        else:
            q = fit_quad(seg)
            if q is None:
                parts.append(f"L {fmt_num(seg[-1][0])} {fmt_num(seg[-1][1])}")
            else:
                parts.append(
                    f"Q {fmt_num(q[0])} {fmt_num(q[1])} "
                    f"{fmt_num(seg[-1][0])} {fmt_num(seg[-1][1])}")
    parts.append("Z")
    return " ".join(parts)


def polygon_area(points):
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def trace_native_contour(rgba, w, h, n_colors, smooth, corner, seam):
    """Full native color tracing pipeline: quantize -> masks -> cycles -> paths."""
    t0 = time.time()
    hist = build_histogram(rgba, w, h)
    if not hist:
        raise PNGError("image is fully transparent")
    palette = median_cut(hist, n_colors)
    labels = assign_colors(rgba, w, h, palette)
    layers = []  # (hex, d, area)
    for cidx, color in enumerate(palette):
        mask = bytearray(w * h)
        for i, v in enumerate(labels):
            if v == cidx:
                mask[i] = 1
        cycles = trace_mask_cycles(mask, w, h)
        if not cycles:
            continue
        d_parts = []
        area = 0.0
        for cyc in cycles:
            d = polygon_to_path(cyc, corner, smooth)
            if d:
                d_parts.append(d)
                area += polygon_area(cyc)
        if not d_parts:
            continue
        layers.append(("#%02x%02x%02x" % color, " ".join(d_parts), area))
    layers.sort(key=lambda l: -l[2])  # big areas first (background below)
    mce = mean_color_error(rgba, w, h, labels, palette)
    return layers, mce, time.time() - t0


# ---------------------------------------------------------------------------
# Mosaic mode (native)
# ---------------------------------------------------------------------------

def _shape_for(x, y, shape, seed):
    if shape != "auto":
        return shape
    h = (x * 31 + y * 17 + seed * 131) & 0x7FFFFFFF
    return ("rect", "circle", "triangle", "diamond")[h % 4]


def trace_native_mosaic(rgba, w, h, cell, shape, gap, seed):
    t0 = time.time()
    elements = []  # (hex, svg_element_string)
    if cell <= 0:
        cell = max(1, min(w, h) // 24)
    for cy in range(0, h, cell):
        chh = min(cell, h - cy)
        for cx in range(0, w, cell):
            cw = min(cell, w - cx)
            hist = {}
            for y in range(cy, cy + chh):
                row = y * w
                for x in range(cx, cx + cw):
                    base = (row + x) * 4
                    if rgba[base + 3] < ALPHA_MIN:
                        continue
                    key = (rgba[base], rgba[base + 1], rgba[base + 2])
                    hist[key] = hist.get(key, 0) + 1
            if not hist:
                continue
            color = max(hist.items(), key=lambda kv: (kv[1], kv[0]))[0]
            hexc = "#%02x%02x%02x" % color
            shp = _shape_for(cx // cell, cy // cell, shape, seed)
            pad = max(0.0, min(0.45, gap)) * cell / 2.0
            x0, y0 = cx + pad, cy + pad
            x1, y1 = cx + cw - pad, cy + chh - pad
            wdt, hgt = x1 - x0, y1 - y0
            if wdt <= 0 or hgt <= 0:
                continue
            cxm, cym = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            if shp == "circle":
                r = min(wdt, hgt) / 2.0
                elements.append((hexc, f'<circle cx="{fmt_num(cxm)}" cy="{fmt_num(cym)}" r="{fmt_num(r)}" fill="{hexc}"/>'))
            elif shp == "triangle":
                elements.append((hexc, f'<polygon points="{fmt_num(cxm)},{fmt_num(y0)} {fmt_num(x0)},{fmt_num(y1)} {fmt_num(x1)},{fmt_num(y1)}" fill="{hexc}"/>'))
            elif shp == "diamond":
                elements.append((hexc, f'<polygon points="{fmt_num(cxm)},{fmt_num(y0)} {fmt_num(x1)},{fmt_num(cym)} {fmt_num(cxm)},{fmt_num(y1)} {fmt_num(x0)},{fmt_num(cym)}" fill="{hexc}"/>'))
            else:  # rect
                elements.append((hexc, f'<rect x="{fmt_num(x0)}" y="{fmt_num(y0)}" width="{fmt_num(wdt)}" height="{fmt_num(hgt)}" fill="{hexc}"/>'))
    return elements, time.time() - t0


# ---------------------------------------------------------------------------
# SVG emission + validation
# ---------------------------------------------------------------------------

def emit_svg(w, h, layers, bg, seam=0.0):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    if bg and bg.lower() != "none":
        parts.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')
    for layer in layers:
        if isinstance(layer, tuple) and len(layer) == 3:
            hexc, d, _area = layer
            stroke = f' stroke="{hexc}" stroke-width="{fmt_num(seam)}"' if seam > 0 else ""
            parts.append(f'<path fill="{hexc}" fill-rule="evenodd" d="{d}"{stroke}/>')
        else:
            hexc, element = layer
            parts.append(element)
    parts.append("</svg>")
    return "\n".join(parts)


def validate_svg(text):
    """Gate: the output must round-trip through an XML parser."""
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        return False, f"invalid SVG XML: {exc}"
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        return False, "root element is not <svg>"
    if "viewBox" not in root.attrib and not (
            "width" in root.attrib and "height" in root.attrib):
        return False, "missing viewBox (and no width/height)"
    return True, "ok"


# ---------------------------------------------------------------------------
# VTracer engine (external binary, used when available)
# ---------------------------------------------------------------------------

def find_vtracer():
    """Return path to the vtracer binary, or None.

    The crates.io package `vtracer-cli` installs an executable named
    `vtracer`; older builds used `vtracer-cli`. Accept both.
    """
    return shutil.which("vtracer") or shutil.which("vtracer-cli")


def vtracer_available():
    return find_vtracer() is not None


def run_vtracer(in_path, out_path, opts):
    vtracer_bin = find_vtracer()
    if vtracer_bin is None:
        raise PNGError("vtracer is not installed")
    cmd = [vtracer_bin, "--input", in_path, "--output", out_path]
    if opts.get("preset") and opts["preset"] != "none":
        cmd += ["--preset", opts["preset"]]
    if opts.get("vtracer_mode") and opts["vtracer_mode"] != "none":
        cmd += ["--mode", opts["vtracer_mode"]]
    if opts.get("colors"):
        cmd += ["--max-colors", str(opts["colors"])]
    if opts.get("color_precision"):
        cmd += ["--color-precision", str(opts["color_precision"])]
    if opts.get("filter_speckle"):
        cmd += ["--filter-speckle", str(opts["filter_speckle"])]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise PNGError(
            f"vtracer-cli failed (exit {proc.returncode}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}")
    return out_path


def svg_stats(text):
    """Lightweight stats from a generated SVG: (width, height, paths, colors).

    Used to enrich reports for engines (vtracer) that do not report
    dimensions internally.
    """
    width = height = None
    m = re.search(r'<svg[^>]*\bwidth="([\d.]+)"', text)
    if m:
        width = float(m.group(1))
    m = re.search(r'<svg[^>]*\bheight="([\d.]+)"', text)
    if m:
        height = float(m.group(1))
    paths = len(re.findall(r"<path\b", text))
    colors = len(set(re.findall(r'\bfill="(#[0-9A-Fa-f]{6})"', text)))
    return width, height, paths, colors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog=PROG,
        description="Convert a PNG image to a vector SVG "
                    "(vtracer-cli when available, built-in tracer otherwise).")
    p.add_argument("-i", "--input", required=True,
                   help="input PNG path, or '-' for stdin")
    p.add_argument("-o", "--output",
                   help="output SVG path, or '-' for stdout "
                        "(default: input path with .svg)")
    p.add_argument("-m", "--mode", choices=("contour", "mosaic"),
                   default="contour", help="vectorization strategy (default: contour)")
    p.add_argument("--engine", choices=("auto", "vtracer", "native"),
                   default="auto",
                   help="engine: auto prefers vtracer-cli if installed "
                        "(default: auto)")
    p.add_argument("--colors", type=int, default=8, metavar="N",
                   help="max colors for native contour tracing (default: 8)")
    p.add_argument("--bg", default="none", metavar="COLOR",
                   help="background rect color, e.g. #ffffff or white "
                        "(default: none, transparent)")
    p.add_argument("--smooth", type=float, default=0.5, metavar="PX",
                   help="native contour: Douglas-Peucker epsilon in px (default: 0.5)")
    p.add_argument("--corner", type=float, default=60.0, metavar="DEG",
                   help="native contour: corner detection threshold in degrees (default: 60)")
    p.add_argument("--seam", type=float, default=0.5, metavar="PX",
                   help="native contour: stroke width to close seams, 0 disables (default: 0.5)")
    p.add_argument("--cell", type=int, default=0, metavar="N",
                   help="mosaic: cell size in px (default: auto)")
    p.add_argument("--shape", choices=("rect", "circle", "triangle", "auto"),
                   default="auto",
                   help="mosaic: primitive shape, auto mixes deterministically (default: auto)")
    p.add_argument("--gap", type=float, default=0.15, metavar="F",
                   help="mosaic: gap as a fraction of the cell (default: 0.15)")
    p.add_argument("--seed", type=int, default=1,
                   help="mosaic: deterministic mix seed (default: 1)")
    p.add_argument("--vtracer-preset", choices=("bw", "poster", "photo", "none"),
                   default="poster",
                   help="vtracer preset (default: poster)")
    p.add_argument("--vtracer-mode", choices=("spline", "polygon", "none"),
                   default="spline",
                   help="vtracer curve mode (default: spline)")
    p.add_argument("--vtracer-color-precision", type=int, metavar="N",
                   help="vtracer bits per RGB channel (1-8)")
    p.add_argument("--vtracer-filter-speckle", type=int, metavar="N",
                   help="vtracer speckle filter radius (px)")
    p.add_argument("--json", action="store_true",
                   help="emit a machine-readable JSON report")
    p.add_argument("--quiet", action="store_true",
                   help="suppress the text report")
    p.add_argument("--version", action="version", version=f"{PROG} {VERSION}")
    return p


def read_input(path):
    if path == "-":
        return sys.stdin.buffer.read()
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError as exc:
        raise PNGError(f"cannot read input: {exc}") from exc


def main(argv=None):
    args = build_parser().parse_args(argv)
    t_start = time.time()
    report = {
        "tool": PROG, "version": VERSION, "mode": args.mode,
        "engine": None, "width": None, "height": None,
        "colors": 0, "paths": 0, "elements": 0,
        "input_bytes": 0, "output_bytes": 0, "compression_ratio": None,
        "mean_color_error": None, "duration_ms": None,
        "warnings": [],
    }

    if args.colors < 1 or args.colors > 256:
        print(f"{PROG}: --colors must be in 1..256", file=sys.stderr)
        return 1

    try:
        data = read_input(args.input)
    except PNGError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return 1
    report["input_bytes"] = len(data)

    out_is_stdout = args.output == "-"
    out_path = args.output
    if out_path is None:
        if args.input == "-":
            print(f"{PROG}: --output required when reading from stdin", file=sys.stderr)
            return 1
        out_path = os.path.splitext(args.input)[0] + ".svg"

    use_vtracer = False
    if args.engine == "vtracer":
        if not vtracer_available():
            print(f"{PROG}: --engine vtracer requested but vtracer-cli is not installed",
                  file=sys.stderr)
            return 2
        use_vtracer = True
    elif args.engine == "auto" and vtracer_available() and args.mode == "contour":
        use_vtracer = True

    try:
        if use_vtracer:
            opts = {
                "preset": args.vtracer_preset,
                "vtracer_mode": args.vtracer_mode,
                "colors": args.colors,
                "color_precision": args.vtracer_color_precision,
                "filter_speckle": args.vtracer_filter_speckle,
            }
            with tempfile.TemporaryDirectory() as tmp:
                in_file = os.path.join(tmp, "input.png")
                out_file = os.path.join(tmp, "output.svg")
                with open(in_file, "wb") as fh:
                    fh.write(data)
                run_vtracer(in_file, out_file, opts)
                with open(out_file, "r", encoding="utf-8") as fh:
                    svg_text = fh.read()
            report["engine"] = "vtracer"
            report["width"], report["height"] = svg_stats(svg_text)[:2]
            report["paths"], report["colors"] = svg_stats(svg_text)[2:]
        else:
            w, h, rgba = decode_png(data)
            report["width"], report["height"] = w, h
            if args.mode == "mosaic":
                elements, dt = trace_native_mosaic(
                    rgba, w, h, args.cell, args.shape, args.gap, args.seed)
                report["engine"] = "native-mosaic"
                report["elements"] = len(elements)
                report["colors"] = len({hexc for hexc, _ in elements})
                report["duration_ms"] = round(dt * 1000)
                svg_text = emit_svg(w, h, elements, args.bg)
            else:
                layers, mce, dt = trace_native_contour(
                    rgba, w, h, args.colors, args.smooth, args.corner, args.seam)
                report["engine"] = "native-contour"
                report["colors"] = len(layers)
                report["paths"] = len(layers)
                report["mean_color_error"] = round(mce, 2)
                report["duration_ms"] = round(dt * 1000)
                svg_text = emit_svg(w, h, layers, args.bg, args.seam)
    except PNGError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return 1
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"{PROG}: engine failure: {exc}", file=sys.stderr)
        return 2

    ok, err = validate_svg(svg_text)
    if not ok:
        print(f"{PROG}: {err}", file=sys.stderr)
        return 2

    out_bytes = svg_text.encode("utf-8")
    report["output_bytes"] = len(out_bytes)
    if report["input_bytes"]:
        report["compression_ratio"] = round(report["input_bytes"] / len(out_bytes), 2)

    if out_is_stdout:
        sys.stdout.write(svg_text)
        if not svg_text.endswith("\n"):
            sys.stdout.write("\n")
    else:
        try:
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(svg_text)
        except OSError as exc:
            print(f"{PROG}: cannot write output: {exc}", file=sys.stderr)
            return 1

    report["duration_ms"] = round(time.time() * 1000 - t_start * 1000)
    report["validation"] = "ok"
    report["output"] = out_path

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif not args.quiet:
        print(f"engine: {report['engine']} | mode: {report['mode']} | "
              f"size: {report['width']}x{report['height']} | "
              f"colors: {report['colors']} | paths: {report['paths']} | "
              f"elements: {report['elements']} | "
              f"input: {report['input_bytes']} B -> output: {report['output_bytes']} B "
              f"(x{report['compression_ratio']}) | {report['duration_ms']} ms | "
              f"validated: {report['validation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())