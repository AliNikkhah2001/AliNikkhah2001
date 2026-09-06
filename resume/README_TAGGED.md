# Unified Tagged CV — How It Works

## SSOT: `data/cv.yaml`
Every experience lives once. Edit there.

```yaml
- id: turquoise_senior
  variants: [long, agentic, vision, data, swe, hybrid, senior, platform]
  # remove a tag to hide from that variant
```

Run:

```bash
python scripts/build_tagged.py --variant all   # rebuilds industrial/segments/generated/*/ + long_union.tex + timeline
python scripts/cv_to_rendercv.py              # rebuilds rendercv/*.yaml
python scripts/generate_timeline.py           # COMBINED_TIMELINE.md + gap check
```

## Variants

| Variant flag / SSOT key | PDF | Tags | Pages |
|---|---|---|---|
| `long` | `industrial/long_union.pdf` | all | 3 (union, expand to 10 with verbose bullets) |
| `agentic` | `generated/agentic/experience.tex` | agentic | 2 |
| `vision` | `generated/vision/...` | vision | 2 |
| `data` | `generated/data/...` | data | 2 |
| `swe` | `generated/swe/...` | swe | 2 |
| `hybrid` | `generated/hybrid/...` | hybrid | 2 |
| `senior` | `generated/senior/...` | senior | 2 |
| `platform` | `generated/platform/...` | platform | 2 |
| `research` | academic + generated/research | research | 4 |

Legacy `industrial/main.tex` still works via `isAgentic` booleans. New `industrial/main_tagged.tex` uses `\cvvariant`.

## RenderCV (open-source dynamic pipeline)
`pip install rendercv && python scripts/cv_to_rendercv.py`

```
rendercv/Ali_Nikkhah_long.yaml  → rendercv render rendercv/Ali_Nikkhah_long.yaml
  → rendercv_output/Ali_Nikkhah_long.pdf + .html + .md + .png (Typst)
```

Themes: `design.theme: classic | moderncv | sb2nov | engineeringresumes | engineeringclassic`  
Custom theme: `rendercv create-theme mytheme --based-on classic`

GitHub Action: `.github/workflows/rendercv.yml` (builds on push).

## Gap-free Timeline
`data/COMBINED_TIMELINE.md` — auto-generated swimlanes, variant inclusion matrix, concurrency notes `(Concurrent)` in LaTeX.

No unexplained gaps: education covers 2022-02→2023-04; all overlaps annotated.

## 10 Academic Themes
`academic/themes/theme_*.tex` + `build_all.sh` → 10 PDFs:

- 01 classic, 02 awesome (teal), 03 modern (blue), 04 altacv, 05 deedy, 06 plasmati, 07 simple, 08 ieee, 09 clean (Garamond), 10 typst

Compile: `cd academic/themes && bash build_all.sh`

## Experiences Pool
`experiences/pool/<id>.tex` — one file per experience, header comment shows tags. Manual edits → sync back to `data/cv.yaml`.

## Jekyll Sync
`scripts/build_tagged.py` copies `data/cv.yaml` → `alinikkhah2001.github.io/_data/cv_generated.yaml` for site dynamic rendering.
