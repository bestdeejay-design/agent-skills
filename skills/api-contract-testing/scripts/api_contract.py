#!/usr/bin/env python3
"""Validate an API contract against an OpenAPI 3.x specification.

Reads an OpenAPI spec (JSON or a YAML subset) from a file or URL, enumerates
the declared operations (paths + webhooks), checks the spec's internal
consistency, and compares it against an optional manifest of expected
contracts ("METHOD path [expected_status]" per line). In live mode (default)
each manifest endpoint is also probed over HTTP and the result is compared
with the expected status.

Pure Python 3 stdlib (argparse, json, os, pathlib, sys, urllib.request) — no
third-party dependencies. YAML is handled by a small built-in subset parser
(block mappings/sequences, flow collections, quoted scalars) that covers the
OpenAPI keys this tool needs; it is NOT a full YAML implementation.

Usage:
    python3 api_contract.py --spec openapi.json --offline --json
    python3 api_contract.py --spec openapi.yaml --manifest endpoints.txt
    python3 api_contract.py --spec-url https://example.com/openapi.json \
        --base-url https://api.example.com --manifest endpoints.txt

Exit codes: 0 conformant (or offline-ok), 1 violations, 2 spec/parse/run error
"""
import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head", "trace")

# minimal YAML subset parser (block + flow; no anchors/aliases/tags)
def _strip_comment(line):
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q: q = None
            continue
        if ch in "'\"": q = ch
        elif ch == "#": return line[:i]
    return line
def _split_key(content):
    q = None
    for i, ch in enumerate(content):
        if q:
            if ch == q: q = None
            continue
        if ch in "'\"": q = ch
        elif ch == ":": return content[:i].strip(), content[i + 1:]
    return content.strip(), ""
def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] in "'\"" and v[-1] == v[0]: return v[1:-1]
    return v
def _is_map_start(item):
    if not item or item[0] in "'\"{[": return False
    q = None
    for ch in item:
        if q:
            if ch == q: q = None
            continue
        if ch in "'\"": q = ch
        elif ch == ":": return True
    return False
def _split_flow(text):
    parts, depth, q, cur = [], 0, None, []
    for ch in text:
        if q:
            cur.append(ch)
            if ch == q: q = None
            continue
        if ch in "'\"": q = ch; cur.append(ch)
        elif ch in "{[":
            depth += 1; cur.append(ch)
        elif ch in "}]":
            depth -= 1; cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip()); cur = []
        else:
            cur.append(ch)
    tail = "".join(cur).strip()
    if tail: parts.append(tail)
    return parts
def _parse_flow(text):
    text = text.strip()
    if not text: return None
    if text[0] == "{":
        inner = text[1:]
        if inner.endswith("}"): inner = inner[:-1]
        out = {}
        for part in _split_flow(inner):
            if not part: continue
            if ":" in part:
                k, v = part.split(":", 1)
                out[_unquote(k)] = _parse_scalar(v.strip())
            else:
                out[_unquote(part)] = None
        return out
    if text[0] == "[":
        inner = text[1:]
        if inner.endswith("]"): inner = inner[:-1]
        return [_parse_scalar(p) for p in _split_flow(inner) if p]
    return _parse_scalar(text)
def _parse_scalar(value):
    value = value.strip()
    if not value: return None
    if value[0] in "{[":
        return _parse_flow(value)
    if value[0] in "'\"":
        return _unquote(value)
    low = value.lower()
    if low in ("null", "~"): return None
    if low == "true": return True
    if low == "false": return False
    try: return int(value)
    except ValueError: pass
    try: return float(value)
    except ValueError: pass
    return value
def _parse_block(lines, start, indent):
    def nxt(j):
        return lines[j][0] if j < len(lines) and lines[j][0] > indent else None
    result, kind, i = None, None, start
    while i < len(lines):
        ind, content = lines[i]
        if ind < indent: break
        if ind > indent: raise ValueError("invalid YAML indentation")
        if content.startswith("-"):
            if kind is None: kind, result = "seq", []
            elif kind != "seq": break
            item = content[1:].strip()
            if not item:
                v, i = (None, i + 1) if nxt(i + 1) is None else _parse_block(lines, i + 1, nxt(i + 1))
                result.append(v)
            elif _is_map_start(item):
                mapping = {}
                key, rest = _split_key(item)
                key = _unquote(key)
                if rest.strip() == "":
                    mapping[key], i = (None, i + 1) if nxt(i + 1) is None else _parse_block(lines, i + 1, nxt(i + 1))
                else:
                    mapping[key] = _parse_scalar(rest); i += 1
                if nxt(i) is not None:
                    extra, i = _parse_block(lines, i, nxt(i))
                    if isinstance(extra, dict): mapping.update(extra)
                result.append(mapping)
            else:
                result.append(_parse_scalar(item)); i += 1
        else:
            if kind is None: kind, result = "map", {}
            elif kind != "map": break
            key, rest = _split_key(content)
            if not key: raise ValueError(f"invalid YAML line: {content!r}")
            key = _unquote(key)
            rest = rest.strip()
            if rest in ("|", ">", "|-", ">-", "|+", ">+"):
                parts, j = [], i + 1
                if nxt(j) is not None:
                    while j < len(lines) and lines[j][0] >= nxt(j):
                        parts.append(lines[j][1]); j += 1
                result[key] = "\n".join(parts); i = j
            elif rest == "":
                result[key], i = (None, i + 1) if nxt(i + 1) is None else _parse_block(lines, i + 1, nxt(i + 1))
            else:
                result[key] = _parse_scalar(rest); i += 1
    return result, i
def parse_yaml(text):
    lines = []
    for raw in text.splitlines():
        line = _strip_comment(raw).rstrip()
        if not line.strip(): continue
        lines.append((len(line) - len(line.lstrip(" ")), line.strip()))
    if not lines: return {}
    value, _ = _parse_block(lines, 0, lines[0][0])
    return value if isinstance(value, dict) else {"value": value}

# spec loading and endpoint enumeration
def load_spec(args):
    if args.spec:
        path = Path(args.spec)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in (".yaml", ".yml"):
            return parse_yaml(text)
        return json.loads(text)
    if args.spec_url:
        try:
            with urllib.request.urlopen(args.spec_url, timeout=30) as resp:
                data = resp.read().decode("utf-8")
        except (urllib.error.URLError, OSError) as exc:
            raise ValueError(f"cannot fetch {args.spec_url}: {exc}") from exc
        if args.spec_url.lower().endswith((".yaml", ".yml")):
            return parse_yaml(data)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return parse_yaml(data)
    raise ValueError("provide --spec <path> or --spec-url <URL>")
def iter_operations(spec):
    ops = []
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict): continue
        for method in HTTP_METHODS:
            op = item.get(method)
            if isinstance(op, dict):
                ops.append((method.upper(), path, op))
    for name, item in (spec.get("webhooks") or {}).items():
        if not isinstance(item, dict): continue
        for method in HTTP_METHODS:
            op = item.get(method)
            if isinstance(op, dict):
                ops.append((method.upper(), f"webhook:{name}", op))
    return ops
def resolve_base_url(spec, args):
    if args.base_url: return args.base_url
    servers = spec.get("servers")
    if isinstance(servers, list) and servers and isinstance(servers[0], dict):
        url = servers[0].get("url")
        if url: return url
    return os.environ.get("APITEST_BASE_URL")
def collect_refs(node, refs):
    if isinstance(node, dict):
        if "$ref" in node: refs.append(node["$ref"])
        for value in node.values(): collect_refs(value, refs)
    elif isinstance(node, list):
        for value in node: collect_refs(value, refs)
def resolve_ref(spec, ref):
    if not ref.startswith("#/"): return True
    current = spec
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current: return False
        current = current[part]
    return True

# checks
def check_internal(spec, ops, report):
    refs = []
    collect_refs(spec, refs)
    for ref in sorted({r for r in refs if r.startswith("#/")}):
        if not resolve_ref(spec, ref):
            report["contract_violations"].append(
                {"method": "", "path": "", "expected": "resolvable $ref",
                 "actual": f"unresolved $ref: {ref}", "severity": "error"})
    seen = set()
    for method, path, _op in ops:
        key = (method, path)
        if key in seen:
            report["contract_violations"].append(
                {"method": method, "path": path, "expected": "unique operation",
                 "actual": "duplicate operation", "severity": "warning"})
        seen.add(key)
    for method, path, op in ops:
        responses = op.get("responses")
        if not isinstance(responses, dict) or not responses:
            report["contract_violations"].append(
                {"method": method, "path": path, "expected": "at least one response",
                 "actual": "no responses declared", "severity": "warning"})
    if not ops:
        report["contract_violations"].append(
            {"method": "", "path": "", "expected": "at least one operation",
             "actual": "spec declares no operations under paths/webhooks",
             "severity": "warning"})
def load_manifest(path):
    entries = []
    for lineno, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"): continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(
                f"manifest line {lineno}: expected 'METHOD path [expected_status]', "
                f"got: {line!r}")
        entries.append({"method": parts[0].upper(), "path": parts[1],
                        "expected": parts[2] if len(parts) > 2 else None})
    return entries
def expected_matches(actual_codes, expected):
    if expected == "default": return "default" in actual_codes
    if len(expected) == 3 and expected[1:] == "xx":
        return any(c.isdigit() and c[0] == expected[0] for c in actual_codes)
    return expected in actual_codes
def live_status_matches(actual, expected):
    if expected == "default": return True
    if len(expected) == 3 and expected[1:] == "xx":
        return str(actual)[0] == expected[0]
    return str(actual) == expected
def live_matches_declared(actual, declared):
    if "default" in declared: return True
    return any(live_status_matches(actual, c) for c in declared)
def check_manifest(spec, manifest, report):
    op_map = {(m, p): op for m, p, op in iter_operations(spec)}
    for entry in manifest:
        op = op_map.get((entry["method"], entry["path"]))
        if op is None:
            report["missing_from_spec"].append(
                {"method": entry["method"], "path": entry["path"],
                 "expected": entry["expected"] or "any"})
            continue
        if entry["expected"]:
            declared = list((op.get("responses") or {}).keys())
            if not expected_matches(declared, entry["expected"]):
                report["contract_violations"].append(
                    {"method": entry["method"], "path": entry["path"],
                     "expected": entry["expected"],
                     "actual": ",".join(declared) if declared else "none",
                     "severity": "error"})
def check_live(spec, manifest, base_url, report):
    if not manifest: return
    if not base_url:
        report["errors"].append(
            "live mode needs a base URL: pass --base-url, add servers[0].url "
            "to the spec, or set APITEST_BASE_URL")
        return
    op_map = {(m, p): op for m, p, op in iter_operations(spec)}
    for entry in manifest:
        op = op_map.get((entry["method"], entry["path"]))
        if op is None: continue
        url = base_url.rstrip("/") + "/" + entry["path"].lstrip("/")
        try:
            request = urllib.request.Request(url, method=entry["method"])
            with urllib.request.urlopen(request, timeout=10) as resp:
                actual = resp.status
        except urllib.error.HTTPError as exc:
            actual = exc.code
        except (urllib.error.URLError, OSError) as exc:
            report["errors"].append(
                f"live check failed for {entry['method']} {entry['path']}: {exc}")
            return
        if entry["expected"]:
            ok = live_status_matches(actual, entry["expected"])
            expected_label = entry["expected"]
        else:
            declared = list((op.get("responses") or {}).keys())
            ok = live_matches_declared(actual, declared)
            expected_label = ",".join(declared) if declared else "any"
        if not ok:
            report["contract_violations"].append(
                {"method": entry["method"], "path": entry["path"],
                 "expected": expected_label, "actual": str(actual),
                 "severity": "error"})
def render_text(report):
    lines = [f"endpoints_count: {report['endpoints_count']}"]
    if report["missing_from_spec"]:
        lines += ["missing_from_spec:"] + [f"  {m['method']} {m['path']} (expected {m['expected']})" for m in report["missing_from_spec"]]
    if report["contract_violations"]:
        lines += ["contract_violations:"] + [f"  [{v['severity']}] {v['method']} {v['path']}: expected {v['expected']}, actual {v['actual']}" for v in report["contract_violations"]]
    lines.append(f"conformant: {report['conformant']}")
    if report["errors"]:
        lines += ["errors:"] + [f"  {e}" for e in report["errors"]]
    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(
        prog="api_contract.py",
        description="Validate an API contract against an OpenAPI 3.x spec "
                    "(JSON or YAML) and an optional manifest of expected endpoints.")
    parser.add_argument("--spec", default="", help="Path to an OpenAPI spec (.json/.yaml/.yml)")
    parser.add_argument("--spec-url", default="", help="URL of an OpenAPI spec (JSON or YAML)")
    parser.add_argument("--base-url", default="",
                        help="Base URL for live checks (default: spec servers[0].url, "
                             "then APITEST_BASE_URL)")
    parser.add_argument("--manifest", default="",
                        help="File with expected endpoints, one per line: "
                             "'METHOD path [expected_status]'")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON on stdout")
    parser.add_argument("--offline", action="store_true",
                        help="No network: validate spec internal consistency and compare "
                             "against the manifest only")
    args = parser.parse_args()
    if not args.spec and not args.spec_url:
        parser.error("provide --spec <path> or --spec-url <URL>")
    if args.spec and args.spec_url:
        parser.error("provide either --spec or --spec-url, not both")
    report = {"endpoints_count": 0, "missing_from_spec": [], "contract_violations": [], "conformant": False, "errors": []}
    try:
        spec = load_spec(args)
        if not isinstance(spec, dict):
            raise ValueError("spec root must be a mapping (object)")
        ops = iter_operations(spec)
        report["endpoints_count"] = len(ops)
        base_url = resolve_base_url(spec, args)
        check_internal(spec, ops, report)
        manifest = load_manifest(args.manifest) if args.manifest else []
        check_manifest(spec, manifest, report)
        if not args.offline:
            check_live(spec, manifest, base_url, report)
        report["conformant"] = (not report["errors"] and not report["missing_from_spec"]
                                and not any(v["severity"] == "error" for v in report["contract_violations"]))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report["errors"].append(str(exc))
    except Exception as exc:
        report["errors"].append(f"internal error: {exc}")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_text(report))
    if report["errors"]: return 2
    if report["missing_from_spec"] or any(
            v["severity"] == "error" for v in report["contract_violations"]):
        return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())