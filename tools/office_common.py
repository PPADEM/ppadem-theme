"""Helpers shared by the Word and PowerPoint builders.

Both builders start from Pandoc's default reference file, restyle it with the
palette from _brand/ppadem-brand.scss, and save it with fixed zip timestamps so
an unchanged build is byte-identical (otherwise CI would commit "new" binaries
on every push).
"""

import importlib.util
import io
import os
import re
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "_brand" / "logo.png"
EU_LOGO = ROOT / "_brand" / "eu-logo.png"
OFFICE = ROOT / "office-templates"


def _sync_brand():
    """tools/sync-brand.py, which reads the brand values from _brand/."""
    spec = importlib.util.spec_from_file_location("sync_brand", ROOT / "tools" / "sync-brand.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BRAND = _sync_brand()

# The brand palette as {"ppadem-red": "990000", ...} (no leading #)
P = {name: value.lstrip("#").upper() for name, value in _BRAND.palette().items()}

# $ppadem-font-office: Word and PowerPoint have no font fallback, so this
# must be a font every collaborator has.
FONT = _BRAND.fonts()["office"]


def logo_ratio(path: Path = LOGO) -> float:
    """Width / height of a PNG (default _brand/logo.png), read from its header."""
    width, height = struct.unpack(">II", path.read_bytes()[16:24])
    return width / height


def pandoc_default(name: str, dest: Path) -> Path:
    """Write Pandoc's default data file (e.g. reference.docx) to dest."""
    quarto = os.environ.get("QUARTO", "quarto")
    subprocess.run(
        [quarto, "pandoc", "-o", str(dest), "--print-default-data-file", name],
        check=True,
    )
    return dest


# ---------------------------------------------------------------------------
# Office theme (theme1.xml): colour picker, charts, SmartArt and theme fonts
# ---------------------------------------------------------------------------

# Theme slot -> palette entry. accent1-6 are the default chart series colours.
THEME_COLOURS = {
    "dk1": "ppadem-text",
    "lt1": "ppadem-white",
    "dk2": "ppadem-red-dark",
    "lt2": "ppadem-gray-light",
    "accent1": "ppadem-red",
    "accent2": "ppadem-teal",
    "accent3": "ppadem-gold",
    "accent4": "ppadem-grey",
    "accent5": "ppadem-slate",
    "accent6": "ppadem-teal-dark",
    "hlink": "ppadem-red",
    "folHlink": "ppadem-teal-dark",
}


def brand_theme(xml: bytes) -> bytes:
    """Replace the colour and font schemes of an Office theme part."""
    text = xml.decode("utf-8")
    slots = "".join(
        f'<a:{slot}><a:srgbClr val="{P[name]}"/></a:{slot}>' for slot, name in THEME_COLOURS.items()
    )
    text = re.sub(
        r"<a:clrScheme .*?</a:clrScheme>",
        f'<a:clrScheme name="PPADEM">{slots}</a:clrScheme>',
        text,
        count=1,
        flags=re.S,
    )
    fonts = f'<a:latin typeface="{FONT}"/><a:ea typeface=""/><a:cs typeface=""/>'
    text = re.sub(
        r"<a:fontScheme .*?</a:fontScheme>",
        f'<a:fontScheme name="PPADEM"><a:majorFont>{fonts}</a:majorFont>'
        f"<a:minorFont>{fonts}</a:minorFont></a:fontScheme>",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r'(<a:theme [^>]*name=")[^"]*"', r'\1PPADEM"', text, count=1)
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

TEMPLATE_TYPES = {
    "presentationml.presentation.main+xml": "presentationml.template.main+xml",
    "wordprocessingml.document.main+xml": "wordprocessingml.template.main+xml",
}


FIXED_DATE = "2000-01-01T00:00:00Z"


def _zip_fixed(entries) -> bytes:
    """A zip of (name, data) pairs with fixed timestamps."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as dst:
        for name, data in entries:
            fixed = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            fixed.compress_type = zipfile.ZIP_DEFLATED
            dst.writestr(fixed, data)
    return buffer.getvalue()


def _fixed_workbook(data: bytes) -> bytes:
    """An embedded chart workbook with its creation time pinned (python-pptx
    stamps the current time, which would make every build differ)."""
    entries = []
    with zipfile.ZipFile(io.BytesIO(data)) as src:
        for item in src.infolist():
            content = src.read(item.filename)
            if item.filename == "docProps/core.xml":
                content = re.sub(rb"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", FIXED_DATE.encode(), content)
            entries.append((item.filename, content))
    return _zip_fixed(entries)


def save_reproducibly(doc, path: Path, template: bool = False):
    """Save a python-docx/python-pptx document with fixed zip timestamps.

    With template=True the main part's content type is switched so the file is
    a real .dotx/.potx: opening it creates a new untitled document.
    """
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw.zip"
        doc.save(str(raw))
        path.parent.mkdir(parents=True, exist_ok=True)
        entries = []
        with zipfile.ZipFile(raw) as src:
            for item in src.infolist():
                data = src.read(item.filename)
                if template and item.filename == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    for document, tmpl in TEMPLATE_TYPES.items():
                        text = text.replace(document, tmpl)
                    data = text.encode("utf-8")
                if item.filename.endswith(".xlsx"):
                    data = _fixed_workbook(data)
                entries.append((item.filename, data))
        path.write_bytes(_zip_fixed(entries))
    print(f"wrote {path.relative_to(ROOT)}")
