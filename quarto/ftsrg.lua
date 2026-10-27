-- ftsrg look: every level-1 heading (section slide) gets the flow-line panel background.
-- "contain" rather than "cover": the image is 16:9 like the deck, so in a letterboxed
-- window it stays aligned with the slide's title instead of being cropped differently.
function Header(el)
  if el.level == 1 and quarto.doc.is_format("revealjs")
      and not el.attributes["background-image"] then
    el.attributes["background-image"] = "assets/brand/section-bg.png"
    el.attributes["background-size"] = "contain"
    return el
  end
end
