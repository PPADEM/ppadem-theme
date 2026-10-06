-- Prevent Pandoc from converting fenced divs (cards, columns, etc.)
-- that start with an h3+ into <section> tags, which Reveal.js interprets
-- as nested/vertical slides and causes slide navigation to crash/reset.
function Div(el)
  if #el.content > 0 and el.content[1].t == 'Header' and el.content[1].level > 2 then
    table.insert(el.content, 1, pandoc.RawBlock('html', ''))
    return el
  end
end
