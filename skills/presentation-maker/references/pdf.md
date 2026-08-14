# PDF export for the deck

The default deliverable of `presentation-maker` is `md -> html -> pdf`. The PDF is
produced by `scripts/build_pdf.py`, which renders the **same themed `slides.html`**
that `build_html.py` generates — no separate layout or theme is re-implemented.

## How it works

1. **Launch** headless Chromium via the Playwright *sync* API and open the deck with
   `file://` (so it works fully offline; web fonts from a `font_url` simply fall back
   to the system stack declared in `--font`).
2. **Reflow for print** — inject a print stylesheet that turns the on-screen carousel
   (one `.active` slide shown at a time) into a paginated document:
   * every `.slide` becomes a `static`, full-page `flex` block, `visible`, with
     `break-after: page` so each slide lands on its own page;
   * `.nav-hint`, `.progress` and the `.slide-head` page number are hidden;
   * `print-color-adjust: exact` is forced on `*` so gradients and tinted backgrounds
     survive the print pipeline.
3. **Emulate `screen` media** before `page.pdf(...)` so web fonts and colors render
   exactly as they do on screen — this is what keeps the PDF visually 1:1 with the HTML.
4. **Emit** `page.pdf(landscape=True, width="1600px", height="900px",
   prefer_css_page_size=True, page_ranges="1-N")` where `N` is the live count of
   `.slide` elements.

## Why the pages are 16:9

The browser viewport is set to **1600×900** (overridable with `--viewport`). Each
slide is sized to `width: 100vw; height: 56.25vw` → at a 1600px viewport that is
exactly **1600×900**, i.e. one 16:9 slide per page. An injected `@page { size: 1600px
900px; margin: 0 }` (with `prefer_css_page_size=True`) pins the paper to the same
16:9 box, so there is no scaling or letterboxing — the PDF page matches the slide
pixel-for-pixel.

## CLI

```bash
python3 build_pdf.py slides.html deck.pdf [--viewport 1600x900]
```

Exit codes: `0` success (prints page count), `1` render failure, `2` Playwright not
installed (prints the install hint).

## Notes / limitations

* **Fonts:** if the deck references a Google Fonts `font_url` and the machine is
  offline, Chromium falls back to the system font stack in `--font` (e.g.
  `-apple-system` / `Segoe UI`). The layout and metrics stay correct; only the exact
  typeface may differ. For guaranteed 1:1 typography, run with network access or
  self-host the fonts.
* **One slide per page** is the contract; slides are designed to fit 1600×900, so no
  slide overflows into a second page.
* Only Playwright is required — no other Python dependencies.
