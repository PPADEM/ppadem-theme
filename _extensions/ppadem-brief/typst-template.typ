// PPADEM brief: Typst template (PDF output).
// The palette and font block below is generated from _brand/ppadem-brand.scss
// by tools/sync-brand.py; edit the colours and fonts there.

// BEGIN GENERATED BRAND VALUES
// GENERATED from _brand/ppadem-brand.scss by tools/sync-brand.py; edit the source, not this copy.
#let ppadem-red = rgb("#990000")
#let ppadem-red-hover = rgb("#b30000")
#let ppadem-red-dark = rgb("#660000")
#let ppadem-red-soft = rgb("#fdf2f2")
#let ppadem-red-border = rgb("#f2d0d0")
#let ppadem-teal = rgb("#298c8c")
#let ppadem-teal-dark = rgb("#1f6b6b")
#let ppadem-teal-soft = rgb("#e8f5f5")
#let ppadem-teal-border = rgb("#b2dede")
#let ppadem-gold = rgb("#f1a226")
#let ppadem-gold-dark = rgb("#b8740b")
#let ppadem-gold-soft = rgb("#fef6e9")
#let ppadem-gold-border = rgb("#fbdca8")
#let ppadem-grey = rgb("#b8b8b8")
#let ppadem-gray = rgb("#555e68")
#let ppadem-gray-light = rgb("#f8f9fa")
#let ppadem-slate = rgb("#24292e")
#let ppadem-border = rgb("#e5e7eb")
#let ppadem-border-strong = rgb("#d1d5db")
#let ppadem-text = rgb("#212529")
#let ppadem-white = rgb("#ffffff")
#let ppadem-fonts = ("Inter", "Arial")
// END GENERATED BRAND VALUES

#let ppadem-accent(name) = {
  if name == "teal" { ppadem-teal }
  else if name == "gold" { ppadem-gold }
  else { ppadem-red }
}

#let ppadem-accent-soft(name) = {
  if name == "teal" { ppadem-teal-soft }
  else if name == "gold" { ppadem-gold-soft }
  else { ppadem-red-soft }
}

#let ppadem-accent-dark(name) = {
  if name == "teal" { ppadem-teal-dark }
  else if name == "gold" { ppadem-gold-dark }
  else { ppadem-red-dark }
}

// ---------------- Components (used by brief-components.lua) ----------------

#let ppadem-label(body) = text(
  size: 0.8em, weight: "bold", fill: ppadem-red, tracking: 0.04em, upper(body),
)

#let ppadem-pill(accent: "red", body) = box(
  inset: (x: 7pt, y: 3pt),
  radius: 99pt,
  stroke: 0.6pt + ppadem-accent(accent).lighten(50%),
  text(size: 0.75em, weight: "semibold", fill: ppadem-accent-dark(accent), tracking: 0.04em, upper(body)),
)

// Gold text uses the darker shade for contrast on white, as in the HTML themes.
#let ppadem-highlight(accent: "red", body) = text(
  fill: if accent == "gold" { ppadem-gold-dark } else { ppadem-accent(accent) },
  body,
)

// One stat tile: the bold text becomes the large number.
#let ppadem-stat(accent: "red", body) = block(
  breakable: false,
  width: 100%,
  fill: ppadem-gray-light,
  stroke: (top: 2.5pt + ppadem-accent(accent)),
  radius: 3pt,
  inset: (x: 8pt, y: 8pt),
  {
    set align(center)
    set text(size: 0.9em, fill: ppadem-slate)
    show strong: it => block(below: 3pt, text(size: 1.9em, weight: "extrabold", fill: ppadem-accent(accent), it.body))
    body
  },
)

#let ppadem-stats(..tiles) = grid(
  columns: (1fr,) * tiles.pos().len(),
  gutter: 8pt,
  ..tiles.pos(),
)

#let ppadem-key-findings(accent: "red", body) = block(
  width: 100%,
  fill: ppadem-accent-soft(accent),
  stroke: 0.6pt + ppadem-accent(accent).lighten(70%),
  radius: 4pt,
  inset: 12pt,
  {
    set enum(numbering: n => box(
      width: 1.5em, height: 1.5em, radius: 50%, fill: ppadem-accent(accent),
      align(center + horizon, text(size: 0.8em, weight: "bold", fill: white, str(n))),
    ), body-indent: 0.6em)
    show enum.item: set block(below: 0.7em)
    body
  },
)

#let ppadem-box(accent: "red", body) = block(
  width: 100%,
  fill: ppadem-gray-light,
  stroke: (left: 3pt + ppadem-accent(accent), rest: 0.5pt + ppadem-border),
  radius: 3pt,
  inset: 12pt,
  body,
)

#let ppadem-quote(body) = block(
  breakable: false,
  width: 100%,
  fill: ppadem-teal-soft,
  stroke: (left: 3pt + ppadem-teal),
  inset: (x: 14pt, y: 10pt),
  text(size: 1.1em, weight: "medium", fill: ppadem-slate, body),
)

#let ppadem-attribution(body) = text(size: 0.8em, weight: "semibold", fill: ppadem-teal-dark, body)

#let ppadem-card(accent: "red", body) = block(
  breakable: false,
  width: 100%,
  stroke: (top: 2.5pt + ppadem-accent(accent), rest: 0.5pt + ppadem-border),
  radius: 3pt,
  inset: 10pt,
  {
    show heading: it => block(below: 6pt, sticky: true, text(size: 1.05em, weight: "bold", fill: ppadem-red-dark, it.body))
    set text(fill: ppadem-gray)
    body
  },
)

#let ppadem-cards(..cards) = grid(
  columns: (1fr,) * calc.min(cards.pos().len(), 3),
  gutter: 8pt,
  ..cards.pos(),
)

#let ppadem-placeholder(body) = block(
  breakable: false,
  width: 100%,
  fill: ppadem-gray-light,
  stroke: (paint: ppadem-border-strong, thickness: 0.8pt, dash: "dashed"),
  radius: 3pt,
  inset: 12pt,
  text(fill: ppadem-gray, body),
)

// ---------------- Branded Quarto callouts ----------------
// Quarto passes fixed default colours to callout(); map them to the brand.
#let _quarto-callout = callout
#let _ppadem-callout-colours = (
  "#0758e5": ppadem-teal,  // note
  "#00a047": ppadem-teal,  // tip
  "#eb9113": ppadem-gold,  // warning
  "#fc5300": ppadem-gold,  // caution
  "#cc1914": ppadem-red,   // important
)
#let callout(icon_color: black, background_color: none, ..args) = {
  let brand = _ppadem-callout-colours.at(icon_color.to-hex(), default: none)
  if brand == none {
    _quarto-callout(icon_color: icon_color, background_color: background_color, ..args)
  } else {
    _quarto-callout(icon_color: brand, background_color: brand.lighten(88%), ..args)
  }
}

// ---------------- Document ----------------

#let ppadem-brief(
  title: none,
  subtitle: none,
  authors: none,
  date: none,
  abstract: none,
  abstract-title: "Summary",
  brief-type: "Policy Brief",
  report-number: none,
  lang: "en",
  region: "GB",
  font: ppadem-fonts,
  fontsize: 10.5pt,
  sectionnumbering: none,
  cols: 1,
  doc,
) = {
  set document(title: title)
  set text(lang: lang, region: region, font: font, size: fontsize, fill: ppadem-text)
  set par(justify: false, leading: 0.68em, spacing: 0.95em)

  set page(
    header: context {
      set text(size: 8pt, fill: ppadem-gray)
      grid(
        columns: (auto, 1fr),
        align: (left + horizon, right + horizon),
        image("logo.png", height: 0.95cm),
        {
          upper(text(weight: "bold", fill: ppadem-red, tracking: 0.05em, brief-type))
          if report-number != none [ #h(4pt) · #h(4pt) #report-number ]
        },
      )
      v(-4pt)
      line(length: 100%, stroke: 1.2pt + ppadem-red)
    },
    footer: context {
      set text(size: 8pt, fill: ppadem-gray)
      line(length: 100%, stroke: 0.5pt + ppadem-border)
      v(-4pt)
      grid(
        columns: (1fr, auto),
        [PPADEM Project #h(4pt) · #h(4pt) Political Parties and Democracy in Africa],
        [#counter(page).display("1 / 1", both: true)],
      )
    },
  )

  // Links, lists, tables
  show link: set text(fill: ppadem-red)
  set list(marker: text(fill: ppadem-red, sym.bullet))
  set enum(numbering: n => text(fill: ppadem-red, weight: "bold", str(n) + "."))
  set table(stroke: (x, y) => if y == 0 { (bottom: 1.2pt + ppadem-red) } else { (bottom: 0.4pt + ppadem-border) },
            fill: (x, y) => if y == 0 { ppadem-red-soft } else if calc.even(y) { ppadem-gray-light },
            inset: 6pt)
  show table.cell.where(y: 0): set text(weight: "bold", fill: ppadem-red-dark)
  show figure.caption: set text(size: 0.88em, fill: ppadem-gray)

  // Headings with the PPADEM accent bar
  set heading(numbering: sectionnumbering)
  show heading: set text(fill: ppadem-slate)
  show heading.where(level: 1): it => block(above: 1.4em, below: 0.8em, sticky: true, {
    text(size: 1.35em, weight: "bold", fill: ppadem-red-dark, it)
    v(-6pt)
    box(width: 32pt, height: 1.6pt, fill: ppadem-red)
    box(width: 1fr, height: 1.6pt, fill: ppadem-red-soft)
  })
  show heading.where(level: 2): it => block(above: 1.2em, below: 0.6em, sticky: true,
    text(size: 1.1em, weight: "bold", fill: ppadem-slate, it))

  // Title block
  if title != none {
    v(4pt)
    text(size: 22pt, weight: "extrabold", fill: ppadem-red-dark, title)
    if subtitle != none {
      v(-8pt)
      text(size: 13pt, weight: "medium", fill: ppadem-teal, subtitle)
    }
    let meta = ()
    if authors != none { meta.push(authors.map(a => a.name).join(", ")) }
    if date != none { meta.push(date) }
    if meta.len() > 0 {
      v(-4pt)
      text(size: 9pt, fill: ppadem-gray, meta.join(h(6pt) + sym.dot + h(6pt)))
    }
    v(-2pt)
    grid(
      columns: (36pt, 36pt, 36pt),
      rect(width: 100%, height: 3pt, fill: ppadem-red),
      rect(width: 100%, height: 3pt, fill: ppadem-gold),
      rect(width: 100%, height: 3pt, fill: ppadem-teal),
    )
    v(6pt)
  }

  if abstract != none {
    block(width: 100%, fill: ppadem-red-soft, stroke: (left: 3pt + ppadem-red), inset: 12pt, radius: 3pt, {
      ppadem-label(abstract-title)
      v(-2pt)
      abstract
    })
    v(6pt)
  }

  if cols == 1 { doc } else { columns(cols, gutter: 16pt, doc) }
}
