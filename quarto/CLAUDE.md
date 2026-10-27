# Big Data visualization lecture: live datashader census walkthrough

## What this is

Slides for the Big Data visualization lecture (ESE course session), built in Quarto
reveal.js instead of PowerPoint. The core is a slide-by-slide walkthrough of the HoloViz
**Census 2010** datashader example (https://examples.holoviz.org/gallery/census/census.html):
every notebook cell that matters gets its own slide, and **every cell runs live during
the lecture**, editable in front of the students (change `how='log'` → `'eq_hist'`,
Shift+Enter, see the result and the wall time). Around it, the rest of the lecture is
reworked from the old PowerPoint deck into one storyline (see Decisions, item 8).

Hard requirement from the lecturer: cells must execute in real time on stage.
Pre-rendered outputs (Quarto executing at render time + `freeze`) were built first and
**rejected** for that reason. Don't reintroduce them for the walkthrough.

## Architecture

- **`_census-live.qmd`** is the single source of truth. Each slide is markdown (title,
  optional one-liner, `::: notes` for speaker view) plus a code block
  ```` ```{#cell-name .python .live} ````. Optional attribute `layout="wide"` puts the
  editor on top and the output below (used for maps and the six-city grid); default is
  code left, output right.
- **`live-cells.lua`** is a Quarto filter. In revealjs output it replaces each `.live`
  block with a lazily loaded iframe (`data-src`) to `http://localhost:5006/cell?name=<cell-name>`.
  The iframe carries reveal's `r-stretch`, so it fills the content area below the slide
  title (662 px under a one-line title, 591 px under two); `height="…"` on the block
  fixes it instead. In other formats (handout HTML/PDF) the blocks remain ordinary code
  listings.
- **`live.py`** is the Panel server, i.e. the "kernel":
  - parses the `.live` blocks from `_census-live.qmd` (re-read on every page load, so
    editing the .qmd needs no server restart);
  - at startup runs `from common import *`, then **all cells once in document order**
    (warm-up), so any slide can be run out of order;
  - one shared namespace (`NS`) across all cells and sessions, like a notebook kernel;
  - each cell page: Ace code editor + Run button + wall-time readout + output pane.
    Output rendering: datashader `tf.Image` → PNG pane; HoloViews objects → HoloViews
    pane (responsive only in wide layout); anything else → `pn.panel`. Errors show a red
    traceback. Cells run in a thread (`asyncio.to_thread`) so the loading spinner shows.
  - `Keys` (a Panel `JSComponent`): Shift+Enter runs the cell; PageUp/PageDown (the
    presenter clicker) are forwarded to reveal.js via `postMessage`. It also switches
    on Ace's soft wrap (Panel's CodeEditor has no option for it), so long code lines
    wrap instead of needing the scrollbar.
- **Live-slide extras** (in `_census-live.qmd`, next to each cell, not seen by
  `live.py`): a `::: try` hint (light-bulb box) and, on slides that show a datashader
  image, a `::: legend` with the exact colour ramp or the `color_key` swatches, both
  inside a `:::: cell-aside` stacked at the bottom of the output column. Wide-layout
  cells use `{.try .inline style="top: …px;"}` next to the Run button and
  `{.legend .top}` beside the title. When a cell's colormap, floor or `how` changes,
  update its legend; test any new hint on the real data.
- **`common.py`** holds notebook setup not worth a slide: regions, `plot_width/height`,
  `background`, `cm`, `export`, `color_key`, `races`, HoloViews imports, `labels` tile layer.
- **`lecture.qmd`** is the deck: the explicit ftsrg title slide, then one include file
  per section, in this order (each file opens with its `#` section slide):
  1. `_problem.qmd`: too many observations (data frames wide vs narrow, real data-set
     sizes, pixel budget and overplotting, which charts scale, sampling, 3D aside);
  2. `_framework.qmd`: Wickham's bin–summarize–smooth–plot (the Iris worked example,
     binning, Z-order, summary taxonomy and sketches, and one slide on smoothing,
     peeling and transforming with Wickham's Fig. 1).
     It ends with the placeholder
     `<!-- flights live case study goes here -->`;
  3. `_bridge.qmd`: datashader as a Python library (with a stack diagram), Jupyter as
     its usual home (an animated JupyterLab recording), the datashader pipeline, rows
     to one pixel, the pipeline read through the framework, and the functional
     architecture diagram;
  4. `_census-live.qmd`: two static slides on the data (the census, its lineage and
     privacy layers; an ethics note on race in the data), then the live walkthrough
     (plus one static histogram-equalization slide after `eqhist`);
  5. `_interactivity.qmd`: re-aggregate on demand vs precomputed tiles/cubes vs query
     engines, each with an architecture diagram;
  6. `_landscape.qmd`: the tool map by where computation happens, and the HoloViz slide;
  7. `_close.qmd`: the pitfalls checklist and take-aways.
- **`figures.py`**: generates the static figures (`assets/figures/*.png`: overplotting,
  curse of dimensionality, census sample vs all, 3D bars vs 2D, Iris pipeline) and the
  data-driven SVGs (dataset sizes, bin-index example, the three interactivity
  architectures). Not a build step: run `python figures.py [name …]` in the `census`
  env after changing one, and commit the outputs. Census figures read `./data`; Iris
  comes from `assets/data/iris.csv` (R's copy).
- **`assets/figures/jupyter-census.webp`**: an animated WebP (9 frames, ~14 s loop)
  recorded from a real JupyterLab 4.6 run of the case study's first steps on the real
  data (Playwright screenshots at 1200×675 × 4/3, assembled with Pillow). To redo it:
  JupyterLab in a venv with `--system-site-packages` over the `census` env, the same
  four cells, frames while busy and when done.
- **Other assets:** `assets/photos/` (the bus-stop display, CC BY-SA 4.0, attributed on
  its slide), `assets/icons/lightbulb.svg` (hint boxes), `assets/video/` (NASA's CO₂
  video for the 3D slide: git-ignored, download line in `README`; without it the slide
  shows a still and links the video).
- **`assets/diagrams/*.svg`**: redrawn diagrams in the theme palette (bin ordering,
  functional architecture, tool landscape, data-frame shapes, rows to one pixel,
  summary merging, plus the generated ones above). They are inlined with
  ```` ```{=html} ```` + `{{< include … >}}` so they use the page fonts, and sized by the
  theme's `svg.diagram` class (`--diagram-h`). Inline SVG `<style>` is page-global, so
  each file scopes its rules to its own `id`.
- **`student-setup.md`**: handout for students running the census example themselves
  (not part of the deck, and not linked from it). **`REWORK.md`** is the brief the
  storyline was built from; **`rework-log.md`** is the step-by-step review trail, with
  judgement calls and open items.
- **`ftsrg.scss`** + **`ftsrg.lua`** + **`assets/fonts/`**: the ftsrg lecture look (see
  STYLE.md). The theme draws the footer, places the slide number, and styles the three
  slide types; the filter gives level-1 (section) slides their background. Open Sans is
  bundled (variable woff2, latin + latin-ext, OFL). `url()`s in the theme are written
  relative to where Quarto puts the compiled CSS (`$ftsrg-root`).
- **`_quarto.yml`**: revealjs 1600×900 (keeps reveal's upscaling small; scaling can
  disturb mouse coordinates in embedded plots), theme, `margin: 0`, plain slide number,
  no progress bar, MathML formulas (no MathJax CDN), both Lua filters. The deck itself
  executes no Python.
- **`environment.yml`**: conda env `census` (conda-forge; includes Quarto).
- **`print_pdf.py`** → **`lecture.pdf`**: the static PDF of the deck. With `live.py`
  running, it shows each live slide in turn, presses Run, screenshots the cell, then
  prints reveal's `?print-pdf` layout with the screenshots in place of the live-cell
  iframes (headless Chromium doesn't print cross-origin iframes, and 21 cell pages
  loaded at once on the long print page go stale). Needs Playwright + its Chromium
  (not in `environment.yml`). Print-only stills: `{.screen-only}` / `{.print-only}`
  pairs (the Jupyter animation → its last frame); the video prints as its poster.
- **`present.sh`**: activates `census`, starts `live.py`, waits for warm-up (polls
  `localhost:5006/cell`), then `quarto preview lecture.qmd --no-browser`. Ctrl+C stops both.

## Environment

Windows 11 + WSL (Ubuntu). Everything runs inside WSL in the conda env `census`
(Miniconda at `~/miniconda3`); the Windows browser reaches both servers through WSL2's
localhost forwarding. Editing via VS Code with the WSL extension.

The project folder lives in an Insync-synced folder under `/mnt/c/...`. The dataset sits
directly in `data/census2010.parq` (git-ignored; download as in `README`). That is the
lecturer's choice: don't suggest moving it to the Linux home or symlinking it. The
cells read `./data/census2010.parq` (live.py chdirs to its own folder).

## Decisions and fixes, in the order they happened

1. PowerPoint → Quarto reveal.js: markdown-native, LLM-cheap to edit, executable/
   interactive content, still exports to pptx for colleagues if needed.
2. Datashader's zoom interactivity needs a live Python process (re-aggregation per
   zoom); no Pyodide/WASM route because Numba doesn't run in the browser. Hence a
   local Panel server embedded via iframes.
3. First design: static cells executed by Quarto at render time + Panel only for the
   two interactive maps. Rejected: all cells must run live. Replaced by the live-cell
   server above.
4. CartoDB label tiles (used in the notebook) now require an API key → replaced with
   Esri's public `World_Boundaries_and_Places` reference layer (in `common.py`).
5. Dask can no longer read Parquet with fastparquet (`engine='fastparquet'` → "not
   supported"), and reading the fastparquet-written census file with pyarrow fails with
   "Not all columns are categoricals". Fix: `dd.read_parquet(..., categories=[])`; the
   following `df.categorize('race')` rebuilds the categories. Verified on a reproduction.
6. Arrow-key forwarding from the iframes to reveal.js caused erratic multi-slide jumps
   (cause not pinned down). Removed: arrows stay inside the cell page (editor cursor);
   only PageUp/PageDown are forwarded; the key listener is installed once per page and
   ignores auto-repeat. To navigate with arrows, click the slide heading first.
7. ftsrg look applied (2026-09-24): `ftsrg.scss`/`ftsrg.lua`, calibrated against
   PowerPoint's PNG export of the reference deck. The title and footer cost the live
   cells height (780 px iframes → content area), so the wide-layout editor in `live.py`
   now sizes to its lines more tightly and the six-city grid uses 380×220 tiles.
8. Storyline rework (2026-09-24, from `REWORK.md`). The old deck's two halves
   (practical demo, then Wickham's theory with static R plots) are joined by one idea:
   **datashader is bin–summarize–smooth–plot with pixels as the bins.** Order: the
   problem → the framework, briefly → the bridge (datashader's pipeline read through
   the framework) → the live census walkthrough → where aggregation runs for
   interactivity → the tool landscape → a pitfalls checklist.
   - The flight-delay case study (old slides 18–27) is out of scope for now; it will
     become a second set of live cells at the placeholder in `_framework.qmd`.
   - Formulas switched to MathML, so no MathJax CDN is needed, like the offline fonts.
9. Wickham's paper prints its fast kernel as K(x) = (1 − |x|³)² I(|x|<1) and calls it
   "triweight". The slide followed the paper; its notes explain that the paper's §4.3
   and the bigvis code actually use tricube, (1 − |x|³)³. (That slide now lives in
   `_backup-framework-smoothing.qmd`, see decision 11.)
10. Round 2 (2026-09-24 afternoon, from the lecturer's dictated comments; details in
   `rework-log.md`, steps R1–R6): a data-frame (wide vs narrow) slide; real data-set
   sizes vs the pixel budget; an overplotting story; sourced explanations on the
   sampling slides and a "just process everything" slide; the NASA video in place and
   a 3D-vs-2D figure; the Iris worked example of the four steps and of the bin index;
   why Z-order matters; merge diagrams for distributive / algebraic / holistic; a rows
   → one pixel diagram; the device range (clusters … bus-stop display); architecture
   diagrams for the three interactivity options; code wrap, legends and hints on the
   live slides; speaker notes on every slide, written to be shareable with students.
11. The three slides after the sketches ("The core tension", "Smoothing: kernel
   methods", "Peel and transform") read as leftovers of the old flight-data material;
   they were replaced by one slide, "Smooth, peel, transform", built on Wickham's
   Fig. 1 (flight data, raw / peeled / modulus-transformed). The originals are kept,
   unrendered, in `_backup-framework-smoothing.qmd`.
12. Static PDF (after the lecture, 2026-09-24): `print_pdf.py`, see Architecture.
   Print fixes in `ftsrg.scss`: the title slide's institution block is placed without
   `translateY(-50%)` in print (Chrome's page breaking ignores transforms and pushed
   its last line off the page), and video controls are hidden.

## Verification status

Tested in a sandbox on synthetic data (200k points) with pip-installed Panel 1.9,
HoloViews 1.23, datashader 0.19, Dask 2026.8: all 21 cells execute and render; each
cell page builds in a real Bokeh session; Run was simulated incl. an edited cell and a
failing one; the deck renders with 21 iframes and speaker notes.
Confirmed working by the lecturer on the real machine: the overall setup, live cells.
Not verifiable in the sandbox (no browser): JS behaviour (key handling, editor font size).
Theme (2026-09-24, Windows Quarto 1.10.18 + headless Chrome): all slide types, 16:9 and
letterboxed windows, `?print-pdf`, and every live slide rendered against `live.py` fed
200k synthetic points (cells run, outputs fit the new area). Not yet seen with the real
dataset or on the lecture-hall projector.
Rework (2026-09-24): after every step `quarto render lecture.qmd` in the `census` env
(Quarto 1.9.38) finished without warnings. Every new slide was screenshotted in headless
Chrome, and a layout check over all 59 slides found no content below the body area
(91.2 %). Claims about papers and tools were checked on the web (sources in the notes
and in `rework-log.md`).
Round 2 (2026-09-24 afternoon): rendered in the `census` env; every changed slide
screenshotted with Playwright's headless Chromium, the live slides with `live.py`
running on the real 306,675,004-row dataset (warm-up ≈ 40 s, ≈ 6 GB RAM) and each cell
executed; every hint's suggested edit run on the real data.
Running this from Claude Code's sandbox: set `XDG_CACHE_HOME` (and `MPLCONFIGDIR`) to a
writable temp dir, because Quarto's sass cache and Numba's cache live under `~/.cache`;
Windows programs (the Windows Chrome) can't be started from inside the sandbox.

## Conventions for further work

- Edit cells in `_census-live.qmd`; cell ids are descriptive names (no codes like A1/S2).
- Keep cell code close to the original notebook; when deviating, say why in `::: notes`.
- Keep the setup low-maintenance: no extra services, no build steps beyond Quarto.
- Speaker notes paraphrase the notebook narrative; don't paste long passages from it.
- One idea per slide; never shrink text to fit, split instead. Speaker detail goes into
  `::: notes`, citations in a `::: source` line or the notes.
- Claims about current tools, systems and papers must be verified on the web before they
  go on a slide. If something can't be verified, leave it out and put a `TODO(verify)`
  line in that slide's notes.
- Diagrams: SVG in `assets/diagrams/`, theme palette, an `id` on the root `<svg>` with
  all CSS scoped to it.
- Speaker notes: short bullets that jog the presenter's memory and still read well if
  the deck is handed to students; sources go there too.
- Explanatory text for readers of the deck: `.small` (21 px); worked examples and
  "why it matters": `.medium` (26 px). Main points stay at body size.

## Open ideas

- Port the lecturer's "Academic Navy" design system to a reveal.js SCSS theme.
- A "playground" live slide with widgets for `how`, colormap and background.
- The flight-delay case study as a second set of live cells, at the placeholder in
  `_framework.qmd`.
- Rename the live slide "Undersampling: lift the floor". By datashader's pitfalls page,
  lifting the floor fixes undersaturation (see `rework-log.md`, step 8).
- "Re-aggregating on every zoom" lists the races twice in its key (HoloViews' own
  categorical legend with the one-letter codes, plus the notebook's invisible points);
  dropping `color_points` from the overlay would fix it but deviate from the notebook.

Visual design: see @STYLE.md
