#!/usr/bin/env python3
"""Generate profile README.md for AliNikkhah2001/AliNikkhah2001 from data/cv.yaml"""
import yaml, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
d = yaml.safe_load(open(ROOT/"data"/"cv.yaml"))
b = d["basics"]

rows = []
for e in sorted(d["experiences"], key=lambda x: x["start"], reverse=True):
    end = "Present" if e["end"]=="present" else e["end"]
    rows.append(f"| {e['start']} – {end} | {e['role']} | {e['company']} |")

edu = []
for e in d["education"]:
    end = "Present" if e["end"]=="present" else e["end"]
    line = f"- **{e['credential']}** — {e['school']} *({e['start']} – {end})*"
    if e.get("gpa"): line += f"  \n  GPA {e['gpa']}"
    if e.get("thesis"): line += f"  \n  Research: {e['thesis']}"
    edu.append(line)

sk = d["skills"]
pubs = "\n".join(f"- *{p['title']}* — {p['venue']} ({p['year']})" for p in d.get("publications",[]))

readme = f'''<div align="center">

# Ali Nikkhah 🧠⚙️

**{b["label"]}** — {b["location"]}

[![Website](https://img.shields.io/badge/website-alinikkhah2001.github.io-0e6eb0?style=flat-square&logo=github)]({b["website"]})
[![LinkedIn](https://img.shields.io/badge/linkedin-alinikkhah2001-0A66C2?style=flat-square&logo=linkedin)]({b["linkedin"]})
[![GitHub](https://img.shields.io/badge/github-AliNikkhah2001-181717?style=flat-square&logo=github)]({b["github"]})
[![Email](https://img.shields.io/badge/email-{b["email"]}-EA4335?style=flat-square&logo=gmail)](mailto:{b["email"]})

</div>

> {b["summary"]}

---

## 🎓 Education

{chr(10).join(edu)}

## 💼 Experience

| Period | Role | Organisation |
|--------|------|--------------|
{chr(10).join(rows)}

## 🛠️ Stack

{chr(10).join(f"**{k.replace('_',' ').title()}** · {', '.join(v)}" for k,v in sk.items())}

## 🧪 Research & Projects

{chr(10).join(f"- **{p['title']}** — {p.get('org','')} ({p.get('period','')})" for p in d.get('research_projects',[]))}

## 📚 Publications

{pubs}

## 📝 Latest Writing — [loss.backward()]({b["website"]}/loss-backward/)

Field notes on shipping applied AI/ML systems.

---

<sub>Auto-generated from `data/cv.yaml` (single source of truth).</sub>
'''
out = ROOT.parents[1] / "README.md"
out.write_text(readme)
print("profile README regenerated ->", out)
