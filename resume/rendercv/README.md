# RenderCV — Dynamic CV Pipeline
Single source `data/cv.yaml` -> rendercv YAMLs per variant (classic theme, RenderCV v2 schema).

## Regenerate inputs
```bash
python scripts/build_tagged.py --variant all
python scripts/cv_to_rendercv.py
```

## Build (requires `pip install "rendercv[full]"`)
```bash
cd resume/rendercv
rendercv render Ali_Nikkhah_long.yaml -o rendercv_output/long
# PDF + HTML + Markdown + PNG + Typst per variant
```

## GitHub Pages
`.github/workflows/rendercv.yml` renders on push and deploys to `gh-pages`.

## Themes
Change `design.theme`: classic | moderncv | sb2nov | engineeringresumes | engineeringclassic
