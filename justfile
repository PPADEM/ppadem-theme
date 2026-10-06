# Tasks for the PPADEM Quarto theme. Run `just` to list them.

# List the available recipes
default:
    @{{just_executable()}} --list

# Remove rendered documents and build artefacts
cls:
    #!/usr/bin/env bash
    set -euo pipefail
    # Rendered starters: website.html, brief.pdf, word.docx, slides_files/, ...
    for qmd in *.qmd; do
        stem="${qmd%.qmd}"
        rm -rf "$stem.html" "$stem.pdf" "$stem.docx" "$stem.pptx" "$stem.typ" "${stem}_files"
    done
    # Copied next to the brief when it renders (the root logo.png is tracked; keep it)
    rm -f eu-logo.png
    # Quarto cache, test installs of the extensions, Python and macOS clutter
    rm -rf .quarto _extensions/PPADEM
    find . -name __pycache__ -type d -prune -not -path "./.git/*" -exec rm -rf {} +
    find . -name .DS_Store -type f -not -path "./.git/*" -delete
    echo "Removed rendered documents and artefacts."
