# Ali Nikkhah — CV (Single Source of Truth)

Full CV source: `data/cv.yaml` → LaTeX + RenderCV (Typst) + Markdown + GitHub Pages JSON.

## Quick start
```bash
pip install pyyaml rendercv
python scripts/build_tagged.py --variant all    # YAML -> LaTeX fragments + timeline
python scripts/cv_to_rendercv.py               # YAML -> rendercv/*.yaml
python scripts/build_markdown_pdf.py           # markdown -> pandoc PDF themes
rendercv render rendercv/Ali_Nikkhah_long.yaml # Typst PDF/HTML/JSON
```

## Variants (all from one YAML via tags)
`agentic · vision · data · swe · hybrid · senior · platform · research · long (union 10pg)`

## Outputs
- `industrial/long_union.tex/.pdf` — union 10-page
- `industrial/segments/generated/<variant>/` — tagged LaTeX
- `rendercv/Ali_Nikkhah_*.yaml` — 9 variants (classic/moderncv/… themes)
- `markdown_resume/resume.md` + `pdf/*.pdf` — 5 pandoc fonts
- `academic/themes/theme_01..10.pdf` — 10 academic LaTeX themes
- `data/COMBINED_TIMELINE.md` — gap-free timeline w/ parallel roles

## CI
`.github/workflows/rendercv.yml` builds on every push → gh-pages CV gallery.
