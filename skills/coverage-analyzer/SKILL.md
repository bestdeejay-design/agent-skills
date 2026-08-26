---
name: coverage-analyzer
description: "Parse coverage.py XML reports (coverage.xml) into a human-readable coverage analysis: total line/branch percent, files with zero coverage, worst-10 ranking, delta vs a stored JSON baseline, and a PASS/FAIL verdict against an optional threshold. Stdlib-only Python script (xml.etree.ElementTree, json, argparse) that closes the loop after test-generator."
license: MIT
metadata:
  author: best
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib only. Input: coverage.py XML report (coverage.xml)."
when_to_use: "Use when turning a coverage.xml report into readable coverage analysis or gating CI. Triggers: 'coverage analysis', 'analyze coverage', 'coverage threshold', 'parse coverage.xml', 'coverage report'. Example: 'analyze coverage.xml and fail CI if below 80%'."
---

# Coverage Analyzer — coverage.py XML → readable analysis

Load this skill when you need to **turn a `coverage.xml` report into a
human-readable coverage analysis**: overall line/branch percent, files with
zero coverage, the 10 worst-covered files, a delta vs a previously stored
baseline, and a PASS/FAIL verdict against a threshold for CI.

The analyzer is **pure Python 3 stdlib** (`xml.etree.ElementTree`, `json`,
`argparse`) — no dependencies, no network. It reads the exact XML format that
[coverage.py](https://coverage.readthedocs.io/) emits via `coverage xml`
(Cobertura-style DTD), so it works with any tool that produces that format
(`pytest-cov --cov-report=xml`, `coverage run -m pytest && coverage xml`).

---

## The analyzer script

`scripts/coverage_analyzer.py` — pure Python 3 stdlib (no dependencies).

| Mode | Command |
|---|---|
| Basic analysis | `python3 coverage_analyzer.py --xml coverage.xml` |
| Delta vs stored baseline | `python3 coverage_analyzer.py --xml coverage.xml --baseline baseline.json` |
| Threshold gate (CI) | `python3 coverage_analyzer.py --xml coverage.xml --threshold 80` |
| Store current totals as baseline | `python3 coverage_analyzer.py --xml coverage.xml --save-baseline baseline.json` |

### Output sections

- **Total** — `line-rate` (and `branch-rate` when branches were actually
  measured; a `branch-rate="0"` with `branches-valid="0"` is treated as
  "not measured", not as 0%), file count, `files_with_zero_lines` (files with
  line-rate == 0) with their names
- **Worst 10 files** — lowest line-rate first, ascending
- **Delta vs baseline** — per-file `before → after → Δ` table plus a `total`
  row; files absent from the baseline are marked `new`
- **Verdict** — `PASS`/`FAIL` when `--threshold` is given

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | analysis succeeded (threshold PASS, or no threshold) |
| `1` | parse/read error, or threshold FAIL |
| `2` | internal error |

---

## Usage example (typical)

```bash
# 1. Produce the XML (coverage.py installed):
coverage run -m pytest && coverage xml

# 2. Analyze:
python3 coverage_analyzer.py --xml coverage.xml

# 3. Store a baseline on the first run:
python3 coverage_analyzer.py --xml coverage.xml --save-baseline baseline.json

# 4. On later runs, diff against the baseline and gate CI:
python3 coverage_analyzer.py --xml coverage.xml --baseline baseline.json --threshold 80
```

## Baseline tracking workflow

1. **First run** — `--save-baseline baseline.json` writes
   `{"files": [{"name": "...", "line_rate": 0.42}, ...], "total": 0.42}`.
   Commit the baseline file so it is reviewable.
2. **Later runs** — `--baseline baseline.json` prints a per-file
   `before → after → Δ` table. A file that appears in the current report but
   not in the baseline is marked `new`; a file that disappeared is simply
   absent from the table.
3. **Trend** — the `total` row shows the overall delta in percentage points,
   so a regression (e.g. `-5.0 pp`) is visible at a glance.

## Threshold gate for CI

```bash
python3 coverage_analyzer.py --xml coverage.xml --threshold 80
echo "exit=$?"   # 0 = PASS, 1 = FAIL
```

Use it as the last step of a test job: the script exits `1` when the total
line-rate percent is below the threshold, failing the pipeline. This closes
the loop after `test-generator` — generate tests, measure coverage, gate on
the result.

## Do NOT use

- **If you don't have a `coverage.xml`** — this skill only *parses* the
  coverage.py XML format; it does not run your tests or measure coverage
  itself. Run `coverage run -m pytest && coverage xml` (or `pytest --cov`)
  first.
- **If you want branching visualization** (branch-by-branch coverage maps,
  HTML reports with per-line coloring) — use coverage.py's own
  `coverage html`/`coverage report` or a dedicated coverage UI. This tool is
  a text/markdown summary + CI gate, not a visualizer.
- **If your report is in a different format** (lcov, JaCoCo, Cobertura from
  other tools) — the parser targets the coverage.py XML schema; other
  Cobertura-style files may parse but attribute names differ.

## Canonical patterns

Full deep dive with upstream sources in `references/canonical-patterns.md`.
Key canons:

- **coverage.py XML schema** (Ned Batchelder) — the `line-rate`/`branch-rate`
  attribute semantics this tool parses verbatim
- **Cobertura DTD** — the XML shape coverage.py emits (`<coverage>`,
  `<packages>`, `<classes>`, `<lines>`)
- **pytest-cov** — the `--cov-report=xml` pipeline that produces the input
- **codecov / coveralls** — the baseline-diff + threshold-gate CI model
- **coverage-badge** — the "percent → verdict" rendering idea (we stay text)

## Files

- `SKILL.md` — this file
- `skill.json` — manifest
- `scripts/coverage_analyzer.py` — the stdlib analyzer (XML parse + baseline
  diff + threshold gate)
- `references/canonical-patterns.md` — coverage.py/pytest-cov/codecov/
  coveralls/coverage-badge deep dive with sources

## Canonical analogues

Full source depth — in `references/canonical-patterns.md`. Backbone:

<table>
<tr><th>Analog</th><th>What we borrow</th></tr>
<tr><td>coverage.py (Ned Batchelder, Apache-2.0)</td><td>XML schema, <code>line-rate</code>/<code>branch-rate</code> semantics, <code>coverage xml</code> output</td></tr>
<tr><td>pytest-cov</td><td>Test-runner integration path (<code>--cov-report=xml</code>) that produces the input</td></tr>
<tr><td>codecov / coveralls</td><td>Baseline-diff + trend + threshold-gate CI model (we stay offline, no upload)</td></tr>
<tr><td>coverage-badge</td><td>Rate → verdict/badge conversion (we emit PASS/FAIL text instead of an SVG)</td></tr>
</table>

## Installation

```bash
# For opencode
cp -r skills/coverage-analyzer ~/.config/opencode/skills/

# For other agents
# Copy the skill folder to your skills directory; requires Python 3.
```

---

> **Note**: this tool analyzes, it does not generate tests or coverage. It
> expects a real `coverage.xml` produced by coverage.py (or a compatible
> tool) and reports what the numbers mean — including a CI exit-code gate so
> coverage regressions fail the build.