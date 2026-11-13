<p align="center">
  <img src="logo.png" alt="PPADEM logo" width="220">
</p>

# PPADEM Theme

Branded templates for the PPADEM project:

| What | Use it for | Where |
| --- | --- | --- |
| **Word template** | Reports, papers and other documents written in Word | [`office-templates/PPADEM-document.dotx`](office-templates/) |
| **PowerPoint template** | Presentations | [`office-templates/PPADEM-presentation.potx`](office-templates/) |
| **Website** (Quarto) | Pages for the PPADEM Data Science site: training courses, guidance, tools and packages (e.g. [scopingreview](https://ppadem.github.io/scopingreview/)) | `ppadem-theme-html` |
| **Word** (Quarto) | Word documents written in Markdown, with the same styles as the Word template | `ppadem-word-docx` |
| **PowerPoint** (Quarto) | PowerPoint decks written in Markdown, with the same layouts as the PowerPoint template | `ppadem-powerpoint-pptx` |

Each template comes with an example file. All of them use the PPADEM palette (red
`#990000`, teal `#298c8c`, gold `#f1a226`, grey `#b8b8b8`) and the PPADEM logo.
The website uses the Inter typeface, and Word and PowerPoint use Arial. Each one
ends with the EU / ERC funding logo ("Funded by the European Union").

> **Not using Quarto?** Download the Word and PowerPoint templates from
> [`office-templates/`](office-templates/). Its README explains how to use them.

## Quick start (Quarto)

You need [Quarto](https://quarto.org/docs/get-started/) (1.3 or later) installed.

1. **Create a project from the starter template.** In an empty folder:

   ```bash
   quarto use template PPADEM/ppadem-theme
   ```

   This installs the Word and PowerPoint formats into `_extensions/` and adds:
   - `website/`: a ready-to-go website project (see [Website](#website) below)
   - `word.qmd`
   - `powerpoint.qmd`

   Delete the ones you don't need and replace the text with your own.

   **Or install only the formats into an existing project**, with no starter files:

   ```bash
   quarto add PPADEM/ppadem-theme
   ```

   To pick up later theme changes, run the same command again.

2. **Render**:

   ```bash
   quarto render website          # the website, into website/_site/
   quarto render word.qmd         # word.docx
   quarto render powerpoint.qmd   # powerpoint.pptx
   ```

To use a format in any other `.qmd` file, set it in the front matter:

```yaml
format: ppadem-word-docx
```

## Website

Use the website format for anything on the PPADEM Data Science site: a training course,
guidance and advice pages, or the home page of a tool or R package. The
[scopingreview](https://ppadem.github.io/scopingreview/) page is a live example.

### Start a new site

The `website/` folder is a complete Quarto website project. Copy it, rename it, and
work inside it:

| File | What it does |
| --- | --- |
| `_quarto.yml` | Site settings: title, navbar (logo, page links, PPADEM Hub and GitHub links), footer, search and the `ppadem-theme-html` format |
| `index.qmd` | The home page. It shows every component, so delete the parts you don't need |
| `logo.png` | The logo used in the navbar, hero and browser tab |
| `_extensions/ppadem-theme/` | The website format. Quarto only looks for formats inside the project, so the folder carries its own copy |

Then:

1. **Edit `_quarto.yml`.** Set `title`, `description` and `site-url`, change the GitHub
   link to your repository, and adjust the footer text if needed.
2. **Write your content in `index.qmd`.** Keep the hero at the top and replace the rest.
   Headings with `##` appear in the contents list on the right.
3. **Add more pages (optional).** Create another `.qmd` file, such as `courses.qmd`,
   and add it to the navbar in `_quarto.yml`:

   ```yaml
   navbar:
     left:
       - text: Home
         href: index.qmd
       - text: Courses
         href: courses.qmd
   ```

   Every page in the project uses the PPADEM format automatically.
4. **Preview while you edit.** From inside the folder, run `quarto preview`. The page reloads
   every time you save.
5. **Publish.** Run `quarto render` and upload `_site/`, or publish to GitHub Pages with
   `quarto publish gh-pages`.

### Use the format in an existing site

In the project folder, run `quarto add PPADEM/ppadem-theme`. Then set the format in
`_quarto.yml`, and copy the `navbar` and `page-footer` settings from
[`website/_quarto.yml`](website/_quarto.yml) for the PPADEM header and footer:

```yaml
format: ppadem-theme-html
```

The format turns on the table of contents on the right, copy buttons on code blocks
and anchor links on headings, and adds the EU funding logo at the end of every page.

### Components

Use these classes in a fenced div, or in a span for inline ones. Most of them take an
optional `.teal` or `.gold` modifier. `website/index.qmd` shows each one in use.

| Class | What it is |
| --- | --- |
| `.ppadem-hero` (+ `.ppadem-hero-title`, `.ppadem-hero-subtitle`) | Intro banner at the top of the page (see below) |
| `.ppadem-pill` | Rounded label, e.g. "PPADEM Data Science". Add `.solid` for a filled pill |
| `.ppadem-label` | Small uppercase label, e.g. as the first line of a box |
| `.ppadem-highlights-strip` / `.ppadem-highlight-tag` | Stat tiles; the **bold** text is the number |
| `.ppadem-card-grid` / `.ppadem-card` / `.card-link` | Grid of cards linking to sections, pages or other sites |
| `.ppadem-key-findings` | Numbered box around a list: key points, rules, steps |
| `.ppadem-quote` with `[— Name]{.attribution}` | Pull quote. Plain `>` quotes get a quieter version of the same look |

Hero with a logo column:

```md
::: {.ppadem-hero}
::: {.row .align-items-center}
::: {.col-lg-8}
[PPADEM Data Science]{.ppadem-pill}

# Page title {.ppadem-hero-title .unlisted}

::: {.ppadem-hero-subtitle}
One line about what this page offers.
:::
:::

::: {.col-lg-4 .text-center}
![](logo.png){fig-alt="PPADEM logo" style="max-height: 120px; width: auto;"}
:::
:::
:::
```

Stat tiles and cards:

```md
::: {.ppadem-highlights-strip}
::: {.ppadem-highlight-tag}
**6** training courses
:::
::: {.ppadem-highlight-tag .teal}
**12** how-to guides
:::
:::

::: {.ppadem-card-grid}
::: {.ppadem-card}
### Training {.unlisted}

Short courses on R and reproducible research.

[See courses &rarr;](#courses){.card-link}
:::
:::
```

Add `.unlisted` to headings inside the hero and cards, so they stay out of the contents list.

Quarto's own features are styled too:
- **Callouts** (`::: {.callout-note}` and so on): note and tip are teal, warning and
  caution are gold, important is red.
- **Tabsets:** `::: {.panel-tabset}`.
- **Code blocks:** get a copy button.
- **Tables:** get a soft red header row.

The palette is also available as CSS custom properties, for example
`style="color: var(--ppadem-teal)"`.

## Word (Quarto)

The Word format uses the same styles as `PPADEM-document.dotx`. In Markdown, `##`
becomes Heading 1, `###` Heading 2, `####` Heading 3 and `#####` Heading 4. There are
two callout boxes:

```md
::: {custom-style="PPADEM Note"}
Background information, a tip or a short summary.
:::

::: {custom-style="PPADEM Warning"}
A caveat or something to watch out for.
:::
```

The website components don't apply in Word, so keep the rest to plain Markdown.

## PowerPoint (Quarto)

The PowerPoint format uses the same slide master as `PPADEM-presentation.potx`:
- a level-1 heading (`# Part one`) makes a red section divider;
- each level-2 heading (`## Slide title`) starts a new slide;
- `:::: {.columns}` makes a two-column slide;
- a slide with text and a picture or table uses the Content with Caption layout.

To change a slide's layout after rendering, use *Home → Layout* in PowerPoint.

## Editing the brand (maintainers)

**Change the brand in `_brand/`, not in the extensions.** Quarto extensions must be
self-contained, so `tools/sync-brand.py` copies the brand from `_brand/` into each
format and rebuilds the Word and PowerPoint files.

| To change | Edit | It reaches |
| --- | --- | --- |
| A colour | The `$ppadem-…: #hex` lines in `_brand/ppadem-brand.scss` | Everything |
| The web font | `$ppadem-font-sans` in `_brand/ppadem-brand.scss` | Website |
| The Office font | `$ppadem-font-office` in `_brand/ppadem-brand.scss` | Word and PowerPoint |
| The website's look and components | The rest of `_brand/ppadem-brand.scss` | Website |
| The logo | Replace `_brand/logo.png` | Both Office templates and `website/logo.png` |
| The EU funding logo | Replace `_brand/eu-logo.png` | Everything |
| How the EU logo is added | `_brand/ppadem-funding.lua` | The Quarto formats |
| Word styles or PowerPoint layouts | `tools/build-reference-docx.py` or `tools/build-powerpoint.py` | The Office templates, examples and Quarto reference files |

In the Office build scripts, use brand values such as `P["ppadem-red"]` rather than
typing colours out. Colour **values** can change freely. Don't rename or remove a
`$ppadem-…` colour without updating the files that use it, or the build fails.

### What is generated

Don't edit these by hand; they are overwritten on every sync:

- `ppadem-brand.scss`, `eu-logo.png` and `ppadem-funding.lua` inside the extensions
- `website/_extensions/` and `website/logo.png`: copies of the website format and the logo
- `ppadem-reference.docx`, `ppadem-reference.pptx` and everything in `office-templates/`
  except its README

### Publishing a change

**You don't need to run anything after editing `_brand/`.** Push to GitHub and the
*Sync brand* action (`.github/workflows/sync-brand.yml`) does the rest:
- regenerates the copies and rebuilds the Word and PowerPoint files;
- commits the result back to your branch as `github-actions[bot]`;
- renders every starter to check nothing broke.

Run `git pull` before your next push so you pick up that commit.

To preview a change locally, run `python3 tools/sync-brand.py`. Add `--office` to
rebuild the Word and PowerPoint files, which needs Quarto and
`pip install python-docx python-pptx`. `python3 tools/sync-brand.py --check` reports
anything out of date without changing it.

`_brand/`, `tools/`, `.github/` and `office-templates/` are listed in `.quartoignore`,
so they are not copied into projects created with `quarto use template`.

## License

The source code in this repository is licensed under the MIT License (see [LICENSE](LICENSE)). The PPADEM logo
is the property of the PPADEM project, and the EU emblem and ERC logo belong to their
owners; none of them is covered by the MIT licence.
