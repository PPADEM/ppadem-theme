# PPADEM Quarto Theme

Quarto theme for the PPADEM project. Provides:

- A **website** theme (`ppadem-theme-html`) for Quarto project sites — the `cosmo`
  Bootswatch theme plus a `styles.css` override, same structure as before, just
  recolored to the official PPADEM brand palette.
- A **report** theme (`ppadem-report-html`) for standalone, self-contained HTML reports
  with a numbered-section layout and a cover-style title block.
- A **presentation** theme (`ppadem-presentation-revealjs`) for Reveal.js slide decks
  with brand title styling, embedded logo, card blocks, badges, and clean color accents.

All three are built on the official PPADEM brand palette (red `#990000`, teal `#298c8c`,
gold `#f1a226`, grey `#b8b8b8`) and the PPADEM logo.

## Install

For an existing project:

```bash
quarto add PPADEM/ppadem-theme
```

This installs all three extensions (`_extensions/ppadem-theme/`, `_extensions/ppadem-report/`, and `_extensions/ppadem-presentation/`).

## Start from a template

To start a new project with a ready-made starter document, run this in an empty directory:

```bash
quarto use template PPADEM/ppadem-theme
```

This installs the extensions and copies in a starter `.qmd`. Each extension ships its own
`template.qmd` (website, report, presentation); if Quarto only offers one, copy the one you
want from `_extensions/<name>/template.qmd` and set its `format:` as shown below.

## Usage

In the YAML front matter of a `.qmd`:

```md
---
title: Untitled
format: ppadem-theme-html
---
```

or, for a report:

```md
---
title: Untitled
format: ppadem-report-html
---
```

or, for a presentation:

```md
---
title: Untitled
format: ppadem-presentation-revealjs
---
```

You can also override the format at the command line:

```bash
quarto render document.qmd --to ppadem-theme-html
quarto render document.qmd --to ppadem-report-html
quarto render document.qmd --to ppadem-presentation-revealjs
```

## Components

The website and presentation themes include reusable content classes ported from the official PPADEM brand design, usable in any `.qmd` fenced div:

- `.ppadem-hero` / `.ppadem-pill` — page hero banner and pill label.
- `.ppadem-highlights-strip` / `.ppadem-highlight-tag` (with optional `.teal` / `.gold`
  modifiers) — stat badges strip.
- `.ppadem-card-grid` / `.ppadem-card` / `.card-link` — card grid with a link.
- `.workstream-grid` / `.workstream-item` (with optional `.teal` / `.gold` modifiers) /
  `.workstream-num` / `.workstream-title` / `.workstream-desc` — numbered workstream grid.
- `.highlight-teal` / `.highlight-gold` / `.highlight-red` — inline color highlights.
- `.placeholder-box` — dashed placeholder box for in-progress sections.

See `_extensions/ppadem-theme/template.qmd` (website), `_extensions/ppadem-report/template.qmd`, and `_extensions/ppadem-presentation/template.qmd` for worked examples of each format.

## License

The source code in this repository is licensed under the MIT License. The PPADEM logo
is the property of the PPADEM project.
