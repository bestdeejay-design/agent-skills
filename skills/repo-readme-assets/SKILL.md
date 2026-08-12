---
name: repo-readme-assets
description: "README.md (EN) + localized mirror + local animated SVG header/footer for a repository. Generates assets/header.svg and assets/footer.svg with SMIL animation (4 presets: default/minimal/dark-first/monochrome), zero external services. Scripts: generate_assets.py, validate_svg.py, extract_context.py. Triggers: 'readme header', 'animated svg', 'waving svg', 'svg banner', 'readme assets', 'readme visual', 'smil animation', 'repo header', 'readme footer', 'readme generator', 'update readme', 'readme badges'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "Requires python3 (stdlib only) for generation/validation"
---

# Repo Readme Assets — README + animated SVG header/footer

Use this skill to **create or update a repository README and its visual header/footer**
with local animated SVG assets. Zero external services: no capsule-render, no shields
generators, no URL banners. Animation is SMIL only (`<animate>`, `<animateTransform>`)
so it works inside `<img>` on GitHub without scripts or network requests.

## When to use

- A repository needs a README with a header/footer banner (local animated SVG).
- Major change happened and the README must reflect the current project state.
- User asks for "readme header", "animated svg", "waving svg", "svg banner",
  "readme assets", "readme visual", "smil animation".

## Do NOT use

- README is already current and the user did not request changes — do not "improve".
- A single tiny fix (e.g. one badge) — edit directly, no skill needed.
- For legal/community files (LICENSE, CONTRIBUTING, SECURITY) — use `repo-community-files`.
- For description/topics/Pages/community-health — use `repo-metadata-health`.
- For the social preview PNG — use `repo-social-preview`.

## Files

- `SKILL.md` — this file
- `scripts/generate_assets.py` — deterministic generation of `assets/header.svg` + `assets/footer.svg`
- `scripts/extract_context.py` — auto-detect name/desc/stack/colors/username from git remote
- `scripts/validate_svg.py` — validate SVG against skill rules (SMIL, mask, morphing)
- `references/svg-animation.md` — full SVG animation spec + header/footer templates
- `references/svg-presets.md` — the four presets
- `references/color-tokens.md` — detected values (USERNAME/PROJECT_NAME/COLD/WARM)
- `references/canonical-patterns.md` — canonical references and gaps

## Scripts

| Script | Purpose | Call |
|---|---|---|
| `generate_assets.py` | Deterministic `assets/header.svg` + `assets/footer.svg` (presets: `--preset default\|minimal\|dark-first\|monochrome`) | `python3 scripts/generate_assets.py --name X --desc Y --user Z --cold #HEX --warm #HEX [--preset default]` |
| `extract_context.py` | Auto-detect generation context from git remote | `python3 scripts/extract_context.py [--path DIR] [--gh-repo owner/repo] [--text]` |
| `validate_svg.py` | Validate SVG rules (SMIL, mask, d-path morphing) | `python3 scripts/validate_svg.py assets/` |

Reports are JSON; exit codes 0/1 (CI-friendly).

## README — required elements

1. **Header**: project name, one-line description, live badge links (3–6, one style).
2. **Status block**: current check numbers (typecheck/contract/integration).
3. **Quick start**: install, infra, run.
4. **Repo structure**: full tree (include new dirs/services).
5. **Stack/events/checks sections** — kept in sync with real code.
6. **GitHub Pages link** (if enabled): `https://<user>.github.io/<repo>/` + homepage in About.
7. **Language switcher**: `**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](…)`.
8. **Hashtags/keywords** for search (description + topics).

Rules:
- `README.md` is **always English** (GitHub international standard).
- `README.<lang>.md` is a localized **mirror**: propagate English changes 1:1 (headings, numbers, statuses).
- Diverged localizations are a typical anti-pattern — run a programmatic heading-diff before release.
- Avoid "AI-slop" wording: "seamless", "unleash", "empower", emoji overload.
- Prefer **relative** links to repo files (absolute links break in clones).
- GitHub auto-generates TOC — no manual table of contents needed.

## Animated SVG header/footer

By default each repo gets `assets/header.svg` (start of README) and `assets/footer.svg`
(end of README), required in both language versions.

**Principle: zero external services.** Animation is SMIL only.

Key techniques: "background wave" effect (a black wave in `<mask>` cuts color → page
background shows through), `d`-path morphing across 4 frames (crest `Q`+`T`, identical
command sequence in every frame), 30% wave desync, a highlight pass once ~16s, a
twinkling speck in the footer.

- Full spec + templates → `references/svg-animation.md`
- Detected values → `references/color-tokens.md`
- Presets → `references/svg-presets.md`

Preset choice: `default` (animated gradient) by default; `minimal` (static gradient, no
waves) for docs/stable tools; `dark-first` (deep dark backdrop, GitHub dark theme);
`monochrome` (b/w, no SMIL) for books/print/specs. Ask the user, else take `default`.

### How to generate (recommended path)

By script (deterministic, then validate):

```bash
python3 scripts/generate_assets.py \
  --name "Project Name" --desc "Short description" --user "username" \
  --cold "#0ABAB5" --warm "#F64A8A"
python3 scripts/validate_svg.py assets/        # expect: all passed
```

Manually (when the script is unavailable): read `references/svg-animation.md`, substitute
`COLD`, `WARM`, `PROJECT_NAME`, `PROJECT_DESC`, `FONTCOLOR`, `USERNAME` into the templates,
create `assets/`, add the links (see "Insert into README.md" in the reference).

### Generation safety

- Do not generate without confirming `USERNAME` when it is not obvious.
- Do not overwrite existing `.svg` without an explicit request.
- Do not touch README content between header and footer.
- Do not add header/footer if they already exist (only on request).
- SVG: no `<script>`, no base64, SMIL only; mask with a white `<rect>` covering the canvas.
