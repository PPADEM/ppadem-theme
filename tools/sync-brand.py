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

Edit files in _brand/, never the generated copies in _extensions/.
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


PALETTE_BEGIN = "// BEGIN GENERATED PALETTE\n"
PALETTE_END = "// END GENERATED PALETTE"


def brief_template(path: Path) -> str:
    """The brief's Typst template with its palette block regenerated."""
    text = path.read_text()
    head, rest = text.split(PALETTE_BEGIN, 1)
    _, tail = rest.split(PALETTE_END, 1)
    lines = [f'#let {name} = rgb("{value.lower()}")' for name, value in palette().items()]
    return head + PALETTE_BEGIN + "\n".join(lines) + "\n" + PALETTE_END + tail


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
