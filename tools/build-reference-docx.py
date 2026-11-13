#!/usr/bin/env python3
"""Build the PPADEM Word reference document, template and example.

Starts from Pandoc's default reference.docx and restyles it with the brand
palette from _brand/ppadem-brand.scss. Writes:

    _extensions/ppadem-word/ppadem-reference.docx   Quarto reference doc
    office-templates/PPADEM-document.dotx           Word template (cover page)
    office-templates/PPADEM-document-example.docx   every style in use

Requires Quarto on PATH (or set QUARTO=/path/to/quarto) and python-docx:

    pip install python-docx
    python3 tools/build-reference-docx.py
"""

import tempfile
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

from office_common import EU_LOGO, FONT, LOGO, OFFICE, P, ROOT, brand_theme, pandoc_default, save_reproducibly

REFERENCE = ROOT / "_extensions" / "ppadem-word" / "ppadem-reference.docx"
TEMPLATE = OFFICE / "PPADEM-document.dotx"
EXAMPLE = OFFICE / "PPADEM-document-example.docx"

# Child order of <w:pPr> required by the OOXML schema (Word rejects files
# whose elements are out of order).
PPR_ORDER = [
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
    "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
    "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
    "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
    "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
    "sectPr", "pPrChange",
]


def rgb(name: str) -> RGBColor:
    return RGBColor.from_string(P[name])


def set_font(style, size=None, colour=None, bold=None, italic=None):
    font = style.font
    font.name = FONT
    # Also set the East Asian / complex-script font slots so Word doesn't
    # fall back to the theme font for them.
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), FONT)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(attr), None)
    if size is not None:
        font.size = Pt(size)
    if colour is not None:
        font.color.rgb = rgb(colour)
    if bold is not None:
        font.bold = bold
    if italic is not None:
        font.italic = italic


def insert_ppr(ppr, child):
    """Insert child into a <w:pPr> at its schema position, replacing any existing one."""
    name = child.tag.split("}")[1]
    old = ppr.find(qn(f"w:{name}"))
    if old is not None:
        if name != "pBdr":
            ppr.remove(old)
        else:
            # Merge border edges into the existing <w:pBdr>
            for edge in child:
                existing = old.find(edge.tag)
                if existing is not None:
                    old.remove(existing)
                old.append(edge)
            sides = ("top", "left", "bottom", "right", "between", "bar")
            for edge in sorted(old, key=lambda e: sides.index(e.tag.split("}")[1])):
                old.append(edge)
            return
    later = PPR_ORDER[PPR_ORDER.index(name) + 1:]
    for i, existing in enumerate(ppr):
        if existing.tag.split("}")[1] in later:
            ppr.insert(i, child)
            return
    ppr.append(child)


def paragraph_border(target, side: str, colour: str, size_eighths: int, space: int = 4):
    """target is a style or a paragraph."""
    ppr = target.element.get_or_add_pPr() if hasattr(target, "element") else target._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    edge = OxmlElement(f"w:{side}")
    edge.set(qn("w:val"), "single")
    edge.set(qn("w:sz"), str(size_eighths))
    edge.set(qn("w:space"), str(space))
    edge.set(qn("w:color"), P[colour])
    borders.append(edge)
    insert_ppr(ppr, borders)


def paragraph_shading(style, colour: str):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), P[colour])
    insert_ppr(style.element.get_or_add_pPr(), shd)


def style_table(style):
    """Header row in soft red with a red rule; light horizontal rules."""
    el = style.element
    for old in el.findall(qn("w:tblStylePr")):
        el.remove(old)

    tblpr = el.find(qn("w:tblPr"))
    if tblpr is None:
        tblpr = OxmlElement("w:tblPr")
        el.append(tblpr)
    for old in tblpr.findall(qn("w:tblBorders")):
        tblpr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "bottom", "insideH"):
        edge = OxmlElement(f"w:{side}")
        edge.set(qn("w:val"), "single")
        edge.set(qn("w:sz"), "4")
        edge.set(qn("w:color"), P["ppadem-border"])
        borders.append(edge)
    later = {qn(f"w:{n}") for n in ("shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription")}
    position = next((i for i, child in enumerate(tblpr) if child.tag in later), len(tblpr))
    tblpr.insert(position, borders)

    header = OxmlElement("w:tblStylePr")
    header.set(qn("w:type"), "firstRow")
    rpr = OxmlElement("w:rPr")
    bold = OxmlElement("w:b")
    colour = OxmlElement("w:color")
    colour.set(qn("w:val"), P["ppadem-red-dark"])
    rpr.extend([bold, colour])
    tcpr = OxmlElement("w:tcPr")
    tc_borders = OxmlElement("w:tcBorders")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:color"), P["ppadem-red"])
    tc_borders.append(bottom)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), P["ppadem-red-soft"])
    tcpr.extend([tc_borders, shd])
    header.extend([rpr, tcpr])
    el.append(header)


def page_field(paragraph, code="PAGE", placeholder=None):
    """Append a field (PAGE by default) to a paragraph."""
    run = paragraph.add_run()
    parts = [("begin", None), (None, code)]
    if placeholder:
        parts.append(("separate", None))
    for kind, text in parts:
        if kind:
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), kind)
            run._r.append(fld)
        else:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = f" {code} " if placeholder else code
            run._r.append(instr)
    if placeholder:
        paragraph.add_run(placeholder)
        run = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(end)
    return run


# ---------------------------------------------------------------------------
# PPADEM named styles (Home → Styles in Word; custom-style="…" in Quarto)
# ---------------------------------------------------------------------------

def add_box_style(styles, name, accent, fill, text="ppadem-text", bold=False):
    """A shaded paragraph with a coloured left rule. Consecutive paragraphs in
    the same style join into one box."""
    style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = styles["Body Text"]
    style.next_paragraph_style = style
    set_font(style, size=10.5, colour=text, bold=bold)
    paragraph_shading(style, fill)
    # Same-colour top and bottom rules pad the box; Word draws them only above
    # the first and below the last paragraph of a run of identical paragraphs.
    for side in ("top", "bottom"):
        paragraph_border(style, side, fill, 4, space=6)
    paragraph_border(style, "left", accent, 24, space=8)
    fmt = style.paragraph_format
    fmt.left_indent = fmt.right_indent = Cm(0.3)
    fmt.space_before, fmt.space_after = Pt(10), Pt(10)
    # No gap between paragraphs inside the same box
    insert_ppr(style.element.get_or_add_pPr(), OxmlElement("w:contextualSpacing"))
    style.quick_style = True
    return style


def add_ppadem_styles(doc):
    add_box_style(doc.styles, "PPADEM Note", "ppadem-teal", "ppadem-teal-soft")
    add_box_style(doc.styles, "PPADEM Warning", "ppadem-gold", "ppadem-gold-soft")


# The styles shown in Home → Styles. Everything else (Pandoc's own styles, which
# Quarto output needs) is hidden until a document uses it.
GALLERY = {
    "Normal", "Body Text", "Title", "Subtitle",
    "Heading 1", "Heading 2", "Heading 3", "Heading 4",
    "PPADEM Note", "PPADEM Warning", "Caption",
}


def tidy_gallery(doc):
    for style in doc.styles:
        shown = style.name in GALLERY
        style.quick_style = shown
        if style.name in ("Normal", "Default Paragraph Font", "Table") or shown:
            style.hidden = False
        else:
            style.hidden = True
            style.unhide_when_used = True


# ---------------------------------------------------------------------------
# Styles and page setup shared by all three files
# ---------------------------------------------------------------------------

def build_styles(doc):
    s = doc.styles

    # Body text
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        set_font(s[name], size=10.5, colour="ppadem-text")
    s["Body Text"].paragraph_format.space_after = Pt(6)
    s["Body Text"].paragraph_format.line_spacing = 1.15

    # Title block
    set_font(s["Title"], size=26, colour="ppadem-red-dark", bold=True)
    s["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    s["Title"].paragraph_format.space_after = Pt(4)
    set_font(s["Subtitle"], size=14, colour="ppadem-teal", bold=False, italic=False)
    s["Subtitle"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for name in ("Author", "Date"):
        set_font(s[name], size=10, colour="ppadem-gray")
        s[name].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_font(s["Abstract Title"], size=9, colour="ppadem-red", bold=True)
    set_font(s["Abstract"], size=10.5, colour="ppadem-slate")
    paragraph_shading(s["Abstract"], "ppadem-red-soft")
    paragraph_border(s["Abstract"], "left", "ppadem-red", 24, space=8)

    # Headings: H1 gets the PPADEM underline
    set_font(s["Heading 1"], size=16, colour="ppadem-red-dark", bold=True)
    s["Heading 1"].paragraph_format.space_before = Pt(18)
    s["Heading 1"].paragraph_format.space_after = Pt(8)
    paragraph_border(s["Heading 1"], "bottom", "ppadem-red-border", 8)
    set_font(s["Heading 2"], size=13, colour="ppadem-slate", bold=True)
    s["Heading 2"].paragraph_format.space_before = Pt(14)
    set_font(s["Heading 3"], size=11.5, colour="ppadem-teal", bold=True, italic=False)
    # Heading 5 and 6 only come from Quarto output; they match Heading 4
    for level in range(4, 7):
        set_font(s[f"Heading {level}"], size=10.5, colour="ppadem-slate", bold=True, italic=True)
    for level in range(1, 7):
        colour = {1: "ppadem-red-dark", 3: "ppadem-teal"}.get(level, "ppadem-slate")
        set_font(s[f"Heading {level} Char"], colour=colour)
    set_font(s["TOC Heading"], size=16, colour="ppadem-red-dark", bold=True)

    # Pressing Enter after a heading or the title block continues in body text
    for name in [f"Heading {level}" for level in range(1, 10)] + ["Title", "Subtitle", "Author", "Date"]:
        s[name].next_paragraph_style = s["Body Text"]

    # Quotes, captions, links
    set_font(s["Block Text"], size=11, colour="ppadem-slate", italic=False)
    paragraph_border(s["Block Text"], "left", "ppadem-teal", 24, space=10)
    paragraph_shading(s["Block Text"], "ppadem-teal-soft")
    for name in ("Caption", "Table Caption", "Image Caption"):
        set_font(s[name], size=9, colour="ppadem-gray", italic=False)
    s["Hyperlink"].font.color.rgb = rgb("ppadem-red")
    style_table(s["Table"])

    add_ppadem_styles(doc)
    tidy_gallery(doc)

    # Theme colours and fonts: the colour picker shows the PPADEM palette
    theme = doc.part.part_related_by(RT.THEME)
    theme._blob = brand_theme(theme.blob)


def page_setup(doc, cover=False):
    """A4, logo in the header, "PPADEM Project · Page n" in the footer.

    With cover=True the first page has no header or footer (the cover page
    carries its own large logo)."""
    for section in doc.sections:
        section.page_height, section.page_width = Cm(29.7), Cm(21.0)
        section.left_margin = section.right_margin = Cm(2.2)
        section.top_margin, section.bottom_margin = Cm(2.5), Cm(2.2)
        # Word requires these on <w:pgMar>; Pandoc's default omits them
        section.header_distance = section.footer_distance = Cm(1.25)
        section.gutter = Cm(0)
        section.different_first_page_header_footer = cover

        head = section.header.paragraphs[0]
        head.text = ""
        head.add_run().add_picture(str(LOGO), height=Cm(1.0))

        foot = section.footer.paragraphs[0]
        foot.text = ""
        run = foot.add_run("PPADEM Project  ·  Page ")
        run.font.size, run.font.color.rgb = Pt(8), rgb("ppadem-gray")
        page = page_field(foot)
        page.font.size, page.font.color.rgb = Pt(8), rgb("ppadem-gray")


def build_base():
    with tempfile.TemporaryDirectory() as tmp:
        doc = Document(str(pandoc_default("reference.docx", Path(tmp) / "reference.docx")))
    build_styles(doc)
    return doc


# ---------------------------------------------------------------------------
# Template and example content
# ---------------------------------------------------------------------------

def clear_body(doc):
    body = doc.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def brand_rule(doc):
    """Short red / gold / teal rule, as under the slide and report titles."""
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    for column in table.columns:
        column.width = Cm(1.3)
    tbl_pr = table._tbl.tblPr
    width = tbl_pr.find(qn("w:tblW"))
    width.set(qn("w:w"), str(int(Cm(3.9).twips)))
    width.set(qn("w:type"), "dxa")
    tbl_pr.find(qn("w:jc")).addnext(parse_xml(f'<w:tblInd {nsdecls("w")} w:w="0" w:type="dxa"/>'))
    for cell, fill in zip(table.rows[0].cells, ("ppadem-red", "ppadem-gold", "ppadem-teal")):
        cell.width = Cm(1.3)
        cell._tc.get_or_add_tcPr().append(
            parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{P[fill]}"/>')
        )
        para = cell.paragraphs[0]
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.line_spacing = Pt(1)
        para.add_run().font.size = Pt(1)
    row = table.rows[0]._tr.get_or_add_trPr()
    row.append(parse_xml(f'<w:trHeight {nsdecls("w")} w:val="80" w:hRule="exact"/>'))


def cover(doc, title, subtitle, author, date):
    doc.add_paragraph().add_run().add_picture(str(LOGO), height=Cm(2.6))
    block = [
        doc.add_paragraph(title, style="Title"),
        doc.add_paragraph(subtitle, style="Subtitle"),
        doc.add_paragraph(author, style="Author"),
        doc.add_paragraph(date, style="Date"),
    ]
    block[0].paragraph_format.space_before = Pt(160)
    # A red bar down the left of the title block, as on the title slide
    for para in block:
        paragraph_border(para, "left", "ppadem-red", 48, space=12)
    block[-1].paragraph_format.space_after = Pt(18)
    brand_rule(doc)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_paragraph("Contents", style="TOC Heading")
    toc = doc.add_paragraph(style="Body Text")
    page_field(toc, 'TOC \\o "1-3" \\h \\z \\u',
               "Right-click here and choose Update Field to build the table of contents.")
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def funding(doc):
    """The EU funding logo, centred at the end of the document."""
    para = doc.add_paragraph(style="Body Text")
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(24)
    para.add_run().add_picture(str(EU_LOGO), width=Cm(7.0))


def build_template(doc):
    clear_body(doc)
    cover(doc, "[Document title]", "[Subtitle]", "[Authors]", "[Date]")
    doc.add_paragraph("[Introduction]", style="Heading 1")
    doc.add_paragraph(
        "[Start writing here. Apply styles from Home → Styles: Heading 1–4, "
        "PPADEM Note and PPADEM Warning.]",
        style="Body Text",
    )
    funding(doc)
    page_setup(doc, cover=True)


def say(doc, text, style="Body Text"):
    return doc.add_paragraph(text, style=style)


def build_example(doc):
    clear_body(doc)
    cover(doc, "Using the PPADEM Word template",
          "How to write branded documents with Word styles", "PPADEM Project Team", "October 2026")

    say(doc, "Getting started", "Heading 1")
    say(doc, "Everything in this document is formatted with styles, so it stays on brand "
             "without any manual formatting. Click in a paragraph and choose a style from "
             "Home → Styles. To see every style, open the Styles pane (the small arrow at the "
             "bottom-right of the Styles group on Windows, or Format → Style on a Mac).")
    say(doc, "To start your own document, double-click PPADEM-document.dotx. Word opens a new "
             "untitled copy, so the template itself is never changed.")
    say(doc, "The Styles gallery holds only what you need: Title and Subtitle, Heading 1 to "
             "Heading 4, Body Text, Caption, and two callout boxes.")

    say(doc, "Headings", "Heading 1")
    say(doc, "Use Heading 1 for main sections. It gets the red rule underneath and appears in "
             "the table of contents.")
    say(doc, "Heading 2 for subsections", "Heading 2")
    say(doc, "Heading 2 is slate grey. Press Enter after any heading and Word switches back to "
             "Body Text automatically.")
    say(doc, "Heading 3 for smaller divisions", "Heading 3")
    say(doc, "Heading 3 is teal.")
    say(doc, "Heading 4 for the smallest divisions", "Heading 4")
    say(doc, "Heading 4 is italic. After adding or renaming headings, right-click the table of "
             "contents and choose Update Field.")

    say(doc, "Callouts", "Heading 1")
    say(doc, "PPADEM Note: a teal box for background information, tips or a short summary.",
        "PPADEM Note")
    say(doc, "Consecutive paragraphs in the same box style join into one box.", "PPADEM Note")
    say(doc, "PPADEM Warning: a gold box for caveats and things to watch out for.",
        "PPADEM Warning")

    say(doc, "Tables and figures", "Heading 1")
    say(doc, "Insert a table, then choose the PPADEM “Table” style from Table Design → Table Styles "
             "(it is under Custom at the top). Put a Table Caption paragraph above it.")
    say(doc, "Table 1: Coverage by region", "Table Caption")
    rows = [("Region", "Countries", "Parties"), ("West Africa", "9", "30"),
            ("East Africa", "7", "22"), ("Southern Africa", "9", "28")]
    table = doc.add_table(rows=len(rows), cols=3, style="Table")
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.cell(r, c).text = value
            if c:
                table.cell(r, c).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    say(doc, "Figure captions go below the figure in the Image Caption style.", "Image Caption")

    say(doc, "Colours", "Heading 1")
    say(doc, "When you colour text, shapes or charts, pick from the Theme Colours row at the top "
             "of the colour menu: it holds the PPADEM red, teal, gold and grey. Charts inserted in "
             "Word use these colours automatically.")
    say(doc, "Funding logo", "Heading 1")
    say(doc, "End every document with the EU funding logo, as below. Keep it on the last page.")
    funding(doc)
    page_setup(doc, cover=True)


def main():
    reference = build_base()
    page_setup(reference)
    save_reproducibly(reference, REFERENCE)

    template = build_base()
    build_template(template)
    save_reproducibly(template, TEMPLATE, template=True)

    example = build_base()
    build_example(example)
    save_reproducibly(example, EXAMPLE)


if __name__ == "__main__":
    main()
