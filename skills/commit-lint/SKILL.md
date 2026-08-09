---
name: commit-lint
description: "Validate git commit messages against Conventional Commits v1.0.0. Script commit_lint.py reads `git log` (subprocess) of one or more repositories (or stdin with --stdin), parses each commit into type/scope/subject, and reports violations: missing type, invalid type, type case, scope, subject length (default 50), subject capitalization, trailing dot/space, header length (100), body line length (72). Plain-text Markdown-friendly report or JSON (--json). Exit codes: 0 all clean, 1 violations found, 2 error. Pure Python 3 stdlib, offline, read-only. Closes the loop for commit-message-writer and version-bumper."
license: MIT
metadata:
  author: best
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib + git executable (optional; --stdin mode works without git)"
---

# Commit Lint — Conventional Commits validator

Load this skill when you need to **validate git commit messages against
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)** and
produce a report of what passes and what violates the convention. It is the
quality gate of the commit pipeline: `commit-message-writer` writes the
commits, `commit-lint` checks them, `version-bumper` derives the next version
from the clean history.

The tool is **read-only and offline**: it never modifies commits, never writes
files, and makes no network calls. It reads `git log` of a real repository
(via `subprocess`), parses each commit header as `<type>(<scope>)?(!)?:
<subject>`, and reports per-commit type/scope/subject plus every violated rule.
For testability the commit list can be fed from stdin (`--stdin`, one commit
per line) — no git repository required.

---

## The linter script

`scripts/commit_lint.py` — pure Python 3 stdlib (no dependencies).

| Mode | Command |
|---|---|
| Auto-detect repo from cwd | `python3 commit_lint.py` |
| Explicit repo path | `python3 commit_lint.py /path/to/repo` |
| Multiple repos | `python3 commit_lint.py repo1 repo2 repo3` |
| Override auto-detection | `python3 commit_lint.py --repo /path/to/repo` |
| Limit to N latest commits | `python3 commit_lint.py --repo . --count 50` |
| No git needed (stdin) | `printf 'feat: ok\n' \| python3 commit_lint.py --stdin` |
| Machine-readable output | `python3 commit_lint.py --repo . --json` |

### Rules enforced (Conventional Commits v1.0.0)

| Violation | Rule | Default |
|---|---|---|
| `missing-type` | no `<type>(<scope>)?(!)?: <subject>` prefix found | — |
| `invalid-type` | type not in the allowed set | `feat fix docs style refactor test perf ci chore build revert` |
| `type-case` | type must be lowercase (`Feat:` is a violation) | — |
| `scope-invalid` | scope must be non-empty and contain no spaces | — |
| `empty-subject` | no description after `<type>: ` | — |
| `space-after-colon` | exactly one space required after `:` | — |
| `subject-too-long` | subject longer than max | 50 chars (`--max-subject`) |
| `header-too-long` | full header longer than max | 100 chars (`--max-header`) |
| `subject-case` | subject must start with a lowercase letter or digit | on (`--no-subject-case` disables) |
| `trailing-dot` | subject must not end with `.` | on (`--no-trailing-dot` disables) |
| `trailing-space` | subject must not end with whitespace | — |
| `body-line-too-long` | body line longer than max | 72 chars (`--max-body-line`) |

### Output

```
commit-lint report
==================
repo: /path/to/repo
generated: 2026-08-09T16:54:04
commits_analyzed: 10
clean: 5
with_violations: 5

[OK]   4a8b27c test: verify lint
[FAIL] 64cf5ff foo: unknown type
         type: foo | scope: (none) | breaking: no
         subject: foo: unknown type
         violations:
           - invalid-type: type not in allowed set: feat, fix, docs, style, refactor, test, perf, ci, chore, build, revert
...

=== Violations by type ===
invalid-type: 1
missing-type: 1

exit: 1
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | all analyzed commits are clean |
| `1` | at least one commit has violations |
| `2` | error (not a git repo, git not installed, bad arguments, unreadable input) |

## Usage example (typical)

```bash
# Lint the current repository (auto-detected from cwd)
python3 skills/commit-lint/scripts/commit_lint.py

# Lint a specific repository, last 50 commits
python3 skills/commit-lint/scripts/commit_lint.py --repo /path/to/repo --count 50

# CI gate: fail the pipeline when any commit violates the convention
python3 skills/commit-lint/scripts/commit_lint.py --repo . && echo "all clean" || echo "violations found"

# Machine-readable report for a bot / dashboard
python3 skills/commit-lint/scripts/commit_lint.py --repo . --json

# Test the rules without a git repo (one commit per line)
printf 'feat: add widget\nFeat: bad case\n' | python3 skills/commit-lint/scripts/commit_lint.py --stdin
```

## Interpretation guidance

- **`exit: 0`** — every analyzed commit follows the convention. The history is
  ready for `version-bumper` and `changelog-generator`.
- **`exit: 1`** — violations found. Read the `[FAIL]` blocks: each lists the
  exact rule that fired. Fix the commit messages (rewrite history only if the
  commits are not yet shared) or adjust the limits (`--max-subject`,
  `--max-header`, `--max-body-line`) to match the project's documented style.
- **`missing-type`** — the commit has no conventional prefix at all. This is
  the most common finding on legacy repos; decide whether to migrate the
  history or accept a baseline of non-conventional commits.
- **`invalid-type`** — the prefix exists but the type is not in the preset
  table. The preset follows the friendly set from the task contract
  (`feat, fix, docs, style, refactor, test, perf, ci, chore, build, revert`);
  the Conventional Commits spec itself only mandates `feat` and `fix` and
  leaves the rest to the project.
- **`subject-too-long` / `header-too-long`** — the 50/100 limits follow the
  git commit man page and the Conventional Commits spec. Long subjects are a
  readability problem: they get truncated in `git log --oneline`.
- **`subject-case`** — the subject must start with a lowercase letter or
  digit. `feat: Add widget` is a violation; `feat: add widget` is not.
- **`trailing-dot`** — subjects must not end with `.`. This is a style rule
  (the spec examples never use a trailing period); disable with
  `--no-trailing-dot` if the project disagrees.

## Do NOT use

- Do NOT use to *rewrite* commit messages or amend history — the tool is
  read-only by design. It reports; you decide what to fix.
- Do NOT use when the repository does not follow Conventional Commits at all —
  the report will be mostly `missing-type` and the signal is noise. Consider
  `commit-message-writer` to establish the convention first.
- Do NOT use for merge-commit validation or signed-commit verification — the
  tool only reads the message text.
- Do NOT use `--stdin` when you need body checks — stdin mode carries only the
  subject line; body rules (`body-line-too-long`) require `git log`.

## Canonical analogues

Full source depth — in `references/canonical-patterns.md`. Backbone:

<table>
<tr><th>Analog</th><th>What we borrow</th></tr>
<tr><td>Conventional Commits spec</td><td>Header format, type taxonomy, `!` marker, `BREAKING CHANGE:` footer</td></tr>
<tr><td>commitlint (conventional-changelog)</td><td>Rule set, subject-length/type-enum checks, exit-code gate</td></tr>
<tr><td>gitlint</td><td>Subject capitalization, trailing-period, body-line-length rules</td></tr>
<tr><td>husky + commit-msg hook</td><td>Pre-commit validation workflow (we stay a standalone CLI)</td></tr>
<tr><td>semantic-release / commitizen</td><td>Type taxonomy and the "clean history drives releases" model</td></tr>
</table>

## Installation

```bash
# For opencode
cp -r skills/commit-lint ~/.config/opencode/skills/

# For other agents
# Copy the skill folder to your skills directory; requires Python 3.
# git is optional — --stdin mode works without it.
```

---

> **Note**: the linter validates; it never rewrites. Wire it into the commit
> pipeline as the quality gate before `version-bumper` derives the next
> version — a clean Conventional Commits history is what makes the release
> tooling trustworthy.