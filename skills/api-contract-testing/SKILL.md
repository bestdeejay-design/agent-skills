---
name: api-contract-testing
description: "Validate an API contract against an OpenAPI 3.x specification (JSON or YAML) and an optional manifest of expected endpoints. Script api_contract.py enumerates operations (paths + webhooks), checks spec internal consistency (unresolved $refs, duplicates, missing responses), compares the manifest against the spec offline, and in live mode probes each manifest endpoint over HTTP and compares the actual status with the expected one. Pure Python 3 stdlib (argparse, json, pathlib, sys, urllib.request) with a built-in minimal YAML subset parser — no PyYAML, no requests. Emits a machine-readable JSON report (endpoints_count, missing_from_spec, contract_violations, conformant, errors) and uses exit codes 0/1/2. Closes the loop for api-doc-generator and test-generator."
license: MIT
metadata:
  author: best
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib only; no third-party packages, no network beyond urllib (and none in --offline mode)"
---

# API Contract Testing — validate an OpenAPI spec against expected endpoints

Load this skill when you need to **check that a running API (or a spec on
disk) actually matches the contract it promises**. It is the verification
counterpart of `api-doc-generator` (which *writes* the spec) and
`test-generator` (which *writes* the tests): this skill *checks* the spec
against a manifest of expected endpoints and, optionally, against the live
API.

The tool is **pure Python 3 stdlib** — no PyYAML, no requests, no pip
install. It reads an OpenAPI 3.x document from a file (`.json` or `.yaml`)
or a URL, enumerates every declared operation (under `paths` and `webhooks`),
checks the spec's internal consistency, and compares it against an optional
manifest file. In `--offline` mode it never touches the network; in live mode
it probes each manifest endpoint over HTTP and compares the actual status
code with the expected one.

## Triggers

Load this skill when the request matches any of these (EN / RU):

- "api contract testing", "contract test", "check the API against the spec"
- "validate openapi spec", "spec vs manifest", "endpoint coverage"
- "проверь контракт API", "тест контракта", "сверь спецификацию с API"
- "валидация openapi", "проверка эндпоинтов", "контрактное тестирование"
- "does the API match the spec", "missing endpoints", "expected status codes"

---

## The api_contract.py script

`scripts/api_contract.py` — pure Python 3 stdlib (no dependencies).

| Mode | Command |
|---|---|
| Offline, JSON report | `python3 api_contract.py --spec openapi.json --offline --json` |
| Offline + manifest | `python3 api_contract.py --spec openapi.yaml --manifest endpoints.txt --offline` |
| Live checks | `python3 api_contract.py --spec openapi.json --manifest endpoints.txt --base-url https://api.example.com` |
| Spec from URL | `python3 api_contract.py --spec-url https://example.com/openapi.json --manifest endpoints.txt` |

### Flags

- `--spec <path>` — OpenAPI spec file (`.json`, `.yaml`, `.yml`). YAML is
  parsed by a built-in subset parser (see Limitations).
- `--spec-url <URL>` — fetch the spec over HTTP(S) with `urllib.request`.
  The format is detected by the URL extension, then by trying JSON first
  and falling back to the YAML parser.
- `--base-url <URL>` — base URL for live checks. Resolution order:
  `--base-url` → spec `servers[0].url` → env `APITEST_BASE_URL`.
- `--manifest <file>` — expected contract, one `METHOD path [expected_status]`
  per line (blank lines and `#` comments ignored). `expected_status` may be an
  exact code (`200`), a class wildcard (`2xx`), or `default`.
- `--json` — emit the report as a JSON object on stdout (machine-readable).
- `--offline` — no network at all: validate spec internal consistency and
  compare the manifest against the spec only.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | conformant (or offline-ok) |
| `1` | contract violations detected (missing endpoints, mismatched statuses) |
| `2` | spec/parse/run error (unreadable file, invalid JSON/YAML, bad manifest, live-check network failure) |

### Report structure

The report is always the same JSON structure; `--json` prints it verbatim,
without `--json` it is rendered as text.

```json
{
  "endpoints_count": 2,
  "missing_from_spec": [{"method": "DELETE", "path": "/pets", "expected": "204"}],
  "contract_violations": [{"method": "GET", "path": "/pets", "expected": "200", "actual": "404", "severity": "error"}],
  "conformant": false,
  "errors": []
}
```

- `endpoints_count` — number of operations declared in the spec (paths + webhooks).
- `missing_from_spec` — manifest entries that do not exist in the spec.
- `contract_violations` — `severity: "error"` breaks the contract (missing
  expected status, unresolved `$ref`); `severity: "warning"` is informational
  (duplicate operation, operation without responses, empty spec).
- `conformant` — `true` iff no errors, no missing endpoints and no
  error-severity violations.
- `errors` — fatal problems (parse failures, live-check network errors).

## Usage example (typical)

```bash
# 1. Offline sanity check of a spec: is it internally consistent?
python3 skills/api-contract-testing/scripts/api_contract.py \
  --spec openapi.yaml --offline --json

# 2. Does the spec cover everything the product promised?
python3 skills/api-contract-testing/scripts/api_contract.py \
  --spec openapi.json --manifest endpoints.txt --offline --json

# 3. Live: does the running API actually return the promised statuses?
python3 skills/api-contract-testing/scripts/api_contract.py \
  --spec openapi.json --manifest endpoints.txt --base-url https://api.example.com

# 4. Machine-readable gate for CI (exit code drives the pipeline)
python3 skills/api-contract-testing/scripts/api_contract.py \
  --spec openapi.yaml --manifest endpoints.txt --offline --json \
  | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin)["conformant"] else 1)'
```

### Manifest format

```
# expected API contract
GET    /pets        200
POST   /pets        201
DELETE /pets/{id}   204
GET    /health      2xx
```

`expected_status` is optional — a line without it only asserts that the
endpoint exists in the spec. Wildcards (`2xx`, `4xx`) match any code in that
class; `default` matches the spec's `default` response key.

## Interpretation guidance

- **`conformant: true`** — the spec is internally consistent and every
  manifest endpoint exists with the expected status (offline), or the live
  API returned the expected statuses (live mode).
- **`missing_from_spec` non-empty** — the product promised endpoints the spec
  does not declare. Either the spec is stale (regenerate with
  `api-doc-generator`) or the manifest is wrong.
- **`contract_violations` with `severity: "error"`** — a promised status is
  not declared in the spec (offline) or the live API returned a different
  status (live). This is the signal that breaks the contract.
- **`severity: "warning"`** — spec hygiene issues (duplicate operations,
  operations without responses, unresolved `$ref`). They do not fail the run
  but should be fixed.
- **`errors` non-empty** — the tool could not do its job (file not found,
  invalid JSON/YAML, bad manifest line, network failure). Exit code `2`.

## Integration notes

- **CI gate**: use `--json` and pipe through a JSON check, or rely on the
  exit code directly (`0`/`1`/`2`).
- **Base URL**: prefer `servers[0].url` in the spec; override with
  `--base-url` or `APITEST_BASE_URL` for per-environment runs.
- **Live mode is manifest-driven**: only endpoints listed in the manifest are
  probed; the spec itself is never called. Use `--offline` in CI when the API
  is not deployed yet.
- **Companion skills**: `api-doc-generator` produces the spec,
  `test-generator` produces the tests — this skill verifies the contract
  between them.

## Limitations

- **YAML support is a subset, not a full YAML parser.** The built-in parser
  handles block mappings/sequences, flow collections (`{...}`, `[...]`),
  quoted scalars, comments and block scalars (`|`, `>`). It does **not**
  support anchors/aliases (`&a`, `*a`), tags (`!!str`), multi-document
  streams (`---` separators), or exotic scalar quoting. If your spec uses
  those, convert it to JSON (`python3 -c 'import yaml,json,sys; print(json.dumps(yaml.safe_load(sys.stdin)))'` with PyYAML available) and pass the `.json` file.
- **No schema validation** — the tool checks structure and consistency, not
  whether every field conforms to the OpenAPI meta-schema.
- **Live checks are status-code only** — request/response bodies are not
  validated against the spec's schemas.
- **Path matching is exact** — `/pets` and `/pets/` are treated as different
  paths; template parameters (`/pets/{id}`) must match literally.

## Canonical analogues

Full source depth — in `references/canonical-patterns.md`. Backbone:

<table>
<tr><th>Analog</th><th>What we borrow</th></tr>
<tr><td>Schemathesis</td><td>Spec-driven contract checking, property-based probing of declared responses</td></tr>
<tr><td>Dredd</td><td>Manifest/transaction-driven verification of endpoints against a live API</td></tr>
<tr><td>oasdiff</td><td>Spec internal-consistency and compatibility analysis</td></tr>
<tr><td>Spectral</td><td>Lint-style rules for spec hygiene (warnings vs. errors)</td></tr>
<tr><td>openapi-generator</td><td>Endpoint enumeration from paths + operations as the source of truth</td></tr>
</table>

## Installation

```bash
# For opencode
cp -r skills/api-contract-testing ~/.config/opencode/skills/

# For other agents
# Copy the skill folder to your skills directory; requires Python 3 only.
```

---

> **Note**: the tool is read-only — it never modifies the spec, the manifest
> or the API. It reports; you decide what to fix.