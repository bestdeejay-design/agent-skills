#!/usr/bin/env python3
"""raster_to_svg_server.py — local web UI for raster_to_svg.py.

Serves a drag-and-drop page (web/index.html) and a POST /convert endpoint
that runs the PNG->SVG conversion in-process. Pure Python 3 stdlib
(http.server), listens on 127.0.0.1 only.

Endpoints:
  GET  /                  -> web/index.html
  GET  /health            -> {"ok": true, "version": ...}
  GET  /defaults          -> {"version": ..., "params": {...}} — single source
                             of truth for every tracing parameter (defaults,
                             ranges, choices, ui hints), read from
                             raster_to_svg.PARAMS
  POST /convert?<params>  -> body = raw PNG bytes; returns JSON
                             {"svg": "...", "report": {...}}
                             errors: 400 bad params/PNG, 413 too large, 415 not PNG
  POST /zip              -> body = JSON {"files": [{"name","svg"}, ...]};
                             returns an application/zip archive (batch pipeline)

Query params (all optional, validated against raster_to_svg.PARAMS): mode,
colors, bg, engine, smooth, corner, seam, cell, shape, gap, seed,
vtracer_preset, vtracer_mode, vtracer_color_precision, vtracer_filter_speckle.

Exit codes: 0 ok, 1 usage error, 2 failed to bind.
"""

import argparse
import io
import json
import os
import sys
import tempfile
import threading
import time
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import raster_to_svg as r2s  # reuse the CLI's whole pipeline

VERSION = "1.1.2"
DEFAULT_PORT = 8642
MAX_MB = 20

CHOICES = {k: v["choices"] for k, v in r2s.PARAMS.items() if v["type"] == "choice"}
INT_RANGES = {k: (v["min"], v["max"]) for k, v in r2s.PARAMS.items()
              if v["type"] == "int" and "min" in v}
FLOAT_RANGES = {k: (v["min"], v["max"]) for k, v in r2s.PARAMS.items()
                if v["type"] == "float" and "min" in v}
STR_PARAMS = tuple(k for k, v in r2s.PARAMS.items() if v["type"] == "str")


def _dflt(key):
    return r2s.PARAMS[key]["default"]


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
            if key == "bg" and not r2s.valid_bg(val):
                return None, ("bg must be a color: 'none', 'transparent', "
                              "'#hex' or a CSS color name")
            out[key] = val
        else:
            return None, f"unknown parameter: {key}"
    return out, None


class _ClientGone(Exception):
    """Raised from a progress callback when the client's connection died."""


def _chunked(frame):
    """Encode one NDJSON frame as a single HTTP/1.1 chunk."""
    data = frame.encode("utf-8")
    return ("%x\r\n" % len(data)).encode("ascii") + data + b"\r\n"


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
        if path in ("/", "/index.html", "/style.css", "/app.js"):
            name = "index.html" if path in ("/", "/index.html") else path.lstrip("/")
            index = os.path.join(HERE, "..", "web", name)
            if not os.path.exists(index):
                self._send_error(500, f"web/{name} not found next to the server script")
                return
            ctype = "text/html; charset=utf-8" if name.endswith(".html") else (
                "text/css; charset=utf-8" if name.endswith(".css")
                else "application/javascript; charset=utf-8")
            with open(index, "rb") as fh:
                body = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/health":
            self._send_json(200, {"ok": True, "version": VERSION,
                                  "vtracer_available": r2s.vtracer_available()})
        elif path == "/defaults":
            self._send_json(200, {"version": VERSION,
                                  "params": r2s.params_schema()})
        else:
            self._send_error(404, f"not found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/zip":
            self._handle_zip()
            return
        if parsed.path == "/export":
            self._handle_export()
            return
        if parsed.path == "/shutdown":
            self._handle_shutdown()
            return
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

        qs = parse_qs(parsed.query)
        stream = qs.pop("progress", ["0"])[0] in ("1", "true")
        params, err = parse_params(qs)
        if err:
            self._send_error(400, err)
            return
        if not stream:
            try:
                svg_text, report = convert(data, params)
            except (r2s.PNGError, OSError) as exc:
                self._send_error(400, str(exc))
                return
            except Exception as exc:  # engine-level failure must not kill the server
                self._send_error(500, f"engine failure: {exc}")
                return
            self._send_json(200, {"svg": svg_text, "report": report})
            return

        # Streaming mode: NDJSON progress events, then a final "done" frame.
        # progress_cb raises _ClientGone when the socket is gone, which aborts
        # the conversion (the client pressed Cancel / closed the tab).
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        def progress_cb(stage, pct):
            try:
                self.wfile.write(_chunked(json.dumps(
                    {"stage": stage, "pct": pct}, ensure_ascii=False) + "\n"))
                self.wfile.flush()
            except OSError:
                raise _ClientGone()

        try:
            svg_text, report = convert(data, params, progress_cb)
        except _ClientGone:
            return  # connection is dead; nothing more to write
        except (r2s.PNGError, OSError) as exc:
            self._write_stream_error(str(exc))
            return
        except Exception as exc:
            self._write_stream_error(f"engine failure: {exc}")
            return

        try:
            self.wfile.write(_chunked(json.dumps(
                {"done": True, "svg": svg_text, "report": report},
                ensure_ascii=False) + "\n"))
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except OSError:
            pass  # client already gone

    def _write_stream_error(self, message):
        try:
            self.wfile.write(_chunked(json.dumps(
                {"error": message}, ensure_ascii=False) + "\n"))
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except OSError:
            pass

    def _handle_zip(self):
        """POST /zip — JSON {"files":[{"name":"a.svg","svg":"..."}...]} -> .zip.

        Used by the batch pipeline (client-side queue): the client converts N
        PNGs via /convert, then asks for one archive instead of N downloads.
        Pure stdlib zipfile — no JSZip on the client.
        """
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            self._send_error(400, "empty body: send {\"files\": [...]}")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            self._send_error(400, f"bad JSON: {exc}")
            return
        files = payload.get("files") if isinstance(payload, dict) else None
        if not isinstance(files, list) or not files:
            self._send_error(400, "expected {\"files\": [{\"name\", \"svg\"}, ...]}")
            return

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, item in enumerate(files):
                if not isinstance(item, dict):
                    self._send_error(400, f"files[{i}] must be an object")
                    return
                name = item.get("name")
                svg = item.get("svg")
                if not isinstance(name, str) or not isinstance(svg, str):
                    self._send_error(400, f"files[{i}] needs string name and svg")
                    return
                if not name.lower().endswith(".svg"):
                    name += ".svg"
                zf.writestr(name, svg.encode("utf-8"))

        body = buf.getvalue()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", 'attachment; filename="raster-to-svg.zip"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_shutdown(self):
        """Stop the server after replying (client can close the tab)."""
        self._send_json(200, {"ok": True, "shutting_down": True})
        threading.Timer(0.2, self.server.shutdown).start()

    def _handle_export(self):
        """POST /export — JSON {"svg":"...","fmt":"dxf"|"eps"} -> converted text.

        Lazily imports scripts/svg_export.py (SVG->DXF / SVG->EPS converters)
        so the server works even before/without that module present.
        """
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            self._send_error(400, "empty body: send {\"svg\": ..., \"fmt\": \"dxf|eps\"}")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            self._send_error(400, f"bad JSON: {exc}")
            return
        svg = payload.get("svg") if isinstance(payload, dict) else None
        fmt = payload.get("fmt") if isinstance(payload, dict) else None
        layers = payload.get("layers", "1") if isinstance(payload, dict) else "1"
        if not isinstance(svg, str) or not svg.strip():
            self._send_error(400, "expected string field \"svg\"")
            return
        if fmt not in ("dxf", "eps"):
            self._send_error(400, "expected \"fmt\": \"dxf\" or \"eps\"")
            return

        export_path = os.path.join(HERE, "svg_export.py")
        if not os.path.exists(export_path):
            self._send_error(501, "svg_export.py not found — DXF/EPS export unavailable")
            return
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("svg_export", export_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            out = mod.svg_to_dxf(svg) if fmt == "dxf" else mod.svg_to_eps(svg)
            if fmt == "dxf" and str(layers) != "1":
                out = _flatten_dxf_layers(out)
        except Exception as exc:
            self._send_error(500, f"export failed: {exc}")
            return
        ctype = "application/dxf" if fmt == "dxf" else "application/postscript"
        body = out.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _flatten_dxf_layers(dxf):
    """Rewrite DXF so every entity lives on layer "0" (drop per-color layers).

    Operates on the R12 text produced by svg_export.svg_to_dxf: it replaces the
    whole TABLES section with a single LAYER "0" definition and renames every
    entity layer reference (group code 8) to "0". Used when the client exports
    DXF with the "layers by color" option turned off.
    """
    lines = dxf.splitlines()
    # find the TABLES section boundaries (code "0" + value "TABLES"/"ENDSEC")
    start = end = None
    i = 0
    while i + 1 < len(lines):
        if lines[i] == "0" and lines[i + 1] == "SECTION":
            j = i + 2
            if j + 1 < len(lines) and lines[j] == "2" and lines[j + 1] == "TABLES":
                start = i
                # find matching ENDSEC
                k = j + 2
                while k + 1 < len(lines):
                    if lines[k] == "0" and lines[k + 1] == "ENDSEC":
                        end = k + 1
                        break
                    k += 1
                break
            i = j + 1
            continue
        i += 1

    tables = ["0", "SECTION", "2", "TABLES",
              "0", "TABLE", "2", "LAYER", "70", "1",
              "0", "LAYER", "2", "0", "70", "64", "62", "7", "6", "CONTINUOUS",
              "0", "ENDTAB",
              "0", "ENDSEC"]
    if start is not None and end is not None:
        lines = lines[:start] + tables + lines[end + 1:]

    out = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        # group code 8 = entity layer name -> rename to "0"
        if lines[i] == "8" and i + 1 < len(lines):
            out.append("0")
            i += 2
            continue
        i += 1
    return "\n".join(out)


def convert(data, params, progress_cb=None):
    """Run the same pipeline as the CLI; returns (svg_text, report)."""
    t0 = time.time()
    mode = params.get("mode", _dflt("mode"))
    engine = params.get("engine", _dflt("engine"))
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
            "preset": params.get("vtracer_preset", _dflt("vtracer_preset")),
            "vtracer_mode": params.get("vtracer_mode", _dflt("vtracer_mode")),
            "colors": params.get("colors", _dflt("colors")),
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
        bg = params.get("bg", _dflt("bg"))
        if bg and bg.lower() != "none":
            w, h = report["width"], report["height"]
            svg_open = svg_text.find("<svg")
            tag_end = svg_text.find(">", svg_open) + 1
            svg_text = svg_text[:tag_end] + (
                f'<rect width="{w}" height="{h}" fill="{bg}"/>') + svg_text[tag_end:]
    else:
        w, h, rgba = r2s.decode_png(data)
        report["width"], report["height"] = w, h
        bg = params.get("bg", _dflt("bg"))
        if mode == "mosaic":
            elements, dt = r2s.trace_native_mosaic(
                rgba, w, h, params.get("cell", _dflt("cell")),
                params.get("shape", _dflt("shape")),
                params.get("gap", _dflt("gap")), params.get("seed", _dflt("seed")))
            report["engine"] = "native-mosaic"
            report["elements"] = len(elements)
            report["colors"] = len({hexc for hexc, _ in elements})
            report["duration_ms"] = round(dt * 1000)
            svg_text = r2s.emit_svg(w, h, elements, bg)
        else:
            layers, mce, dt = r2s.trace_native_contour(
                rgba, w, h, params.get("colors", _dflt("colors")),
                params.get("smooth", _dflt("smooth")),
                params.get("corner", _dflt("corner")),
                params.get("seam", _dflt("seam")), progress_cb)
            report["engine"] = "native-contour"
            report["colors"] = len(layers)
            report["paths"] = len(layers)
            report["mean_color_error"] = round(mce, 2)
            report["duration_ms"] = round(dt * 1000)
            svg_text = r2s.emit_svg(w, h, layers, bg, params.get("seam", _dflt("seam")))

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