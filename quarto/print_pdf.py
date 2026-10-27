"""Static PDF of the deck, with every live cell run on the real data.

    python print_pdf.py [lecture.pdf]

Needs: the deck rendered (`quarto render lecture.qmd`), live.py running on
localhost:5006 (e.g. via present.sh; it needs ~6 GB RAM, so don't start a second
copy), and Playwright with its Chromium, which is not in environment.yml:

    pip install playwright && playwright install chromium

Two passes, because headless Chromium does not print cross-origin iframes, and
cell pages loaded all at once on reveal's long print page go stale:
1. Presentation mode, one live slide at a time: press Run, wait for the wall
   time, screenshot the cell (2×, so the code stays crisp; JPEG, to keep the PDF
   small).
2. Print mode (?print-pdf): replace every live-cell iframe by its screenshot and
   print. Animations print as their print-only stills (.print-only in ftsrg.scss),
   the video as its poster.
"""
import asyncio, base64, pathlib, re, sys

from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).parent
DECK = (HERE / "lecture.html").as_uri()
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "lecture.pdf"

# A cell is done when its status shows "Wall time: <number>" or a traceback appears.
# Only visible text counts (shadow-root style sheets contain words like "error").
DONE = r"""() => {
  const texts = [document.body.innerText];
  const walk = root => root.querySelectorAll('*').forEach(n => {
    if (n.shadowRoot) { texts.push(n.shadowRoot.textContent.replace(/[.#][\w-]*error[\w-]*/g, '')); walk(n.shadowRoot); } });
  walk(document);
  const t = texts.join(' ');
  return /Wall time: [0-9]/.test(t) || /Traceback/.test(t);
}"""

SWAP = """(shots) => document.querySelectorAll('iframe.live-cell').forEach(el => {
  // print mode has already moved data-src to src
  const name = new URL(el.getAttribute('src') || el.dataset.src).searchParams.get('name');
  const r = el.getBoundingClientRect(), img = document.createElement('img');
  img.src = shots[name];
  img.style.cssText = 'display:block;margin:0;max-width:none;max-height:none;width:' + r.width + 'px;height:' + r.height + 'px';
  el.replaceWith(img);
})"""


async def capture(page):
    """Run every live cell in presentation mode; return {cell name: JPEG data URI}."""
    await page.goto(DECK)
    await page.wait_for_timeout(3000)
    slides = await page.evaluate("""() => [...document.querySelectorAll('section.slide')]
        .filter(s => s.querySelector('iframe.live-cell'))
        .map(s => [s.id, new URL(s.querySelector('iframe.live-cell').dataset.src).searchParams.get('name')])""")
    shots = {}
    for slide_id, name in slides:
        await page.evaluate("id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v); }", slide_id)
        frame = None
        for _ in range(120):
            frame = next((f for f in page.frames if f.url.endswith("name=" + name)), None)
            if frame:
                break
            await page.wait_for_timeout(500)
        await frame.get_by_role("button", name=re.compile("Run")).click(timeout=60000)
        await frame.wait_for_function(DONE, timeout=300000)
        await page.wait_for_timeout(6000 if name in ("racemap", "popmap") else 2500)   # map tiles
        iframe = page.locator(f"#{slide_id} iframe.live-cell")
        jpeg = await iframe.screenshot(type="jpeg", quality=90)   # PNG would triple the PDF's size
        shots[name] = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()
        print("ran", name, flush=True)
    return shots


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=2)
        shots = await capture(page)
        await page.goto(DECK + "?print-pdf")
        await page.wait_for_timeout(4000)
        await page.evaluate(SWAP, shots)
        await page.wait_for_timeout(2000)
        await page.pdf(path=str(OUT), prefer_css_page_size=True, print_background=True)
        print("wrote", OUT, f"({len(shots)} live cells)")
        await browser.close()


asyncio.run(main())
