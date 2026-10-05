-- Map the shared PPADEM component classes to the Typst functions defined in
-- typst-template.typ, so the same markup works in HTML and PDF briefs.

local function raw(text)
  return pandoc.RawBlock("typst", text)
end

local function accent(el)
  for _, name in ipairs({ "teal", "gold" }) do
    if el.classes:includes(name) then return name end
  end
  return "red"
end

-- Wrap a block list in a Typst function call: #fn(accent: "x")[ ... ]
local function wrap(fn, el, with_accent)
  local args = with_accent and ('(accent: "' .. accent(el) .. '")') or ""
  local blocks = pandoc.List({ raw("#" .. fn .. args .. "[") })
  blocks:extend(el.content)
  blocks:insert(raw("]"))
  return blocks
end

-- Wrap each child div as a positional argument: #fn([..], [..])
local function grid(fn, child_fn, el)
  local blocks = pandoc.List({ raw("#" .. fn .. "(") })
  for _, child in ipairs(el.content) do
    if child.t == "Div" then
      blocks:insert(raw(child_fn .. '(accent: "' .. accent(child) .. '")['))
      blocks:extend(child.content)
      blocks:insert(raw("],"))
    end
  end
  blocks:insert(raw(")"))
  return blocks
end

-- Grids run in a first pass, while their children are still plain divs.
local grid_handlers = {
  ["ppadem-highlights-strip"] = function(el) return grid("ppadem-stats", "ppadem-stat", el) end,
  ["ppadem-card-grid"] = function(el) return grid("ppadem-cards", "ppadem-card", el) end,
}

local div_handlers = {
  ["ppadem-card"] = function(el) return wrap("ppadem-card", el, true) end,
  ["ppadem-key-findings"] = function(el) return wrap("ppadem-key-findings", el, true) end,
  ["ppadem-exec-summary"] = function(el) return wrap("ppadem-box", el, true) end,
  ["ppadem-box"] = function(el) return wrap("ppadem-box", el, true) end,
  ["ppadem-quote"] = function(el) return wrap("ppadem-quote", el, false) end,
  ["placeholder-box"] = function(el) return wrap("ppadem-placeholder", el, false) end,
}

local span_handlers = {
  ["ppadem-label"] = "ppadem-label",
  ["ppadem-pill"] = "ppadem-pill",
  ["attribution"] = "ppadem-attribution",
}

local function dispatch(handlers)
  return function(el)
    for class, handler in pairs(handlers) do
      if el.classes:includes(class) then return handler(el) end
    end
  end
end

local function wrap_inline(call, el)
  local inlines = pandoc.List({ pandoc.RawInline("typst", call .. "[") })
  inlines:extend(el.content)
  inlines:insert(pandoc.RawInline("typst", "]"))
  return inlines
end

local function span(el)
  for class, fn in pairs(span_handlers) do
    if el.classes:includes(class) then
      local args = (fn == "ppadem-pill") and ('(accent: "' .. accent(el) .. '")') or ""
      return wrap_inline("#" .. fn .. args, el)
    end
  end
  for _, name in ipairs({ "red", "teal", "gold" }) do
    if el.classes:includes("highlight-" .. name) then
      return wrap_inline('#ppadem-highlight(accent: "' .. name .. '")', el)
    end
  end
end

return {
  { Div = dispatch(grid_handlers) },
  { Div = dispatch(div_handlers), Span = span },
}
