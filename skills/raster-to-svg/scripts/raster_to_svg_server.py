#!/usr/bin/env python3
"""raster_to_svg_server.py — local web UI for raster_to_svg.py.

Serves a drag-and-drop page (web/index.html) and a POST /convert endpoint
that runs the PNG->SVG conversion in-process. Pure Python 3 stdlib
(http.server), listens on 127.0.0.1 only.

Endpoints:
  GET  /                  -> web/index.html
  GET  /health            -> {"ok": true, "version": ...}
  POST /convert?<params>  -> body = raw PNG bytes; returns JSON
                             {"svg": "...", "report": {...}}
                             errors: 400 bad params/PNG, 413 too large, 415 not PNG

Query params (all optional, validated): mode, colors, bg, engine, smooth,
corner, seam, cell, shape, gap, seed, vtracer_preset, vtracer_mode,
vtracer_color_precision, vtracer_filter_speckle.

Exit codes: 0 ok, 1 usage error, 2 failed to bind.
"""

import argparse
import json
import os
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import raster_to_svg as r2s  # reuse the CLI's whole pipeline

VERSION = "1.0.0"
DEFAULT_PORT = 8642
MAX_MB = 20

# parameter whitelists / ranges (mirror the CLI)
CHOICES = {
    "mode": ("contour", "mosaic"),
    "engine": ("auto", "vtracer", "native"),
    "shape": ("auto", "rect", "circle", "triangle"),
    "vtracer_preset": ("bw", "poster", "photo", "none"),
    "vtracer_mode": ("spline", "polygon", "none"),
}
INT_RANGES = {
    "colors": (1, 256),
    "cell": (0, 100000),
    "seed": (-10**9, 10**9),
    "vtracer_color_precision": (1, 8),
    "vtracer_filter_speckle": (0, 1000),
}
FLOAT_RANGES = {
    "smooth": (0.0, 100.0),
    "corner": (0.0, 180.0),
    "seam": (0.0, 20.0),
    "gap": (0.0, 0.45),
}
STR_PARAMS = ("bg",)


def parse_params(qs):
    """Validate query params; returns (dict, error_string_or_None)."""
    out = {}
    for key, values in qs.items():
        val = values[-1]
        if key in CHOICES:
            if val not in CHOICES[key]:
                return None, f"bad value for {key}: {val!r} (choose from {', '.join(CHOICES[key])})"
            out[key] = val
        elif key in INT_RANGES:
            try:
                iv = int(val)
            except ValueError:
                return None, f"{key} must be an integer, got {val!r}"
            lo, hi = INT_RANGES[key]
            if not (lo <= iv <= hi):
                return None, f"{key} out of range {lo}..{hi}"
            out[key] = iv
        elif key in FLOAT_RANGES:
            try:
                fv = float(val)
            except ValueError:
                return None, f"{key} must be a number, got {val!r}"
            lo, hi = FLOAT_RANGES[key]
            if not (lo <= fv <= hi):
                return None, f"{key} out of range {lo}..{hi}"
            out[key] = fv
        elif key in STR_PARAMS:
            out[key] = val
        else:
            return None, f"unknown parameter: {key}"
    return out, None


class Handler(BaseHTTPRequestHandler):
    server_version = f"raster-to-svg-web/{VERSION}"

    def log_message(self, fmt, *args):
        sys.stderr.write("[web] %s\n" % (fmt % args))

    def _send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code, message):
        self._send_json(code, {"error": message})

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            index = os.path.join(HERE, "..", "web", "index.html")
            if not os.path.exists(index):
                self._send_error(500, "web/index.html not found next to the server script")
                return
            with open(index, "rb") as fh:
                body = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/health":
            self._send_json(200, {"ok": True, "version": VERSION,
                                  "vtracer_available": r2s.vtracer_available()})
        else:
            self._send_error(404, f"not found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/convert":
            self._send_error(404, f"not found: {parsed.path}")
            return

        length = int(self.headers.get("Content-Length") or 0)
        max_bytes = getattr(self.server, "max_bytes", MAX_MB * 1024 * 1024)
        if length == 0:
            self._send_error(400, "empty body: send PNG bytes")
            return
        if length > max_bytes:
            self._send_error(413, f"file too large: {length} bytes (limit {max_bytes})")
            return
        data = self.rfile.read(length)

        if not data.startswith(r2s.PNG_SIG):
            self._send_error(415, "not a PNG file (bad signature)")
            return

        params, err = parse_params(parse_qs(parsed.query))
        if err:
            self._send_error(400, err)
            return

        try:
            svg_text, report = convert(data, params)
        except (r2s.PNGError, OSError) as exc:
            self._send_error(400, str(exc))
            return
        except Exception as exc:  # engine-level failure must not kill the server
            self._send_error(500, f"engine failure: {exc}")
            return

        self._send_json(200, {"svg": svg_text, "report": report})


def convert(data, params):
    """Run the same pipeline as the CLI; returns (svg_text, report)."""
    t0 = time.time()
    mode = params.get("mode", "contour")
    engine = params.get("engine", "auto")
    use_vtracer = False
    if engine == "vtracer":
        if not r2s.vtracer_available():
            raise r2s.PNGError("vtracer-cli is not installed; use engine=auto or native")
        use_vtracer = True
    elif engine == "auto" and r2s.vtracer_available() and mode == "contour":
        use_vtracer = True

    report = {"mode": mode, "engine": None, "width": None, "height": None,
              "colors": 0, "paths": 0, "elements": 0,
              "input_bytes": len(data), "output_bytes": 0,
              "compression_ratio": None, "mean_color_error": None,
              "duration_ms": None}

    if use_vtracer:
        opts = {
            "preset": params.get("vtracer_preset", "poster"),
            "vtracer_mode": params.get("vtracer_mode", "spline"),
            "colors": params.get("colors", 8),
            "color_precision": params.get("vtracer_color_precision"),
            "filter_speckle": params.get("vtracer_filter_speckle"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            in_file = os.path.join(tmp, "input.png")
            out_file = os.path.join(tmp, "output.svg")
            with open(in_file, "wb") as fh:
                fh.write(data)
            r2s.run_vtracer(in_file, out_file, opts)
            with open(out_file, "r", encoding="utf-8") as fh:
                svg_text = fh.read()
        report["engine"] = "vtracer"
        report["output_bytes"] = len(svg_text.encode("utf-8"))
        report["width"], report["height"] = r2s.svg_stats(svg_text)[:2]
        report["paths"], report["colors"] = r2s.svg_stats(svg_text)[2:]
    else:
        w, h, rgba = r2s.decode_png(data)
        report["width"], report["height"] = w, h
        bg = params.get("bg", "none")
        if mode == "mosaic":
            elements, dt = r2s.trace_native_mosaic(
                rgba, w, h, params.get("cell", 0), params.get("shape", "auto"),
                params.get("gap", 0.15), params.get("seed", 1))
            report["engine"] = "native-mosaic"
            report["elements"] = len(elements)
            report["colors"] = len({hexc for hexc, _ in elements})
            report["duration_ms"] = round(dt * 1000)
            svg_text = r2s.emit_svg(w, h, elements, bg)
        else:
            layers, mce, dt = r2s.trace_native_contour(
                rgba, w, h, params.get("colors", 8),
                params.get("smooth", 0.5), params.get("corner", 60.0),
                params.get("seam", 0.5))
            report["engine"] = "native-contour"
            report["colors"] = len(layers)
            report["paths"] = len(layers)
            report["mean_color_error"] = round(mce, 2)
            report["duration_ms"] = round(dt * 1000)
            svg_text = r2s.emit_svg(w, h, layers, bg, params.get("seam", 0.5))

    ok, err = r2s.validate_svg(svg_text)
    if not ok:
        raise RuntimeError(err)
    out_bytes = svg_text.encode("utf-8")
    report["output_bytes"] = len(out_bytes)
    report["compression_ratio"] = round(len(data) / len(out_bytes), 2)
    report["duration_ms"] = round((time.time() - t0) * 1000)
    return svg_text, report


def main(argv=None):
    p = argparse.ArgumentParser(prog="raster_to_svg_server",
                                description="Local web UI for PNG->SVG conversion.")
    p.add_argument("--host", default="127.0.0.1", help="bind host (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"bind port (default: {DEFAULT_PORT})")
    p.add_argument("--max-mb", type=int, default=MAX_MB, help=f"max upload size in MB (default: {MAX_MB})")
    p.add_argument("--no-browser", action="store_true", help="do not open the browser")
    args = p.parse_args(argv)

    if not (0 < args.port < 65536):
        print(f"raster_to_svg_server: bad port {args.port}", file=sys.stderr)
        return 1

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    httpd.max_bytes = args.max_mb * 1024 * 1024
    url = f"http://{args.host}:{args.port}/"
    print(f"raster-to-svg web UI: {url}")
    print(f"vtracer-cli: {'available' if r2s.vtracer_available() else 'not installed (native tracer only)'}")
    print("Ctrl+C to stop")
    if not args.no_browser:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())