<p align="center">
  <img src="logo.png" alt="PPADEM logo" width="220">
</p>

# PPADEM Quarto Theme

Quarto themes and starter templates for the PPADEM project. Five formats are included:

| Format | Use it for | Format name |
| --- | --- | --- |
| **Website** | Quarto project sites and web pages | `ppadem-theme-html` |
| **Report** | Standalone, self-contained HTML reports with numbered sections and a cover-style title block | `ppadem-report-html` |
| **Presentation** | Reveal.js slide decks with title, section and closing slides | `ppadem-presentation-revealjs` |
| **Brief** | Printable A4 PDF policy briefs (Typst, needs Quarto 1.4+) | `ppadem-brief-typst` |
| **Word** | Word documents for collaborators who edit in Microsoft Word | `ppadem-word-docx` |

All five use the official PPADEM brand palette (red `#990000`, teal `#298c8c`,
gold `#f1a226`, grey `#b8b8b8`), the Inter typeface and the PPADEM logo.

## Quick start

You need [Quarto](https://quarto.org/docs/get-started/) (1.3 or later) installed.

1. **Create a project from the starter templates** (recommended). In an empty folder:

   ```bash
   quarto use template PPADEM/ppadem-theme
   ```

   This installs the themes into `_extensions/` and adds a starter file for each
   format: `website.qmd`, `report.qmd`, `presentation.qmd`, `brief.qmd` and
   `word.qmd`. Delete the ones you don't need and replace the text with your own content.

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

### Presentation slides

```md
## Part one {.ppadem-section}          <!-- red section divider -->
## Part two {.ppadem-section .teal}    <!-- or .gold -->
## Thank you {.ppadem-closing}         <!-- closing slide -->
```

The logo, footer and slide number are hidden on section dividers.

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
`logo.png` next to your document so Typst can find it.

### Word

The Word format uses Arial (Word has no font fallback, so a universally
installed font is safer than Inter). The HTML component classes don't apply in
Word, so keep Word documents to plain Markdown.

## Editing the brand (maintainers)

The shared design lives in `_brand/` and is copied into each extension, because
Quarto extensions must be self-contained:

| Source | Used by |
| --- | --- |
| `_brand/ppadem-brand.scss` | Palette, fonts and shared components. Copied into the website, report and presentation extensions; its colours are also written into the brief's Typst template. |
| `_brand/logo.png` | Copied into the presentation and brief extensions, and embedded in the report title block. |
| `_brand/templates/title-block.html.in` | The report cover. |

Each extension's `custom.scss` holds only format-specific rules.

**You don't need to run anything after editing `_brand/`.** Push to GitHub and the
*Sync brand* action (`.github/workflows/sync-brand.yml`) regenerates the copies,
rebuilds the Word reference document, commits the result back to your branch as
`github-actions[bot]`, and renders every starter to check nothing broke. Run
`git pull` before your next push so you pick up that commit.

To preview a brand change locally before pushing, you can still run
`python3 tools/sync-brand.py` (add `--docx` to rebuild the Word document, which
needs `pip install python-docx`).

`_brand/`, `tools/` and `.github/` are listed in `.quartoignore`, so they are not
copied into projects created with `quarto use template`.

## License

The source code in this repository is licensed under the MIT License (see [LICENSE](LICENSE)). The PPADEM logo
is the property of the PPADEM project and is not covered by the MIT licence.
