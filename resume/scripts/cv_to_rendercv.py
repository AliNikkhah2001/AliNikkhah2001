#!/usr/bin/env python3
"""Convert data/cv.yaml -> rendercv YAML(s) for dynamic PDF/HTML/JSON generation"""
import yaml, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "cv.yaml"
OUT_DIR = ROOT / "rendercv"
OUT_DIR.mkdir(exist_ok=True)

def load(): return yaml.safe_load(open(SRC))

def to_rendercv_experience(exp):
    return {
        "company": exp["company"],
        "position": exp["role"],
        "start_date": exp["start"],
        "end_date": exp["end"],
        "location": exp["location"] + (f" — {exp['work_model']}" if exp.get("work_model") else ""),
        "summary": exp.get("summary",""),
        "highlights": exp.get("bullets", []) + ([f"Stack: {', '.join(exp['skills'][:6])}"] if exp.get("skills") else []) + ([exp["concurrent_note"]] if exp.get("concurrent_note") else [])
    }

THEMES = ["classic","moderncv","sb2nov","engineeringresumes","engineeringclassic"]
# generate one rendercv file per variant + long union
data = load()
for variant, vinfo in data["variants"].items():
    exps = [e for e in data["experiences"] if variant in e.get("variants", [])]
    exps.sort(key=lambda e: e["start"], reverse=True)
    rc = {
        "cv": {
            "name": data["basics"]["name"],
            "location": data["basics"]["location"].split("·")[0].strip(),
            "email": data["basics"]["email"],
            "phone": data["basics"]["phone"],
            "website": data["basics"]["website"],
            "social_networks": [
                {"network":"LinkedIn","username":"alinikkhah2001"},
                {"network":"GitHub","username":"AliNikkhah2001"},
            ],
            "sections": {
                "education": [
                    {"institution": e["school"], "area": e["credential"], "degree": e["credential"].split("—")[0] if "—" in e["credential"] else e["credential"],
                     "start_date": e["start"], "end_date": e["end"], "location": e["location"],
                     "highlights": ([f"GPA: {e['gpa']}"] if e.get("gpa") else []) + ([f"Thesis: {e['thesis']}"] if e.get("thesis") else []) + ([f"Coursework: {', '.join(e.get('coursework',[]))}"] if e.get("coursework") else [])} for e in data["education"]
                ],
                "experience": [to_rendercv_experience(e) for e in exps],
                "publications": [
                    {"title": p["title"], "authors": p["authors"], "doi": p.get("url",""), "journal": p["venue"], "date": p["year"]}
                    for p in data.get("publications",[])
                ],
                "teaching": [
                    {"name": t["course"], "date": t["period"], "summary": t["role"]} for t in data.get("teaching_history",[])
                ],
                "skills": [f"{k}: {', '.join(v)}" for k,v in data["skills"].items()],
            }
        },
        "design": {
            "theme": "classic",
            "page": {"size":"a4paper","top_margin":"0.55in","bottom_margin":"0.55in","left_margin":"0.6in","right_margin":"0.6in"},
            "colors": {"name":"rgb(0,79,144)","connection":"rgb(0,79,144)","section":"rgb(0,79,144)","link":"rgb(0,79,144)"},
            "text": {"font_family":"Source Sans 3","font_size":"10pt","line_spacing":"1.0"},
            "header": {"name_font_size":"30pt","alignment":"center"},
        }
    }
    out = OUT_DIR / f"Ali_Nikkhah_{variant}.yaml"
    with open(out,"w") as f:
        f.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.3/schema.json\n")
        yaml.dump(rc, f, sort_keys=False, allow_unicode=True)
    print(f"[rendercv] {variant} -> {out} ({len(exps)} exps)")

# also write a README for rendercv usage
(OUT_DIR / "README.md").write_text("""# RenderCV — Dynamic CV Pipeline
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
""")
print("done rendercv conversion")
