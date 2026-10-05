# Ali Nikkhah — consolidated CV workspace

This repository is the working home for all four local CV collections and the GitHub profile.
`data/cv.yaml` is the working master. Conflicting historical dates and wording are preserved for review.

## Start here

- [Ten additional minimal academic templates: source, licenses, PDFs and visual gallery](academic/template-library/README.md)
- [Original ten house themes](academic/themes/README.md)
- [All local source versions, PDFs, checksums and restore instructions](../archive/local-versions/README.md)
- [Content reconciliation notes](data/CONSOLIDATION_REVIEW.md)

The imported library is numbered **11–20** and uses upstream sample content for design comparison.

## Quick start

Run these commands from `resume/`:

```bash
pip install pyyaml rendercv
python scripts/build_tagged.py --variant all    # YAML -> LaTeX fragments + timeline
python scripts/cv_to_rendercv.py               # YAML -> rendercv/*.yaml
python scripts/generate_profile_readme.py       # YAML -> repository-root README.md
python scripts/build_markdown_pdf.py           # markdown -> pandoc PDF themes
rendercv render rendercv/Ali_Nikkhah_long.yaml # Typst PDF/HTML/JSON
```

## Variants (all from one YAML via tags)
`agentic · vision · data · swe · hybrid · senior · platform · research · long`

Variant names describe intended content; current PDF filenames do not enforce a page limit.

## Outputs
- `industrial/long_union.tex/.pdf` — full experience union
- `industrial/segments/generated/<variant>/` — tagged LaTeX
- `rendercv/Ali_Nikkhah_*.yaml` — 9 variants (classic/moderncv/… themes)
- `markdown_resume/resume.md` + `pdf/*.pdf` — 5 pandoc fonts
- `academic/themes/theme_01..10.pdf` — 10 academic LaTeX themes
- `academic/template-library/` — 10 additional licensed upstream templates and compiled previews
- `data/COMBINED_TIMELINE.md` — gap-free timeline w/ parallel roles

## Synchronization

Use this repository for future edits. The four original local folders are historical snapshots.
Their complete document contents are recoverable from the archive manifest; repeated files are stored once.
The archive verifier checks all 283 source-file mappings against SHA-256 hashes.

The profile generator writes to the root `README.md`. Website YAML export is opt-in:
`python scripts/build_tagged.py --variant all --jekyll-data /path/to/site/_data/cv_generated.yaml`.

## CI

- `.github/workflows/build-cv.yml`: working CV generation and PDF builds.
- `.github/workflows/build-gallery.yml`: original house theme gallery.
- `.github/workflows/template-library.yml`: archive integrity and all ten added template builds.

Workflow paths are relative to the repository root.
