# Visual design: ftsrg lecture look in Quarto reveal.js

Goal: the Quarto deck should look like the lecturer's existing PowerPoint template
(source: `2024_ESE_Big_Data_visualization.pptx`, not in this repo; latest copy in
`SessionStore/2025_10_08_Empirical/`). Only three slide
types are used: **title slide**, **section slide**, **content slide**. Don't build the
other PowerPoint layouts.

Implemented as a custom SCSS theme (`ftsrg.scss`, used as `theme: [default, ftsrg.scss]`
in `_quarto.yml`), plus `ftsrg.lua` for the section-slide backgrounds. Positions were
calibrated against PowerPoint's own PNG export of the reference deck (title, footer and
slide number match it to ±1 px); where that measurement differs from the numbers first
written here, the text below gives the measured value. Keep the deck at 1600×900 (same 16:9 as the PPTX's 13.33″×7.5″),
so **1 inch = 120 px** and **1 pt = 1.667 px**. All positions below are given as
percentages of slide width/height so they survive any resizing.

## Assets (`assets/brand/`)

| File | Use |
|---|---|
| `title-bg.png` | Full-slide background of the title slide (1920×1080; dark band with blue→red flow lines, white strip at the bottom for logos) |
| `section-bg.png` | Full-slide background of section slides (1920×1080; flow-line panel with a diagonal right edge + grey outlined parallelogram; geometry is baked in) |
| `ftsrg-logo-white.png` | Logo inside the footer tab |
| `ftsrg-logo-color.png` | Logo on the title slide (black with crimson dot) |
| `bme-logo.jpg` | BME logo on the title slide |

`assets/legacy/` holds the old deck's figures, named by old slide number (`s04-…`).
They are raw material for the rework, not part of the style.

## Palette (from the PPTX theme)

| Role | Hex |
|---|---|
| Title text | `#2F2D2E` |
| Body text | `#000000` |
| Background | `#FFFFFF` |
| Footer bar grey | `#A7A8A7` |
| Primary accent (callout boxes, emphasis fills) | `#1446A0` |
| Secondary accent (crimson, = the red ftsrg dot) | `#960018` |
| Further accents, use sparingly | `#522B47` plum, `#FB8B24` orange |
| Footer tab gradient | `#283C88` (from 32 %) → `#5F2C60` (100 %), CSS `linear-gradient(154deg, …)` |
| Links | `#0563C1`, underlined |

## Typography

- Headings: **Open Sans ExtraBold** (weight 800). Body: **Open Sans** (400); bold = 700.
- Bundle the fonts locally (woff2 in `assets/fonts/`, `@font-face`), don't rely on
  Google Fonts at runtime: lecture-hall network is not guaranteed. Fallback stack:
  `"Open Sans", "Segoe UI", Arial, sans-serif`.
- Sizes: slide title 40 pt ≈ **66 px**, colour `#2F2D2E`, line-height 1.08 (the PPTX's
  "90 %" is of PowerPoint's 1.2 single spacing), left-aligned.
  Body text **36 px**, second level **30 px**. (The PPTX master says 28/24 pt, but the
  real slides were autofit-shrunk; don't emulate shrinking. If content doesn't fit,
  split the slide.)
- Bullets: level 1 `•`, level 2 `–` (en dash). Generous space between level-1 items,
  tight between level-2 items.

## Content slide (the default `##` slide)

- White background. Title at left 4.7 %, top 4.6 %; body starts at ~17.5 % from the top,
  same left edge; right margin like the left one.
- **Footer**, on every content and section slide, height 6.4 % of the slide, flush with
  the bottom edge:
  - grey bar `#A7A8A7` from the left edge to about 92 % width, its right end cut with a
    "/" slant (top-right corner at 92.4 %, bottom-right at 91.0 %);
  - a thin white gap, then the **tab**: from the slant (top-left at 93.4 %, bottom-left at
    92.0 %) to the right edge, filled with the gradient above, holding
    `ftsrg-logo-white.png` (left edge ≈ 93.8 %, width ≈ 5.4 %, vertically centred);
  - slide number centred in the grey bar, 12 pt ≈ 20 px, black.
- Implementation: the bar and tab are `::before` / `::after` of `.reveal .slides`
  (it has the 1600×900 slide coordinate system and scales with the deck) using
  `clip-path: polygon(…)`; in PDF export they are drawn on every `.pdf-page` instead.
  reveal's `.slide-number` lives outside `.slides`; it is centred on the bar with the
  `--slide-scale` variable reveal publishes. `margin: 0` in `_quarto.yml` keeps the
  footer flush with the bottom edge of a 16:9 window.
- No other decoration: no title underlines, no stripes, no progress bar; Quarto's menu
  button is hidden (the menu still opens with M).
- Live cells stretch to fill the content area below the title (reveal's `r-stretch`), so
  they end at the body bottom (91.2 %) whatever the title's length.

## Section slide (level-1 `#` headings)

- Background: `section-bg.png`, added to every level-1 heading by `ftsrg.lua`, with
  `background-size: contain` (not cover): the image is 16:9 like the deck, so in a
  letterboxed window it stays aligned with the title instead of being cropped differently.
- Title in white, Open Sans ExtraBold 72 px (the reference deck's 48 pt autofit to 90 %;
  1.1× the slide titles), placed on the dark panel: left 4.7 %, vertically centred on the
  panel (~51 % from the top, where the reference deck's section titles sit; the
  layout's unmoved placeholder would give ~40 %), max width 42 % (it must stay left of
  the diagonal edge).
- Footer as on content slides.

## Title slide

Build it as an explicit first slide (simpler to control than Quarto's generated title
slide; `lecture.qmd` has `pagetitle:` instead of `title:` so Quarto generates none); give
it class `.ftsrg-title` and `data-state="ftsrg-title"` (reveal puts the state as a class
on the viewport element, `<body>`; a plain "title" would collide with Quarto's `.title`)
and hide the footer there.

- Background: `title-bg.png`, `background-size: contain` (see section slides).
- Title: white, Open Sans ExtraBold 73 px (44 pt, as in the reference deck), left 8.3 %,
  bottom-anchored in the 17 %–41 % box.
- Subtitle block below it (`::: course`; left 8.3 %, from ~43 % top), white Open Sans
  33 px (20 pt), lines: course name, term, then after a gap the author line with e-mail
  (white, underlined).
- Bottom white strip (from ~82 % top): `bme-logo.jpg` on the left (left 1.9 %, width ≈ 22 %),
  a centred three-line institution text in black 26 px (the PPTX's 30 px would not fit
  the department's longer new name between the logos), `ftsrg-logo-color.png` on the
  right (crop frame at left ≈ 80.6 %, width ≈ 13 %; the PNG has transparent margins).
- Institution text (the department was renamed since the old deck):
  "Budapest University of Technology and Economics /
  Department of Artificial Intelligence and Systems Engineering / ftsrg Research Group".

## Reusable elements

- `.bubble`: callout box, fill `#1446A0`, white Open Sans text ~24 px, rounded corners
  (~8 px), used to annotate figures (as on the old HoloViz slide). Optional tail:
  `.tail-down` / `.tail-up`, aimed with `style="--tail-x: 120px;"`. The trailing `;`
  matters, because Quarto appends `.absolute` positions to the same attribute.
- `.fig-grid` (with `layout-ncol` or `layout`): figures of mixed aspect ratio at one
  common height (`--fig-h`), scaled down, never cropped.
- Diagrams: inline SVG from `assets/diagrams/`, class `diagram`, sized by `--diagram-h`.
- Tables at 30 px (the second-level size); set column widths with the dash counts of
  the separator row.
- Figures: prefer Quarto layout (`layout-ncol`, `.columns`) over absolute positioning;
  images never exceed the content area (they must not overlap the footer).
- Source links under figures: `::: source`, small (18 px), bottom-left of the content
  area; a stretched figure on the same slide stops above it.
- Code blocks: keep Quarto's highlighting; font size such that ~70 characters fit in
  half the slide width (the live cells use two-column layouts).
- Explanatory text for readers of the deck: `.small` (21 px, `[text]{.small}` under a
  bullet or `::: small` under a figure; tables inside it shrink to 22 px). Worked
  examples and "why it matters" blocks: `.medium` (26 px). Main points stay at body
  size.
- Live slides: `:::: cell-aside` at the bottom of the output column stacks a `::: try`
  hint (grey rounded box, `assets/icons/lightbulb.svg`, 20 px) above a `::: legend`
  (18 px; `[]{.ramp style="--ramp: linear-gradient(…)"}` with `[[low]{} [high]{}]{.ends}`,
  or `[label]{.swatch style="--c: …;"}` swatches). For wide-layout cells:
  `{.try .inline style="top: …px;"}` right of the Run button, `{.legend .top}` beside
  the title.
- Local video: `<video class="video-embed" controls preload="metadata" poster=… src=…>`
  in a raw-HTML block; the poster doubles as the fallback when the file is missing,
  and is what the PDF shows (controls hidden in print).
- Animations: give the animated image `{.screen-only}` and add a still of its final
  state with `{.print-only}`; `?print-pdf` and the PDF show the still.
- Photos from outside: freely licensed only, with author, licence link, source and
  "cropped" in the slide's source line.
- Figures generated by `figures.py` use the palette above and Open Sans (the TTF must
  be installed for matplotlib); charts at 200 dpi.

## Live cell pages (`live.py`)

These render inside iframes, so the theme does not reach them. Match the look lightly:
Open Sans for UI text, Run button in `#1446A0`, white background, tracebacks in the
crimson `#960018`. The output side of datashader cells stays black
(`background = "black"` in `common.py`). `live.py` serves `assets/` itself, so the
bundled font needs no network either.
