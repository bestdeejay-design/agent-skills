# raster-to-svg

**Convert PNG images to clean vector SVG locally — no uploads, no dependencies, no cloud.**

Two tracing engines in one tool: a built-in pure-Python tracer (Bezier contours / mosaic primitives) and an optional **vtracer** binary (high-quality color tracing, 2–4× faster on photos). A polished dark-themed web UI wraps it all: drag & drop, live preview, a ×4 magnifier over the result, quick presets, progress bar with ETA, and SVG code view.

![UI](docs/ui_v2_final.png)

## Features

- **Two engines**: `native` (Python stdlib, zero deps) and `vtracer` (when installed); `auto` picks vtracer when available
- **Two native modes**: `contour` (smooth Bezier paths, holes) and `mosaic` (rect/circle/triangle/diamond primitives)
- **vtracer knobs in UI**: preset (poster/photo/bw), color precision, speckle filter
- **Color palette editor**: swatches grouped by color — click to recolor, «→» to merge two colors into one
- **Export**: DXF R12 (layers per fill color, flattenable), EPS, PNG (client-side canvas, ×1–×4 scale)
- **Batch processing**: convert multiple PNGs with current settings, download all SVGs as one `.zip`
- **Smart UI**: options that don't apply to the selected engine are hidden automatically; 12 quick presets (flat, minimal, line art, icon, logo, photo-flat, photo, duotone, vintage, B&W, mosaic poster, mosaic circles) with a «custom» badge when tweaked by hand; photo prep (blur + color steps) before tracing; sticky preview column; upscale ×2/×4 for small sources; JPG/WEBP accepted (re-encoded locally to PNG)
- **Progress bar** with empirical ETA (accurate within ~10%)
- **100% local**: files never leave your machine — server runs on `127.0.0.1`
- **Deterministic output**, SVG validated before write, JSON report (CLI), MIT license

## Requirements

- Python 3 (stdlib only — no pip packages)
- Optional: `vtracer` binary (`cargo install vtracer-cli --version 1.0.0-alpha.3`, executable name `vtracer`)

## Quick start

You need **Python 3 only** — the tracer is pure stdlib, no `pip install` required. `vtracer` is optional (see [Engine notes](#engine-notes)).

### macOS — one-click desktop app

1. Download **`R2S.app.zip`** from the [latest release](releases/latest)
2. Unzip it (double-click), drag `R2S.app` to your Desktop or Applications
3. Double-click `R2S.app` — it starts the local server in the background and opens the browser

The bundle is self-contained: `scripts/` + `web/` live inside the app, so it works from any location. To stop the server use the **⏻ Остановить сервер** button in the web UI header.

### macOS / Linux — from source

```bash
git clone https://github.com/bestdeejay-design/raster-to-svg.git
cd raster-to-svg
python3 scripts/raster_to_svg_server.py --port 8642
# open http://127.0.0.1:8642/  (the browser opens automatically)
```

Press `Ctrl+C` in the terminal to stop the server.

### Windows — from source

1. Install Python 3 from [python.org](https://www.python.org/downloads/) — **tick “Add python.exe to PATH”** during setup
2. Download the repo: green **Code → Download ZIP** (or `git clone` if you have Git)
3. Double-click **`scripts\start_server.bat`** — it starts the server and opens the browser
   (or run `python scripts\raster_to_svg_server.py` in a terminal; `Ctrl+C` stops it)

### CLI

```bash
# Basic conversion (Bezier contour, auto engine)
python3 scripts/raster_to_svg.py -i logo.png -o logo.svg

# Fewer colors, white background
python3 scripts/raster_to_svg.py -i logo.png -o logo.svg --colors 4 --bg white

# Mosaic mode
python3 scripts/raster_to_svg.py -i photo.png -o photo_mosaic.svg --mode mosaic

# Force vtracer + JSON report
python3 scripts/raster_to_svg.py -i photo.png -o out.svg --engine vtracer --json
```

## Engine notes

| | native | vtracer |
|---|---|---|
| Install | built-in | optional binary |
| Modes | contour / mosaic | spline (preset-driven) |
| Photos (1024²) | ~9 s, 8 paths | ~2 s, 2014 paths |
| Flat graphics | compact, exact | fast, slightly heavier |
| CLI flags | `--smooth --corner --seam --cell --shape` | `--vtracer-preset --vtracer-mode --vtracer-color-precision --vtracer-filter-speckle` |

Full benchmark: `BENCHMARK.md` (included in the `agent-skills` distribution).

## Repository layout

```
raster-to-svg/
├── SKILL.md            # skill documentation (agent-readable)
├── skill.json          # skill manifest
├── scripts/
│   ├── raster_to_svg.py          # engines + CLI (Python 3 stdlib)
│   ├── raster_to_svg_server.py   # local web server
│   ├── svg_export.py             # SVG → DXF R12 / EPS converters
│   └── raster_to_svg_mcp.py      # optional MCP server (AI agents)
├── web/                # UI: index.html + style.css + app.js (vanilla)
├── evals/             # fixtures + pixel QA + generator
└── docs/              # screenshots
```

## License

MIT © 2026 [bestdeejay-design](https://github.com/bestdeejay-design)

---

*Also distributed as part of [agent-skills](https://github.com/bestdeejay-design/agent-skills) — a collection of skills for AI agents. Russian readme: [README.ru.md](README.ru.md).*
