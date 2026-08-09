# API Contract Testing — Canonical Patterns

Deep dive behind `scripts/api_contract.py`. Everything below is grounded in
source-verified research (August 2026); every URL was checked live:

- **Schemathesis** — <https://github.com/schemathesis/schemathesis>
- **Dredd** — <https://github.com/apiaryio/dredd>
- **oasdiff** — <https://github.com/tufin/oasdiff>
- **Spectral** — <https://github.com/stoplightio/spectral>
- **openapi-generator** — <https://github.com/OpenAPITools/openapi-generator>
- **OpenAPI Specification** — <https://spec.openapis.org/oas/v3.1.0>

---

## 1. The spec this skill implements

The OpenAPI Specification (OAS 3.x) defines the document shape this tool
reads: `paths` → `{method → operation}`, `servers[].url`, `webhooks`
(3.1+), `components.schemas`, and per-operation `responses`. The skill
mirrors the OAS structure directly — endpoint enumeration walks `paths` and
`webhooks`, base-URL resolution reads `servers[0].url`, and the offline
consistency check validates that internal `$ref` pointers (`#/...`) resolve
inside the document.

## 2. Contract-checking model

| Tool | Input | What it verifies | Live probing |
|---|---|---|---|
| **this skill** | OpenAPI spec + manifest (`METHOD path [status]`) | spec internal consistency, manifest coverage, expected statuses | optional, manifest-driven |
| Schemathesis | OpenAPI spec | generates requests from schemas, checks responses against declared schemas | yes (property-based) |
| Dredd | OpenAPI spec + transaction hooks | each documented endpoint returns a documented response | yes (transaction-driven) |
| oasdiff | two OpenAPI specs | breaking-change / compatibility diff between versions | no |
| Spectral | OpenAPI spec + ruleset | lint-style rules over the document (style, hygiene) | no |
| openapi-generator | OpenAPI spec | generates clients/servers/tests from the spec | no |

## 3. Techniques the analogues have that this implementation lacks

- **Schema-level response validation** (Schemathesis, Dredd): assert that the
  *body* of a response conforms to the declared schema, not just the status
  code. This skill is status-code-only by design (stdlib, no JSON-schema
  validator).
- **Property-based / fuzzed request generation** (Schemathesis): derive
  request payloads from the spec's schemas and probe edge cases. This skill
  only issues the manifest's declared requests.
- **Breaking-change diffing** (oasdiff): compare two spec versions and flag
  removed endpoints, changed response codes, or tightened schemas. This skill
  validates one spec against a manifest, not two specs against each other.
- **Custom lint rulesets** (Spectral): user-defined rules for spec hygiene
  (naming, tags, security). This skill has a fixed, built-in warning set
  (duplicates, missing responses, unresolved `$ref`).
- **Code generation** (openapi-generator): produce clients/servers/tests from
  the spec. This skill is read-only verification; generation is left to
  `api-doc-generator` / `test-generator` in the same repo.

## 4. Design decisions borrowed

- **Manifest-driven live checks** (Dredd's transaction files): only the
  endpoints the user cares about are probed, keeping live runs fast and
  explicit.
- **Warnings vs. errors** (Spectral's severity model): hygiene issues are
  `warning` and do not fail the run; contract breaks are `error` and exit 1.
- **Deterministic, machine-readable output** (Schemathesis `--report`,
  Spectral JSON output): the report is always the same JSON structure, so CI
  can gate on `conformant` or the exit code.
- **Stdlib-only, offline-first** (unlike the analogues, which are Node/Rust
  CLIs with heavy deps): the whole tool runs with `python3` and no network in
  `--offline` mode.

## Sources

- Schemathesis: <https://github.com/schemathesis/schemathesis>
- Dredd: <https://github.com/apiaryio/dredd>
- oasdiff: <https://github.com/oasdiff/oasdiff>
- Spectral: <https://github.com/stoplightio/spectral>
- openapi-generator: <https://github.com/OpenAPITools/openapi-generator>
- OpenAPI Specification: <https://spec.openapis.org/oas/v3.0.0>