#!/usr/bin/env python3
"""Build the PPADEM PowerPoint template, example deck and Quarto reference doc.

Starts from Pandoc's default reference.pptx (so the layout names Pandoc looks
for are kept), rebuilds the slide master and every layout in the PPADEM style,
and writes:

    _extensions/ppadem-powerpoint/ppadem-reference.pptx   Quarto reference doc
    office-templates/PPADEM-presentation.potx             PowerPoint template
    office-templates/PPADEM-presentation-example.pptx     every layout in use

Requires Quarto on PATH (or set QUARTO=/path/to/quarto) and python-pptx:

    pip install python-pptx
    python3 tools/build-powerpoint.py
"""

import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml import parse_xml
from pptx.parts.slide import SlideLayoutPart
from pptx.dml.color import RGBColor
from pptx.util import Pt

from office_common import LOGO, OFFICE, P, ROOT, brand_theme, pandoc_default, save_reproducibly

REFERENCE = ROOT / "_extensions" / "ppadem-powerpoint" / "ppadem-reference.pptx"
TEMPLATE = OFFICE / "PPADEM-presentation.potx"
EXAMPLE = OFFICE / "PPADEM-presentation-example.pptx"

# Office's standard 16:9 slide, 13.333 x 7.5 in
SLIDE_W, SLIDE_H = 13.333, 7.5
MARGIN = 0.6
CONTENT_W = SLIDE_W - 2 * MARGIN
LOGO_RATIO = 259 / 229  # width / height of _brand/logo.png

NS = (
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
)
SCHEME = {"tx1", "tx2", "bg1", "bg2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"}


# ---------------------------------------------------------------------------
# DrawingML snippets
# ---------------------------------------------------------------------------

def emu(inches: float) -> int:
    return int(round(inches * 914400))


def colour(name: str) -> str:
    """A theme colour (accent1, tx2, ...) or a palette entry (ppadem-red-soft)."""
    if name in SCHEME:
        return f'<a:solidFill><a:schemeClr val="{name}"/></a:solidFill>'
    return f'<a:solidFill><a:srgbClr val="{P[name]}"/></a:solidFill>'


def xfrm(x, y, w, h) -> str:
    return (
        f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
        f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
    )


class Shapes:
    """Collects shape XML for one slide master or layout, numbering ids."""

    def __init__(self):
        self.xml = []
        self.next_id = 2

    def _id(self):
        self.next_id += 1
        return self.next_id - 1

    def rect(self, name, x, y, w, h, fill):
        self.xml.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{self._id()}" name="{name}"/><p:cNvSpPr/>'
            f'<p:nvPr userDrawn="1"/></p:nvSpPr><p:spPr>{xfrm(x, y, w, h)}'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{colour(fill)}<a:ln><a:noFill/></a:ln>'
            f"</p:spPr></p:sp>"
        )

    def text(self, name, x, y, w, h, runs, size=10, fill="ppadem-gray", align="l"):
        """Static text box. runs is plain text, or "#" for the slide number."""
        rpr = f'<a:rPr lang="en-GB" sz="{size * 100}" dirty="0">{colour(fill)}</a:rPr>'
        if runs == "#":
            body = (
                f'<a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum">'
                f"{rpr}<a:t>‹#›</a:t></a:fld>"
            )
        else:
            body = f"<a:r>{rpr}<a:t>{runs}</a:t></a:r>"
        self.xml.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{self._id()}" name="{name}"/><p:cNvSpPr txBox="1"/>'
            f'<p:nvPr userDrawn="1"/></p:nvSpPr><p:spPr>{xfrm(x, y, w, h)}'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/>'
            f'<a:lstStyle/><a:p><a:pPr algn="{align}"/>{body}</a:p></p:txBody></p:sp>'
        )

    def picture(self, name, rid, x, y, h):
        w = h * LOGO_RATIO
        self.xml.append(
            f'<p:pic><p:nvPicPr><p:cNvPr id="{self._id()}" name="{name}" descr="PPADEM logo"/>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr userDrawn="1"/>'
            f'</p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch>'
            f'</p:blipFill><p:spPr>{xfrm(x, y, w, h)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f"</p:spPr></p:pic>"
        )

    def placeholder(self, name, ph, prompt, box=None, anchor=None, style="", inset=True):
        """A placeholder. Without box it inherits position from the master."""
        sppr = f"<p:spPr>{xfrm(*box)}</p:spPr>" if box else "<p:spPr/>"
        attrs = f' anchor="{anchor}"' if anchor else ""
        if not inset:
            attrs += ' lIns="0" rIns="0"'
        lst = f"<a:lstStyle>{style}</a:lstStyle>" if style else "<a:lstStyle/>"
        self.xml.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{self._id()}" name="{name}"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph {ph}/></p:nvPr></p:nvSpPr>'
            f"{sppr}<p:txBody><a:bodyPr{attrs}><a:normAutofit/></a:bodyPr>{lst}"
            f'<a:p><a:r><a:rPr lang="en-GB" dirty="0"/><a:t>{prompt}</a:t></a:r></a:p></p:txBody></p:sp>'
        )

    def tree(self) -> str:
        return (
            '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + "".join(self.xml)
            + "</p:spTree>"
        )


def level1(size=None, bold=False, fill=None, align=None, bullets=False) -> str:
    """lstStyle override for the first paragraph level of a placeholder."""
    ppr = f' algn="{align}"' if align else ""
    if not bullets:
        ppr += ' marL="0" indent="0"'
    rpr = f' sz="{size * 100}"' if size else ""
    rpr += ' b="1"' if bold else ""
    inner = colour(fill) if fill else ""
    bu = "" if bullets else "<a:buNone/>"
    return f"<a:lvl1pPr{ppr}>{bu}<a:defRPr{rpr}>{inner}</a:defRPr></a:lvl1pPr>"


# ---------------------------------------------------------------------------
# Slide master
# ---------------------------------------------------------------------------

TITLE_BOX = (MARGIN, 0.45, CONTENT_W, 0.95)
BODY_BOX = (MARGIN, 1.75, CONTENT_W, 4.85)


def body_level(lvl, mar, size, bullet, fill, space=10):
    return (
        f'<a:lvl{lvl}pPr marL="{emu(mar)}" indent="{-emu(0.3)}" algn="l" defTabSz="914400" '
        f'rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1">'
        f'<a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="{space * 100}"/></a:spcBef>'
        f'<a:buClr><a:schemeClr val="{fill}"/></a:buClr><a:buFont typeface="Arial"/>'
        f'<a:buChar char="{bullet}"/><a:defRPr sz="{size * 100}" kern="1200">'
        f'<a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/>'
        f'<a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl{lvl}pPr>'
    )


def text_styles() -> str:
    title = (
        '<p:titleStyle><a:lvl1pPr algn="l" defTabSz="914400" rtl="0" eaLnBrk="1" latinLnBrk="0" '
        'hangingPunct="1"><a:lnSpc><a:spcPct val="90000"/></a:lnSpc><a:spcBef><a:spcPct val="0"/>'
        '</a:spcBef><a:buNone/><a:defRPr sz="2800" b="1" kern="1200">'
        '<a:solidFill><a:schemeClr val="tx2"/></a:solidFill><a:latin typeface="+mj-lt"/>'
        '<a:ea typeface="+mj-ea"/><a:cs typeface="+mj-cs"/></a:defRPr></a:lvl1pPr></p:titleStyle>'
    )
    levels = [
        body_level(1, 0.3, 20, "•", "accent1"),
        body_level(2, 0.75, 18, "–", "accent2", space=4),
        body_level(3, 1.2, 16, "•", "accent2", space=4),
    ] + [body_level(n, 0.45 * n + 0.3, 14, "–", "accent4", space=4) for n in range(4, 10)]
    body = "<p:bodyStyle>" + "".join(levels) + "</p:bodyStyle>"
    other = (
        '<p:otherStyle><a:defPPr><a:defRPr lang="en-GB"/></a:defPPr>'
        '<a:lvl1pPr marL="0" algn="l" defTabSz="914400" rtl="0" eaLnBrk="1" latinLnBrk="0" '
        'hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/>'
        '</a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/>'
        "</a:defRPr></a:lvl1pPr></p:otherStyle>"
    )
    return f"<p:txStyles>{title}{body}{other}</p:txStyles>"


def footer(shapes: Shapes, rid: str):
    """Footer text, slide number and logo along the bottom of the slide."""
    shapes.text("Footer", MARGIN, 6.92, 5, 0.3, "PPADEM Project")
    logo_h = 0.55
    logo_x = SLIDE_W - MARGIN - logo_h * LOGO_RATIO
    shapes.text("Slide number", logo_x - 1.2, 6.92, 0.95, 0.3, "#", align="r")
    shapes.picture("Logo", rid, logo_x, 6.75, logo_h)


def build_master(master):
    _, rid = master.part.get_or_add_image_part(str(LOGO))
    shapes = Shapes()
    shapes.placeholder("Title", 'type="title"', "Click to edit title", TITLE_BOX, anchor="b", inset=False)
    shapes.placeholder("Text", 'type="body" idx="1"', "Click to edit text", BODY_BOX, inset=False)
    footer(shapes, rid)

    el = master._element
    old_tree = el.cSld.spTree
    old_tree.getparent().replace(old_tree, parse_xml(f"<p:wrap {NS}>{shapes.tree()}</p:wrap>")[0])
    bg = el.cSld.find("{http://schemas.openxmlformats.org/presentationml/2006/main}bg")
    if bg is not None:
        el.cSld.remove(bg)
    el.cSld.insert(0, parse_xml(f'<p:bg {NS}><p:bgPr>{colour("bg1")}<a:effectLst/></p:bgPr></p:bg>'))
    old_styles = el.find("{http://schemas.openxmlformats.org/presentationml/2006/main}txStyles")
    old_styles.getparent().replace(old_styles, parse_xml(f"<p:wrap {NS}>{text_styles()}</p:wrap>")[0])


# ---------------------------------------------------------------------------
# Layouts
# ---------------------------------------------------------------------------

def title_rule(shapes: Shapes, x=MARGIN, y=1.44, w=CONTENT_W):
    """Soft full-width underline with a short red bar (the h2 accent)."""
    shapes.rect("Title rule", x, y, w, 0.025, "ppadem-red-border")
    shapes.rect("Title accent", x, y - 0.0125, 0.75, 0.05, "accent1")


def titled(shapes: Shapes):
    # Explicit boxes (not inherited from the master): Pandoc reads the
    # placeholder size from the layout to place tables and images.
    shapes.placeholder("Title", 'type="title"', "Click to add title", TITLE_BOX, anchor="b", inset=False)
    title_rule(shapes)


def half(side: int, y=1.75, h=4.85):
    w = (CONTENT_W - 0.3) / 2
    return (MARGIN + side * (w + 0.3), y, w, h)


def layout_title(s: Shapes, rid):
    s.picture("Logo", rid, 0.8, 0.7, 1.0)
    s.rect("Accent bar", 0.8, 2.35, 0.09, 3.35, "accent1")
    s.placeholder("Title", 'type="ctrTitle"', "Presentation title", (1.15, 2.35, 10.8, 1.75),
                  anchor="b", inset=False, style=level1(40, bold=True, fill="tx2"))
    s.placeholder("Subtitle", 'type="subTitle" idx="1"', "Subtitle · Presenter · Date",
                  (1.15, 4.2, 10.8, 1.1), anchor="t", inset=False, style=level1(20, fill="accent2"))
    # Pandoc puts the document date here; in PowerPoint it shows only when
    # Insert → Header & Footer → Date is ticked.
    s.placeholder("Date", 'type="dt" sz="half" idx="10"', "Date", (1.15, 5.35, 6, 0.35),
                  anchor="t", inset=False, style=level1(14, fill="ppadem-gray"))
    for i, fill in enumerate(("accent1", "accent3", "accent2")):
        s.rect("Brand rule", 1.15 + i * 0.6, 6.0, 0.6, 0.07, fill)
    s.text("Footer", 0.8, 6.85, 5, 0.3, "PPADEM Project")


def layout_section(text_fill):
    def build(s: Shapes, rid):
        s.placeholder("Title", 'type="title"', "Section title", (0.8, 2.3, 11.7, 1.6),
                      anchor="b", inset=False, style=level1(44, bold=True, fill=text_fill))
        s.rect("Accent bar", 0.8, 4.05, 0.9, 0.07, text_fill)
        s.placeholder("Text", 'type="body" idx="1"', "Optional one-line description",
                      (0.8, 4.3, 11.7, 1.4), anchor="t", inset=False, style=level1(20, fill=text_fill))
    return build


def layout_content(s: Shapes, rid):
    titled(s)
    s.placeholder("Content", 'idx="1"', "Click to add text, a table, chart or picture", BODY_BOX, inset=False)


def layout_two(s: Shapes, rid):
    titled(s)
    s.placeholder("Left", 'sz="half" idx="1"', "Left column", half(0), inset=False)
    s.placeholder("Right", 'sz="half" idx="2"', "Right column", half(1), inset=False)


def layout_comparison(s: Shapes, rid):
    titled(s)
    head = level1(20, bold=True, fill="accent2")
    s.placeholder("Left heading", 'type="body" idx="1"', "Left heading", half(0, 1.75, 0.55),
                  anchor="b", inset=False, style=head)
    s.placeholder("Left", 'sz="half" idx="2"', "Left column", half(0, 2.45, 4.15), inset=False)
    s.placeholder("Right heading", 'type="body" sz="quarter" idx="3"', "Right heading",
                  half(1, 1.75, 0.55), anchor="b", inset=False, style=head)
    s.placeholder("Right", 'sz="quarter" idx="4"', "Right column", half(1, 2.45, 4.15), inset=False)


def layout_title_only(s: Shapes, rid):
    titled(s)


def layout_blank(s: Shapes, rid):
    pass


def with_caption(content_ph, prompt):
    def build(s: Shapes, rid):
        s.placeholder("Title", 'type="title"', "Click to add title", (MARGIN, 0.6, 4.2, 1.3),
                      anchor="b", inset=False, style=level1(24))
        title_rule(s, y=2.0, w=4.2)
        s.placeholder("Caption", 'type="body" sz="half" idx="2"', "Caption or key message",
                      (MARGIN, 2.25, 4.2, 4.35), inset=False, style=level1(16))
        s.placeholder("Content", content_ph, prompt, (5.2, 0.6, SLIDE_W - MARGIN - 5.2, 6.0))
    return build


def layout_closing(s: Shapes, rid):
    logo_h = 1.3
    s.picture("Logo", rid, (SLIDE_W - logo_h * LOGO_RATIO) / 2, 1.0, logo_h)
    s.placeholder("Title", 'type="title"', "Thank you", (MARGIN, 2.6, CONTENT_W, 1.2),
                  anchor="b", inset=False, style=level1(44, bold=True, fill="tx2", align="ctr"))
    s.rect("Accent bar", (SLIDE_W - 0.9) / 2, 3.95, 0.9, 0.07, "accent1")
    s.placeholder("Text", 'type="body" idx="1"', "Contact details or next steps",
                  (1.6, 4.25, SLIDE_W - 3.2, 1.6), anchor="t", inset=False,
                  style=level1(20, fill="ppadem-gray", align="ctr"))


# (name, layout type, builder, background, show master shapes)
# The first seven names are the ones Pandoc looks for; keep them.
LAYOUTS = [
    ("Title Slide", "title", layout_title, None, False),
    ("Title and Content", "obj", layout_content, None, True),
    ("Section Header", "secHead", layout_section("bg1"), "accent1", False),
    ("Section Header (Teal)", None, layout_section("bg1"), "accent2", False),
    ("Section Header (Gold)", None, layout_section("accent5"), "accent3", False),
    ("Two Content", "twoObj", layout_two, None, True),
    ("Comparison", "twoTxTwoObj", layout_comparison, None, True),
    ("Title Only", "titleOnly", layout_title_only, None, True),
    ("Content with Caption", "objTx", with_caption('idx="1"', "Click to add a table, chart or text"), None, True),
    ("Picture with Caption", "picTx", with_caption('type="pic" idx="1"', "Click the icon to add a picture"), None, True),
    ("Blank", "blank", layout_blank, None, True),
    ("Closing", None, layout_closing, "ppadem-red-soft", False),
]


def layout_xml(name, kind, shapes: Shapes, background, show_master) -> str:
    attrs = f' type="{kind}"' if kind else ""
    attrs += "" if show_master else ' showMasterSp="0"'
    bg = f"<p:bg><p:bgPr>{colour(background)}<a:effectLst/></p:bgPr></p:bg>" if background else ""
    return (
        f'<p:sldLayout {NS}{attrs} preserve="1"><p:cSld name="{name}">{bg}{shapes.tree()}</p:cSld>'
        f"<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"
    )


def build_layouts(prs):
    master = prs.slide_master
    existing = {layout.name: layout for layout in master.slide_layouts}
    wanted = {name for name, *_ in LAYOUTS}
    for name, layout in existing.items():
        if name not in wanted:
            master.slide_layouts.remove(layout)

    id_list = master._element.sldLayoutIdLst
    ids = {int(e.get("id")): e for e in id_list}
    next_id = max(ids) + 1
    package = prs.part.package
    order = []
    for name, kind, builder, background, show_master in LAYOUTS:
        if name in existing:
            part = existing[name].part
            rid = next(e.rId for e in id_list if master.part.related_part(e.rId) is part)
        else:
            partname = package.next_partname("/ppt/slideLayouts/slideLayout%d.xml")
            placeholder = parse_xml(layout_xml(name, kind, Shapes(), background, show_master))
            part = SlideLayoutPart(partname, CT.PML_SLIDE_LAYOUT, package, placeholder)
            part.relate_to(master.part, RT.SLIDE_MASTER)
            rid = master.part.relate_to(part, RT.SLIDE_LAYOUT)
            id_list.append(parse_xml(f'<p:sldLayoutId {NS} id="{next_id}" r:id="{rid}"/>'))
            next_id += 1
        _, image_rid = part.get_or_add_image_part(str(LOGO))
        shapes = Shapes()
        builder(shapes, image_rid)
        part._element = parse_xml(layout_xml(name, kind, shapes, background, show_master))
        order.append(rid)
        # Drop the logo relationship from layouts that don't use it
        if f'r:embed="{image_rid}"' not in "".join(shapes.xml):
            part.drop_rel(image_rid)

    # Reorder the New Slide gallery to match LAYOUTS
    entries = {e.rId: e for e in id_list}
    for e in list(id_list):
        id_list.remove(e)
    for rid in order:
        id_list.append(entries[rid])


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------

def delete_slides(prs):
    id_list = prs.slides._sldIdLst
    for sld in list(id_list):
        prs.part.drop_rel(sld.rId)
        id_list.remove(sld)


def build_base() -> Presentation:
    with tempfile.TemporaryDirectory() as tmp:
        prs = Presentation(str(pandoc_default("reference.pptx", Path(tmp) / "reference.pptx")))

    prs.slide_width, prs.slide_height = emu(SLIDE_W), emu(SLIDE_H)
    # The default file has guides placed for a smaller slide; drop them.
    ext = prs.part._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}extLst")
    if ext is not None:
        prs.part._element.remove(ext)
    delete_slides(prs)

    master = prs.slide_master
    theme = master.part.part_related_by(RT.THEME)
    theme._blob = brand_theme(theme.blob)
    build_master(master)
    build_layouts(prs)

    props = prs.core_properties
    props.title = "PPADEM presentation"
    props.author = props.last_modified_by = "PPADEM Project"
    return prs


def layout(prs, name):
    return next(l for l in prs.slide_layouts if l.name == name)


def add(prs, name, title=None, *bodies):
    slide = prs.slides.add_slide(layout(prs, name))
    phs = sorted(slide.placeholders, key=lambda p: p.placeholder_format.idx)
    if title is not None:
        phs[0].text = title
    for ph, body in zip(phs[1:], bodies):
        lines = body if isinstance(body, list) else [body]
        tf = ph.text_frame
        tf.text = ""
        for i, line in enumerate(lines):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            if isinstance(line, tuple):
                para.level, line = line
            para.text = line
    return slide


def stat_tile(slide, x, y, number, label, fill):
    from pptx.util import Inches
    tile = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(3.4), Inches(1.9))
    tile.adjustments[0] = 0.06
    tile.fill.solid()
    tile.fill.fore_color.rgb = RGBColor.from_string(P["ppadem-gray-light"])
    tile.line.color.rgb = RGBColor.from_string(P["ppadem-border"])
    tile.shadow.inherit = False
    tf = tile.text_frame
    tf.text = ""
    big = tf.paragraphs[0].add_run()
    big.text = number
    big.font.size, big.font.bold = Pt(48), True
    big.font.color.rgb = RGBColor.from_string(P[fill])
    small = tf.add_paragraph().add_run()
    small.text = label
    small.font.size = Pt(18)
    small.font.color.rgb = RGBColor.from_string(P["ppadem-slate"])
    for para in tf.paragraphs:
        para.alignment = PP_ALIGN.CENTER


def build_example(prs):
    from pptx.util import Inches

    add(prs, "Title Slide", "Using the PPADEM template",
        ["How to build a branded PowerPoint deck", "PPADEM Project Team · October 2026"])
    add(prs, "Title and Content", "Start here", [
        "Add slides with Home → New Slide and pick a layout from the list",
        "Every layout already has the logo, colours and fonts – just type into the boxes",
        "Change a slide's layout with Home → Layout",
        (1, "Use the Tab key to indent a bullet, Shift+Tab to go back"),
        "Pick colours from the Theme Colours row so they stay on brand",
    ])
    add(prs, "Section Header", "Section divider", "Use the red divider to start each part of a talk")
    add(prs, "Two Content", "Two Content layout",
        ["Put text, a picture, a table or a chart on each side", "Good for before/after or text plus figure"],
        ["Each side has its own placeholder", "Click the icons in an empty box to insert content"])
    add(prs, "Comparison", "Comparison layout", "Option A",
        ["Short teal heading above each column", "Use it to compare two cases"],
        "Option B", ["The headings are styled for you", "Keep each column to a few bullets"])

    slide = add(prs, "Title Only", "Key programme highlights")
    for i, (number, label, fill) in enumerate(
        (("25", "Countries", "ppadem-red"), ("80", "Political parties", "ppadem-teal"),
         ("6", "Active workstreams", "ppadem-gold-dark"))
    ):
        stat_tile(slide, MARGIN + 0.55 + i * 4.0, 2.4, number, label, fill)
    note = slide.shapes.add_textbox(Inches(MARGIN), Inches(5.0), Inches(CONTENT_W), Inches(0.6))
    note.text_frame.text = "Copy these stat tiles to other slides and change the numbers."
    note.text_frame.paragraphs[0].runs[0].font.size = Pt(16)
    note.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string(P["ppadem-gray"])

    slide = add(prs, "Title Only", "Charts use the brand colours automatically")
    data = CategoryChartData()
    data.categories = ["2022", "2023", "2024", "2025"]
    data.add_series("Ruling parties", (12, 18, 21, 25))
    data.add_series("Opposition parties", (9, 14, 20, 27))
    data.add_series("New parties", (3, 5, 8, 11))
    frame = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(MARGIN), Inches(1.75), Inches(CONTENT_W), Inches(4.85), data
    )
    chart = frame.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.font.size = Pt(14)

    slide = add(prs, "Title Only", "Tables pick up the brand style")
    rows = [("Country", "Parties surveyed", "Interviews"), ("Ghana", "4", "62"),
            ("Kenya", "5", "71"), ("Zambia", "3", "48"), ("Total", "12", "181")]
    table = slide.shapes.add_table(len(rows), 3, Inches(MARGIN), Inches(1.75), Inches(CONTENT_W),
                                   Inches(0.5 * len(rows))).table
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            cell.text_frame.paragraphs[0].runs[0].font.size = Pt(18)

    # Placeholders are filled in idx order: content (idx 1), then caption (idx 2)
    add(prs, "Content with Caption", "Content with Caption",
        ["Large content area", "Paste a chart, table or picture here"],
        "Use the narrow column for the key message and the large area for a chart or table.")
    add(prs, "Section Header (Teal)", "Teal section divider", "An alternative colour for a second part")
    add(prs, "Section Header (Gold)", "Gold section divider", "And a third, for appendices or Q&A")
    add(prs, "Closing", "Thank you", ["Questions and discussion", "[Your name] · [email address]"])


def main():
    reference = build_base()
    save_reproducibly(reference, REFERENCE)

    template = build_base()
    add(template, "Title Slide")
    save_reproducibly(template, TEMPLATE, template=True)

    example = build_base()
    build_example(example)
    save_reproducibly(example, EXAMPLE)


if __name__ == "__main__":
    main()
