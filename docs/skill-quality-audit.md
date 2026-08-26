# Skill Quality Audit — Layer A / Layer B snapshot

Generated: 2026-08-26 · methodology: `docs/SKILL_QUALITY_GATE.md`

**Layer A flags**: `when_to_use` presence, body>500 (soft guideline), desc+wtu>1536 (hard Claude listing cap).
**Layer B class** is a *signal-based heuristic*: does the skill mention exit codes / verification / tests / CI gate?

| # | skill | wtu | desc | desc+wtu | body | Layer B | Layer A flags |
|---|---|---|---|---|---|---|---|
| 1 | api-contract-testing | Y | 769 | 1221 | 199 | Strong | ok |
| 2 | api-doc-generator | Y | 567 | 814 | 64 | None | ok |
| 3 | changelog-generator | Y | 565 | 795 | 62 | Partial | ok |
| 4 | code-review | Y | 525 | 736 | 129 | Partial | ok |
| 5 | commit-lint | Y | 612 | 865 | 171 | Strong | ok |
| 6 | commit-message-writer | Y | 379 | 626 | 128 | Partial | ok |
| 7 | coverage-analyzer | Y | 353 | 609 | 153 | Partial | ok |
| 8 | csv-pro | Y | 610 | 827 | 60 | None | ok |
| 9 | data-analysis | Y | 492 | 720 | 66 | None | ok |
| 10 | diagram-maker | Y | 422 | 715 | 189 | Partial | ok |
| 11 | docs-product | Y | 454 | 695 | 65 | Weak | ok |
| 12 | docs-project | Y | 590 | 883 | 75 | Partial | ok |
| 13 | docs-system | Y | 522 | 830 | 47 | Partial | ok |
| 14 | dsh-runner | Y | 831 | 1145 | 121 | Weak | ok |
| 15 | frontend-design-taste | Y | 635 | 989 | 121 | Partial | ok |
| 16 | frontend-perfection | Y | 1158 | 1497 | 192 | Strong | ok |
| 17 | github-repo-hygiene | Y | 506 | 793 | 27 | None | ok |
| 18 | long-running-agent-workflow | Y | 489 | 779 | 156 | Strong | ok |
| 19 | mermaid-to-image | Y | 469 | 765 | 62 | None | ok |
| 20 | mobile-frontend | Y | 195 | 491 | 123 | Partial | ok |
| 21 | pdf-report-builder | Y | 537 | 806 | 55 | Weak | ok |
| 22 | plan-skill | Y | 692 | 988 | 88 | Weak | ok |
| 23 | presentation-craft | Y | 475 | 806 | 116 | Partial | ok |
| 24 | presentation-engineering | Y | 218 | 549 | 524 | Partial | body 524>500 |
| 25 | presentation-maker | Y | 249 | 554 | 416 | Strong | ok |
| 26 | raster-to-svg | Y | 801 | 1073 | 104 | None | ok |
| 27 | reddit-karma | Y | 418 | 647 | 184 | None | ok |
| 28 | repo-community-files | Y | 400 | 679 | 60 | None | ok |
| 29 | repo-metadata-health | Y | 509 | 765 | 80 | Weak | ok |
| 30 | repo-readme-assets | Y | 507 | 777 | 107 | Partial | ok |
| 31 | repo-social-preview | Y | 424 | 681 | 70 | Partial | ok |
| 32 | secret-scanner | Y | 338 | 586 | 132 | Strong | ok |
| 33 | security-review | Y | 451 | 717 | 89 | Strong | ok |
| 34 | seo-audit | Y | 533 | 791 | 31 | None | ok |
| 35 | seo-content | Y | 527 | 794 | 37 | None | ok |
| 36 | seo-crawl | Y | 444 | 711 | 30 | None | ok |
| 37 | seo-schema | Y | 502 | 742 | 40 | None | ok |
| 38 | seo-toolkit | Y | 391 | 615 | 28 | None | ok |
| 39 | skill-forge | Y | 2 | 264 | 144 | Strong | ok |
| 40 | skill-suggester | Y | 592 | 845 | 110 | Weak | ok |
| 41 | sql-helper | Y | 484 | 743 | 61 | Weak | ok |
| 42 | systematic-debugger | Y | 586 | 860 | 82 | Weak | ok |
| 43 | test-generator | Y | 581 | 854 | 65 | Weak | ok |
| 44 | test-graphics | Y | 401 | 688 | 231 | Weak | ok |
| 45 | version-bumper | Y | 527 | 803 | 140 | Partial | ok |
| 46 | video-script-writer | Y | 507 | 776 | 62 | None | ok |
| 47 | web-scraper | Y | 536 | 810 | 81 | Weak | ok |

**Totals**: 47 skills · with `when_to_use`: 47 · body>500: 1 · desc+wtu>1536: 0

## Reading the result
- **Layer A `when_to_use`**: ✅ all 47/47 skills now carry `when_to_use` (backfilled 2026-08-26).
- **Layer B Strong** (verification built in): api-contract-testing, commit-lint, frontend-perfection, long-running-agent-workflow, presentation-maker, secret-scanner, security-review, skill-forge.
- **Layer B None** (reference/doc skills — verification less applicable, but a self-check could be added): docs-*, seo-*, repo-*, github-repo-hygiene, reddit-karma, mermaid-to-image, raster-to-svg, video-script-writer, csv-pro, data-analysis.