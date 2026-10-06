#!/usr/bin/env python3
"""Propagate the shared PPADEM brand from _brand/ into each extension.

Quarto extensions must be self-contained (files in a sibling extension can't
be referenced once installed with `quarto add`), so shared files are copied
into every extension that needs them and committed alongside it.

Usage:
    python3 tools/sync-brand.py           # write all generated files
    python3 tools/sync-brand.py --check   # exit 1 if anything is out of date
    python3 tools/sync-brand.py --office  # also rebuild the Word and PowerPoint files
    python3 tools/sync-brand.py --docx    # also rebuild the Word files only

Edit files in _brand/, never the generated copies in _extensions/. Besides
whole-file copies, the script regenerates marked blocks inside hand-written
files (between "BEGIN GENERATED" and "END GENERATED" comments), so those files
can use the brand values:

    custom.scss (website, report, slides)   every $ppadem-* variable
    ppadem-slides.lua                       the palette as a Lua table
    typst-template.typ (brief)              the palette and fonts
"""

import argparse
import base64
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "_brand"
EXT = ROOT / "_extensions"

BRAND_SCSS = BRAND / "ppadem-brand.scss"
LOGO = BRAND / "logo.png"
TITLE_BLOCK_IN = BRAND / "templates" / "title-block.html.in"

# Extensions that load the shared SCSS layer
SCSS_TARGETS = ["ppadem-theme", "ppadem-report", "ppadem-slides"]
# Extensions that ship their own copy of the logo
LOGO_TARGETS = ["ppadem-slides", "ppadem-brief"]
# Extensions whose custom.scss gets a generated block of brand variables
CUSTOM_SCSS_TARGETS = SCSS_TARGETS

NOTICE = "GENERATED from {src} by tools/sync-brand.py; edit the source, not this copy."


def scss_copy() -> str:
    text = BRAND_SCSS.read_text()
    # The header goes after the first section marker so Quarto still sees the
    # marker as the start of the file.
    first, rest = text.split("\n", 1)
    return f"{first}\n// {NOTICE.format(src='_brand/ppadem-brand.scss')}\n{rest}"


def palette() -> dict:
    """Read `$ppadem-name: #hex` definitions from the shared SCSS."""
    pattern = re.compile(r"^\$(ppadem-[a-z-]+):\s*(#[0-9a-fA-F]{3,8})\b", re.M)
    return dict(pattern.findall(BRAND_SCSS.read_text()))


def brand_variables() -> list:
    """Every one-line `$ppadem-…: …;` definition in the shared SCSS, in order."""
    return re.findall(r"^\$ppadem-[a-z-]+:.*;$", BRAND_SCSS.read_text(), re.M)


def fonts() -> dict:
    """The web font (first family of $ppadem-font-sans) and the Office font."""
    text = BRAND_SCSS.read_text()

    def first_family(name):
        value = re.search(rf"^\${name}:\s*([^,;!]+)", text, re.M).group(1)
        return value.strip().strip('"').strip("'")

    return {"web": first_family("ppadem-font-sans"), "office": first_family("ppadem-font-office")}


def with_block(path: Path, comment: str, lines: list) -> str:
    """path's text with the block between its BEGIN/END GENERATED markers replaced."""
    begin = f"{comment} BEGIN GENERATED BRAND VALUES"
    end = f"{comment} END GENERATED BRAND VALUES"
    text = path.read_text()
    if begin not in text:
        sys.exit(f"{path.relative_to(ROOT)} is missing its '{begin}' marker")
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    notice = f"{comment} {NOTICE.format(src='_brand/ppadem-brand.scss')}"
    return head + "\n".join([begin, notice, *lines, end]) + tail


def custom_scss(path: Path) -> str:
    """A format's custom.scss with every brand variable defined at the top.

    Quarto emits a later layer's defaults *before* the brand layer's, so
    without this block custom.scss couldn't use $ppadem-* in scss:defaults.
    The definitions are all !default, so they match the brand layer exactly.
    """
    return with_block(path, "//", brand_variables())


def slides_lua(path: Path) -> str:
    lines = ["local ppadem = {"]
    lines += [f'  ["{name[len("ppadem-"):]}"] = "{value.lower()}",' for name, value in palette().items()]
    lines.append("}")
    return with_block(path, "--", lines)


def brief_template(path: Path) -> str:
    """The brief's Typst template with its palette and fonts regenerated."""
    lines = [f'#let {name} = rgb("{value.lower()}")' for name, value in palette().items()]
    f = fonts()
    lines.append(f'#let ppadem-fonts = ("{f["web"]}", "{f["office"]}")')
    return with_block(path, "//", lines)


def title_block() -> str:
    logo = base64.b64encode(LOGO.read_bytes()).decode("ascii")
    body = TITLE_BLOCK_IN.read_text().replace("{{LOGO_BASE64}}", logo)
    notice = NOTICE.format(src="_brand/templates/title-block.html.in")
    return f"$-- {notice}\n{body}"


def outputs() -> dict:
    """Map each generated path to its expected contents (str or bytes)."""
    out = {}
    for ext in SCSS_TARGETS:
        out[EXT / ext / "ppadem-brand.scss"] = scss_copy()
    for ext in LOGO_TARGETS:
        out[EXT / ext / "logo.png"] = LOGO.read_bytes()
    for ext in CUSTOM_SCSS_TARGETS:
        path = EXT / ext / "custom.scss"
        out[path] = custom_scss(path)
    lua = EXT / "ppadem-slides" / "ppadem-slides.lua"
    out[lua] = slides_lua(lua)
    brief = EXT / "ppadem-brief" / "typst-template.typ"
    out[brief] = brief_template(brief)
    out[EXT / "ppadem-report" / "title-block.html"] = title_block()
    return out


def read(path: Path, like):
    if not path.exists():
        return None
    return path.read_bytes() if isinstance(like, bytes) else path.read_text()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="report stale files without writing")
    parser.add_argument("--docx", action="store_true", help="also rebuild the Word files")
    parser.add_argument("--office", action="store_true",
                        help="also rebuild the Word and PowerPoint files (Quarto reference docs "
                             "and office-templates/)")
    args = parser.parse_args()

    stale = []
    for path, expected in outputs().items():
        if read(path, expected) == expected:
            continue
        stale.append(path)
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(expected, bytes):
                path.write_bytes(expected)
            else:
                path.write_text(expected)

    for path in stale:
        verb = "out of date" if args.check else "updated"
        print(f"{verb}: {path.relative_to(ROOT)}")

    if args.check:
        if stale:
            print("Run `python3 tools/sync-brand.py` and commit the result.")
            return 1
        print("Brand files are in sync.")
        return 0

    if args.docx or args.office:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build-reference-docx.py")], check=True)
    if args.office:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build-powerpoint.py")], check=True)

    if not stale:
        print("Brand files already in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
