# Skill Quality Audit (Layer A/B)

Generated: 48 skills

| skill | when_to_use | desc+wtu len | when_to_use len | body lines | Layer A issues | Layer B | Notes |
|---|---|---|---|---|---|---|---|
| api-contract-testing | Y | 1221 | 452 | 157 | refs=0 | references=0 | Partial |
| api-doc-generator | Y | 812 | 247 | 47 | refs=0 | references=0 | Partial |
| changelog-generator | Y | 793 | 230 | 45 | none | references=4 | Strong |
| code-review | Y | 736 | 211 | 91 | none | references=7 | Strong |
| commit-lint | Y | 865 | 253 | 136 | none | references=11 | Strong |
| commit-message-writer | Y | 626 | 247 | 90 | none | references=9 | Strong |
| coverage-analyzer | Y | 609 | 256 | 115 | refs=0 | references=0 | Partial |
| csv-pro | Y | 827 | 217 | 41 | refs=0 | references=0 | Partial |
| data-analysis | Y | 720 | 228 | 46 | refs=0 | references=0 | Partial |
| diagram-maker | Y | 715 | 293 | 154 | refs=0 | references=0 | Partial |
| docs-product | Y | 695 | 241 | 47 | none | no script | Weak |
| docs-project | Y | 883 | 293 | 55 | none | no script | Weak |
| docs-system | Y | 830 | 308 | 32 | none | no script | Weak |
| dsh-runner | Y | 1145 | 314 | 88 | none | references=1 | Strong |
| frontend-design-taste | Y | 989 | 354 | 95 | none | no script | Weak |
| frontend-perfection | Y | 1497 | 339 | 164 | refs=0 | references=0 | Partial |
| github-repo-hygiene | Y | 793 | 287 | 17 | none | no script | Weak |
| long-running-agent-workflow | Y | 779 | 290 | 109 | refs=0 | references=0 | Partial |
| mermaid-to-image | Y | 765 | 296 | 41 | none | references=4 | Strong |
| mobile-frontend | Y | 296 | 296 | 95 | none | no script | Weak |
| pdf-report-builder | Y | 806 | 269 | 37 | none | references=11 | Strong |
| plan-skill | Y | 986 | 296 | 71 | refs=0 | references=0 | Partial |
| presentation-craft | Y | 806 | 331 | 99 | none | no script | Weak |
| presentation-engineering | Y | 549 | 331 | 375 | none | no script | Weak |
| presentation-maker | Y | 305 | 305 | 334 | none | references=18 | Strong |
| raster-to-svg | Y | 1073 | 272 | 71 | none | references=5 | Strong |
| reddit-karma | Y | 647 | 229 | 137 | none | no script | Weak |
| repo-community-files | Y | 679 | 279 | 42 | none | no script | Weak |
| repo-metadata-health | Y | 765 | 256 | 56 | none | references=12 | Strong |
| repo-readme-assets | Y | 777 | 270 | 79 | none | references=7 | Strong |
| repo-social-preview | Y | 681 | 257 | 58 | none | references=5 | Strong |
| secret-scanner | Y | 586 | 248 | 98 | none | references=3 | Strong |
| security-review | Y | 717 | 266 | 65 | none | references=1 | Strong |
| seo-audit | Y | 791 | 258 | 20 | none | no script | Weak |
| seo-content | Y | 794 | 267 | 24 | refs=0 | references=0 | Partial |
| seo-crawl | Y | 711 | 267 | 19 | none | no script | Weak |
| seo-schema | Y | 742 | 240 | 27 | refs=0 | references=0 | Partial |
| seo-toolkit | Y | 615 | 224 | 18 | refs=0 | references=0 | Partial |
| skill-feedback | Y | 797 | 366 | 62 | refs=0 | references=0 | Partial |
| skill-forge | Y | 262 | 262 | 121 | none | no script | Weak |
| skill-suggester | Y | 845 | 253 | 78 | refs=0 | references=0 | Partial |
| sql-helper | Y | 743 | 259 | 42 | refs=0 | references=0 | Partial |
| systematic-debugger | Y | 858 | 274 | 61 | refs=0 | references=0 | Partial |
| test-generator | Y | 852 | 273 | 49 | none | references=1 | Strong |
| test-graphics | Y | 688 | 287 | 159 | refs=0 | references=0 | Partial |
| version-bumper | Y | 803 | 276 | 108 | none | references=11 | Strong |
| video-script-writer | Y | 776 | 269 | 43 | refs=0 | references=0 | Partial |
| web-scraper | Y | 810 | 274 | 57 | refs=0 | references=0 | Partial |

## Reading the result
- **when_to_use**: Y means discoverable trigger present (our backfilled standard).
- **desc+wtu len**: must be <=1536 (Claude Code listing truncation).
- **body lines**: soft cap 500 (skill-forge).
- **Layer B = Strong** when the skill has a script and references a runner (subprocess/os.system/Popen/run/check_*).

## Layer C feedback
Usage feedback is captured by the `skill-feedback` skill into `feedback/<skill>/YYYY-MM-DD.jsonl` and fed into the skill-forge improvement loop. Re-run this audit after acting on feedback.