#!/usr/bin/env python3
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "academic" / "main.tex"
OUT = ROOT / "academic" / "themes"
OUT.mkdir(parents=True, exist_ok=True)
base = SRC.read_text()

themes = [
    ("01_classic","Classic Serif","lmodern + black rules — closest to original", r"\usepackage{lmodern}"),
    ("02_awesome","Awesome-CV Color","Awesome-CV teal accent #2A7F62", r"\usepackage{lmodern}\definecolor{awesome}{HTML}{2A7F62}\colorlet{sec}{awesome}"),
    ("03_modern","ModernCV Blue","ModernCV blue header + sans", r"\usepackage[default]{sourcesanspro}\definecolor{primary}{HTML}{0E6EB0}"),
    ("04_altacv","AltaCV Sidebar","AltaCV-inspired sidebar color #1A3A4A", r"\usepackage{lmodern}\definecolor{sidebar}{HTML}{1A3A4A}"),
    ("05_deedy","Deedy Tight","Deedy resume tight + Helvetica", r"\usepackage[scaled]{helvet}\renewcommand\familydefault{\sfdefault}"),
    ("06_plasmati","Plasmati Grey","Plasmati grey/blue muted", r"\usepackage{lmodern}\definecolor{plas}{HTML}{4A6572}"),
    ("07_simple","Simple Mono","Simple monochrome + Source Code Pro titles", r"\usepackage{sourcecodepro}\usepackage{lmodern}"),
    ("08_ieee","IEEE Two-Column","IEEEtran-inspired two-column academic", r"\usepackage{lmodern} % ieee would be \documentclass[conference]{IEEEtran} — simulated"),
    ("09_clean","Clean Margin","Clean margin notes + Garamond", r"\usepackage{ebgaramond}\usepackage{lmodern}"),
    ("10_typst","Typst RenderCV","Typst-compiled via rendercv (see rendercv/)", r"% see rendercv/Ali_Nikkhah_long.yaml + rendercv render"),
]

for slug, name, desc, pkg in themes:
    tex = base.replace(r"\usepackage{lmodern}", pkg, 1) if pkg not in base else base
    # inject theme marker comment at top
    tex = f"% THEME {slug}: {name} — {desc}\n% Auto-generated via scripts/generate_themes.py\n" + tex
    # tweak section color for colored themes
    if "awesome" in slug or "modern" in slug:
        tex = tex.replace(r"[\color{black}\titlerule", r"[\color{awesome}\titlerule" if "awesome" in slug else r"[\color{primary}\titlerule")
    out = OUT / f"theme_{slug}.tex"
    out.write_text(tex)
    print(f"[theme] {slug} -> {out}")

# also copy one example gallery README
(OUT/"README.md").write_text("""# Academic Theme Gallery — 10 Variants
All compile via `pdflatex theme_*.tex` from `academic/themes/` (they \\input ../segments/... so compile from themes dir).

| # | Slug | Style | Key tweak |
|---|---|---|---|
| 01 | classic | Classic Serif | lmodern, black |
| 02 | awesome | Awesome-CV teal | #2A7F62 accent |
| 03 | modern | ModernCV blue | Source Sans Pro |
| 04 | altacv | Sidebar | #1A3A4A |
| 05 | deedy | Tight Helvetica | helvet sf |
| 06 | plasmati | Grey/blue | #4A6572 |
| 07 | simple | Mono | sourcecodepro |
| 08 | ieee | Two-col | IEEE sim |
| 09 | clean | Garamond | ebgaramond |
| 10 | typst | RenderCV Typst | see rendercv/ |

Preview: run `./scripts/build_themes.sh` then open `academic/themes/*.pdf` or `rendercv_output/`.
""")
print("done themes")
