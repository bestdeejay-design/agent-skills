# Skill Quality Audit — Layer A / Layer B snapshot

Generated: 2026-08-26 · methodology: `docs/SKILL_QUALITY_GATE.md`

**Layer A flags**: `when_to_use` presence, body>500 (soft guideline), desc+wtu>1536 (hard Claude listing cap).
**Layer B class** is a *signal-based heuristic*: does the skill mention exit codes / verification / tests / CI gate?

| # | skill | wtu | desc | desc+wtu | body | Layer B | Layer A flags |
|---|---|---|---|---|---|---|---|
| 1 | api-contract-testing | Y | 769 | 1221 | 199 | Strong | ok |
| 2 | api-doc-generator | — | 567 | 567 | 64 | None | no when_to_use |
| 3 | changelog-generator | — | 565 | 565 | 62 | Partial | no when_to_use |
| 4 | code-review | — | 525 | 525 | 129 | Partial | no when_to_use |
| 5 | commit-lint | — | 612 | 612 | 171 | Strong | no when_to_use |
| 6 | commit-message-writer | — | 379 | 379 | 128 | Partial | no when_to_use |
| 7 | coverage-analyzer | — | 353 | 353 | 153 | Partial | no when_to_use |
| 8 | csv-pro | — | 610 | 610 | 60 | None | no when_to_use |
| 9 | data-analysis | — | 492 | 492 | 66 | None | no when_to_use |
| 10 | diagram-maker | — | 422 | 422 | 189 | Partial | no when_to_use |
| 11 | docs-product | — | 454 | 454 | 65 | Weak | no when_to_use |
| 12 | docs-project | — | 590 | 590 | 75 | Partial | no when_to_use |
| 13 | docs-system | — | 522 | 522 | 47 | Partial | no when_to_use |
| 14 | dsh-runner | — | 831 | 831 | 121 | Weak | no when_to_use |
| 15 | frontend-design-taste | — | 635 | 635 | 121 | Partial | no when_to_use |
| 16 | frontend-perfection | — | 1158 | 1158 | 192 | Strong | no when_to_use |
| 17 | github-repo-hygiene | — | 506 | 506 | 27 | None | no when_to_use |
| 18 | long-running-agent-workflow | — | 489 | 489 | 156 | Strong | no when_to_use |
| 19 | mermaid-to-image | — | 469 | 469 | 62 | None | no when_to_use |
| 20 | mobile-frontend | — | 195 | 195 | 123 | Partial | no when_to_use |
| 21 | pdf-report-builder | — | 537 | 537 | 55 | Weak | no when_to_use |
| 22 | plan-skill | — | 692 | 692 | 88 | Weak | no when_to_use |
| 23 | presentation-craft | — | 475 | 475 | 116 | Partial | no when_to_use |
| 24 | presentation-engineering | — | 218 | 218 | 524 | Partial | no when_to_use, body 524>500 |
| 25 | presentation-maker | — | 249 | 249 | 416 | Strong | no when_to_use |
| 26 | raster-to-svg | — | 801 | 801 | 104 | None | no when_to_use |
| 27 | reddit-karma | — | 418 | 418 | 184 | None | no when_to_use |
| 28 | repo-community-files | — | 400 | 400 | 60 | None | no when_to_use |
| 29 | repo-metadata-health | — | 509 | 509 | 80 | Weak | no when_to_use |
| 30 | repo-readme-assets | — | 507 | 507 | 107 | Partial | no when_to_use |
| 31 | repo-social-preview | — | 424 | 424 | 70 | Partial | no when_to_use |
| 32 | secret-scanner | — | 338 | 338 | 132 | Strong | no when_to_use |
| 33 | security-review | — | 451 | 451 | 89 | Strong | no when_to_use |
| 34 | seo-audit | — | 533 | 533 | 31 | None | no when_to_use |
| 35 | seo-content | — | 527 | 527 | 37 | None | no when_to_use |
| 36 | seo-crawl | — | 444 | 444 | 30 | None | no when_to_use |
| 37 | seo-schema | — | 502 | 502 | 40 | None | no when_to_use |
| 38 | seo-toolkit | — | 391 | 391 | 28 | None | no when_to_use |
| 39 | skill-forge | — | 2 | 2 | 144 | Strong | no when_to_use |
| 40 | skill-suggester | — | 592 | 592 | 110 | Weak | no when_to_use |
| 41 | sql-helper | — | 484 | 484 | 61 | Weak | no when_to_use |
| 42 | systematic-debugger | — | 586 | 586 | 82 | Weak | no when_to_use |
| 43 | test-generator | — | 581 | 581 | 65 | Weak | no when_to_use |
| 44 | test-graphics | — | 401 | 401 | 231 | Weak | no when_to_use |
| 45 | version-bumper | — | 527 | 527 | 140 | Partial | no when_to_use |
| 46 | video-script-writer | — | 507 | 507 | 62 | None | no when_to_use |
| 47 | web-scraper | — | 536 | 536 | 81 | Weak | no when_to_use |

**Totals**: 47 skills · with `when_to_use`: 1 · body>500: 1 · desc+wtu>1536: 0

## Reading the result
- **Layer A**: systemic gap = missing `when_to_use` (46/47). Highest-leverage fix: add trigger phrases / example requests.
- **Layer B Strong** (verification built in): api-contract-testing, commit-lint, frontend-perfection, long-running-agent-workflow, presentation-maker, secret-scanner, security-review, skill-forge.
- **Layer B None** (reference/doc skills — verification less applicable, but a self-check could be added): docs-*, seo-*, repo-*, github-repo-hygiene, reddit-karma, mermaid-to-image, raster-to-svg, video-script-writer, csv-pro, data-analysis.

Run `python3 scripts/... ` — see methodology for how to re-audit.