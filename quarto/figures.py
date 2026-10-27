"""Static figures for the deck (assets/figures/*.png).  Not a build step: run it once
in the `census` env after changing a figure, and commit the PNGs.

    python figures.py            # all figures
    python figures.py overplot   # only the named ones

The census figures read ./data/census2010.parq (one pass each). Fonts: Open Sans, as
in the deck (matplotlib needs the TTF installed; it falls back to DejaVu Sans).
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "assets" / "figures"

# ftsrg palette (STYLE.md)
TEXT, BLUE, CRIMSON, GREY, PLUM, ORANGE = "#2F2D2E", "#1446A0", "#960018", "#A7A8A7", "#522B47", "#FB8B24"

plt.rcParams.update({
    "font.family": ["Open Sans", "DejaVu Sans"],
    "font.size": 15, "axes.titlesize": 16, "axes.titleweight": "bold",
    "text.color": TEXT, "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT,
    "axes.edgecolor": GREY, "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.05,
})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", facecolor="white")
    plt.close(fig)
    print("wrote", OUT / f"{name}.png")


# ---------------------------------------------------------------- the problem
def overplot():
    """Simulated drive fleet: the same 200,000 dots, two drawing orders."""
    rng = np.random.default_rng(7)
    n, share = 200_000, 0.02
    nf = int(n * share)
    healthy = np.c_[rng.gamma(3.0, 0.9, n - nf), rng.normal(33, 4, n - nf)]
    failed = np.c_[rng.normal(4.8, 1.6, nf), rng.normal(39, 4.5, nf)]
    small = rng.choice(n, 500, replace=False)
    both = np.r_[healthy, failed]
    is_failed = np.r_[np.zeros(n - nf, bool), np.ones(nf, bool)]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharex=True, sharey=True)
    panels = [
        ("500 drives: readable", [(both[small][~is_failed[small]], BLUE), (both[small][is_failed[small]], CRIMSON)], 14),
        ("200,000 drives, failed drawn first", [(failed, CRIMSON), (healthy, BLUE)], 5),
        ("The same drives, failed drawn last", [(healthy, BLUE), (failed, CRIMSON)], 5),
    ]
    for ax, (title, layers, size) in zip(axes, panels):
        for pts, colour in layers:
            ax.scatter(pts[:, 0], pts[:, 1], s=size, c=colour, linewidths=0, rasterized=True)
        ax.set_title(title, loc="left")
        ax.set_xlim(0, 10); ax.set_ylim(18, 56)
        ax.set_xlabel("power-on time (years)")
    axes[0].set_ylabel("temperature (°C)")
    axes[0].scatter([], [], c=BLUE, s=40, label="healthy")
    axes[0].scatter([], [], c=CRIMSON, s=40, label="failed (2 %)")
    axes[0].legend(loc="upper right", frameon=False, handletextpad=0.2)
    fig.tight_layout(w_pad=2)
    save(fig, "overplot-drives")


def curse():
    """Three panels, one per bullet of the curse-of-dimensionality slide."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.0))
    p = np.arange(1, 21)

    ax = axes[0]   # ESL §2.5: edge of a sub-cube holding a fraction r of uniform data
    for r, c in [(0.1, BLUE), (0.01, CRIMSON)]:
        ax.plot(p, r ** (1 / p), "o-", c=c, ms=4, lw=2, label=f"{r:.0%} of the data")
    ax.axvline(10, c=GREY, lw=1, ls=":")
    ax.annotate("10D: 80 % of each axis\nfor 10 % of the data", (10, 0.1 ** 0.1), (11.2, 0.42),
                arrowprops=dict(arrowstyle="->", color=TEXT), fontsize=13)
    ax.set_ylim(0, 1.02); ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_xlabel("dimensions p"); ax.set_ylabel("edge length of the box")
    ax.set_title("A 'local' box is not local", loc="left")
    ax.legend(frameon=False, loc="lower right")

    ax = axes[1]   # cross-classification: k^d cells vs n rows
    d = np.arange(1, 13)
    ax.semilogy(d, 4.0 ** d, "o-", c=BLUE, ms=4, lw=2, label="cells, 4 levels each")
    ax.axhline(1e6, c=CRIMSON, lw=2, ls="--")
    ax.text(1, 1.6e6, "rows: 1 million", color=CRIMSON, fontsize=13)
    ax.annotate("d = 10: about\none row per cell", (10, 4.0 ** 10), (7.6, 20),
                arrowprops=dict(arrowstyle="->", color=TEXT), fontsize=13)
    ax.set_xlabel("variables d to split by"); ax.set_ylabel("number of cells")
    ax.set_title("Subgroups run out of rows", loc="left")
    ax.set_xticks([1, 4, 8, 12])

    ax = axes[2]   # ESL eq. 2.24: median distance from the centre to the nearest of N points
    for N, c in [(1_000, BLUE), (1_000_000, CRIMSON)]:
        ax.plot(p, (1 - 0.5 ** (1 / N)) ** (1 / p), "o-", c=c, ms=4, lw=2, label=f"N = {N:,}")
    ax.set_ylim(0, 1.02); ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_xlabel("dimensions p"); ax.set_ylabel("distance to nearest point")
    ax.set_title("Nearest neighbours drift away", loc="left")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(w_pad=2.5)
    save(fig, "curse-of-dimensionality")


def _census(columns=("easting", "northing")):
    import dask.dataframe as dd
    # categories=[]: the read fix from the live cells (see student-setup.md)
    return dd.read_parquet(HERE / "data" / "census2010.parq", columns=list(columns), categories=[])


def sample_vs_all():
    """All 306 M people vs a 0.1 % random sample, same shading."""
    import datashader as ds, datashader.transfer_functions as tf
    from datashader.colors import Greys9
    from datashader.utils import lnglat_to_meters as webm
    df = _census().persist()
    x_range, y_range = webm((-124.72, -66.95), (23.55, 50.06))
    cvs = ds.Canvas(700, 408, x_range=x_range, y_range=y_range)
    imgs = []
    for frac in (None, 0.001):
        d = df if frac is None else df.sample(frac=frac, random_state=1)
        agg = cvs.points(d, "easting", "northing")
        imgs.append((tf.set_background(tf.shade(agg, cmap=Greys9[1:], how="eq_hist"), "black"),
                     int(agg.sum())))
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    for ax, (img, total), title in zip(axes, imgs, ["All rows", "A 0.1 % random sample"]):
        ax.imshow(img.to_pil())
        ax.set_title(f"{title}: {total:,} people", loc="left")
        ax.set_axis_off()
    fig.tight_layout(w_pad=1.5)
    save(fig, "sample-vs-all")


def bars3d():
    """Population of New York in 3D bars vs the same counts as a 2D colour grid."""
    import datashader as ds
    from datashader.utils import lnglat_to_meters as webm
    from matplotlib.colors import LogNorm
    from colorcet import fire
    from matplotlib.colors import ListedColormap
    df = _census()
    x_range, y_range = webm((-74.30, -73.70), (40.50, 40.95))
    agg = ds.Canvas(36, 30, x_range=x_range, y_range=y_range).points(df, "easting", "northing")
    z = agg.values.astype(float)            # rows: south → north

    fig = plt.figure(figsize=(12, 5.2))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    ny, nx = z.shape
    xx, yy = np.meshgrid(np.arange(nx), np.arange(ny))
    ax.bar3d(xx.ravel(), yy.ravel(), 0, 0.9, 0.9, z.ravel(), color=ORANGE, shade=True,
             edgecolor="none")
    ax.view_init(elev=24, azim=-62)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.set_title("3D bars: tall ones hide what is behind them", loc="left", pad=0)
    ax.set_box_aspect((nx, ny, 22), zoom=1.25)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.imshow(np.where(z > 0, z, np.nan), origin="lower", cmap=ListedColormap(fire),
               norm=LogNorm(vmin=max(1, np.nanmin(z[z > 0])), vmax=z.max()))
    ax2.set_facecolor("black")
    ax2.set_xticks([]); ax2.set_yticks([])
    ax2.set_title("The same counts in 2D: nothing hidden", loc="left")
    fig.tight_layout(w_pad=0.5)
    save(fig, "bars3d-vs-2d")


def dataset_sizes():
    """Row counts of real data sets on a log axis, against the 4K pixel budget.
    Written as an inline SVG diagram (page fonts): assets/diagrams/dataset-sizes.svg.
    Sources and dates: speaker notes of the "Too many rows" slide."""
    data = [  # label, rows, value label
        ("HDFS logs (Loghub): log lines", 11.2e6, "11 M"),
        ("NYC yellow-taxi trips, 2024", 41.2e6, "41 M"),
        ("US domestic flights 2000–2011", 78e6, "78 M"),
        ("US census 2010: people (today’s case)", 306.7e6, "307 M"),
        ("Backblaze drive stats: drive-days", 530e6, "530 M"),
        ("English Wikipedia: edits", 1.37e9, "1.4 B"),
        ("Gaia DR3: stars and other sources", 1.81e9, "1.8 B"),
        ("Azure VM trace: CPU readings, 30 days", 1.94e9, "1.9 B"),
        ("OpenStreetMap: nodes", 10.9e9, "11 B"),
        ("Wikimedia page views, 2025", 175.6e9, "176 B"),
        ("OpenSky ADS-B messages, 2013–2025", 40e12, "> 40 T"),
    ]
    W, x0, x1, top, row = 1400, 560, 1330, 64, 40
    lo, hi = 6, 14
    X = lambda v: x0 + (np.log10(v) - lo) / (hi - lo) * (x1 - x0)
    H = top + row * len(data) + 64
    px4k = 3840 * 2160
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" id="dataset-sizes" class="diagram" role="img"',
         ' aria-label="Row counts of eleven real data sets on a logarithmic axis from one million to one hundred trillion; all lie to the right of the 8.3 million pixels of a 4K screen">',
         '<style>#dataset-sizes .l{font-size:22px;fill:#2F2D2E;text-anchor:end} #dataset-sizes .v{font-size:20px;fill:#2F2D2E}'
         ' #dataset-sizes .a{font-size:20px;fill:#2F2D2E;text-anchor:middle} #dataset-sizes .p{font-size:20px;fill:#960018;font-weight:700}'
         ' #dataset-sizes .hl{font-weight:700;fill:#1446A0}</style>',
         f'<rect x="{x0}" y="{top - 30}" width="{X(px4k) - x0:.1f}" height="{row * len(data) + 30}" fill="#960018" fill-opacity="0.07"/>']
    for e in range(lo, hi + 1):
        s.append(f'<line x1="{X(10**e):.1f}" y1="{top - 30}" x2="{X(10**e):.1f}" y2="{top + row * len(data)}" stroke="#A7A8A7" stroke-width="1" stroke-opacity="0.6"/>')
        s.append(f'<text x="{X(10**e):.1f}" y="{top + row * len(data) + 30}" class="a">10<tspan dy="-9" font-size="15">{e}</tspan></text>')
    s.append(f'<text x="{(x0 + x1) / 2}" y="{H - 4}" class="a">rows (log scale)</text>')
    s.append(f'<line x1="{X(px4k):.1f}" y1="{top - 30}" x2="{X(px4k):.1f}" y2="{top + row * len(data)}" stroke="#960018" stroke-width="3"/>')
    s.append(f'<text x="{X(px4k) - 8:.1f}" y="{top - 40}" class="p" text-anchor="middle">4K screen: 8.3 M pixels</text>')
    for i, (label, v, vl) in enumerate(data):
        y = top + row * i + row / 2
        hl = " hl" if "census" in label else ""
        colour = "#1446A0" if hl else "#522B47"
        s.append(f'<text x="{x0 - 16}" y="{y + 7}" class="l{hl}">{label}</text>')
        s.append(f'<line x1="{x0}" y1="{y}" x2="{X(v):.1f}" y2="{y}" stroke="{colour}" stroke-width="2" stroke-opacity="0.35"/>')
        s.append(f'<circle cx="{X(v):.1f}" cy="{y}" r="9" fill="{colour}"/>')
        s.append(f'<text x="{X(v) + 16:.1f}" y="{y + 7}" class="v{hl}">{vl}</text>')
    s.append("</svg>")
    path = HERE / "assets" / "diagrams" / "dataset-sizes.svg"
    path.write_text("\n".join(s) + "\n", encoding="utf-8")
    print("wrote", path)


# ---------------------------------------------------------------- the framework
def _iris():
    """Fisher's Iris data as shipped with R (assets/data/iris.csv), exact decimals."""
    import pandas as pd
    from decimal import Decimal as D
    df = pd.read_csv(HERE / "assets" / "data" / "iris.csv", dtype=str)
    for c in ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]:
        df[c] = df[c].map(D)
    df["x1"] = df["Petal.Length"].map(lambda v: int((v - D("1.0")) // D("0.5")))   # 12 bins
    df["x2"] = df["Petal.Width"].map(lambda v: int(v // D("0.5")))                   # 6 bins
    return df


SPECIES = {"setosa": BLUE, "versicolor": ORANGE, "virginica": PLUM}


def iris_pipeline():
    """Counts per petal-length bin, stacked by species, plus the ¼-½-¼ smooth."""
    df = _iris()
    counts = {s: np.bincount(df.loc[df.Species == s, "x1"], minlength=12) for s in SPECIES}
    total = sum(counts.values())
    padded = np.r_[0, total, 0]
    smooth = 0.25 * padded[:-2] + 0.5 * padded[1:-1] + 0.25 * padded[2:]
    left = 1.0 + 0.5 * np.arange(12)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    bottom = np.zeros(12)
    for s, c in SPECIES.items():
        ax.bar(left, counts[s], width=0.46, align="edge", bottom=bottom, color=c, label=s)
        bottom += counts[s]
    ax.plot(left + 0.23, smooth, "-o", color=CRIMSON, lw=2.5, ms=5, label="smoothed count")
    ax.set_xticks(np.arange(1, 7.5, 1.0))
    ax.set_xlabel("petal length (cm), bins of 0.5 cm"); ax.set_ylabel("flowers per bin")
    ax.legend(frameon=False, fontsize=13, loc="upper right")
    fig.tight_layout()
    save(fig, "iris-pipeline")


def bin_index_grid():
    """12 × 6 grid of 2D Iris bins numbered b = x1 + 12·x2; occupied bins tinted,
    flower 51's bin (31) highlighted. Inline SVG: assets/diagrams/bin-index-example.svg."""
    df = _iris()
    occupied = set(zip(df.x1, df.x2))
    n1, n2, w, h, X0, Y0 = 12, 6, 46, 34, 70, 14
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 290" id="bin-index-example" class="diagram" role="img"',
         ' aria-label="A 12 by 6 grid of petal-length and petal-width bins numbered row by row from 0 to 71; the 20 bins holding flowers are tinted; bin 31, at x1 = 7 and x2 = 2, is highlighted">',
         '<style>#bin-index-example .b{font-size:14px;fill:#555;text-anchor:middle} #bin-index-example .hit{font-size:17px;font-weight:700;fill:#960018}'
         ' #bin-index-example .tk{font-size:15px;fill:#2F2D2E;text-anchor:middle} #bin-index-example .ax{font-size:17px;fill:#2F2D2E;text-anchor:middle}</style>']
    for x2 in range(n2):
        for x1 in range(n1):
            x, y = X0 + x1 * w, Y0 + (n2 - 1 - x2) * h
            b = x1 + n1 * x2
            fill = ('fill="#960018" fill-opacity="0.25"' if b == 31 else
                    'fill="#1446A0" fill-opacity="0.15"' if (x1, x2) in occupied else 'fill="#fff"')
            s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {fill} stroke="#A7A8A7" stroke-width="1"/>')
            s.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" class="{"b hit" if b == 31 else "b"}">{b}</text>')
    for x1 in range(n1):
        s.append(f'<text x="{X0 + x1 * w + w / 2}" y="{Y0 + n2 * h + 20}" class="tk">{x1}</text>')
    for x2 in range(n2):
        s.append(f'<text x="{X0 - 14}" y="{Y0 + (n2 - 1 - x2) * h + h / 2 + 5}" class="tk">{x2}</text>')
    s.append(f'<text x="{X0 + n1 * w / 2}" y="{Y0 + n2 * h + 48}" class="ax">x₁: petal-length bin (n₁ = 12)</text>')
    s.append(f'<text x="18" y="{Y0 + n2 * h / 2}" class="ax" transform="rotate(-90 18 {Y0 + n2 * h / 2})">x₂: petal-width bin</text>')
    s.append("</svg>")
    path = HERE / "assets" / "diagrams" / "bin-index-example.svg"
    path.write_text("\n".join(s) + "\n", encoding="utf-8")
    print("wrote", path)


# ---------------------------------------------------------------- interactivity
# Three architecture diagrams in one visual language (inline SVG, page fonts):
# browser (Small Data, blue) · server / engine · data (Big Data, crimson).
def _arch_svg(id_, h, label, body):
    style = " ".join([
        f"#{id_} .t{{font-size:24px;font-weight:700;fill:#2F2D2E;text-anchor:middle}}",
        f"#{id_} .s{{font-size:20px;fill:#2F2D2E;text-anchor:middle}}",
        f"#{id_} .a{{font-size:20px;font-style:italic;fill:#2F2D2E;text-anchor:middle}}",
        f"#{id_} .ab{{font-size:20px;font-style:italic;fill:#960018;text-anchor:middle}}",
        f"#{id_} .a, #{id_} .ab{{paint-order:stroke;stroke:#fff;stroke-width:7px;stroke-linejoin:round}}",
        f"#{id_} .zb{{font-size:22px;font-weight:700;fill:#960018;text-anchor:middle}}",
        f"#{id_} .zs{{font-size:22px;font-weight:700;fill:#1446A0;text-anchor:middle}}",
        f"#{id_} .band{{font-size:20px;font-weight:700;fill:#522B47}}",
    ])
    marker = lambda name, colour: (f'<marker id="{id_}-{name}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" '
                                   f'markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{colour}"/></marker>')
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 {h}" id="{id_}" class="diagram" role="img"',
        f' aria-label="{label}">',
        f'<defs>{marker("k", TEXT)}{marker("r", CRIMSON)}</defs>',
        f"<style>{style}</style>", *body, "</svg>", ""])


def _browser(x, y, w=280, h=190, title="Browser", sub=""):
    cells = []
    for i in range(5):
        for j in range(3):
            op = [0.35, 0.6, 0.85, 0.5, 0.3][i] * [0.7, 1, 0.8][j]
            cells.append(f'<rect x="{x + 40 + i * 36}" y="{y + 48 + j * 30}" width="34" height="28" fill="#1446A0" fill-opacity="{op:.2f}"/>')
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#fff" stroke="#1446A0" stroke-width="2.5"/>',
            f'<path d="M{x},{y + 26} v-16 a10,10 0 0 1 10,-10 h{w - 20} a10,10 0 0 1 10,10 v16 z" fill="#1446A0" fill-opacity="0.15"/>',
            *[f'<circle cx="{x + 16 + 14 * k}" cy="{y + 13}" r="4" fill="#1446A0" fill-opacity="0.5"/>' for k in range(3)],
            *cells,
            f'<text x="{x + w / 2}" y="{y + h + 30}" class="t">{title}</text>',
            f'<text x="{x + w / 2}" y="{y + h + 56}" class="s">{sub}</text>' if sub else ""]


def _box(x, y, w, h, title, lines, fill="#960018", op=0.06):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" fill-opacity="{op}" stroke="#A7A8A7" stroke-width="2"/>',
           f'<text x="{x + w / 2}" y="{y + 36}" class="t">{title}</text>']
    out += [f'<text x="{x + w / 2}" y="{y + 72 + 28 * i}" class="s">{t}</text>' for i, t in enumerate(lines)]
    return out


def _db(x, y, w, h, title, lines):
    r = 18
    out = [f'<path d="M{x},{y + r} a{w / 2},{r} 0 0 0 {w},0 v{h - 2 * r} a{w / 2},{r} 0 0 1 {-w},0 z" fill="#960018" fill-opacity="0.08" stroke="#A7A8A7" stroke-width="2"/>',
           f'<ellipse cx="{x + w / 2}" cy="{y + r}" rx="{w / 2}" ry="{r}" fill="#F3E6E8" stroke="#A7A8A7" stroke-width="2"/>',
           f'<text x="{x + w / 2}" y="{y + 72}" class="t">{title}</text>']
    out += [f'<text x="{x + w / 2}" y="{y + 104 + 28 * i}" class="s">{t}</text>' for i, t in enumerate(lines)]
    return out


def _arrow(id_, x1, y1, x2, y2, text="", dy=-12, red=False, width=2.5, both=False):
    m = "r" if red else "k"
    c = CRIMSON if red else TEXT
    start = f' marker-start="url(#{id_}-{m})"' if both else ""
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{width}"{start} marker-end="url(#{id_}-{m})"/>']
    if text:
        out.append(f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 + dy}" class="{"ab" if red else "a"}">{text}</text>')
    return out


def _split(x, y1, y2):
    return [f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#FB8B24" stroke-width="3" stroke-dasharray="10 7"/>']


def interactivity():
    """assets/diagrams/arch-on-demand.svg, arch-precompute.svg, arch-query-engine.svg"""
    D = HERE / "assets" / "diagrams"

    i = "arch-on-demand"
    body = [f'<text x="170" y="30" class="zs">Small Data</text>', f'<text x="1010" y="30" class="zb">Big Data</text>',
            *_split(485, 10, 330),
            *_browser(30, 70, sub="a Bokeh plot"),
            *_box(665, 70, 330, 180, "Python server", ["HoloViews + datashader:", "aggregate + shade the", "visible x, y range"]),
            *_db(1130, 60, 240, 210, "all rows", ["300 M in RAM (Dask),", "or Parquet on disk"]),
            *_arrow(i, 314, 120, 659, 120, "① zoom / pan: new x, y ranges"),
            *_arrow(i, 659, 210, 314, 210, "③ an image, or ~1 value per pixel", dy=34),
            *_arrow(i, 1001, 165, 1124, 165, "② full pass", red=True, width=5, both=True)]
    (D / f"{i}.svg").write_text(_arch_svg(i, 330,
        "Browser sends the new x and y ranges to a Python server on every zoom or pan; the server runs datashader over all rows of the data and returns an image or one value per pixel",
        body), encoding="utf-8")

    i = "arch-precompute"
    pyr = []
    for k, (n, x0) in enumerate([(1, 640), (2, 730), (4, 830)]):
        cell = 72 / n
        for a in range(n):
            for b in range(n):
                pyr.append(f'<rect x="{x0 + a * cell:.1f}" y="{62 + b * cell:.1f}" width="{cell:.1f}" height="{cell:.1f}" fill="#960018" fill-opacity="{0.12 + 0.1 * ((a + b) % 3)}" stroke="#fff" stroke-width="1"/>')
        pyr.append(f'<text x="{x0 + 36}" y="160" class="s">z{k}</text>')
    pyr.append('<text x="945" y="104" class="s">…</text>')
    body = [f'<rect x="0" y="0" width="1400" height="190" fill="#522B47" fill-opacity="0.05"/>',
            f'<text x="20" y="28" class="band">once, ahead of time</text>',
            f'<text x="20" y="222" class="band">every interaction</text>',
            *_db(40, 40, 230, 140, "all rows", []),
            *_arrow(i, 276, 105, 612, 105, "batch job: aggregate every zoom level", dy=-14, red=True, width=4),
            *_box(620, 44, 350, 130, "", [], op=0.0), *pyr,
            f'<text x="795" y="36" class="s">tile pyramid / data cube</text>',
            *_arrow(i, 976, 105, 1066, 105, "store", dy=-14),
            *_box(1070, 50, 300, 250, "Tile / cube server", ["static files, a CDN,", "or an in-memory cube"], op=0.04),
            *_browser(300, 225, w=250, h=150, title="", sub=""),
            f'<text x="425" y="398" class="t" style="font-size:20px">Browser</text>',
            *_arrow(i, 556, 258, 1064, 258, "① fetch the tiles of the viewport (z / x / y)"),
            *_arrow(i, 1064, 340, 556, 340, "② stored results: a lookup, no pass over the rows", dy=34)]
    (D / f"{i}.svg").write_text(_arch_svg(i, 410,
        "Ahead of time a batch job aggregates all rows at every zoom level into a tile pyramid or data cube, stored on a tile server; on each interaction the browser fetches the tiles of its viewport, a lookup without a pass over the rows",
        body), encoding="utf-8")

    i = "arch-query-engine"
    body = [f'<text x="170" y="30" class="zs">Small Data</text>', f'<text x="1010" y="30" class="zb">Big Data</text>',
            *_split(485, 10, 330),
            *_browser(30, 70, sub="linked views (Mosaic, Altair)"),
            *_box(665, 60, 350, 190, "Query engine", ["DuckDB, DataFusion:", "columnar, vectorized,", "pre-aggregated tables"]),
            f'<text x="840" y="285" class="s">runs on a server, in the kernel, or in the browser</text>',
            *_db(1140, 60, 230, 210, "tables", ["Parquet, a database"]),
            *_arrow(i, 314, 120, 659, 120, "① SQL: GROUP BY bin(x), bin(y)"),
            *_arrow(i, 659, 210, 314, 210, "② a small result: a row per bin", dy=34),
            *_arrow(i, 1021, 165, 1134, 165, "scan", red=True, width=5, both=True)]
    (D / f"{i}.svg").write_text(_arch_svg(i, 330,
        "Each view in the browser sends SQL with a GROUP BY over binned x and y to a query engine such as DuckDB or DataFusion, which scans the tables and returns a small result with one row per bin; the engine can run on a server, in the kernel or in the browser",
        body), encoding="utf-8")
    print("wrote", D / "arch-*.svg")


FIGURES = {f.__name__: f for f in [overplot, curse, sample_vs_all, bars3d, dataset_sizes,
                                   iris_pipeline, bin_index_grid, interactivity]}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()
