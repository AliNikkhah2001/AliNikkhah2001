#!/usr/bin/env python3
"""Generate profile README.md for AliNikkhah2001/AliNikkhah2001 from career_db.json.

Single source of truth is career-dashboard/career_db.json (edited via the
dashboard). Importable as `generate_readme(db_dict)` so the API
(GET /api/export/github-readme) serves byte-identical content.

--check : compare only, exit 0 if in sync, 1 if drifted/missing (no write)
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
DB_PATH = REPO / "career-dashboard" / "career_db.json"
OUT_PATH = REPO / "README.md"

CAT_LABELS = {
    "language": "Programming",
    "ml_vision": "ML & Vision",
    "agentic": "Agentic AI & RAG",
    "llm_serving": "LLM Serving & GPU",
    "data_mlop": "Data & MLOps",
    "human": "Languages",
}


def _fmt(d):
    if not d or d.get("year") in (None, 9999):
        return ""
    if d.get("month"):
        return f"{d['year']}-{d['month']:02d}"
    return str(d["year"])


def _end(item):
    if item.get("ongoing"):
        return "Present"
    return _fmt(item.get("end")) or "Present"


def generate_readme(db: dict) -> str:
    """Render the profile README markdown from a career_db dict."""
    profile = db.get("profile", {})
    orgs = {o["id"]: o.get("name", "Unknown") for o in db.get("organizations", [])}

    def org_name(oid):
        return orgs.get(oid, "Unknown")

    positions = sorted(
        db.get("positions", []),
        key=lambda p: ((p.get("start") or {}).get("year", 0), ((p.get("start") or {}).get("month") or 0)),
        reverse=True,
    )
    rows = [
        f"| {_fmt(p.get('start'))} – {_end(p)} | {p.get('title', '')} | {org_name(p.get('organization_id'))} |"
        for p in positions
    ]

    edu = []
    for e in db.get("education", []):
        line = f"- **{e.get('degree', '')}** — {org_name(e.get('organization_id'))} *({_fmt(e.get('start'))} – {_end(e)})*"
        if e.get("gpa"):
            line += f"<br>\n  GPA {e['gpa']}"
        if e.get("thesis"):
            line += f"<br>\n  Research: {e['thesis']}"
        edu.append(line)

    skills_by_cat: dict[str, list[str]] = {}
    for s in db.get("skills", []):
        label = CAT_LABELS.get(s.get("category", ""), s.get("category", ""))
        skills_by_cat.setdefault(label, []).append(s.get("name", ""))
    stack = [f"**{cat}** · {', '.join(names)}" for cat, names in skills_by_cat.items()]

    projects = []
    for p in db.get("projects", []):
        period = f"{_fmt(p.get('start'))} – {_end(p)}".strip(" –")
        org = org_name(p.get("organization_id")) if p.get("organization_id") else ""
        projects.append(f"- **{p.get('title', '')}** — {org} ({period})".rstrip())

    pubs = "\n".join(
        f"- *{p.get('title', '')}* — {p.get('venue', '')} ({p.get('year', '')})"
        for p in db.get("publications", [])
    )

    website = profile.get("website", "")
    linkedin = profile.get("linkedin", "https://linkedin.com/in/alinikkhah2001")
    github = profile.get("github", "https://github.com/AliNikkhah2001")
    email = profile.get("email", "")

    return f'''<div align="center">

# Ali Nikkhah 🧠⚙️

**{profile.get("headline", "")}** — {profile.get("location", "")}

[![Website](https://img.shields.io/badge/website-alinikkhah2001.github.io-0e6eb0?style=flat-square&logo=github)]({website})
[![LinkedIn](https://img.shields.io/badge/linkedin-alinikkhah2001-0A66C2?style=flat-square&logo=linkedin)]({linkedin})
[![GitHub](https://img.shields.io/badge/github-AliNikkhah2001-181717?style=flat-square&logo=github)]({github})
[![Email](https://img.shields.io/badge/email-{email}-EA4335?style=flat-square&logo=gmail)](mailto:{email})

</div>

> {profile.get("summary", "")}

---

## 🎓 Education

{chr(10).join(edu)}

## 💼 Experience

| Period | Role | Organisation |
|--------|------|--------------|
{chr(10).join(rows)}

## 🛠️ Stack

{chr(10).join(stack)}

## 🧪 Research & Projects

{chr(10).join(projects)}

## 📚 Publications

{pubs}

## 📝 Latest Writing — [loss.backward()]({website}/loss-backward/)

Field notes on shipping applied AI/ML systems.

---

## CV workspace

- [Working CV sources and build instructions](resume/README.md)
- [Ten additional minimal academic LaTeX templates](resume/academic/template-library/README.md)
- [Consolidated local versions and content manifest](archive/local-versions/README.md)

<sub>Auto-generated from `career-dashboard/career_db.json` (single source of truth).</sub>
'''


def main() -> None:
    db = json.loads(DB_PATH.read_text(encoding="utf-8"))
    readme = generate_readme(db)
    if "--check" in sys.argv:
        current = OUT_PATH.read_text() if OUT_PATH.exists() else None
        if current == readme:
            print("in_sync")
            sys.exit(0)
        print("drift" if current is not None else "missing")
        sys.exit(1)
    OUT_PATH.write_text(readme)
    print("profile README regenerated ->", OUT_PATH)


if __name__ == "__main__":
    main()
