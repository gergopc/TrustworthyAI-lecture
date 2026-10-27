# Rework brief: turning the old lecture into the new deck

Context: `CLAUDE.md` (project, live-cell architecture) and `STYLE.md` (visual design) apply
throughout. The old PowerPoint deck is not in the repo; its relevant text is quoted under
"Source material" below and its figures are in `assets/legacy/` (named by old slide number).

## The storyline

The old deck had two disconnected halves: a practical part (tools + the census demo, which
carried the lecture) and a theoretical part (Wickham's bin–summarize–smooth–plot framework,
illustrated with static R plots on flight data, placed *after* the demo). The new deck
connects them: **datashader is bin–summarize–smooth–plot with pixels as the bins.** So:
the problem → the framework, briefly → the bridge (datashader's pipeline read through the
framework) → the live census walkthrough → how interactivity at scale is architected →
the tool landscape → a pitfalls checklist.

Deck order in `lecture.qmd` (one include file per section; section slides are `#` headings):

1. title slide (explicit first slide, see STYLE.md)
2. `_problem.qmd` — "Too many observations"
3. `_framework.qmd` — "Bin, summarize, smooth, plot"
4. `_bridge.qmd` — "Datashader: the framework at pixel resolution"
5. `_census-live.qmd` — existing live walkthrough (already has its own `#` section)
6. `_interactivity.qmd` — "Interactivity at scale: where does aggregation run?"
7. `_landscape.qmd` — "Tools, 2026"
8. `_close.qmd` — pitfalls checklist, take-aways

**Out of scope for now:** the flight-delay case study (old slides 18–27 as a worked
example). It will later become a second set of live cells. In `_framework.qmd`, leave an
HTML comment `<!-- flights live case study goes here -->` where it will slot in, and don't
create slides, data scripts or cells for it.

## Rules

- One idea per slide; no shrinking text to fit: split instead. Speaker detail goes into
  `::: notes`.
- Slides in English. Descriptive names for files, slide ids and cells (no codes like A1).
- Don't change `.live` cell ids, `live.py` or `common.py` unless a step says so.
- Reuse `assets/legacy/` figures where they're still right; don't upscale small images
  beyond readability. Diagrams you redraw: SVG or Mermaid in the theme palette.
- Claims about current tools and systems: verify on the web (official docs, papers)
  before putting them on a slide. If you can't verify something, leave it out and add a
  `TODO(verify)` line in the slide's notes instead.
- Run unattended: don't stop for confirmation between steps. After each step,
  `quarto render lecture.qmd` (env `census`) must succeed without warnings before you
  move on; if it doesn't, fix it first.
- Keep a review trail for the lecturer: after each step append a short entry to
  `rework-log.md` (what changed, which files, any `TODO(verify)` items, judgement calls you
  made). If the project is a git repository, also commit after each step with a message
  naming the step.
- If something is genuinely blocked (e.g. a source can't be reached), record it in the log,
  work around it conservatively, and continue with the next step.

## Steps

### 1. Skeleton and title slide
Create the include files with their section slides (empty section bodies are fine),
wire them into `lecture.qmd` in the order above, and build the title slide per STYLE.md:
"Big Data visualization" / "Empirical Systems Engineering" / "2026. Fall" /
"Dr. Imre Kocsis, kocsis.imre@vik.bme.hu", institution text as in STYLE.md.

### 2. `_problem.qmd`
From source slides 2, 3, 4, 5, 6–7:
- Scope: the "too many observations" problem; "too many variables" is a different topic.
- Pixel budget (use `s03-pixel-count-tv.jpg`): even 4K ≈ 8.3 M pixels; hard upper limit to
  laying out data, no upper limit on data size; overplotting bites much earlier.
- "Which charts scale with the number of observations?": the 8 `s04-scaling-gallery-*`
  images in a grid, then a follow-up slide sorting them into *scales* (aggregate-based:
  histograms, 2D bins/heatmaps, boxplots, bar charts of summaries) vs *doesn't scale*
  (one mark per observation: scatter, parallel coordinates…). Check each image to sort it
  correctly.
- What works: (2D) EDA/CDA of statistical aggregates; subsetting is situational;
  sampling is hard to get right (keep all sub-bullets from source slide 5, with
  `s05-curse-of-dimensionality.png`), conclusion: much easier to "just process everything".
- 3D EDA: one aside slide (both images side by side: "sometimes it works… sometimes it
  doesn't"), with the video link.

### 3. `_framework.qmd`
From source slides 17, 20, 25, 27, *without* the flight figures:
- The four steps (`s17-bin-summarize-icons.png` may serve as illustration): fixed-width
  bins over n dimensions; per-bin summaries over m dimensions; smooth, peel, transform
  distributions; plot. Cite Wickham, "Bin-summarise-smooth: a framework for visualising
  large data" (2013; had.co.nz link from source slide 2).
- Binning is a logical operation (a perfect hash); the n-dimensional bin index formula
  (typeset in LaTeX); locality-preserving ordering (Z-order).
- Per-bin computation taxonomy: distributive (count, sum), algebraic (mean, sd, higher
  moments) are easy to distribute; holistic ones need either full cost or approximation:
  count-distinct → HyperLogLog, median/quantiles → sketches (remedian historically;
  today t-digest / KLL; verify one-line descriptions). The core tension: robust
  (high breakdown point) statistics are slow, efficient ones are sensitive.
- Smoothing: kernel methods, Gaussian usual, triweight fast (formula), bandwidth h;
  the formula on the old slide doesn't match the textbook triweight (1 − x²)³: check it
  against Wickham's paper and use whatever the paper says, noting it in the notes;
  automatic bandwidth selection exists. Distribution transforms: one conceptual slide
  (why: dynamic range; link forward to histogram equalization in the census part).
- Placeholder comment for the flights case study (see above).

### 4. `_bridge.qmd`
From source slides 11, 12:
- The datashader pipeline (`s11-datashader-pipeline.png`), then the same pipeline mapped
  onto the framework: `Canvas` = the bins; the reduction (`count`, `by(...)`, `mean`…) =
  per-bin summaries; `shade(how=...)` / `eq_hist` = distribution transform + colour
  mapping; embedding in Bokeh/HoloViews = plot. Be precise: `spread`/`dynspread` enlarge
  points for display, they are not statistical smoothing.
- Redraw the functional architectural view (old version overflowed): pipeline stages
  Data → Scene → Aggregate(s) → Image → Plot, with the split "Big Data storage / Big Data
  processing | Small Data visualization" at the aggregate, and the notes "SQL and/or
  DataFrame API", "interactivity: quasi-real-time Big Data processing". Clean SVG,
  theme colours, nothing overflowing.

### 5. `_census-live.qmd`: one insertion
Right after the `eqhist` slide, add a static slide "Histogram equalization" from source
slide 15 (`s15-histeq-schematic.png`, `s15-histeq-wikipedia.png`, Wikipedia link):
goal = use every colour for about the same number of pixels. Plain markdown slide, not
a live cell.

### 6. `_interactivity.qmd` (new content)
Three architectures for interactive views over big data, one slide each, then one
comparison slide (latency per interaction, data freshness, flexibility of queries,
cost/infrastructure):
- **Server-side re-aggregation on demand**: what the census demo does (Python process
  re-runs datashader per zoom; only the image travels).
- **Precomputed tiles / data cubes**: e.g. the Cooper Center's prerendered census tiles
  (mentioned in the census notebook); research systems such as Nanocubes and imMens.
- **Aggregation pushed into a database engine**: e.g. Mosaic (DuckDB-backed linked views),
  VegaFusion (server-side evaluation of Vega transforms, usable from Altair).
Verify each system's description and citation on the web; keep it to one line each.

### 7. `_landscape.qmd`
Replaces source slides 9 and 13 and the "also check out" list from slide 2:
- One compact map, organized by where computation happens (browser / Python server /
  database engine / GPU), at most ~10 tools, each verified as current. Candidates to
  check: HoloViz (hvPlot, HoloViews, Datashader, Panel), Plotly (+ plotly-resampler),
  Altair/Vega-Lite, deck.gl / lonboard, Mosaic, VegaFusion, RAPIDS (cuDF, cuxfilter),
  Polars, DuckDB, Dask.
- Keep the HoloViz slide from source slide 10: `s10-holoviz-tools.png` with `.bubble`
  callouts ("Quick interactive plots", "Rasterization for Big Data", "Annotate data for
  visualization (\"easy interactive datashader\")", "Data-driven dashboards"); verify the
  tool set is still current.
- Glyph-support table: no slide; link datashader's docs from the landscape notes.

### 8. `_close.qmd`
- Pitfalls checklist, cross-referenced to what the students saw live: overplotting,
  oversaturation, undersampling, undersaturation, underutilized dynamic range,
  non-uniform colormaps; "always look at both the linear and the equalized view".
  Base the list on datashader's own plotting-pitfalls material (verify the page).
- Take-aways (3–4 lines) mirroring the storyline.

### 9. Student setup handout
`student-setup.md` (not in the deck): how to run the census example themselves: WSL2,
Miniforge/conda, the HoloViz "Download project" bundle, our `environment.yml`, the
`categories=[]` read fix and why, RAM expectations, keeping data off `/mnt/c`. Link it
from the last slide.

### 10. Wrap-up
Update `CLAUDE.md` (architecture section: include files and deck order; decisions:
the storyline above), and finish `rework-log.md` with a summary of all open
`TODO(verify)` items and judgement calls.

## Source material (old deck, lecturer's own text)

**Slide 2, Overview.** A focus on the "too many observations" problem; "too many
variables" is a different topic. Core techniques based on
http://vita.had.co.nz/papers/bigvis.pdf (R snippets with bigvis, but ~trivial to
transpose to Pandas/Dask/Spark). A ~contemporary tool: datashader. You should also check
out (if you have/get the HW): Nvidia RAPIDS, deck.gl, pola.rs.

**Slide 3, Limited real estate.** Even 4k is only ~8 million pixels. Hard upper limit to
"lay out data"; no upper limit on data size. Overplotting: problems even "earlier".

**Slide 5, What works.** (2D) EDA/CDA of (n,m) dim statistical aggregates. Subsetting –
situational (may remain a Big Data problem). Sampling is *hard* to get right: curse of
dimensionality: consistent coverage of sample space as dimensions increase? – to achieve a
fixed sampling density (points per unit volume); to maintain statistical power in
hypothesis testing; to keep a consistent distance between nearest neighbor points.
Causal distortions: the return visitor ratio problem. … (Stratified sampling) … Much
easier to "just process everything".

**Slides 6–7.** 3D EDA? Sometimes it works… (NASA CO2 visualization,
https://www.youtube.com/watch?v=syU1rRCp7E8). Sometimes it doesn't.

**Slide 10, HoloViz.** A reasonable and cooperating collection: HoloViz. Callouts: Quick
interactive plots; Rasterization for Big Data; Annotate data for visualization ("easy
interactive datashader"!); Data-driven dashboards.

**Slide 11.** The datashader pipeline (https://datashader.org/).

**Slide 12, A functional architectural view.** Pipeline diagram with: Big Data storage |
Big Data processing | Small Data visualization; SQL and/or Data Frame API; Interactivity:
quasi-real-time Big Data processing (we have some tricks).

**Slide 15, Histogram equalization.** Goal: use each color as "equally" as possible (use
for an equal amount of pixels). https://en.wikipedia.org/wiki/Histogram_equalization

**Slide 17, Bin-summarize-smooth-plot.** Over n dimensions: fixed width bins. Over m
dimensions: per-bin summaries. Smooth, peel, distribution transform. Plotting.

**Slide 20, Bin-summarize.** This is just a histogram! "Binning" can be a logical
operation – "just a perfect hash". For n dimensions: [bin index formula]
x₁ + x₂·n₁ + x₃·n₁·n₂ + ⋯ + x_m·∏_{i=1}^{m−1} nᵢ = x₁ + n₁·(x₂ + n₂·(x₃ + ⋯ x_m)).
(Locality-preserving ordering: Z-order/Lebesgue curve.) Per-bin distributed computation
is easy for distributive summaries (count, sum) and algebraic summaries (mean, sd,
higher order moments). Holistic? Either bite the bullet (in complexity), or approximate:
count distinct → hyperloglog algorithm; median → remedian; … THE problem: robust (high
breakdown point) stats slow; efficient ones sensitive.

**Slide 25, Smoothing.** Kernel method: neighbors with weights. Usual: Gaussian. A fast
one: triweight, K(x) = (1 − |x|³)² I_{|x|<1}, kᵢ = K((x_j − xᵢ)/h). h "bandwidth":
neighborhood. Methods for automatic bandwidth selection.
