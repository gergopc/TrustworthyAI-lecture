# Rework log

Review trail for the rework described in `REWORK.md`, one entry per step.
The project is not a git repository, so there are no per-step commits; this log is the
record. "Render check" = `quarto render lecture.qmd` in the `census` env (WSL, Quarto
1.9.38), which must finish without warnings.

## Step 1: skeleton and title slide

- **Changed:** `lecture.qmd` now holds only the title slide and the includes, in the
  brief's order. The two placeholder slides ("Your own slides go here", "Back to your own
  material") are gone. New include files, each holding only its section slide for now:
  `_problem.qmd` "Too many observations", `_framework.qmd` "Bin, summarize, smooth, plot",
  `_bridge.qmd` "Datashader: the framework at pixel resolution", `_interactivity.qmd`
  "Interactivity at scale: where does aggregation run?", `_landscape.qmd` "Tools, 2026",
  `_close.qmd` "Pitfalls and take‑aways".
- **Title slide:** title changed to "Big Data visualization" (lower-case v, as in the
  brief and the old deck); the rest was already per STYLE.md.
- **Judgement calls:** the brief names no section title for `_close.qmd`, so I used
  "Pitfalls and take‑aways" (with a non-breaking hyphen so the word doesn't split across
  lines).
- **Render check:** clean. All section titles fit the dark panel (the longest takes four
  lines).

## Step 2: `_problem.qmd`

- **Changed:** `_problem.qmd` gained 8 slides: scope; the pixel budget; "Which charts
  scale…" (the 8-image grid); "Aggregates scale, one-mark-per-row charts don't" (the same
  images sorted); "What works at scale"; two sampling slides; a 3D aside.
  `ftsrg.scss` gained a reusable `.fig-grid` class: equal image heights for figures of
  mixed aspect ratio, never cropped; the height is set per use with `--fig-h`.
- **Sorting of the gallery** (checked image by image):
  - *Scales:* bar chart of course headcounts (4), histogram (2), boxplots (7), 2D-binned
    heatmap (5), treemap of population totals (3), mosaic plot (1).
  - *Doesn't scale:* scatter plot (6), parallel coordinates (8).
- **Judgement calls:**
  - **Treemap:** filed under "scales". It has one tile per country (totals), so its mark
    count is bounded by categories, not rows; the notes say so.
  - **Boxplot caveat:** its outlier dots do grow with n. The notes point to letter-value
    plots (Hofmann, Wickham & Kafadar, JCGS 26(3), 2017; verified).
  - **Old slide 5 split into three slides** (overview; curse of dimensionality with the
    figure; other traps) so each holds one idea at full text size. All its sub-bullets
    are kept.
  - **"… (Stratified sampling) …"** became "Stratified sampling can help, if you know
    what to stratify on". The return-visitor-ratio problem is explained in the notes
    (sampling visits rather than visitors biases per-visitor ratios). This is my
    paraphrase; please check it matches what you meant.
  - **3D aside:** titled "3D EDA: an aside" (one line), with the two images captioned
    "Sometimes it works…" / "…sometimes it doesn't.". The video link sits in the source
    line, and the slide id is `three-d-eda`, since Pandoc would have made it "d-eda-…".
  - **Hungarian figure labels** are translated in the notes. The images themselves still
    carry Hungarian labels.
- **Verified afterwards:** the video is NASA Goddard's "Following Carbon Dioxide
  Through the Atmosphere" (public on YouTube; NASA SVS page 12445). The link text now
  uses that title.
- **Render check:** clean.

## Step 3: `_framework.qmd`

- **Changed:** 8 slides: the four steps (with `s17-bin-summarize-icons.png` and the
  paper as source line); binning as a perfect hash with the bin-index formula (LaTeX);
  Z-order; the distributive / algebraic / holistic table; sketches for holistic
  summaries; the robust-vs-efficient tension; kernel smoothing; peel and transform.
  The flights placeholder comment sits at the end of the file.
- **New diagram:** `assets/diagrams/bin-ordering.svg`, row-major vs Z-order on a 4×4
  grid in the theme palette.
- **Plumbing:**
  - Diagrams are pulled in with `{{< include >}}` inside a raw-HTML block, so their
    text uses the bundled Open Sans (an SVG loaded as `<img>` can't).
  - `ftsrg.scss` gained `svg.diagram` sizing (`--diagram-h`) and a 30 px table font.
  - `_quarto.yml` now uses `html-math-method: mathml`. Formulas are rendered at build
    time, so the deck no longer loads MathJax from a CDN, in line with the offline
    fonts.
- **Verified (Wickham 2013 read in full, plus primary sources):**
  - Title and URL (tech report, had.co.nz). The source line uses the https URL of the
    same PDF.
  - Four steps, fixed-width bins, the "perfect hash" wording, the peeling and modulus
    transform (§5), the Fig. 5 smoothing panels (artificial data, so not a flight
    figure).
  - LOOCV bandwidth selection.
  - HyperLogLog (Flajolet et al., AofA 2007), remedian (Rousseeuw & Bassett, JASA 1990),
    t-digest (Dunning & Ertl, arXiv 1902.04023), KLL (Karnin, Lang & Liberty, FOCS 2016),
    breakdown points (Rousseeuw & Hubert 2011), Gray et al.'s aggregate classes (1997).
- **Kernel formula:** as the brief asked, I checked it against the paper. The paper
  prints exactly the old slide's K(x) = (1 − |x|³)² I(|x|<1) and calls it
  "triweight", so the slide shows that and labels it "the paper's 'triweight'".
  - The notes explain that this is neither textbook kernel. Triweight is (1 − x²)³ and
    tricube (1 − |x|³)³.
  - The paper's own §4.3 says "tricube", and the bigvis code computes (1 − |x|³)³.
- **Judgement calls:**
  - **Formula variables:** the formula uses d for the number of binned dimensions, where
    the old slide used m, which clashes with the m summary dimensions.
  - **Count distinct:** Gray et al. don't list it as holistic; the notes attribute that
    to Wickham.
  - **Remedian and sketches:** remedian is presented as the historical approximation,
    t-digest and KLL as today's.
  - **Transforms slide:** "distribution transforms" is one slide, "Peel and transform:
    taming the dynamic range", covering peeling plus log / modulus / rank transforms.
    It links forward to `eq_hist` in the census part.
  - **Placeholder:** the flights comment sits at the end of the section, after all four
    steps, since the case study would walk through all of them.
- **Render check:** clean.

## Step 4: `_bridge.qmd`

- **Changed:** 3 slides:
  - the datashader pipeline (`s11-datashader-pipeline.png`, source: datashader.org
    Pipeline page);
  - "The same pipeline, read through the framework", a table from Bin / Summarize /
    Smooth, peel / Transform + colour / Plot to Canvas / reductions / xarray operations /
    `shade(how=…)` / Bokeh-HoloViews embedding, plus the `spread`/`dynspread` caveat;
  - the redrawn functional architectural view.
- **New diagram:** `assets/diagrams/functional-architecture.svg`.
  - Data → Scene → Aggregate(s) → Image → Plot, with the five operations; the orange
    dashed Big Data | Small Data split at the aggregate.
  - Zone labels in crimson and blue; the two notes ("SQL and/or DataFrame API",
    "Interactivity: quasi-real-time Big Data processing") in plum.
  - Fits the content area with room to spare.
- **Verified** on datashader.org (Pipeline page, API reference):
  - the stage names and what each does;
  - `Canvas` is "an abstract canvas representing the space in which to bin";
  - the listed reductions (`count`, `mean`, `by`);
  - the `shade(how=…)` values `eq_hist` (default), `cbrt`, `log`, `linear`;
  - `spread` "spread[s] pixels in an image", and `dynspread` does it depending on image
    density.
- **Judgement calls:**
  - **Smoothing in datashader:** it has no smoothing stage, so the table says so,
    instead of forcing a match: the aggregate is an xarray array, open to any operation.
    `shade` counts as "transform + colour".
  - **Where the split sits:** as on the old slide, between the aggregate and the
    transformed aggregate, so transformation belongs to the Small Data side.
  - **"(we have some tricks)":** now a forward pointer in the notes to the
    interactivity section.
- **Render check:** clean.

## Step 5: `_census-live.qmd`, one insertion

- **Changed:** a static "Histogram equalization" slide right after the `eqhist` live
  cell.
  - Left: "Goal: use every colour for about the same number of pixels" and
    `s15-histeq-schematic.png`.
  - Right: `s15-histeq-wikipedia.png`. Source line: the Wikipedia article (verified to
    exist).
  - No live-cell ids, cell code, `live.py` or `common.py` changed.
- **Judgement call:** the schematic is only 300×135 px, so it is shown at 1.5×
  (450 px), the most it takes before looking soft.
- **Render check:** clean.

## Step 6: `_interactivity.qmd`

- **Changed:** 4 slides:
  - "Re-aggregate on demand, on the server" (what the census demo does);
  - "Precompute: tiles and data cubes" (Racial Dot Map, Nanocubes, imMens);
  - "Push aggregation into a query engine" (Mosaic, VegaFusion);
  - "Three architectures compared": latency per interaction, data freshness, query
    flexibility, cost/infrastructure.
- **Verified** (full citations and URLs in each slide's notes):
  - **Racial Dot Map:** Dustin Cable, Weldon Cooper Center, UVA, 2013; 308,745,538
    dots.
    - The HoloViz census notebook mentions it as "the Cooper Center" with prerendered
      tiles "limited to the specific plotting choices they made".
    - The map is **offline**: the Center's own statement, archived Dec 2022. The slide
      says "now offline".
  - **Nanocubes:** Lins, Klosowski, Scheidegger, IEEE TVCG 19(12), 2013. The code is
    dormant.
  - **imMens:** Liu, Jiang, Heer, CGF 32(3), 2013 (EuroVis). An unmaintained prototype.
  - **Mosaic:** Heer & Moritz, IEEE TVCG 30(1), 2024 (VIS 2023). DuckDB-backed,
    pre-aggregated tables at pixel resolution; active in 2026.
  - **VegaFusion:** Kruchten, Mease, Moritz, IEEE VIS 2022. Transforms run on Apache
    DataFusion; Altair integration via `alt.data_transformers.enable("vegafusion")`;
    maintained under the Vega organisation, releases infrequent.
- **Judgement calls:**
  - **Section wording:** the brief says "database engine". I titled the third
    architecture "query engine", because VegaFusion runs on DataFusion, a query engine
    but not a database.
  - **Year shown for Mosaic:** the slide gives 2023, the conference year (VIS 2023);
    the journal version is TVCG 2024.
  - **Comparison table:** qualitative, my own synthesis rather than benchmarks; the
    notes say so.
- **Render check:** clean.

## Step 7: `_landscape.qmd`

- **Changed:** 2 slides.
  - **"Where the computation happens":** a new SVG map,
    `assets/diagrams/tool-landscape.svg`, with 10 tools in four columns:
    - Browser: Plotly, Altair/Vega-Lite, deck.gl + lonboard.
    - Python server/kernel: HoloViz, Dask.
    - Query engine: DuckDB, Polars, Mosaic, VegaFusion.
    - GPU: RAPIDS cuDF.
  - **"HoloViz: a cooperating collection":** `s10-holoviz-tools.png` at 1.5× with the
    four `.bubble` callouts, placed on the logos measured in the image: hvPlot,
    Datashader, HoloViews, Lumen.
  - This replaces old slides 9 and 13 and the "also check out" list (RAPIDS, deck.gl,
    Polars are all on the map). The glyph-support table is only a link in the notes:
    `datashader.org/user_guide/Performance.html#data-objects`.
- **Verified (Sep 2026)**; versions are in the notes:
  - every tool on the map has a 2025–2026 release;
  - the HoloViz site lists exactly the eight libraries in the image, so it is still
    current;
  - Datashader runs on CPU, Dask or GPU;
  - Polars' GPU engine is still open beta, on cuDF.
- **Left off, with reasons in the notes:**
  - **cuxfilter:** sunset by RAPIDS (notice RSN 60) and archived in July 2026.
  - **plotly-resampler:** maintenance mode; new work goes into its successor FlexViz.
- **Theme and diagram fixes:**
  - **Speech-bubble tails:** `.bubble` gained optional tails (`.tail-down` /
    `.tail-up`, aimed with `--tail-x`), as on the old slide.
  - **Diagram styles:** the inline-SVG `<style>` rules turned out to be page-global
    (the Z-order diagram's `.n` restyled the map). All three diagrams now carry an id
    and scope their CSS to it; the arrow marker is renamed `fa-arrow`.
  - **Quarto quirk:** Quarto appends `.absolute` positions to an existing `style`
    attribute without a separator, so `style="--tail-x: …px;"` needs the trailing
    semicolon.
- **Judgement calls:**
  - **Which ten tools:** HoloViz counts as one entry (its four libraries are named on
    the chip), and deck.gl and lonboard share one chip.
  - **Slide title:** "A reasonable and cooperating collection: HoloViz" became
    "HoloViz: a cooperating collection", to fit one line.
  - **Callout text:** without the old "!" after "easy interactive datashader", as the
    brief quotes it.
- **Render check:** clean.

## Step 8: `_close.qmd`

- **Changed:** 3 slides:
  - "Pitfalls, part 1: too many marks": overplotting, oversaturation, undersampling;
  - "Pitfalls, part 2: too few colours": undersaturation, underutilized range,
    nonuniform colormapping, plus **"Always look at both the linear and the equalized
    view"**;
  - "Take‑aways": four lines, one per storyline stage.
  - Each pitfall row says where the students saw it (the problem section, the sampling
    slides, or the census live slides).
- **Verified:** datashader's "Plotting Pitfalls" page
  (`datashader.org/user_guide/Plotting_Pitfalls.html`, v0.19.1) and its six sections.
  The page names the fifth one "Underutilized range"; only its summary figure says
  "underutilized dynamic range". The slide uses the page's name.
- **Judgement calls:**
  - **Split:** six rows in one table would be cramped, so there are two slides of
    three, grouped as marks vs colours.
  - **Terminology clash (for you to decide):** the census notebook, and the live slide
    "Undersampling: lift the floor" that follows it, calls raising the colormap floor
    "preventing undersampling". By datashader's pitfalls page, that fixes
    *undersaturation*; undersampling there means a random subsample losing the
    distribution's shape. I left the live slide's title alone, since step 5 allowed
    only one insertion in that file. The checklist cross-references it under
    undersaturation, and the notes explain the clash. Consider renaming that slide.
- **Render check:** clean.

## Step 9: student setup handout

- **Changed:** new `student-setup.md` (not in the deck), in nine steps:
  1. WSL2 (`wsl --install`);
  2. keeping the project in the Linux home, off `/mnt/c`;
  3. Miniforge;
  4. the HoloViz "Download project" bundle;
  5. our environment (as a listing);
  6. the data;
  7. the `categories=[]` read fix, and the optional map-label fix;
  8. memory;
  9. running JupyterLab.

  The Take‑aways slide links it in its source line.
- **Verified:**
  - **WSL:** the `wsl --install` requirements and Microsoft's "store your files in the
    WSL file system" advice (learn.microsoft.com); WSL2's defaults of 50 % of Windows
    RAM and 25 % swap, `.wslconfig` location, `wsl --shutdown` (wsl-config page).
  - **Miniforge:** the installer commands (conda-forge/miniforge README).
  - **The bundle:** `census.zip` from examples.holoviz.org; I listed its contents. It
    has no data, and its anaconda-project recipe pins Python 3.10, Dask 2023.5 and
    datashader 0.15.
  - **The data:** zip ≈ 1.44 GB and ≈ 2.2 GB unpacked, measured. It unpacks to
    `census2010.parq/`; I checked this on the zip's own index.
  - **The notebook:** its read cell (`engine='fastparquet'`), its label layer
    (`xyz.CartoDB.PositronOnlyLabels()`), and its "less than 16GB of RAM → omit
    `.persist()`" advice.
  - **Dask:** fastparquet engine deprecated in 2024.1.0 and later removed (changelog and
    current source); what `categories=` means (read_parquet docs).
- **Judgement calls:**
  - **Environment listing:** the handout inlines our `environment.yml` with Quarto
    dropped and JupyterLab added; our env has no Jupyter, and students won't have the
    lecture repo. Keep the two in sync if you change one.
  - **Unzipping:** with `python -m zipfile -e`, because Ubuntu on WSL doesn't
    necessarily ship `unzip`.
  - **Disk budget:** "roughly 8 GB", from the measured size of our `census` env
    (2.6 GB) plus the data. The package-cache share is an estimate.
  - **Map labels:** the fix is conditional ("if the city names don't appear"). CLAUDE.md
    records that CartoDB's label tiles now need an API key, but I couldn't confirm that
    on the web, so the handout doesn't claim it.
  - **Handout link:** the Take‑aways slide links `student-setup.md` relatively. That
    works from the project folder; for students, publish the file (e.g. on the course
    page) and point the link there.
- **Render check:** clean.

## Step 10: wrap-up

- **Changed:**
  - **`CLAUDE.md`:** the deck order and include files, the diagrams folder, the
    handout / brief / log files, and MathML under Architecture. New decisions 8 (the
    storyline, flights out of scope) and 9 (the kernel formula). A verification note
    for the rework. New conventions: one idea per slide, web-verified claims with
    `TODO(verify)`, scoped SVG diagrams. Open ideas: the flights case study and the
    slide rename replace "migrate the rest of the PowerPoint".
  - **`STYLE.md`:** the new reusable elements (bubble tails, `.fig-grid`, diagrams,
    table size).
- **Final check:** clean render in the `census` env, 59 slides. A layout check found
  no content below the body area on any slide.

## Summary for review

**Open `TODO(verify)` items: none.** Every claim that reached a slide was checked on
the web, and anything unverifiable was left off the slides. Three things are not fully
verified:

- **CartoDB label tiles:** CLAUDE.md (decision 4, from an earlier session) says they
  now need an API key; I couldn't confirm that. The handout's label fix is therefore
  phrased "if the city names don't appear".
- **Racial Dot Map takedown:** the exact date is unclear (end of 2021 vs 2022). The
  slide only says "now offline".
- **Not tested with the real data or the projector:** the deck was never run against
  the real 2.2 GB dataset. The live cells were tested earlier with synthetic data; the
  new sections contain no live cells.

**Judgement calls worth a look** (details under each step):

1. **Sampling slides (step 2):** my paraphrases of "… (stratified sampling) …" and of
   the return-visitor-ratio problem.
2. **Treemap as "scales" (step 2):** one tile per country; the boxplot caveat goes to
   the notes, with letter-value plots.
3. **Kernel formula (step 3):** shown exactly as the paper prints it and labelled "the
   paper's 'triweight'"; the notes explain that it is really tricube.
4. **Notation (step 3):** d instead of m for the number of binned dimensions in the
   bin-index formula.
5. **"Query engine" (step 6):** used instead of "database engine" for the third
   interactivity architecture, because VegaFusion runs on DataFusion.
6. **Tool map (step 7):** the choice of ten tools. cuxfilter (sunset) and
   plotly-resampler (maintenance mode) are left off, with reasons in the notes.
7. **Undersampling vs undersaturation (step 8):** the live slide "Undersampling: lift
   the floor" (named after the notebook) is filed under undersaturation in the
   checklist. **Consider renaming that live slide.**
8. **Handout environment (step 9):** it duplicates `environment.yml`, minus Quarto,
   plus JupyterLab. Keep them in sync.
9. **Handout link (step 9):** to be pointed at wherever students will get the file.

**Not in the brief, added in passing:**

- MathML formulas instead of CDN MathJax (offline, like the fonts).
- New reusable theme elements, documented in STYLE.md.
- Three new SVG diagrams in `assets/diagrams/`.

The flights case study is only the placeholder comment in `_framework.qmd`, as the brief
asked.

# Round 2: the lecturer's dictated comments (2026-09-24, afternoon)

Slide numbers below are the lecturer's, counted on the deck as it stood before this
round (title slide = 1). Render check as before; in addition, every changed slide was
screenshotted in headless Chromium (Playwright), live slides with `live.py` running on
the real 306,675,004-row dataset and the cell executed. Commits are per step.

## Step R1: live slides (25 onwards): code wrap, colour legends, "try this" hints, notes

- **Code wrap:** `live.py`'s `Keys` component now switches Ace's soft wrap on
  (Panel's `CodeEditor` has no option for it): long lines wrap at the editor edge
  instead of needing the horizontal scrollbar. Nothing else in `live.py` changed.
- **Legends:** every slide that shows a datashader image (27–30, 32–43) has a small
  legend at the bottom right of the output column: the colour ramp with its exact stops
  (computed from `Greys9` with the slide's floor, colorcet `fire`, matplotlib `hot`,
  viridis), the scale (linear / log / histogram-equalized), and "black: nobody" where
  a floor makes that distinction. Categorical slides show the five `color_key`
  swatches plus "hue = mix, brightness = count". The three Bokeh slides (45–47) keep
  their own legends/colorbar. The six-city grid fills the width, so its legend sits
  beside the slide title.
- **Hints:** a grey rounded box with a light-bulb icon (`assets/icons/lightbulb.svg`) on
  every live slide, 25–47, suggesting one edit to try. Each suggested edit was run on
  the real data first (all 21 work; timings in the notes where they make the point,
  e.g. the six-city grid: 1.07 s at full resolution vs 0.83 s with 16× fewer bins).
- **Theme:** `ftsrg.scss` gained `.cell-aside` (stacks hint + legend at the bottom of
  the output column, absolutely positioned so the iframe keeps the full content area),
  `.legend` (`.ramp`, `.ends`, `.swatch`, `.top`) and `.try` (`.inline` for the
  wide-layout cells, placed right of the Run button).
- **Speaker notes:** rewritten for all live slides and the two section slides, as short
  bullets that also read well for students.
- **Judgement calls:**
  - Hints avoid editing shared names (`create_image`, `color_key`), since the cells
    share one namespace; the one exception, `size=10` on the colour-key slide, only
    changes that slide's plot.
  - The dev note about the city-tile size moved from the notes into an HTML comment.
  - **Found in passing, not changed:** on "Re-aggregating on every zoom" the key lists
    the races twice (one-letter codes from HoloViews' own categorical legend, full names
    from the notebook's invisible-points trick). The notes mention it; dropping
    `color_points` from the overlay would remove the duplicate but deviate from the
    notebook, so that is your call.
- **Render check:** clean; layout check over the live slides: nothing below the body.

## Step R2: the problem section (old slides 3–10)

- **New slide before old 3, "The data frame: rows and columns":** rows = observations,
  columns = variables; wide vs narrow (long) shown on one small server-metrics table in
  both shapes, with melt / pivot between them (new diagram
  `assets/diagrams/data-frame-shapes.svg`). Source line: Wickham, Tidy Data, JSS 59(10),
  2014 (verified); the notes give the tidy-data rules and the melt/pivot names in
  pandas, tidyr and SQL.
- **Old 3, "Too many rows…":** now carries a log-scale chart of eleven real data sets
  against the 4K pixel budget (`assets/diagrams/dataset-sizes.svg`, generated by
  `figures.py dataset_sizes`), from 11 M HDFS log lines to > 40 T ADS-B messages, with
  today's census highlighted. Every number was checked on its primary source (dataset
  pages, papers, APIs; list with dates in the notes). Rubin/LSST is only in the notes
  (planned, not yet data); LAION-5B, GH Archive and the cluster traces were left off
  (withdrawn / no official counts).
- **Old 4, "The pixel budget":** added a three-panel overplotting figure with a simple
  story: a simulated drive fleet (2 % failed), 500 drives readable, then 200,000 drives
  drawn failed-first (failures vanish) and failed-last (failures seem everywhere), and a
  one-line caption. The TV picture is smaller; the long explanation is in the notes.
- **Old 8, curse of dimensionality:** the old figure (unlabelled "required sample size"
  curve) is replaced by three panels, one per bullet, each with a short scientific
  explanation underneath: sub-cube edge r^(1/p) (ESL §2.5), k^d cells vs 1 M rows and
  the standard-error argument (+ Gelman, Hill & Vehtari §16.4 on interactions), the
  nearest-neighbour distance (ESL eq. 2.24) and distance concentration (Beyer et al.,
  ICDT 1999). All sources verified; the power argument is textbook algebra, the ROS
  quote is its citable anchor.
- **Old 9, "Sampling: other traps":** each bullet got an explanatory snippet; a small
  table works the return-visitor problem through on a toy site (computed exactly:
  returning users 40 % → 17 %, visits per user 2.5 → 1.2, heavy users 10 % → 32 %).
  Sources: Deng, Knoblich & Lu, KDD 2018 (randomization vs analysis unit), Cochran
  ch. 5 (stratification, Neyman allocation).
- **New slide after old 9, "Just process everything":** the real census, all
  306,675,001 people in the frame vs a 0.1 % random sample (306,677 people), same
  shading: the sparse structure disappears. Quote from datashader's pitfalls page.
- **Old 10, 3D EDA:** the NASA video now plays in the slide from a local, git-ignored
  file (`assets/video/nasa-co2-following.mp4`, NASA SVS 12445, 1080p, 78 s, H.264);
  if the file is missing, the old still is the poster and the source line links the
  download page and YouTube. The "sometimes it doesn't" figure is replaced by the same
  New York population counts as 3D bars and as a 2D colour grid (census data), with a
  one-line explanation under each side. The old taxi figure stays in
  `assets/legacy/s07-3d-scatter-fail.png`.
- **Plumbing:** new `figures.py` (run in the `census` env; writes
  `assets/figures/*.png` and the dataset chart; not a build step, the outputs are
  committed). `ftsrg.scss`: `.small` (21 px explanatory text), small tables inside it,
  `video.video-embed`.
- **Speaker notes:** rewritten for every slide of the section.
- **Judgement calls:**
  - The overplotting story uses drives rather than something more everyday because it
    fits a systems-engineering audience and the Backblaze row on the previous slide;
    it is labelled as simulated.
  - The curse and sampling slides stay one slide each, with small text; "just process
    everything" became its own slide because the figure needs the space.
  - README gained the video download line.
- **Render check:** clean; layout check over all slides: nothing new below the body
  (the pre-existing column containers on the "Aggregates scale" and smoothing slides
  are reported by the checker but nothing visible overflows).

## Step R3: the framework section (old slides 12–15)

- **Two new slides after old 12, the Iris example:** "Iris example: bin" (a slice of
  the real data frame with a bin column; petal length into 12 bins of 0.5 cm,
  b = ⌊(x − 1.0)/0.5⌋, flower 51 worked through) and "Iris example: summarize, smooth,
  plot" (per-bin table: flowers, mean petal width, a ¼-½-¼ smoothed count; a stacked
  bar chart by species with the smoothed line, `assets/figures/iris-pipeline.png`).
  All numbers computed exactly (decimal arithmetic) from R's `iris`, now in
  `assets/data/iris.csv` (150 rows) so `figures.py` can regenerate the figures.
- **Old 13, "Binning is a logical operation":** a worked 2D example: flower 51,
  x₁ = 7 of 12, x₂ = 2 of 6, b = 7 + 2·12 = 31, with a 12 × 6 grid of the Iris bins
  (`assets/diagrams/bin-index-example.svg`, generated: occupied bins tinted, 20 of 72;
  bin 31 holds 7 flowers).
- **Old 14, Z-order:** "why it matters here" next to the (smaller) diagram: viewport
  windows become few key runs, and map tiles are keyed this way; the notes add the
  concrete systems (Bing Maps quadkeys, geohash / Redis GEO, Delta Lake ZORDER BY,
  Iceberg z-order, Hilbert in spatialpandas and S2) and Moon et al. (TKDE 2001) on why
  the number of runs grows with the window's perimeter. All verified (research notes
  with URLs).
- **Old 15, per-bin summaries:** three small worked diagrams under the unchanged table
  (`assets/diagrams/summary-merge.svg`), the same five numbers split into two
  partitions: sums add up; the mean needs (n, Σ) (the mean of the means, 2.92, is
  wrong); the median of the medians (2.75) is not the median (3).
- **Notes:** rewritten for the whole section, including the unchanged slides.
- **Judgement calls:**
  - Bins count from 0 in the examples (the formula's convention); the paper counts
    from 1 with 0 for missing values: said in the notes of the four-steps slide.
  - Smoothing is shown with the simplest possible kernel (¼, ½, ¼), and the notes say
    that with 150 rows it is cosmetic.
  - `ftsrg.scss` gained `.medium` (26 px) for worked examples, larger than the
    explanatory `.small`, since students must read the numbers during the lecture.
- **Render check:** clean; screenshots checked, nothing below the body.

## Step R4: the bridge section (old slides 21–23)

- **New slide between old 21 and 22, "From rows to one pixel":** a 3D-ish diagram
  (`assets/diagrams/rows-to-pixel.svg`): the table as a slab with hundreds of millions
  of rows; the scattered rows that fall into one pixel are highlighted, with ① the x, y
  columns (which pixel?) and ② the value / group columns (what to aggregate) marked;
  beams from those rows converge on one lit pixel of a tilted 12 × 8 screen; ③ shade
  sets colour, brightness, alpha. Kept deliberately simple, as asked.
- **Old 23, the functional architectural view:** the diagram is a little smaller, and
  the white space below now holds the two statements: Big Data side, clusters of
  machines, GPUs, GPU clusters, cloud services; Small Data side, anything, down to a
  smart display at a bus stop, with a photo of one showing a city map (Tyumen, by RG72,
  CC BY-SA 4.0, licence read from the Commons file metadata; cropped, attribution and
  licence link in the source line). The crop is `assets/photos/smart-bus-stop-tyumen.jpg`.
- **Notes:** rewritten for the section.
- **Judgement calls:** the photo was chosen from three freely licensed bus-stop
  screens with a map (the other two: Shenzhen, CC BY-SA 4.0, clearest map but a
  burned-in timestamp; Taoyuan, a route diagram rather than a map). LinkNYC / kiosk
  photos on Commons show ads or blank screens.
- **Render check:** clean; screenshots checked.

## Step R5: the interactivity section

- **An architecture figure for every option** (generated by `figures.py interactivity`,
  one visual language: browser in blue = Small Data, server / engine, data cylinder in
  crimson = Big Data, the orange dashed split from the functional-architecture slide,
  numbered arrows for what happens on each interaction):
  - `arch-on-demand.svg`: ① zoom/pan sends the new x, y ranges → ② the Python server
    makes a full pass over the rows → ③ an image or ~1 value per pixel comes back;
  - `arch-precompute.svg`: "once, ahead of time" (all rows → batch job at every zoom
    level → tile pyramid z0, z1, z2 … → tile / cube server) vs "every interaction"
    (the browser fetches its viewport's tiles: a lookup, no pass over the rows);
  - `arch-query-engine.svg`: ① SQL with GROUP BY over binned x, y → the engine
    (DuckDB, DataFusion; columnar, vectorised, pre-aggregated tables; on a server, in
    the kernel or in the browser) scans the tables → ② a small result, a row per bin.
- **Slides:** each diagram sits above the bullets; the bullets were condensed to fit
  (the systems and citations moved into one small line on the precompute slide, the
  full details stay in the notes). The comparison table is unchanged.
- **Notes:** rewritten, including a rule of thumb on the comparison slide (one analyst
  → on demand; many users, fixed views → precompute; data in a warehouse → push down).
- **Render check:** clean; screenshots checked.

## Step R6: remaining notes, documentation, final check

- **Speaker notes** for the slides not touched yet: the title slide (the road map), the
  tools section and the pitfalls / take-aways, rewritten from verification records
  into presenter prompts (versions and sources kept). Every one of the 64 slides now
  has notes.
- **Docs:** `CLAUDE.md` (live-slide extras, `figures.py`, the new asset folders,
  decision 10, round-2 verification and the sandbox tips, conventions for notes and
  text sizes, open ideas); `STYLE.md` (`.small`, `.medium`, `cell-aside` / `try` /
  `legend`, local video, photo attribution, generated figures).
- **Final check:** clean render (no warnings); all 64 slides screenshotted with
  `live.py` on the real data and every live cell run; the layout check flags only the
  title slide (absolutely placed logos, by design) and the two pre-existing column
  containers (nothing visible overflows).

## Round 2 summary for review

**Things to look at first:**

1. **Speaker notes** everywhere: proposals, written as short bullets that also read
   well for students. Edit freely.
2. **The overplotting story** (pixel budget): simulated drives, healthy vs failed,
   two drawing orders. Labelled as simulated.
3. **The new "sometimes it doesn't" figure** (3D aside): New York population as 3D
   bars vs 2D colours, from the census data. Your NYC-taxi figure is still in
   `assets/legacy/s07-3d-scatter-fail.png` if you prefer it.
4. **The video** plays from `assets/video/nasa-co2-following.mp4` (git-ignored; one
   `curl` line in `README`). Chromium-based browsers and Firefox play its H.264.
5. **The Iris worked example** uses bins counted from 0, like the formula; the notes
   mention that the paper counts from 1.
6. **Hints** on the live slides: each was run on the real data; two contain the
   answer in the notes (agg.sum() → all but three people; the six-city wall time
   barely drops with 16× fewer bins).

**Open items (not changed):**

- The duplicated race key on "Re-aggregating on every zoom" (HoloViews' own legend +
  the notebook's invisible points); see CLAUDE.md, open ideas.
- The "Undersampling: lift the floor" title (undersaturation by datashader's terms)
  and the handout link on the take-aways slide, both from round 1.
- The flights case study placeholder.

**Verified this round** (details and URLs in the research notes the notes cite): all
dataset sizes on the chart; ESL §2.5 and eq. 2.24; Gelman, Hill & Vehtari §16.4; Beyer
et al. 1999; Deng, Knoblich & Lu 2018; Cochran ch. 5; Tidy Data (JSS 59(10)); Bing
Maps quadkeys, Delta Lake / Iceberg z-ordering, Moon et al. 2001; the photo's licence
(Commons metadata); the NASA video (SVS 12445).

## Step R7 (2026-09-24, evening): datashader and Jupyter; the census data and ethics

- **Before the datashader pipeline slide, two new slides:**
  - "Datashader: a Python library": BSD licence, HoloViz, developed with Anaconda's
    support (datashader.org/about), `pip install datashader` / conda, 0.19.1 of
    19 May 2026 (PyPI), its dependencies (Numba, NumPy, pandas, xarray; Dask and
    cuDF / CuPy as optional backends), links; a stack diagram of today's demo
    (`assets/diagrams/datashader-stack.svg`: notebook / Panel app, HoloViews + Bokeh,
    Datashader, pandas · xarray · Numba, Dask · cuDF / CuPy, hardware; the Big | Small
    Data split drawn in).
  - "Where datashader usually lives: Jupyter": notebook, kernel, inline output, and
    that the live slides are notebook cells lifted out; next to it an animated
    JupyterLab recording (`assets/figures/jupyter-census.webp`, 286 kB) of a real run
    on the real data: imports, loading 306,675,004 rows, aggregating, the fire map
    appearing under the cell.
- **Before "The data: one row per person", two new slides:**
  - "The data: the 2010 US census": the census (Constitution Art. I §2, 1 April 2010,
    10 questions, 308,745,538 people), the privacy layers (Title 13 confidentiality,
    the 72-year rule, swapping in the 2010 tables, differential privacy in 2020, dots
    at random within blocks), what the columns mean (w, b, a = non-Hispanic White,
    Black, Asian; h = Hispanic of any race; o = everyone else), and a lineage diagram
    (`assets/diagrams/census-lineage.svg`: census → Summary File 1, table P5, per block
    → Racial Dot Map (Cable, UVA, 2013) → the HoloViz Parquet file).
  - "A note on ethics: race in the data": why the US asks (civil and voting rights;
    "a social definition of race"), how it looks from Europe (GDPR Art. 9(1) and
    Recital 51, France's 2007 Constitutional Council decision, Hungary's 2022 census:
    ethnicity voluntary, no race question), why we still use the data (a public,
    aggregated benchmark; the maps say nothing about individuals and nothing for or
    against any group), and the lesson (visualisation persuades).
- **Corrected in passing:** the first live slide's note said "o = Other (mostly Native
  American)" after the HoloViz page; the Racial Dot Map's own definition is broader
  (all other non-Hispanic answers, including multiracial).
- **Verified** (census.gov briefs C2010BR-01/-02, the race topic page, the 72-year-rule
  page, disclosure-avoidance briefs C2020BR-03/-04; Title 13 §9 and §214 at LII; the
  archived Cooper Center page; the HoloViz page; GDPR via an archived EUR-Lex copy;
  conseil-constitutionnel.fr; KSH). Three details worth knowing:
  - The HoloViz file has 306,675,004 rows; the 2010 count minus Alaska and Hawaii is
    306,675,006. No source explains the two missing rows; the notes say so.
  - Title 13 §214 itself says "$5,000 or … 5 years"; census.gov says up to $250,000
    (via the general federal fine statute). The slide says only "up to 5 years in
    prison"; the notes give census.gov's figure.
  - The 72-year rule is in Public Law 95-416 / the 1952 Census–Archives agreement that
    44 U.S.C. 2108(b) refers to, not in the statute's wording.
- **Judgement calls:**
  - Tone of the ethics slide: measured ("unusual and uncomfortable" rather than
    stronger words), factual about both sides, and explicit that the demo is
    technical. Your own words in the room can be stronger.
  - The ethics slide is text only, set a little larger (29 px) than other explanatory
    text, because it is a statement to read, not a diagram to explain.
- **Render check:** clean; all 68 slides layout-checked (only the known title-slide and
  column-container reports).

## Step R8: one slide instead of three for smooth / peel / transform

- **Removed from the deck** (lecturer's request: they didn't lead anywhere): "The core
  tension", "Smoothing: kernel methods", "Peel and transform: taming the dynamic
  range". Kept verbatim, with their notes, in `_backup-framework-smoothing.qmd`
  (not included by `lecture.qmd`; the leading underscore keeps Quarto from rendering
  it on its own).
- **New single slide, "Smooth, peel, transform":** three one-line core ideas, the
  paper's Fig. 1 as the 2D example (average delay by distance × speed for 76 million
  flights: raw, peeled to the middle 99.5 %, modulus-transformed; the figure was
  already in `assets/legacy/s27-distribution-transforms.png`, identified against the
  paper), a one-line caption paraphrasing the paper's, and the report in the source
  line. The notes carry the essentials of the three old slides (peeling, the modulus
  transform, kernel smoothing and bandwidth, the robust-vs-fast tension).
- **Verified:** Fig. 1's caption and the peeling / modulus text (§5.3.1–5.3.2) in the
  report PDF.
- **Render check:** clean; the deck has 66 slides.

## Step R9 (after the lecture): a static PDF of the deck

- **`lecture.pdf`** (66 pages, 16:9, 14 MB): printed with the new `print_pdf.py`
  from reveal's print layout. Text, formulas and diagrams stay vector; links work.
  Every live slide shows its cell after a real run on the 306,675,004-row data (code,
  output, wall time; the two Bokeh maps with their tiles and colour key).
- **How:** headless Chromium does not print the live cells' cross-origin iframes, and
  loading all 21 cell pages at once on the long print page left most of them stale
  (and running them together exhausted the RAM). So the script shows each live slide
  in turn, presses Run, waits for the wall time, screenshots the cell (2×, JPEG 90),
  then swaps the screenshots in for the iframes on the print layout and prints.
- **Print fixes** (`ftsrg.scss`): the title slide's institution block lost its last
  line in print (Chrome's page breaking ignores the centring transform); it is now
  placed without the transform in print. Video controls are hidden in print, so the
  3D slide shows the video's poster. New `{.screen-only}` / `{.print-only}` pair: the
  Jupyter animation prints as a still of its final frame
  (`assets/figures/jupyter-census-final.png`).
- **To regenerate:** with `live.py` running (e.g. `present.sh`),
  `python print_pdf.py`; Playwright is needed (see README).
