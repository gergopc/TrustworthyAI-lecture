-- Replace ```{#name .python .live} blocks with an iframe to the live.py cell server.
-- Other formats (e.g. an HTML/PDF handout) keep them as ordinary code listings.
local SERVER = "http://localhost:5006"

function CodeBlock(el)
  if el.classes:includes("live") and quarto.doc.is_format("revealjs") then
    -- Default: reveal's r-stretch fills the slide's content area below the title
    -- (ftsrg.scss keeps the width); height="…" on the block sets a fixed height.
    local height = el.attributes["height"]
    local sizing = height and string.format('class="live-cell" style="height:%spx"', height)
                          or 'class="live-cell r-stretch"'
    return pandoc.RawBlock("html", string.format(
      '<iframe data-src="%s/cell?name=%s" data-preload %s></iframe>',
      SERVER, el.identifier, sizing))
  end
end
