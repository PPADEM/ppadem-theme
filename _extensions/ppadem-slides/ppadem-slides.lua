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

-- BEGIN GENERATED BRAND VALUES
-- GENERATED from _brand/ppadem-brand.scss by tools/sync-brand.py; edit the source, not this copy.
local ppadem = {
  ["red"] = "#990000",
  ["red-hover"] = "#b30000",
  ["red-dark"] = "#660000",
  ["red-soft"] = "#fdf2f2",
  ["red-border"] = "#f2d0d0",
  ["teal"] = "#298c8c",
  ["teal-dark"] = "#1f6b6b",
  ["teal-soft"] = "#e8f5f5",
  ["teal-border"] = "#b2dede",
  ["gold"] = "#f1a226",
  ["gold-dark"] = "#b8740b",
  ["gold-soft"] = "#fef6e9",
  ["gold-border"] = "#fbdca8",
  ["grey"] = "#b8b8b8",
  ["gray"] = "#555e68",
  ["gray-light"] = "#f8f9fa",
  ["slate"] = "#24292e",
  ["border"] = "#e5e7eb",
  ["border-strong"] = "#d1d5db",
  ["text"] = "#212529",
  ["white"] = "#ffffff",
}
-- END GENERATED BRAND VALUES

local section_colours = {
  teal = ppadem["teal"],
  gold = ppadem["gold"],
}

function Header(el)
  if el.classes:includes("ppadem-section") then
    local colour = ppadem["red"]
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
      el.attributes["background-color"] = ppadem["red-soft"]
    end
    return el
  end
end
