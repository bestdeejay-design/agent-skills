# Commit Lint — Canonical Patterns

Deep dive behind `scripts/commit_lint.py`. Everything below is grounded in
source-verified research (August 2026); every URL was checked live:

- **Conventional Commits v1.0.0** — <https://www.conventionalcommits.org/en/v1.0.0/>
  — the spec this skill implements
- **commitlint** (conventional-changelog) — <https://github.com/conventional-changelog/commitlint>
- **gitlint** (jorisroovers) — <https://github.com/jorisroovers/gitlint>
- **husky** (typicode) — <https://github.com/typicode/husky>
- **semantic-release** — <https://github.com/semantic-release/semantic-release>
- **commitizen** (commitizen-tools) — <https://github.com/commitizen-tools/commitizen>

---

## 1. The spec this skill implements

Conventional Commits v1.0.0 defines the commit header format:

```
<type>[optional scope][!]: <description>
```

- **Types**: the spec mandates only `feat` (new feature) and `fix` (bug fix);
  the rest of the set (`docs`, `style`, `refactor`, `perf`, `test`, `build`,
  `ci`, `chore`, `revert`, …) is left to the project. This skill uses the
  friendly preset table from the task contract:
  `feat, fix, docs, style, refactor, test, perf, ci, chore, build, revert`.
- **Scope**: an optional noun in parentheses describing the affected section
  (`feat(api): …`). Must be non-empty and contain no spaces.
- **Breaking changes**: a `!` immediately before the `:` of the type prefix,
  OR a footer `BREAKING CHANGE: <description>` in the commit body. The linter
  parses the `!` marker and reports `breaking: yes` per commit.
- **Description**: a short summary. The spec says the whole header must not
  exceed 100 characters; the git commit man page recommends a 50-character
  subject. This skill enforces both (`--max-subject` 50, `--max-header` 100).

## 2. Rule-set lineage

| Tool | Rules this skill borrows | Where |
|---|---|---|
| **commitlint** | `type-enum` (type must be in a configured set), `header-max-length` (100), `subject-empty`, `scope-empty` | `invalid-type`, `header-too-long`, `empty-subject`, `scope-invalid` |
| **gitlint** | `title-max-length` (50), `title-trailing-punctuation` (no trailing `.`), `title-must-not-contain-word`, body `body-max-line-length` (72) | `subject-too-long`, `trailing-dot`, `body-line-too-long` |
| **husky + commit-msg hook** | The "validate before accept" workflow — a commit-msg hook runs the linter and blocks the commit on failure | exit-code gate (0/1) |
| **semantic-release / commitizen** | The type taxonomy and the "clean Conventional Commits history drives releases" model | allowed-type preset, `missing-type` detection |

## 3. Techniques the analogues have that this implementation lacks

- **Interactive fixup** (commitlint `--fix`, commitizen `cz commit`): the
  analogues can *rewrite* a failing message in place. This skill is read-only
  by design — it reports, the agent/user fixes.
- **Pre-commit hook integration** (husky + commitlint): the analogues run
  automatically on `git commit` via a hook. This skill is a standalone CLI;
  wiring it into a hook is a one-liner (`commit_lint.py --repo . && …`) but is
  left to the consumer.
- **Config files** (commitlint `commitlint.config.js`, gitlint
  `.gitlint`): per-repo rule overrides and custom type tables. This skill is
  deliberately config-free — limits are CLI flags (`--max-subject`,
  `--max-header`, `--max-body-line`).
- **Multi-line body parsing for BREAKING CHANGE** (commitlint, semantic-release):
  they parse the full message footer. This skill reads the body via
  `git log --format=%b` for the `body-line-too-long` rule and the `!` marker
  for breaking detection; the `--stdin` fallback mode is subject-only.
- **Ignore patterns** (commitlint `ignores`, gitlint `ignore`): skip
  merge/revert/squash commits. This skill lints everything it is given;
  filtering is the caller's choice (`--count`, or pre-filter the input).
- **Auto-fix of trailing whitespace** (gitlint `ignore-merge-commits` +
  editor tooling): git itself strips trailing whitespace from commit messages
  at commit time, so `trailing-space` is most useful in `--stdin` mode or when
  analyzing messages from non-git sources.

## 4. Exit-code contract

The exit code is the CI gate — the pipeline step fails when the history is
not clean:

- `0` — all analyzed commits are clean.
- `1` — at least one commit has violations (the report lists them).
- `2` — error: not a git repository, git not installed, bad arguments,
  unreadable input.

This mirrors commitlint's `--quiet`/exit-code behavior and gitlint's
`--fail-without-commits` gate: a non-zero exit fails the pipeline step.

## 5. Input contract

- **Git mode**: `git -C <repo> log --format=%H%x00%s%x00%b%x1e` via
  `subprocess` — hash, subject, body, record separator. `--count N` appends
  `-n N`. The record separator keeps multi-line bodies intact.
- **Stdin mode**: one commit per line, `[hash<TAB>]subject`. No git required;
  used for tests and for linting messages from non-git sources.
- **Auto-detection**: with no `PATH` and no `--repo`, the repo is resolved
  from the current directory via `git rev-parse --show-toplevel`.

## Sources

- Conventional Commits v1.0.0: <https://www.conventionalcommits.org/en/v1.0.0/>
- commitlint: <https://github.com/conventional-changelog/commitlint> —
  `@commitlint/config-conventional` rule set
- gitlint: <https://github.com/jorisroovers/gitlint> — default rules
  (`subject-max-length`, `body-max-line-length`, `title-trailing-punctuation`)
- husky: <https://github.com/typicode/husky> — commit-msg hook workflow
- semantic-release: <https://github.com/semantic-release/semantic-release> —
  commit-driven release model
- commitizen: <https://github.com/commitizen-tools/commitizen> — type
  taxonomy, commit message conventions