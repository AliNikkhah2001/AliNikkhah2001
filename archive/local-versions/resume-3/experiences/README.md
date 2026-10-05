# Experiences Pool — Tag-Driven CV

All experiences live **once** in `data/cv.yaml`. The pool `industrial/segments/generated/<variant>/` is auto-generated.

## How to tag
Edit `data/cv.yaml` → `experiences[].variants`:

```yaml
- id: turquoise_senior
  variants: [long, agentic, vision, data, swe, hybrid, senior, platform] # add/remove tags
```

Tags:
- `long` — 10-page union (always true for every experience)
- `agentic`, `vision`, `data`, `swe`, `hybrid`, `senior`, `platform`, `research` — targeted 1/2-page variants
- Remove a tag to exclude that experience from that variant.

## Rebuild
```bash
python scripts/build_tagged.py --variant all        # all variants
python scripts/build_tagged.py --variant vision     # single variant
# then compile latex:
cd industrial && pdflatex main_tagged.tex
# or long union:
cd industrial && pdflatex long_union.tex
```

## Folder map
```
data/cv.yaml                ← SSOT (edit here)
industrial/segments/generated/<variant>/experience.tex  ← auto-generated, do not edit
experiences/pool/*.tex      ← legacy archive (read-only)
industrial/segments/{agentic_ai,...}  ← legacy archive (read-only)
```

## Parallel roles
`concurrent_with` + `concurrent_note` renders as `(Concurrent)` badge + italic note. Gap-free timeline: `data/timeline_gapfree.md`.
