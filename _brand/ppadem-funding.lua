-- Adds the "Funded by the European Union" / ERC logo (eu-logo.png, next to
-- this filter) at the end of the document.
--
-- HTML formats embed the image as a data URI, so nothing is copied next to the
-- document; Word and PowerPoint take it from Pandoc's media bag. In Reveal.js
-- the logo ends up on the last slide; PowerPoint gets a final slide of its own.

local ALT = "Funded by the European Union. European Research Council"

function Pandoc(doc)
  local file = io.open(quarto.utils.resolve_path("eu-logo.png"), "rb")
  if not file then
    return doc
  end
  local data = file:read("a")
  file:close()

  local src, width
  if quarto.doc.is_format("html") then
    src = "data:image/png;base64," .. quarto.base64.encode(data)
    width = "320px"
  else
    pandoc.mediabag.insert("eu-logo.png", "image/png", data)
    src = "eu-logo.png"
    width = "7cm"
  end

  if quarto.doc.is_format("pptx") then
    -- Its own final slide (a horizontal rule starts an untitled slide), so the
    -- last slide keeps its layout. No caption: Pandoc would print it under the
    -- picture, and the logo already carries the text.
    doc.blocks:insert(pandoc.HorizontalRule())
    doc.blocks:insert(pandoc.Para({ pandoc.Image({}, src, "", pandoc.Attr("", {}, { width = width })) }))
  else
    local image = pandoc.Image(ALT, src, "", pandoc.Attr("", {}, { width = width }))
    doc.blocks:insert(pandoc.Div(pandoc.Plain({ image }), pandoc.Attr("", { "ppadem-funding" })))
  end
  return doc
end
