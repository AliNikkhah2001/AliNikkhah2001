"""Import pipeline: cv.yaml -> CareerDatabase."""
from __future__ import annotations

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from models import (
    CareerDatabase, Organization, Position, Project, Education,
    Publication, Teaching, Skill, Achievement, Profile, Variant,
    DatePrecision
)


def load_cv_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


import re

def parse_date(s: str) -> DatePrecision:
    if s == "present":
        return DatePrecision(year=9999)
    if not s:
        return DatePrecision(year=2020)
    # Try YYYY-MM or YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}", s):
        parts = s.split("-")
        return DatePrecision(year=int(parts[0]), month=int(parts[1]) if len(parts) > 1 else None)
    # Try "Month YYYY" or "Mon YYYY"
    month_map = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12,
    }
    parts = s.strip().split()
    if len(parts) >= 2:
        mon = parts[0].lower()[:3]
        if mon in month_map and parts[1].isdigit():
            return DatePrecision(year=int(parts[1]), month=month_map[mon])
    # Fallback
    if s.isdigit():
        return DatePrecision(year=int(s))
    return DatePrecision(year=2020)


def build_database(cv_data: dict) -> CareerDatabase:
    org_map: dict[str, Organization] = {}
    org_counter = 0

    def get_org_id(name: str, org_type: str = "employer") -> str:
        nonlocal org_counter
        for oid, org in org_map.items():
            if org.name.lower() == name.lower():
                return oid
        org_counter += 1
        oid = f"org_{org_counter:03d}"
        org_map[oid] = Organization(id=oid, name=name, type=org_type)
        return oid

    # Profile
    basics = cv_data["basics"]
    profile = Profile(
        name=basics["name"],
        headline=basics["label"],
        email=basics["email"],
        phone=basics.get("phone"),
        location=basics["location"],
        website=basics.get("website"),
        linkedin=basics.get("linkedin"),
        github=basics.get("github"),
        summary=basics["summary"],
        summary_brief=basics["summary"][:200] + "…" if len(basics["summary"]) > 200 else basics["summary"],
        summary_detailed=basics["summary"],
    )

    # Skills
    skills = []
    cat_map = {
        "languages": "language",
        "ml_vision": "ml_vision",
        "agentic": "agentic",
        "llm_serving": "llm_serving",
        "data_mlop": "data_mlop",
        "human": "human",
    }
    for cat, items in cv_data.get("skills", {}).items():
        for item in items:
            skills.append(Skill(name=item, category=cat_map.get(cat, "language")))

    # Organizations, Positions, Achievements
    positions = []
    achievements = []
    achievement_id_map: dict[str, str] = {}  # bullet text -> achievement id

    for exp in cv_data.get("experiences", []):
        org_id = get_org_id(exp["company"])
        pos_id = f"pos_{exp['id']}"

        # Create achievements from bullets
        pos_achievements = []
        for bullet in exp.get("bullets", []):
            ach_id = f"ach_{exp['id']}_{len(pos_achievements)}"
            achievement = Achievement(
                id=ach_id,
                position_id=pos_id,
                text=bullet,
                skills=exp.get("skills", []),
                source_refs=[exp["id"]],
                verified=True,
            )
            achievements.append(achievement)
            pos_achievements.append(ach_id)
            achievement_id_map[bullet] = ach_id

        # Also create achievements from research_projects if linked
        for rp in cv_data.get("research_projects", []):
            if rp.get("id") in exp.get("concurrent_with", []):
                for bullet in rp.get("bullets", []):
                    ach_id = f"ach_rp_{rp['id']}_{len(pos_achievements)}"
                    achievement = Achievement(
                        id=ach_id,
                        project_id=rp["id"],
                        text=bullet,
                        source_refs=[rp["id"]],
                        verified=True,
                    )
                    achievements.append(achievement)
                    pos_achievements.append(ach_id)

        position = Position(
            id=pos_id,
            organization_id=org_id,
            title=exp["role"],
            start=parse_date(exp["start"]),
            end=parse_date(exp["end"]) if exp["end"] != "present" else None,
            ongoing=exp["end"] == "present",
            employment_type="full_time" if exp.get("work_model", "").startswith("Full-time") else "part_time",
            location=exp.get("location"),
            remote="Remote" in exp.get("work_model", ""),
            work_model=exp.get("work_model"),
            summary=exp.get("summary"),
            achievements=pos_achievements,
            concurrent_with=exp.get("concurrent_with", []),
            concurrent_note=exp.get("concurrent_note"),
        )
        positions.append(position)

    # Projects
    projects = []
    for rp in cv_data.get("research_projects", []):
        org_id = get_org_id(rp.get("org", ""), "research_lab")
        project = Project(
            id=rp["id"],
            title=rp["title"],
            organization_id=org_id,
            start=parse_date(rp["period"].split("–")[0].strip()) if "period" in rp else DatePrecision(year=2020),
            end=parse_date(rp["period"].split("–")[1].strip()) if "period" in rp and "–" in rp["period"] else None,
            summary=rp.get("title"),
            description="\n".join(rp.get("bullets", [])),
            skills=[],
        )
        projects.append(project)

    # Education
    education = []
    for ed in cv_data.get("education", []):
        org_id = get_org_id(ed["school"], "university")
        edu_id = ed["id"]
        education.append(Education(
            id=edu_id,
            organization_id=org_id,
            degree=ed["credential"],
            field=ed.get("coursework", [None])[0] if ed.get("coursework") else None,
            start=parse_date(ed["start"]),
            end=parse_date(ed["end"]) if ed["end"] != "present" else None,
            ongoing=ed["end"] == "present",
            gpa=ed.get("gpa"),
            thesis=ed.get("thesis"),
            coursework=ed.get("coursework", []),
        ))

    # Publications
    publications = []
    for pub in cv_data.get("publications", []):
        publications.append(Publication(
            id=pub["id"],
            title=pub["title"],
            authors=[a.strip() for a in pub["authors"].split(",")],
            venue=pub["venue"],
            year=pub["year"],
            url=pub.get("url"),
            status="preprint" if "preprint" in pub["venue"].lower() else "published",
        ))

    # Teaching
    teaching = []
    for t in cv_data.get("teaching_history", []):
        org_id = get_org_id("Sharif University of Technology", "university")
        teaching.append(Teaching(
            id=f"teach_{len(teaching)}",
            course=t["course"],
            role=t["role"],
            organization_id=org_id,
            period=t["period"],
        ))

    # Variants from cv.yaml
    variants = []
    for vid, vinfo in cv_data.get("variants", {}).items():
        # Select positions that have this variant tag
        pos_ids = [
            f"pos_{exp['id']}"
            for exp in cv_data.get("experiences", [])
            if vid in exp.get("variants", []) or (vid == "long" and "long" in exp.get("variants", []))
        ]
        variants.append(Variant(
            id=vid,
            label=vinfo["label"],
            audience="academic" if vid == "research" else "industry",
            length_target="10page" if vid == "long" else f"{vinfo['pages']}page",
            template="academic" if vid == "research" else "industrial",
            sections=[],
            position_ids=pos_ids,
            wording_level="standard",
            page_limit=vinfo["pages"],
        ))

    return CareerDatabase(
        schema_version=1,
        profile=profile,
        organizations=list(org_map.values()),
        positions=positions,
        projects=projects,
        education=education,
        publications=publications,
        teaching=teaching,
        skills=skills,
        achievements=achievements,
        variants=variants,
    )


def main():
    cv_path = Path(__file__).resolve().parents[2] / "resume" / "data" / "cv.yaml"
    cv_data = load_cv_yaml(cv_path)
    db = build_database(cv_data)

    out_path = Path(__file__).resolve().parents[1] / "career_db.json"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(db.model_dump_json(indent=2, exclude_none=True))
    print(f"Imported {len(db.organizations)} orgs, {len(db.positions)} positions, {len(db.achievements)} achievements")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()