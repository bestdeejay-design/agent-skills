#!/usr/bin/env python3
"""raster_to_svg_mcp.py — MCP server wrapping raster_to_svg.py over stdio.

Implements the Model Context Protocol as JSON-RPC 2.0 over stdlib pipes:
one JSON object per line on stdin, one JSON object per line on stdout. No
third-party deps (no mcp SDK). A generic MCP client (e.g.
`npx @modelcontextprotocol/inspector -- python3 scripts/raster_to_svg_mcp.py`)
can connect, run initialize, list tools, and call them.

Tools exposed:
  convert  — PNG (base64) -> SVG, same pipeline as the CLI/server
  defaults — tracing parameter schema (defaults/ranges/choices)
  health   — liveness + vtracer-cli availability

The stdio loop reads a line, parses it as a JSON-RPC request, dispatches it,
and writes the response line. Requests without an "id" are notifications and
are not answered. All diagnostics go to stderr; stdout carries only responses.
"""

import argparse
import base64
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import raster_to_svg as r2s  # reuse the CLI's whole pipeline

VERSION = "1.0.0"

CHOICES = {k: v["choices"] for k, v in r2s.PARAMS.items() if v["type"] == "choice"}
INT_RANGES = {k: (v["min"], v["max"]) for k, v in r2s.PARAMS.items()
              if v["type"] == "int" and "min" in v}
FLOAT_RANGES = {k: (v["min"], v["max"]) for k, v in r2s.PARAMS.items()
                if v["type"] == "float" and "min" in v}
STR_PARAMS = tuple(k for k, v in r2s.PARAMS.items() if v["type"] == "str")


def _dflt(key):
    return r2s.PARAMS[key]["default"]


def validate_params(params):
    """Validate tracing params against PARAMS; returns (dict, error_or_None)."""
    out = {}
    for key, val in params.items():
        if key in CHOICES:
            if val not in CHOICES[key]:
                return None, (f"недопустимое значение для {key}: {val!r} "
                              f"(допустимо: {', '.join(CHOICES[key])})")
            out[key] = val
        elif key in INT_RANGES:
            if isinstance(val, bool) or not isinstance(val, int):
                return None, f"{key} должен быть целым числом, получено {val!r}"
            lo, hi = INT_RANGES[key]
            if not (lo <= val <= hi):
                return None, f"{key} вне диапазона {lo}..{hi}"
            out[key] = val
        elif key in FLOAT_RANGES:
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                return None, f"{key} должен быть числом, получено {val!r}"
            lo, hi = FLOAT_RANGES[key]
            if not (lo <= val <= hi):
                return None, f"{key} вне диапазона {lo}..{hi}"
            out[key] = val
        elif key in STR_PARAMS:
            if key == "bg" and not r2s.valid_bg(val):
                return None, ("bg должен быть цветом: 'none', 'transparent', "
                              "'#hex' или CSS-имя цвета")
            out[key] = val
        else:
            return None, f"неизвестный параметр: {key}"
    return out, None


def convert_png(data, params):
    """Run the same pipeline as the CLI/server; returns (svg_text, report)."""
    t0 = time.time()
    mode = params.get("mode", _dflt("mode"))
    engine = params.get("engine", _dflt("engine"))
    use_vtracer = False
    if engine == "vtracer":
        if not r2s.vtracer_available():
            raise r2s.PNGError("vtracer-cli не установлен; используйте engine=auto или native")
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
                params.get("seam", _dflt("seam")))
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


def _build_tool_schemas():
    """MCP Tool list: convert (PNG->SVG) plus defaults/health read-only tools."""
    props = {"png_b64": {"type": "string",
                         "description": "PNG-изображение в виде base64-строки"}}
    type_map = {"choice": "string", "int": "integer", "float": "number", "str": "string"}
    for name, spec in r2s.PARAMS.items():
        p = {"description": spec.get("help", "")}
        p["type"] = type_map[spec["type"]]
        if spec["type"] == "choice":
            p["enum"] = list(spec["choices"])
        if spec.get("default") is not None:
            p["default"] = spec["default"]
        if spec["type"] in ("int", "float"):
            if "min" in spec:
                p["minimum"] = spec["min"]
            if "max" in spec:
                p["maximum"] = spec["max"]
        props[name] = p
    convert_tool = {
        "name": "convert",
        "description": "Конвертировать PNG (base64) в SVG, используя тот же "
                       "конвейер, что и CLI/сервер. Возвращает {\"svg\":..., "
                       "\"report\":...}.",
        "inputSchema": {"type": "object", "properties": props,
                        "required": ["png_b64"]},
    }
    defaults_tool = {
        "name": "defaults",
        "description": "Вернуть схему параметров трассировки (значения по "
                       "умолчанию, диапазоны, варианты, ui-подсказки).",
        "inputSchema": {"type": "object", "properties": {}},
    }
    health_tool = {
        "name": "health",
        "description": "Проверка работоспособности сервера и доступности vtracer-cli.",
        "inputSchema": {"type": "object", "properties": {}},
    }
    return [convert_tool, defaults_tool, health_tool]


TOOLS = _build_tool_schemas()


def _result(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message}}


def _tool_text(req_id, text):
    return _result(req_id, {"content": [{"type": "text", "text": text}],
                            "isError": False})


def _tool_error(req_id, message):
    return _result(req_id, {"content": [{"type": "text", "text": message}],
                            "isError": True})


def _tool_convert(req_id, args):
    png_b64 = args.get("png_b64")
    if not isinstance(png_b64, str) or not png_b64:
        return _tool_error(req_id, "параметр png_b64 обязателен (base64 PNG)")
    try:
        data = base64.b64decode(png_b64)
    except Exception:
        return _tool_error(req_id, "не удалось раскодировать png_b64: некорректные base64-данные")
    if not data.startswith(r2s.PNG_SIG):
        return _tool_error(req_id, "переданные данные не являются PNG-файлом (неверная сигнатура)")
    tracing = {k: v for k, v in args.items() if k != "png_b64"}
    params, err = validate_params(tracing)
    if err:
        return _tool_error(req_id, err)
    try:
        svg_text, report = convert_png(data, params)
    except r2s.PNGError as exc:
        return _tool_error(req_id, f"ошибка декодирования PNG: {exc}")
    except (OSError, RuntimeError) as exc:
        return _tool_error(req_id, f"ошибка конвертации: {exc}")
    except Exception as exc:  # engine-level failure must not kill the server
        return _tool_error(req_id, f"непредвиденная ошибка движка: {exc}")
    payload = json.dumps({"svg": svg_text, "report": report}, ensure_ascii=False)
    return _tool_text(req_id, payload)


def _handle_tools_call(req_id, params):
    name = params.get("name")
    args = params.get("arguments") or {}
    if name == "convert":
        return _tool_convert(req_id, args)
    if name == "defaults":
        return _tool_text(req_id, json.dumps(r2s.params_schema(), ensure_ascii=False))
    if name == "health":
        return _tool_text(req_id, json.dumps(
            {"ok": True, "version": VERSION,
             "vtracer_available": r2s.vtracer_available()}, ensure_ascii=False))
    return _error(req_id, -32602, f"неизвестный инструмент: {name}")


def handle_request(obj):
    """Dispatch one JSON-RPC object; return a response dict or None (notification)."""
    if not isinstance(obj, dict):
        return _error(None, -32600, "некорректный JSON-RPC объект")
    method = obj.get("method")
    req_id = obj.get("id")
    params = obj.get("params") or {}

    # Notifications (no id) are not answered.
    if req_id is None and method is not None:
        return None

    if method == "initialize":
        return _result(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "raster_to_svg_mcp", "version": VERSION},
        })
    if method == "ping":
        return _result(req_id, {})
    if method == "tools/list":
        return _result(req_id, {"tools": TOOLS})
    if method == "tools/call":
        return _handle_tools_call(req_id, params)
    return _error(req_id, -32601, f"метод не найден: {method}")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="raster_to_svg_mcp",
        description="MCP server (JSON-RPC 2.0 over stdio) for PNG->SVG conversion.")
    p.add_argument("--version", action="version", version=f"raster_to_svg_mcp {VERSION}")
    try:
        p.parse_args(argv)
    except SystemExit as exc:
        return 1 if exc.code else 0

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                sys.stderr.write(f"[mcp] некорректный JSON: {exc}\n")
                continue
            resp = handle_request(obj)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
