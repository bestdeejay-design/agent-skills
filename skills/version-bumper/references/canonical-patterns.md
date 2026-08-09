# Version Bumper — Canonical Patterns

Deep dive behind `scripts/bumper.py`. Everything below is grounded in
source-verified research (August 2026); every URL was checked live:

- **Conventional Commits v1.0.0** — <https://www.conventionalcommits.org/en/v1.0.0/>
  — the spec this skill implements
- **python-semantic-release** — <https://github.com/python-semantic-release/python-semantic-release>
- **semantic-release** — <https://github.com/semantic-release/semantic-release>
- **bump-my-version** (successor of `bumpversion`) — <https://github.com/callowayproject/bump-my-version>
- **commitizen** — <https://github.com/commitizen-tools/commitizen>
- **git-cliff** — <https://github.com/orhun/git-cliff>

---

## 1. The spec this skill implements

Conventional Commits v1.0.0 defines the commit format and the bump semantics:

```
<type>[optional scope][!]: <description>
```

- **Types**: `feat` (new feature), `fix` (bug fix), plus a free set of other
  types (`docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`,
  `revert`, …). The spec does not mandate the non-feat/fix set — tools pick
  their own table; this skill uses the preset table from the task contract.
- **Breaking changes**: a `!` immediately before the `:` of the type prefix,
  OR a footer `BREAKING CHANGE: <description>` in the commit body.
- **Bump semantics**: `feat` → MINOR, `fix` → PATCH, breaking → MAJOR.
  `perf`/`refactor` are treated as PATCH here (matching the repo's
  `changelog-generator` mapping, where they land in "Changed").

The skill mirrors the spec's own examples: `feat(api): ...` → MINOR,
`fix: ...` → PATCH, `feat!: ...` / `BREAKING CHANGE:` footer → MAJOR.

## 2. Version resolution model

| Tool | Baseline resolution | Bump decision | Tag format |
|---|---|---|---|
| **this skill** | `--current` or highest semver tag (`v?X.Y.Z`), fallback `0.0.0` | breaking > feat > fix/perf/refactor > none | `vX.Y.Z` |
| python-semantic-release | highest tag matching `v?X.Y.Z` | same priority, configurable per-type | configurable prefix |
| semantic-release | `git describe` / tags | same priority; **skips release entirely when no release commits** | `vX.Y.Z` |
| bump-my-version | explicit `current_version` in config | manual `--patch/--minor/--major` | configurable |
| commitizen | `cz bump --dry-run` from tags | same priority | `cz bump` creates it |
| git-cliff | tag range `tag..HEAD` | n/a (changelog only) | n/a |

## 3. Techniques the analogues have that this implementation lacks

- **Pre-release / build-metadata support** (python-semantic-release,
  bump-my-version): `1.2.3-rc.1`, `1.2.3+build.5`, and automatic
  `rc → final` transitions. This skill accepts only plain `X.Y.Z` / `vX.Y.Z`.
- **Changelog coupling** (python-semantic-release, commitizen, semantic-release):
  they generate the changelog *and* bump the version in one pass, keeping the
  version number and the changelog header in sync. This skill only prints the
  number; the repo's `changelog-generator` does the rendering separately.
- **Commit-range analysis** (git-cliff, semantic-release): analyze commits
  *between* two tags (`v1.0.0..v1.1.0`) to build per-release notes. This skill
  analyzes the whole history up to HEAD against one baseline.
- **Config files** (python-semantic-release `pyproject.toml`, bump-my-version
  `[tool.bumpversion]`, commitizen `cz.toml`): per-repo type tables, tag
  prefixes, and bump overrides. This skill is deliberately config-free.
- **Pre-release bumping** (commitizen `--prerelease`, python-semantic-release
  `--prerelease`): bump `1.2.3` → `1.3.0-rc.1` without a full MINOR. Not
  implemented here.
- **Dry-run vs. real execution** (semantic-release `--dry-run`): the analogues
  have a real "do it" mode (create tag, push, publish). This skill is
  read-only by design — `--dry-run` is accepted for pipeline compatibility and
  is the only mode.
- **Commit body parsing for BREAKING CHANGE** (all analogues): they parse the
  full commit message. This skill reads `git log --format=%s` subjects plus the
  body footer (`%b`) so `BREAKING CHANGE:` is detected; the `--commits FILE`
  fallback mode is subject-only and detects breaking via the `!` marker or an
  inline `BREAKING CHANGE:` text.

## 4. Determinism contract

The skill is part of the repo release pipeline, so the output must be
reproducible:

- Fixed field order (`latest_tag`, `current_version`, `next_version`,
  `suggested_tag`, `bump`, `commits_analyzed`, `counts`).
- Counts printed in the preset type-table order, then `breaking`, then `other`.
- No timestamps, no wall-clock dependence, no network.
- `-s` / `--stable` sorts the analyzed commits by `(type, breaking)` so the
  result is provably order-independent; identical input → identical
  `next_version`.

## 5. Exit-code contract

- `0` — success with meaningful output (including `bump: none`).
- `1` — error, message on stderr: not a git repository, git not installed,
  invalid `--current`, unreadable `--commits` file, git log/tag failure.

## Sources

- Conventional Commits v1.0.0: <https://www.conventionalcommits.org/en/v1.0.0/>
- python-semantic-release: <https://github.com/python-semantic-release/python-semantic-release>
- semantic-release: <https://github.com/semantic-release/semantic-release>
- bump-my-version: <https://github.com/callowayproject/bump-my-version>
- commitizen: <https://github.com/commitizen-tools/commitizen>
- git-cliff: <https://github.com/orhun/git-cliff>