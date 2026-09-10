#!/usr/bin/env python3
"""Convert data/cv.yaml -> rendercv YAML(s) (RenderCV v2 schema) for PDF/HTML/JSON generation"""
import yaml
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "cv.yaml"
OUT_DIR = ROOT / "rendercv"
OUT_DIR.mkdir(exist_ok=True)


def load():
    with open(SRC, encoding="utf-8") as f:
        return yaml.safe_load(f)


SKILL_LABELS = {
    "languages": "Programming",
    "ml_vision": "ML & Vision",
    "agentic": "Agentic AI & RAG",
    "llm_serving": "LLM Serving & GPU",
    "data_mlop": "Data & MLOps",
    "human": "Languages",
}


def to_rendercv_experience(exp):
    return {
        "company": exp["company"],
        "position": exp["role"],
        "start_date": exp["start"],
        "end_date": exp["end"],
        "location": exp["location"] + (f" — {exp['work_model']}" if exp.get("work_model") else ""),
        "summary": exp.get("summary", ""),
        "highlights": exp.get("bullets", [])
        + ([f"Stack: {', '.join(exp['skills'][:6])}"] if exp.get("skills") else [])
        + ([exp["concurrent_note"]] if exp.get("concurrent_note") else []),
    }


def to_rendercv_education(e):
    return {
        "institution": e["school"],
        "area": e["credential"],
        "degree": e["credential"],
        "start_date": e["start"],
        "end_date": e["end"],
        "location": e["location"],
        "highlights": ([f"GPA: {e['gpa']}"] if e.get("gpa") else [])
        + ([f"Thesis: {e['thesis']}"] if e.get("thesis") else [])
        + ([e["program"]] if e.get("program") else [])
        + ([f"Coursework: {', '.join(e.get('coursework', []))}"] if e.get("coursework") else []),
    }


data = load()
for variant, vinfo in data["variants"].items():
    exps = [e for e in data["experiences"] if variant in e.get("variants", [])]
    exps.sort(key=lambda e: e["start"], reverse=True)
    pub = data.get("publications", [])
    rc = {
        "cv": {
            "name": data["basics"]["name"],
            "headline": data["basics"]["label"],
            "location": data["basics"]["location"],
            "email": data["basics"]["email"],
            "phone": data["basics"]["phone"],
            "website": data["basics"]["website"],
            "social_networks": [
                {"network": "LinkedIn", "username": "alinikkhah2001"},
                {"network": "GitHub", "username": "AliNikkhah2001"},
            ],
            "sections": {
                "summary": [data["basics"]["summary"]],
                "education": [to_rendercv_education(e) for e in data["education"]],
                "experience": [to_rendercv_experience(e) for e in exps],
                "publications": [
                    {
                        "title": p["title"],
                        "authors": [a.strip() for a in p["authors"].split(",")],
                        "journal": p["venue"],
                        "date": str(p["year"]),
                    }
                    for p in pub
                ],
                "teaching": [
                    {"name": t["course"], "summary": f"{t['role']} ({t['period']})"}
                    for t in data.get("teaching_history", [])
                ],
                "skills": [
                    {"label": SKILL_LABELS.get(k, k), "details": ", ".join(v)}
                    for k, v in data["skills"].items()
                ],
            },
        },
        "design": {"theme": "classic"},
    }
    out = OUT_DIR / f"Ali_Nikkhah_{variant}.yaml"
    with open(out, "w", encoding="utf-8") as f:
        f.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json\n")
        yaml.dump(rc, f, sort_keys=False, allow_unicode=True)
    print(f"[rendercv] {variant} -> {out} ({len(exps)} exps)")

# also write a README for rendercv usage
(OUT_DIR / "README.md").write_text(
    """# RenderCV — Dynamic CV Pipeline
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
""",
    encoding="utf-8",
)
print("done rendercv conversion")
