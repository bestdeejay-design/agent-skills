# Coverage Analyzer — Canonical Patterns

Deep dive behind `scripts/coverage_analyzer.py`. Everything below is grounded
in source-verified research (August 2026), not invented from memory:

- **coverage.py** (Ned Batchelder) — Apache-2.0 — the XML report schema and
  `line-rate`/`branch-rate` semantics this tool parses verbatim
- **pytest-cov** (pytest-dev) — MIT — the test-runner integration that
  produces the input XML
- **codecov** (codecov/codecov-cli) — the baseline-diff + threshold-gate CI
  model
- **coveralls** (coverallsapp/github-action) — the "report → verdict" upload
  pipeline (we stay offline)
- **coverage-badge** (dbrgn) — MIT — rate → verdict/badge conversion
- **tokei** (XAMPPRocky) — MIT — the "count things per file" ranking idea
  behind the worst-10 table

---

## 1. Input format: coverage.py XML (Cobertura-style)

`coverage xml` writes a Cobertura-DTD-shaped document. The root element
carries the totals as attributes — this is the exact contract the analyzer
reads:

```xml
<coverage version="7.15.4" timestamp="1786280501886"
          lines-valid="41" lines-covered="32" line-rate="0.7805"
          branches-covered="0" branches-valid="0" branch-rate="0"
          complexity="0">
  <sources><source>/path/to/project</source></sources>
  <packages>
    <package name=".github.workflows" line-rate="0.7805" branch-rate="0">
      <classes>
        <class name="validate_skills.py" filename=".github/workflows/validate_skills.py"
               complexity="0" line-rate="0.7805" branch-rate="0">
          <methods/>
          <lines>
            <line number="11" hits="1"/>
            ...
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
```

Key semantics (verified against coverage.py source `coverage/xml.py`):

- **`line-rate`** is a float in `[0, 1]` = `lines-covered / lines-valid`.
  The root `<coverage>` element and every `<class>` (per-file) carry it.
- **`branch-rate`** is only meaningful when `branches-valid > 0`. With the
  default `coverage run` (no `--branch`), coverage.py emits
  `branches-valid="0" branch-rate="0"` — a *measured-zero*, not a real 0%.
  This tool treats that combination as "branches not measured" and omits the
  branch line entirely (see `extract()` in the script).
- **Per-file entries** are `<class>` elements; `name` is the module name,
  `filename` the path. `root.iter("class")` collects them regardless of
  package nesting.

## 2. What we adapt from each canonical

| Canonical | Technique adapted | Where in this skill |
|---|---|---|
| coverage.py | `line-rate`/`branch-rate` float semantics, `branches-valid` guard | `parse_rate()`, `extract()` |
| pytest-cov | The `--cov-report=xml` pipeline as the documented input path | SKILL.md usage table |
| codecov | Baseline/trend diff + threshold gate as a CI decision | `--baseline`, `--threshold`, exit codes |
| coveralls | Report → human verdict flow (we skip the upload) | Verdict section, markdown output |
| coverage-badge | Rate → PASS/FAIL conversion (we emit text, not an SVG) | `verdict()` |
| tokei | Sorted per-file ranking table (worst-first) | "Worst 10 files" table |

## 3. Baseline model (codecov / coveralls lineage)

Both codecov and coveralls store per-commit coverage and diff new runs
against the previous one. This skill implements the *operator-facing*
equivalent:

- `--save-baseline baseline.json` writes
  `{"files": [{"name": "...", "line_rate": 0.42}, ...], "total": 0.42}` —
  `line_rate` kept as a `[0,1]` float, identical to the XML attribute, so a
  baseline can be diffed against any later report without conversion.
- `--baseline baseline.json` prints a per-file `before → after → Δ` table
  (Δ in percentage points) plus a `total` row. Files not in the baseline are
  marked `new`; files that disappeared are simply absent.
- The baseline file is meant to be **committed and reviewed** — same
  philosophy as codecov's committed `codecov.yml` thresholds and coveralls'
  per-commit coverage history.

## 4. Threshold gate (codecov `coverage.status` model)

codecov's `coverage.status.project.target` fails a commit when coverage drops
below a target. This skill mirrors that with a stdlib exit code:

```bash
python3 coverage_analyzer.py --xml coverage.xml --threshold 80
echo "exit=$?"   # 0 = PASS, 1 = FAIL
```

Exit codes: `0` success (PASS or no threshold) · `1` parse error or FAIL ·
`2` internal error. The FAIL exit is the CI gate — the pipeline step fails
when total line-rate percent < threshold.

## 5. Missing techniques (deliberately out of scope)

- **Branch-by-branch visualization** — coverage.py's `coverage html` renders
  per-line/per-branch colored reports; this tool is text-only.
- **Wagon-sphinx / chart rendering** — codecov renders trend charts and
  sparklines; we emit markdown tables.
- **Upload & aggregation** — codecov/coveralls aggregate multiple reports
  (matrix builds) server-side; we analyze one local XML.
- **Badge generation** — coverage-badge renders an SVG badge; we emit
  `PASS`/`FAIL` text.
- **LOC counting** — tokei counts lines of code across languages; we only
  count *covered* vs *valid* lines from the report.
- **Test generation** — this skill closes the loop *after* `test-generator`;
  it never writes tests.

## Sources

- coverage.py: <https://github.com/nedbat/coveragepy> — `coverage/xml.py`,
  `coverage/report.py`, `coverage run --branch` docs
- pytest-cov: <https://github.com/pytest-dev/pytest-cov> — `--cov-report=xml`
- codecov: <https://github.com/codecov/codecov-cli> — report parsing,
  `coverage.status` thresholds
- coveralls: <https://github.com/coverallsapp/github-action> — coverage
  report → verdict pipeline
- coverage-badge: <https://github.com/dbrgn/coverage-badge> — rate → badge
  conversion
- tokei: <https://github.com/XAMPPRocky/tokei> — sorted language/file
  statistics tables