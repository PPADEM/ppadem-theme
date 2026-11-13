# Tasks for the PPADEM Quarto theme. Run `just` to list them.

# List the available recipes
default:
    @{{just_executable()}} --list

# Remove rendered documents and build artefacts
cls:
    #!/usr/bin/env bash
    set -euo pipefail
    # Rendered starters: website/_site/, word.docx, powerpoint.pptx
    for qmd in *.qmd; do
        stem="${qmd%.qmd}"
        rm -rf "$stem.html" "$stem.docx" "$stem.pptx" "${stem}_files"
    done
    # Website output, Quarto cache, test installs of the extensions, Python and macOS clutter
    rm -rf website/_site website/.quarto .quarto _extensions/PPADEM
    find . -name __pycache__ -type d -prune -not -path "./.git/*" -exec rm -rf {} +
    find . -name .DS_Store -type f -not -path "./.git/*" -delete
    echo "Removed rendered documents and artefacts."
