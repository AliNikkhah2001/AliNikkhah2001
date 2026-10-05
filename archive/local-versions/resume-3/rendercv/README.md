# RenderCV — Dynamic CV Pipeline
Single source `data/cv.yaml` -> rendercv YAMLs per variant (classic theme).

## Build (requires `pip install rendercv` + Typst)
```bash
rendercv render rendercv/Ali_Nikkhah_long.yaml        # -> rendercv_output/
rendercv render rendercv/Ali_Nikkhah_agentic.yaml
# HTML + PDF + Markdown + PNG via same YAML
```

## GitHub Pages
`.github/workflows/rendercv.yml` (see below) renders on push and deploys PDFs + HTML to `gh-pages`.

## Themes
Change `design.theme` in YAML: classic | moderncv | sb2nov | engineeringresumes | engineeringclassic
Or `rendercv create-theme mytheme --based-on classic` to fork.
