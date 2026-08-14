---
name: repo-social-preview
description: "Generate a custom GitHub social preview (og:image) PNG 1280x640 for a repository: header composition + waves, solid background recommended, <1MB, PNG/JPG/GIF. Script: generate_social_preview.py (requires Pillow). Triggers: 'social preview', 'og image', 'og:image', 'social share image', 'repo preview png', 'open graph image', 'github social preview'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.1"
compatibility: "Requires pip install pillow for generate_social_preview.py; python3"
---

# Repo Social Preview — custom og:image for GitHub

Use this skill to **generate a custom social preview (og:image) for a repository**.
GitHub auto-generates a default preview, but a custom one (header composition + waves)
gives a branded, crop-safe image for social shares.

## When to use

- The repository needs a branded social preview instead of the auto-generated one.
- User asks for "social preview", "og image", "social share image", "repo preview png".

## Do NOT use

- For README content/visual header/footer — use `repo-readme-assets`.
- For legal/community files — use `repo-community-files`.
- For description/topics/Pages/health — use `repo-metadata-health`.

## Files

- `SKILL.md` — this file
- `scripts/generate_social_preview.py` — generates PNG 1280x640 (header composition + waves; **requires Pillow**)
- `references/social-preview.md` — details + OG tags for Pages

## Requirements (GitHub)

- File in root / `docs/` / default branch; format PNG/JPG/GIF; **< 1 MB**; **≥ 640×320**,
  recommended **1280×640**.
- Set in Settings → Social preview → Edit → Upload (**UI only**, no API).
- Transparency is supported, but a solid background is recommended.
- Crop-safety: keep essential text away from the edges (share previews crop on some platforms).

## Usage

```bash
python3 scripts/generate_social_preview.py \
  --name X --desc Y --user Z --cold #HEX --warm #HEX [--out og.png]
```

Then upload via Settings → Social preview. For GitHub Pages OG tags, see
`references/social-preview.md`.

## Anti-patterns

- Oversized file (>1 MB) or too small (under 640×320).
- Essential text/logo at the edges (cropped in shares).
- Overwriting an existing preview without explicit request.
