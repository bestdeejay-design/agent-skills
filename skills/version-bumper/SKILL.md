---
name: version-bumper
description: "Suggest the next semantic version and release tag from Conventional Commits in git history. Script bumper.py reads git log subjects (fallback: COMMITS env or --commits FILE for testability), classifies commit types (feat->MINOR, fix/perf/refactor->PATCH, `!` or BREAKING CHANGE->MAJOR) and prints latest_tag, next_version, suggested_tag (e.g. v1.5.0) and counts by type. Pure Python 3 stdlib, offline, deterministic output (-s), read-only (never creates tags). Closes the loop for commit-message-writer and changelog-generator."
license: MIT
metadata:
  author: best
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib + git executable (optional; --commits FILE mode works without git)"
---

# Version Bumper — semantic version from Conventional Commits

Load this skill when you need to **compute the next semantic version and a
suggested release tag from the commit history** of a git repository that
follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
It is the release-pipeline counterpart of `commit-message-writer` (writes the
commits) and `changelog-generator` (renders the changelog): this skill decides
what version number the changelog and the release tag should carry.

The tool is **read-only and offline**: it never creates tags, never writes
files, and makes no network calls. It reads `git log` subjects, classifies
each commit by type, and prints the current version, the next version and a
suggested tag. For testability the commit list can be fed from the `COMMITS`
environment variable or a file (`--commits FILE`, one subject per line) — no
git repository required.

---

## The bumper script

`scripts/bumper.py` — pure Python 3 stdlib (no dependencies).

| Source of commits | Command |
|---|---|
| Git repository (default) | `python3 bumper.py --path /path/to/repo` |
| Explicit current version | `python3 bumper.py --path . --current 1.2.3` |
| Latest semver tag | `python3 bumper.py --path . --from-tags` |
| File (no git needed) | `python3 bumper.py --commits commits.txt --current 1.2.3` |
| Environment (no git needed) | `COMMITS='feat: a\nfix: b' python3 bumper.py --current 1.2.3` |

### Bump rules (Conventional Commits v1.0.0)

| Signal | Bump | Example |
|---|---|---|
| Breaking (`!` or `BREAKING CHANGE:` footer) | MAJOR | `feat!: drop python 3.7` |
| `feat` | MINOR | `feat: add widget` |
| `fix`, `perf`, `refactor` | PATCH | `fix: repair crash` |
| `docs`, `style`, `test`, `chore`, `build`, `ci`, `revert`, unknown | no bump | `docs: readme` |

Type matching is case-insensitive (`Feat:` counts as `feat`). Unknown types
are counted as `other` and never trigger a bump.

### Output

```
latest_tag: v1.0.0
current_version: 1.0.0
next_version: 1.5.0
suggested_tag: v1.5.0
bump: minor
commits_analyzed: 14
counts: feat=1, fix=8, perf=2, refactor=1, docs=1, style=1, test=2, chore=1, build=0, ci=0, revert=0, breaking=1, other=0
```

### Flags

- `--current X.Y.Z` — baseline version; skips tag lookup
- `--from-tags` — take the baseline from the highest semver tag (`v1.2.3`,
  `1.2.3`); falls back to `0.0.0` with a warning when no tags exist
- `--commits FILE` — read commit subjects from a file (one per line) instead
  of `git log`; useful for tests and for repos without git
- `--dry-run` — accepted for pipeline compatibility; the tool is read-only, so
  this is the default behavior
- `-s` / `--stable` — deterministic output: sorts the analyzed commits and
  guarantees the same `next_version` for the same input

## Usage example (typical)

```bash
# Before a release: what version should the next tag carry?
python3 skills/version-bumper/scripts/bumper.py --path . --from-tags

# Pin the baseline explicitly (no tag lookup)
python3 skills/version-bumper/scripts/bumper.py --path . --current 1.2.3

# Deterministic output for CI / release pipeline
python3 skills/version-bumper/scripts/bumper.py --path . --from-tags -s

# Test the classifier without a git repo
python3 skills/version-bumper/scripts/bumper.py --commits commits.txt --current 1.2.3
```

## Interpretation guidance

- **`bump: major`** — at least one breaking commit (`!` or `BREAKING CHANGE:`
  footer). Review the breaking changes before tagging; MAJOR signals a
  compatibility break to consumers.
- **`bump: minor`** — new features present, no breaking changes.
- **`bump: patch`** — only fixes/refactors/perf; no features.
- **`bump: none`** — only docs/chore/style/test/build/ci/revert commits. Do
  not create a release tag; the version stays unchanged.
- **`latest_tag: none`** — no semver tags found; the tool started from
  `0.0.0`. For a first release, decide whether `v0.1.0` (first feature) or
  `v1.0.0` (first stable API) is appropriate.
- The tool only **suggests** a tag. Creating the tag, updating the changelog
  and pushing are separate steps — run `changelog-generator` with the
  suggested version, then tag manually.

## Do NOT use

- Do NOT use when the repository does not follow Conventional Commits — the
  classification will be mostly `other` and the suggestion meaningless.
- Do NOT use to *create* tags or modify the repository — the tool is read-only
  by design.
- Do NOT use for pre-release/build-metadata schemes (`1.2.3-rc.1`,
  `1.2.3+build.5`) — the parser accepts only plain `X.Y.Z` / `vX.Y.Z`.
- Do NOT use to rewrite history or reorder commits — the tool only reads.

## Canonical analogues

Full source depth — in `references/canonical-patterns.md`. Backbone:

<table>
<tr><th>Analog</th><th>What we borrow</th></tr>
<tr><td>Conventional Commits spec</td><td>Type taxonomy, `!` marker, `BREAKING CHANGE:` footer, bump semantics</td></tr>
<tr><td>python-semantic-release</td><td>Version-from-tags, bump-level resolution, deterministic output</td></tr>
<tr><td>semantic-release</td><td>Commit-driven release decision, no-release-when-no-release-commits</td></tr>
<tr><td>bump-my-version</td><td>Strict semver parsing, tag prefix handling</td></tr>
<tr><td>commitizen</td><td>Commit classification, changelog+version coupling</td></tr>
<tr><td>git-cliff</td><td>Conventional-Commits parsing, tag-range analysis</td></tr>
</table>

## Installation

```bash
# For opencode
cp -r skills/version-bumper ~/.config/opencode/skills/

# For other agents
# Copy the skill folder to your skills directory; requires Python 3.
# git is optional — --commits FILE mode works without it.
```

---

> **Note**: the tool suggests a version; it never tags, never commits and
> never pushes. Wire it into the release pipeline as the version source for
> `changelog-generator`, then create the tag yourself.