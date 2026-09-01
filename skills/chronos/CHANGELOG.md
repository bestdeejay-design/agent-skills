# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-01

### Added

- **Chronos** — Orchestrator agent, staleness detection
- **Censor** — Duplicate detection, broken link detection
- **Dewey** — Document classification by hierarchy (L1-L6)
- **Veles** — Orphan detection, link statistics
- **Canon** — Preset orchestration (minimal/standard/full)
- CLI interface with presets and fail-on thresholds
- JSON + Markdown report output
- 67 pytest tests
- GitHub Actions CI/CD

### Fixed

- Canon.orchestrate() — Dewey dict return was breaking issues list
- Dewey.check() — check_missing() now properly called
- reader.py — now handles .yml files alongside .yaml
- Chronos.find_target() — proper Optional return type
- Chronos.extract_links() — code blocks now skipped
- Veles.find_orphans() — proper path resolution

## [0.1.0] - 2026-09-01

### Added

- Initial release (pre-release)
