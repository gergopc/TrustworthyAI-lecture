"""Live cell server for the census walkthrough.  Run in WSL:  python live.py
 
Reads the ```{#name .python .live} blocks from _census-live.qmd, runs them all
once at startup (so any slide works out of order), then serves each one at
http://localhost:5006/cell?name=<name> as an editable cell with a Run button.
All cells share one namespace, like a notebook kernel.
"""
import ast, asyncio, contextlib, io, os, re, time, traceback
from pathlib import Path
 
import holoviews as hv
import panel as pn
import datashader.transfer_functions as tf
from panel.custom import JSComponent
 
HERE = Path(__file__).parent
os.chdir(HERE)                       # cells use ./data/...
SOURCE = HERE / "_census-live.qmd"
PREAMBLE = "from common import *"
CODE_FONT = "20px"

# ftsrg look (STYLE.md), lightly: Open Sans (bundled, served below under
# /assets), Run button in the deck's blue, white page, errors in its crimson.
UI_FONT = '"Open Sans", "Segoe UI", Arial, sans-serif'
CSS = f"""
@font-face {{
  font-family: "Open Sans"; font-weight: 300 800;
  src: url("/assets/fonts/open-sans-latin-wght-normal.woff2") format("woff2");
}}
:root {{ --design-primary-color: #1446A0; --bokeh-base-font: {UI_FONT}; }}
body {{ font-family: {UI_FONT}; background: #fff; }}
"""
ERROR_COLOR = "#960018"

pn.extension("codeeditor", raw_css=[CSS])
 
# ---------------------------------------------------------------- cells
BLOCK = re.compile(r"^```\{([^}]*\.live[^}]*)\}\n(.*?)^```", re.M | re.S)
 
def read_cells():
    cells = {}
    for attrs, code in BLOCK.findall(SOURCE.read_text(encoding="utf-8")):
        name = re.search(r"#([\w-]+)", attrs).group(1)
        layout = re.search(r'layout="?(\w+)', attrs)
        cells[name] = (code.rstrip(), layout.group(1) if layout else "column")
    return cells
 
NS = {}          # the shared "kernel" namespace
 
def execute(code):
    """Run code in NS; return (value of last expression, stdout, seconds)."""
    tree = ast.parse(code)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    out, t0 = io.StringIO(), time.perf_counter()
    with contextlib.redirect_stdout(out):
        exec(compile(tree, "<cell>", "exec"), NS)
        value = eval(compile(ast.Expression(last.value), "<cell>", "eval"), NS) if last else None
    return value, out.getvalue(), time.perf_counter() - t0
 
def render(value, wide):
    if value is None:
        return None
    if isinstance(value, tf.Image):
        return pn.pane.PNG(value._repr_png_(), sizing_mode="scale_both")
    if isinstance(value, hv.core.Dimensioned):
        if wide:  # maps fill the output area; small plots (the legend) keep their size
            with contextlib.suppress(Exception):
                value = value.opts(responsive=True, clone=True)
            return pn.pane.HoloViews(value, sizing_mode="stretch_both")
        return pn.pane.HoloViews(value)
    return pn.panel(value, sizing_mode="stretch_both")
 
# ---------------------------------------------------------------- keys
class Keys(JSComponent):
    """Shift+Enter runs the cell; PageUp/PageDown (clicker) go back to the slides.
    Arrow keys stay inside the page (editor cursor); click the slide heading to
    use them for slide navigation. Also soft-wraps long code lines in the editor,
    which Panel's CodeEditor has no option for."""
    _esm = """
    // Ace keeps its editor on the container element (el.env.editor); Panel puts
    // the container inside shadow roots, so search them all.
    function wrapEditors(root) {
      for (const el of root.querySelectorAll('.ace_editor')) {
        const ed = el.env && el.env.editor;
        if (ed && !ed.session.getUseWrapMode()) ed.session.setUseWrapMode(true);
      }
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) wrapEditors(n.shadowRoot);
    }

    export function render({ model }) {
      // Install once per page, even if Panel re-renders this component
      if (!window.__liveKeys) {
        window.__liveKeys = true;
        let tries = 0;                  // the editor may render after this component
        const timer = setInterval(() => {
          wrapEditors(document);
          if (++tries > 40) clearInterval(timer);
        }, 250);
        const fwd = {PageDown: 'next', PageUp: 'prev'};   // presenter clicker
        window.addEventListener('keydown', (e) => {
          if (e.repeat) return;
          if (e.shiftKey && e.key === 'Enter') {
            e.preventDefault(); e.stopPropagation(); window.__liveRun(); return;
          }
          if (fwd[e.key]) {
            e.preventDefault(); e.stopPropagation();
            window.parent.postMessage(JSON.stringify({method: fwd[e.key]}), '*');
          }
        }, true);
      }
      window.__liveRun = () => model.send_msg('run');     // always the current model
      return document.createElement('span');
    }
    """
    def __init__(self, on_run, **params):
        super().__init__(**params)
        self._on_run = on_run
 
    def _handle_msg(self, msg):
        if msg == "run":
            pn.state.execute(self._on_run)
 
# ---------------------------------------------------------------- page
def cell_page():
    name = pn.state.session_args.get("name", [b""])[0].decode()
    cells = read_cells()               # re-read: edits to the .qmd need no restart
    if name not in cells:
        return pn.pane.Markdown(f"No live cell `{name}`. Known: {', '.join(cells)}")
    code, layout = cells[name]
 
    editor = pn.widgets.CodeEditor(
        value=code, language="python", theme="github", sizing_mode="stretch_both",
        stylesheets=[f".ace_editor {{ font-size: {CODE_FONT} !important; }}"])
    run = pn.widgets.Button(name="▶ Run  (Shift+Enter)", button_type="primary", width=220)
    status = pn.pane.Markdown("", margin=(0, 10))
    output = pn.Column(sizing_mode="stretch_both")
 
    async def run_cell(*_):
        output.loading, status.object = True, "running…"
        try:
            value, printed, dt = await asyncio.to_thread(execute, editor.value)
            parts = [pn.pane.Str(printed)] if printed else []
            shown = render(value, layout == "wide")
            output.objects = parts + ([shown] if shown is not None else [])
            status.object = f"Wall time: {dt:.2f} s"
        except Exception:
            output.objects = [pn.pane.Str(traceback.format_exc(limit=-2),
                                          styles={"color": ERROR_COLOR})]
            status.object = "error"
        finally:
            output.loading = False
 
    run.on_click(run_cell)
    controls = pn.Row(run, status, Keys(on_run=run_cell), height=45)
    if layout == "wide":
        lines = code.count("\n") + 1   # ~23 px per line at CODE_FONT, + scrollbar
        return pn.Column(pn.Column(editor, height=min(24 + 26 * lines, 320)),
                         controls, output, sizing_mode="stretch_both")
    return pn.Row(pn.Column(editor, controls, sizing_mode="stretch_both"),
                  output, sizing_mode="stretch_both")
 
# ---------------------------------------------------------------- main
if __name__ == "__main__":
    exec(PREAMBLE, NS)
    for name, (code, _) in read_cells().items():   # warm-up, in slide order
        print(f"warm-up: {name}", flush=True)
        execute(code)
    pn.serve({"cell": cell_page}, port=5006, show=False, title="Census live cells",
             static_dirs={"assets": str(HERE / "assets")})