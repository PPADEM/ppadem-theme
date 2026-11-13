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

Edit files in _brand/, never the generated copies in _extensions/ or website/.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "_brand"
EXT = ROOT / "_extensions"
WEBSITE = ROOT / "website"

BRAND_SCSS = BRAND / "ppadem-brand.scss"
LOGO = BRAND / "logo.png"
# "Funded by the European Union" / ERC logo, shown at the end of every document
EU_LOGO = BRAND / "eu-logo.png"
FUNDING_LUA = BRAND / "ppadem-funding.lua"

# Extensions that load the brand stylesheet
SCSS_TARGETS = ["ppadem-theme"]
# Extensions that add the EU logo at the end with ppadem-funding.lua
FUNDING_TARGETS = ["ppadem-theme", "ppadem-word", "ppadem-powerpoint"]

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


def fonts() -> dict:
    """The web font (first family of $ppadem-font-sans) and the Office font."""
    text = BRAND_SCSS.read_text()

    def first_family(name):
        value = re.search(rf"^\${name}:\s*([^,;!]+)", text, re.M).group(1)
        return value.strip().strip('"').strip("'")

    return {"web": first_family("ppadem-font-sans"), "office": first_family("ppadem-font-office")}


def funding_lua() -> str:
    notice = NOTICE.format(src="_brand/ppadem-funding.lua")
    return f"-- {notice}\n{FUNDING_LUA.read_text()}"


def outputs() -> dict:
    """Map each generated path to its expected contents (str or bytes)."""
    out = {}
    for ext in SCSS_TARGETS:
        out[EXT / ext / "ppadem-brand.scss"] = scss_copy()
    for ext in FUNDING_TARGETS:
        out[EXT / ext / "eu-logo.png"] = EU_LOGO.read_bytes()
        out[EXT / ext / "ppadem-funding.lua"] = funding_lua()

    # The website starter is a Quarto project of its own, and Quarto only looks
    # for extensions inside the project, so it carries a copy of the format.
    theme = EXT / "ppadem-theme"
    for src in sorted(theme.iterdir()):
        out[WEBSITE / "_extensions" / "ppadem-theme" / src.name] = out.get(src) or src.read_bytes()
    out[WEBSITE / "logo.png"] = LOGO.read_bytes()
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
