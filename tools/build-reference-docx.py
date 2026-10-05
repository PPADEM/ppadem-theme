#!/usr/bin/env python3
"""Build the PPADEM Word reference document.

Starts from Pandoc's default reference.docx and restyles it with the brand
palette from _brand/ppadem-brand.scss. The result is committed as
_extensions/ppadem-word/ppadem-reference.docx.

Requires Quarto on PATH (or set QUARTO=/path/to/quarto) and python-docx:

    pip install python-docx
    python3 tools/build-reference-docx.py
"""

import importlib.util
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_extensions" / "ppadem-word" / "ppadem-reference.docx"
LOGO = ROOT / "_brand" / "logo.png"

# Word has no font fallback, so use a font every collaborator will have.
FONT = "Arial"


def load_palette() -> dict:
    spec = importlib.util.spec_from_file_location("sync_brand", ROOT / "tools" / "sync-brand.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {name: value.lstrip("#") for name, value in module.palette().items()}


P = load_palette()


def rgb(name: str) -> RGBColor:
    return RGBColor.from_string(P[name].upper())


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


def paragraph_border(style, side: str, colour: str, size_eighths: int, space: int = 4):
    ppr = style.element.get_or_add_pPr()
    borders = ppr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        ppr.append(borders)
    edge = OxmlElement(f"w:{side}")
    edge.set(qn("w:val"), "single")
    edge.set(qn("w:sz"), str(size_eighths))
    edge.set(qn("w:space"), str(space))
    edge.set(qn("w:color"), P[colour])
    borders.append(edge)


def paragraph_shading(style, colour: str):
    ppr = style.element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), P[colour])
    ppr.append(shd)


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
    tblpr.append(borders)

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


def page_field(paragraph):
    """Append a PAGE field to a paragraph."""
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), kind)
            run._r.append(fld)
        else:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = text
            run._r.append(instr)
    return run


def save_reproducibly(doc, path: Path):
    """Save with fixed zip timestamps so an unchanged build is byte-identical
    (otherwise CI would commit a "new" docx on every push)."""
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw.docx"
        doc.save(str(raw))
        with zipfile.ZipFile(raw) as src, zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                fixed = zipfile.ZipInfo(item.filename, date_time=(1980, 1, 1, 0, 0, 0))
                fixed.compress_type = zipfile.ZIP_DEFLATED
                dst.writestr(fixed, src.read(item.filename))


def main():
    quarto = os.environ.get("QUARTO", "quarto")
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "reference.docx"
        subprocess.run(
            [quarto, "pandoc", "-o", str(base), "--print-default-data-file", "reference.docx"],
            check=True,
        )
        doc = Document(str(base))

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
    for level in range(3, 7):
        set_font(s[f"Heading {level}"], size=11, colour="ppadem-slate", bold=True, italic=False)
    for level in range(1, 7):
        set_font(s[f"Heading {level} Char"], colour="ppadem-red-dark" if level == 1 else "ppadem-slate")
    set_font(s["TOC Heading"], size=16, colour="ppadem-red-dark", bold=True)

    # Quotes, captions, links
    set_font(s["Block Text"], size=11, colour="ppadem-slate", italic=False)
    paragraph_border(s["Block Text"], "left", "ppadem-teal", 24, space=10)
    paragraph_shading(s["Block Text"], "ppadem-teal-soft")
    for name in ("Caption", "Table Caption", "Image Caption"):
        set_font(s[name], size=9, colour="ppadem-gray", italic=False)
    s["Hyperlink"].font.color.rgb = rgb("ppadem-red")
    style_table(s["Table"])

    # Page setup, header logo and footer
    for section in doc.sections:
        section.page_height, section.page_width = Cm(29.7), Cm(21.0)
        section.left_margin = section.right_margin = Cm(2.2)
        section.top_margin, section.bottom_margin = Cm(2.5), Cm(2.2)

        head = section.header.paragraphs[0]
        head.text = ""
        head.add_run().add_picture(str(LOGO), height=Cm(1.0))

        foot = section.footer.paragraphs[0]
        foot.text = ""
        run = foot.add_run("PPADEM Project  ·  Page ")
        run.font.size, run.font.color.rgb = Pt(8), rgb("ppadem-gray")
        page = page_field(foot)
        page.font.size, page.font.color.rgb = Pt(8), rgb("ppadem-gray")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    save_reproducibly(doc, OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
