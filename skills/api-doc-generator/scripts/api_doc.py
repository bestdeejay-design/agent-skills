#!/usr/bin/env python3
"""Render REST API documentation from an OpenAPI 3.x schema to Markdown.

Reads an OpenAPI JSON document (from a file or stdin) and emits Markdown
with one section per endpoint: method, path, summary, parameters table
(query/path/header), request body schema, and response codes.

Usage:
    python3 api_doc.py --schema openapi.json
    python3 api_doc.py --schema openapi.json --out API.md
    cat openapi.json | python3 api_doc.py --stdin
"""
import argparse
import json
import sys
from dataclasses import dataclass, field


@dataclass
class Endpoint:
    method: str
    path: str
    summary: str
    operation_id: str
    params: list[dict] = field(default_factory=list)
    request_body: str = ""
    responses: list[tuple[str, str]] = field(default_factory=list)


def load_schema(source: str) -> dict:
    return json.loads(source)


def iter_endpoints(schema: dict) -> list[Endpoint]:
    endpoints: list[Endpoint] = []
    for path, item in (schema.get("paths") or {}).items():
        for method in ("get", "post", "put", "patch", "delete", "options", "head"):
            op = item.get(method)
            if not op:
                continue
            params = op.get("parameters") or []
            responses = []
            for code, resp in (op.get("responses") or {}).items():
                desc = (resp or {}).get("description", "")
                responses.append((code, desc))
            request_body = ""
            rb = op.get("requestBody")
            if rb:
                content = (rb.get("content") or {})
                if content:
                    request_body = ", ".join(content.keys())
            endpoints.append(
                Endpoint(
                    method=method.upper(),
                    path=path,
                    summary=op.get("summary", ""),
                    operation_id=op.get("operationId", ""),
                    params=params,
                    request_body=request_body,
                    responses=responses,
                )
            )
    return endpoints


def render_markdown(endpoints: list[Endpoint], title: str) -> str:
    lines = [f"# {title}", ""]
    if not endpoints:
        lines.append("_No endpoints found in schema._")
        return "\n".join(lines)

    for ep in endpoints:
        lines.append(f"## {ep.method} {ep.path}")
        if ep.summary:
            lines.append(f"> {ep.summary}")
        if ep.operation_id:
            lines.append(f"**operationId:** `{ep.operation_id}`")
        lines.append("")
        if ep.params:
            lines.append("### Parameters")
            lines.append("| Name | In | Required | Description |")
            lines.append("|------|----|----------|-------------|")
            for p in ep.params:
                name = p.get("name", "")
                loc = p.get("in", "")
                req = "yes" if p.get("required") else "no"
                desc = (p.get("schema") or {}).get("description", "")
                lines.append(f"| `{name}` | {loc} | {req} | {desc} |")
            lines.append("")
        if ep.request_body:
            lines.append(f"### Request body: `{ep.request_body}`")
            lines.append("")
        if ep.responses:
            lines.append("### Responses")
            for code, desc in ep.responses:
                lines.append(f"- **{code}**: {desc}")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", default="", help="Path to openapi.json")
    parser.add_argument("--stdin", action="store_true", help="Read schema from stdin")
    parser.add_argument("--title", default="API Reference", help="Document title")
    parser.add_argument("--out", default="", help="Write to file instead of stdout")
    args = parser.parse_args()

    if args.stdin:
        source = sys.stdin.read()
    elif args.schema:
        try:
            with open(args.schema, encoding="utf-8") as f:
                source = f.read()
        except OSError as e:
            sys.exit(f"❌ Cannot read {args.schema}: {e}")
    else:
        parser.error("Provide --schema <file> or --stdin")

    try:
        schema = json.loads(source)
    except json.JSONDecodeError as e:
        sys.exit(f"❌ Invalid JSON: {e}")

    endpoints = iter_endpoints(schema)
    markdown = render_markdown(endpoints, args.title)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(markdown + "\n")
        print(f"✅ Wrote {args.out}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()