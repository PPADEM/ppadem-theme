-- Section divider and closing slides.
--
--   ## Part one {.ppadem-section}          red background
--   ## Part two {.ppadem-section .teal}    teal background
--   ## Part three {.ppadem-section .gold}  gold background
--   ## Thank you {.ppadem-closing}         soft red background
--
-- Sets the slide background (an explicit background-color still wins). Section
-- slides also get a Reveal.js state so the CSS can hide the logo, footer and
-- slide number while they are showing.

local section_colours = {
  teal = "#298c8c",
  gold = "#f1a226",
}

function Header(el)
  if el.classes:includes("ppadem-section") then
    local colour = "#990000"
    for name, value in pairs(section_colours) do
      if el.classes:includes(name) then colour = value end
    end
    if not el.attributes["background-color"] then
      el.attributes["background-color"] = colour
    end
    el.attributes["data-state"] = "ppadem-section-slide"
    return el
  end

  if el.classes:includes("ppadem-closing") then
    if not el.attributes["background-color"] then
      el.attributes["background-color"] = "#fdf2f2"
    end
    return el
  end
end
