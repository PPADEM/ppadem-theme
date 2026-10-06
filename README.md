<p align="center">
  <img src="logo.png" alt="PPADEM logo" width="220">
</p>

# PPADEM Quarto Theme

Quarto themes and starter templates for the PPADEM project. Six formats are included:

| Format | Use it for | Format name |
| --- | --- | --- |
| **Website** | Quarto project sites and web pages | `ppadem-theme-html` |
| **Report** | Standalone, self-contained HTML reports with numbered sections and a cover-style title block | `ppadem-report-html` |
| **Slides** | Reveal.js slide decks (HTML, shown in a browser) with title, section and closing slides | `ppadem-slides-revealjs` |
| **Brief** | Printable A4 PDF policy briefs (Typst, needs Quarto 1.4+) | `ppadem-brief-typst` |
| **Word** | Word documents for collaborators who edit in Microsoft Word | `ppadem-word-docx` |
| **PowerPoint** | PowerPoint decks for collaborators who edit in Microsoft PowerPoint | `ppadem-powerpoint-pptx` |

All six use the official PPADEM brand palette (red `#990000`, teal `#298c8c`,
gold `#f1a226`, grey `#b8b8b8`), the PPADEM logo and the Inter typeface (Arial in
Word and PowerPoint).

Every format ends with the EU / ERC funding logo ("Funded by the European Union"),
added automatically: after the last section of a website page, report, brief or Word
document, on the last Reveal.js slide, and on a final slide of its own in PowerPoint.

> **Not using Quarto?** Ready-made PowerPoint and Word templates with the same branding
> are in [`office-templates/`](office-templates/), with instructions for using them.

## Quick start

You need [Quarto](https://quarto.org/docs/get-started/) (1.3 or later) installed.

1. **Create a project from the starter templates** (recommended). In an empty folder:

   ```bash
   quarto use template PPADEM/ppadem-theme
   ```

   This installs the themes into `_extensions/` and adds a starter file for each
   format: `website.qmd`, `report.qmd`, `slides.qmd`, `brief.qmd`,
   `word.qmd` and `powerpoint.qmd`. Delete the ones you don't need and replace the text with your own content.

   **Or install only the themes**, with no starter files:

   ```bash
   quarto add PPADEM/ppadem-theme
   ```

   To pick up later theme changes, run the same command again.

2. **Render**:

   ```bash
   quarto render report.qmd
   ```

## Using a theme without a template

Set the format in the YAML front matter of any `.qmd` file:

```yaml
---
title: My document
format: ppadem-report-html
---
```

You can also choose the format when you render:

```bash
quarto render document.qmd --to ppadem-brief-typst
```

## Components

Use the component classes in a fenced div (or a span for inline ones) in any `.qmd`:

```md
::: {.ppadem-card-grid}
::: {.ppadem-card}
### Research
Comparative research on party systems.
:::
:::
```

Most components take an optional `.teal` or `.gold` modifier. The starter templates show them in use.

| Class | What it is | Website | Report | Slides | Brief |
| --- | --- | :-: | :-: | :-: | :-: |
| `.ppadem-hero` | Page hero banner | ✓ | ✓ | ✓ | |
| `.ppadem-pill` / `.ppadem-badge` | Pill label (add `.solid` for filled; HTML only) | ✓ | ✓ | ✓ | ✓ |
| `.ppadem-label` | Small uppercase label | ✓ | ✓ | ✓ | ✓ |
| `.ppadem-highlights-strip` / `.ppadem-highlight-tag` | Stat tiles; the **bold** text is the number | ✓ | ✓ | ✓ | ✓ |
| `.ppadem-card-grid` / `.ppadem-card` / `.card-link` | Card grid | ✓ | ✓ | ✓ | ✓ |
| `.workstream-grid` / `.workstream-item` (+ `-num`, `-title`, `-desc`) | Numbered workstream grid | ✓ | ✓ | ✓ | |
| `.ppadem-key-findings` | Numbered findings box around a list | ✓ | ✓ | ✓ | ✓ |
| `.ppadem-quote` with `[— Name]{.attribution}` | Pull quote | ✓ | ✓ | ✓ | ✓ |
| `.highlight-teal` / `.highlight-gold` / `.highlight-red` | Inline colour highlights | ✓ | ✓ | ✓ | ✓ |
| `.placeholder-box` | Dashed placeholder for unfinished sections | ✓ | ✓ | ✓ | ✓ |
| `.ppadem-exec-summary` | Executive summary box | | ✓ | | ✓ |
| `.ppadem-team-grid` / `.ppadem-person` | Team member cards | ✓ | | | |
| `.ppadem-cta` | Call-to-action banner | ✓ | | | |

Quarto callouts (`::: {.callout-note}` and so on) use the brand colours in the
HTML formats and the brief: note and tip are teal, warning and caution are gold,
important is red. Tables get a soft red header row in every format, Word included.

The palette is also available as CSS custom properties in the HTML formats,
for example `style="color: var(--ppadem-teal)"`.

### Slides (Reveal.js)

```md
## Part one {.ppadem-section}          <!-- red section divider -->
## Part two {.ppadem-section .teal}    <!-- or .gold -->
## Thank you {.ppadem-closing}         <!-- closing slide -->
```

The logo, footer and slide number are hidden on section dividers.

> **Renamed:** this format used to be `ppadem-presentation-revealjs` (starter
> `presentation.qmd`). It was renamed so it isn't confused with the PowerPoint format.
> In existing documents, change the format to `ppadem-slides-revealjs`, then delete the old
> `_extensions/ppadem-presentation/` folder after updating with `quarto add PPADEM/ppadem-theme`.

### Report options

Add `report-number: "Report 2026-01"` to the front matter to show a pill above
the title. Sections marked `{.appendix}` are moved to the end of the report.

### Brief options

| Option | Default | Effect |
| --- | --- | --- |
| `brief-type` | `Policy Brief` | Label in the page header |
| `report-number` | none | Shown next to the label, e.g. `No. 1` |
| `abstract` | none | Shown as a shaded summary box under the title |
| `columns` | `1` | Set to `2` for a two-column body |

The brief uses Inter if it is installed, otherwise Arial. Install
[Inter](https://rsms.me/inter/) for the intended look. When you render, Quarto copies
`logo.png` and `eu-logo.png` next to your document so Typst can find them.

### Word

The Word format uses Arial (Word has no font fallback, so a universally
installed font is safer than Inter). The HTML component classes don't apply in
Word, so keep Word documents to plain Markdown.

The PPADEM paragraph styles from the Word template are available as custom styles:

```md
::: {custom-style="PPADEM Key Findings"}
First finding

Second finding
:::
```

The styles are `PPADEM Executive Summary`, `PPADEM Key Findings`, `PPADEM Note`,
`PPADEM Warning`, `PPADEM Important`, `PPADEM Pull Quote`, `PPADEM Quote Attribution`
and `PPADEM Label`.

### PowerPoint

The PowerPoint format uses the same slide master as the
[PowerPoint template](office-templates/). A level-1 heading (`# Part one`) makes a red
section divider and each level-2 heading (`## Slide title`) starts a new slide. Use
`:::: {.columns}` for two-column slides. As with Word, keep to plain Markdown: the HTML
components, the teal/gold dividers and the closing slide aren't available, but you can
switch layouts in PowerPoint after rendering (*Home → Layout*).

## Editing the brand (maintainers)

**Change the brand in `_brand/`, not in the extensions.** Quarto extensions must be
self-contained, so `tools/sync-brand.py` copies the brand from `_brand/` into every
format, including the Word and PowerPoint templates.

### What to edit where

| To change | Edit | It reaches |
| --- | --- | --- |
| A colour | The `$ppadem-…: #hex` lines in `_brand/ppadem-brand.scss` | Every format: website, report, slides, brief, Word and PowerPoint (Quarto formats and `office-templates/`) |
| The web font | `$ppadem-font-sans` in `_brand/ppadem-brand.scss` | Website, report and slides; its first font is also the brief's main font |
| The Office font | `$ppadem-font-office` in `_brand/ppadem-brand.scss` | Word, PowerPoint, and the brief's fallback font |
| Shared components (cards, pills, callouts, spacing, corners) | The rest of `_brand/ppadem-brand.scss` | Website, report and slides |
| The logo | Replace `_brand/logo.png` | Every format and both Office templates |
| The EU funding logo | Replace `_brand/eu-logo.png` | The end of every format and both Office templates |
| How the EU logo is added | `_brand/ppadem-funding.lua` (the brief: its `typst-template.typ`) | Website, report, slides, Word and PowerPoint |
| The report cover | `_brand/templates/title-block.html.in` | The report |
| One format's layout or look | That extension's `custom.scss`, `_extension.yml` or Lua/Typst file | That format only |
| Word or PowerPoint layouts and styles | `tools/build-reference-docx.py` or `tools/build-powerpoint.py` | Word or PowerPoint only |

Format files should only hold what is specific to that format, and should use brand
values rather than typing colours out: `$ppadem-red` in SCSS, `ppadem["red"]` in
`ppadem-slides.lua`, `ppadem-red` in the brief's Typst template, and `P["ppadem-red"]` in
the Office build scripts.

Colour **values** can change freely, but don't rename or remove a `$ppadem-…` colour
without updating the files that use it, or the build fails. A new colour is available
everywhere straight away, but only appears once a format uses it.

### What is generated

Don't edit these by hand; they are overwritten on every sync:

- `ppadem-brand.scss`, `logo.png`, `eu-logo.png` and `ppadem-funding.lua` inside the extensions, and the report's `title-block.html`
- The `BEGIN GENERATED BRAND VALUES` … `END GENERATED BRAND VALUES` blocks at the top of
  each `custom.scss`, in `ppadem-slides.lua` and in the brief's `typst-template.typ`.
  These define the brand values so the rest of the file can use them. The rest of each
  file is hand-written.
- The Word and PowerPoint files: `ppadem-reference.docx`, `ppadem-reference.pptx` and
  everything in `office-templates/` except its README

### Publishing a change

**You don't need to run anything after editing `_brand/`.** Push to GitHub and the
*Sync brand* action (`.github/workflows/sync-brand.yml`) regenerates the copies,
rebuilds the Word and PowerPoint files, commits the result back to your branch as
`github-actions[bot]`, and renders every starter to check nothing broke. Run
`git pull` before your next push so you pick up that commit.

To preview a brand change locally before pushing, run `python3 tools/sync-brand.py`
(add `--office` to rebuild the Word and PowerPoint files, which needs Quarto and
`pip install python-docx python-pptx`). `python3 tools/sync-brand.py --check` reports
anything out of date without changing it.

`_brand/`, `tools/`, `.github/` and `office-templates/` are listed in `.quartoignore`, so
they are not copied into projects created with `quarto use template`.

## License

The source code in this repository is licensed under the MIT License (see [LICENSE](LICENSE)). The PPADEM logo
is the property of the PPADEM project, and the EU emblem and ERC logo belong to their
owners; none of them is covered by the MIT licence.
