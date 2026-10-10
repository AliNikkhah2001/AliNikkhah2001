"""Pydantic models for career database and export formats."""
from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class DatePrecision(BaseModel):
    """Date with optional month/day precision."""
    year: int
    month: Optional[int] = None
    day: Optional[int] = None

    def to_iso(self) -> str:
        if self.month and self.day:
            return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
        if self.month:
            return f"{self.year:04d}-{self.month:02d}"
        return str(self.year)

    @classmethod
    def from_iso(cls, s: str) -> DatePrecision:
        parts = s.split("-")
        return cls(year=int(parts[0]), month=int(parts[1]) if len(parts) > 1 else None, day=int(parts[2]) if len(parts) > 2 else None)

    @classmethod
    def from_cv_yaml(cls, s: str) -> DatePrecision:
        """Parse YYYY-MM or YYYY-MM-DD or 'present'."""
        if s == "present":
            return cls(year=9999, month=None, day=None)
        return cls.from_iso(s)


class Organization(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str
    aliases: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    type: Literal["employer", "university", "research_lab", "other"] = "employer"

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    position_id: Optional[str] = None
    project_id: Optional[str] = None
    text: str
    brief_text: Optional[str] = None
    detailed_text: Optional[str] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    verified: bool = False

    @model_validator(mode="after")
    def ensure_fallbacks(self) -> Achievement:
        if self.brief_text is None:
            self.brief_text = self.text[:160] + ("…" if len(self.text) > 160 else "")
        if self.detailed_text is None:
            self.detailed_text = self.text
        return self


class Position(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    organization_id: str
    title: str
    start: DatePrecision
    end: Optional[DatePrecision] = None
    ongoing: bool = False
    employment_type: Literal["full_time", "part_time", "contract", "internship", "fellowship"] = "full_time"
    location: Optional[str] = None
    remote: bool = False
    work_model: Optional[str] = None
    summary: Optional[str] = None
    description_md: Optional[str] = None
    tech_stack: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    promotion_of: Optional[str] = None
    concurrent_with: list[str] = Field(default_factory=list)
    concurrent_note: Optional[str] = None

    @model_validator(mode="after")
    def sync_ongoing(self) -> Position:
        if self.ongoing and self.end is None:
            self.end = DatePrecision(year=9999)
        return self


class Project(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    title: str
    organization_id: Optional[str] = None
    start: DatePrecision
    end: Optional[DatePrecision] = None
    ongoing: bool = False
    summary: Optional[str] = None
    description: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    position_ids: list[str] = Field(default_factory=list)
    url: Optional[str] = None


class Education(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    organization_id: str
    degree: str
    field: Optional[str] = None
    start: DatePrecision
    end: Optional[DatePrecision] = None
    ongoing: bool = False
    gpa: Optional[str] = None
    thesis: Optional[str] = None
    coursework: list[str] = Field(default_factory=list)


class Publication(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    title: str
    authors: list[str] = Field(default_factory=list)
    venue: Optional[str] = None
    year: int
    url: Optional[str] = None
    status: Literal["published", "preprint", "in_preparation", "under_review"] = "preprint"


class Teaching(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    course: str
    role: str
    organization_id: Optional[str] = None
    period: str
    students: Optional[int] = None


class Skill(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str
    category: Literal["language", "ml_vision", "agentic", "llm_serving", "data_mlop", "human"] = "language"
    proficiency: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)


class Profile(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str
    headline: str
    email: str
    phone: Optional[str] = None
    location: str
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: str
    summary_brief: Optional[str] = None
    summary_detailed: Optional[str] = None


class Variant(BaseModel):
    id: str
    label: str
    audience: Literal["academic", "industry", "research", "general"]
    length_target: Literal["1page", "2page", "4page", "10page"]
    template: str
    sections: list[str] = Field(default_factory=list)
    position_ids: list[str] = Field(default_factory=list)
    achievement_overrides: dict[str, str] = Field(default_factory=dict)
    wording_level: Literal["brief", "standard", "detailed"] = "standard"
    page_limit: int = 2


class CareerDatabase(BaseModel):
    schema_version: int = 1
    profile: Profile
    organizations: list[Organization] = Field(default_factory=list)
    positions: list[Position] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    teaching: list[Teaching] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    variants: list[Variant] = Field(default_factory=list)

    def get_organization(self, org_id: str) -> Optional[Organization]:
        return next((o for o in self.organizations if o.id == org_id), None)

    def get_position(self, pos_id: str) -> Optional[Position]:
        return next((p for p in self.positions if p.id == pos_id), None)

    def get_achievement(self, ach_id: str) -> Optional[Achievement]:
        return next((a for a in self.achievements if a.id == ach_id), None)

    def positions_by_date(self, reverse: bool = True) -> list[Position]:
        def sort_key(p: Position):
            y = p.start.year
            m = p.start.month or 1
            return (y, m)
        return sorted(self.positions, key=sort_key, reverse=reverse)

    def to_json_resume(self) -> dict:
        """Export to JSON Resume format."""
        org_map = {o.id: o for o in self.organizations}
        ach_map = {a.id: a for a in self.achievements}
        pos_map = {p.id: p for p in self.positions}
        edu_map = {e.id: e for e in self.education}

        work = []
        for p in self.positions:
            org = org_map.get(p.organization_id)
            work.append({
                "name": org.name if org else "Unknown",
                "location": p.location or "",
                "description": p.summary or "",
                "position": p.title,
                "startDate": p.start.to_iso() if p.start.year != 9999 else "",
                "endDate": p.end.to_iso() if p.end and p.end.year != 9999 else "",
                "summary": p.summary or "",
                "highlights": [
                    ach_map[aid].text
                    for aid in p.achievements
                    if ach_map.get(aid)
                ],
                "url": org.url if org else "",
            })

        education = []
        for e in self.education:
            org = org_map.get(e.organization_id)
            education.append({
                "institution": org.name if org else "Unknown",
                "url": org.url if org else "",
                "area": e.field or "",
                "studyType": e.degree,
                "startDate": e.start.to_iso(),
                "endDate": e.end.to_iso() if e.end and e.end.year != 9999 else "",
                "score": e.gpa or "",
                "courses": e.coursework,
            })

        skills = []
        cat_map = {
            "language": "Programming",
            "ml_vision": "ML & Vision",
            "agentic": "Agentic AI & RAG",
            "llm_serving": "LLM Serving & GPU",
            "data_mlop": "Data & MLOps",
            "human": "Languages",
        }
        for s in self.skills:
            skills.append({
                "name": cat_map.get(s.category, s.category),
                "level": s.proficiency or "Proficient",
                "keywords": [s.name] + s.aliases,
            })

        return {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": self.profile.name,
                "label": self.profile.headline,
                "image": "",
                "email": self.profile.email,
                "phone": self.profile.phone or "",
                "url": self.profile.website or "",
                "summary": self.profile.summary,
                "location": {
                    "address": "",
                    "postalCode": "",
                    "city": self.profile.location.split("·")[0].strip() if "·" in self.profile.location else self.profile.location,
                    "countryCode": "IR",
                    "region": "",
                },
                "profiles": [
                    {"network": "LinkedIn", "username": "alinikkhah2001", "url": self.profile.linkedin or "https://linkedin.com/in/alinikkhah2001"},
                    {"network": "GitHub", "username": "AliNikkhah2001", "url": self.profile.github or "https://github.com/AliNikkhah2001"},
                ],
            },
            "work": work,
            "education": education,
            "skills": skills,
            "projects": [
                {
                    "name": pr.title,
                    "description": pr.description or "",
                    "highlights": [ach_map[aid].text for aid in pr.achievements if ach_map.get(aid)],
                    "keywords": pr.skills,
                    "startDate": pr.start.to_iso(),
                    "endDate": pr.end.to_iso() if pr.end and pr.end.year != 9999 else "",
                    "url": pr.url or "",
                    "roles": [],
                    "entity": "",
                    "type": "",
                }
                for pr in self.projects
            ],
            "publications": [
                {
                    "name": pub.title,
                    "publisher": pub.venue or "",
                    "releaseDate": f"{pub.year}-01-01",
                    "url": pub.url or "",
                    "summary": "",
                }
                for pub in self.publications
            ],
            "volunteer": [],
            "awards": [],
            "certificates": [],
            "languages": [
                {"language": s.name, "fluency": s.proficiency or "Professional"}
                for s in self.skills if s.category == "human"
            ],
            "interests": [],
            "references": [],
            "meta": {
                "canonical": self.profile.website or "",
                "version": "1.0.0",
                "lastModified": date.today().isoformat(),
            },
        }

    def to_rendercv(self, variant_id: str) -> dict:
        """Export to RenderCV YAML for a specific variant."""
        variant = next((v for v in self.variants if v.id == variant_id), None)
        if not variant:
            raise ValueError(f"Variant {variant_id} not found")

        org_map = {o.id: o for o in self.organizations}
        pos_map = {p.id: p for p in self.positions}
        edu_map = {e.id: e for e in self.education}
        ach_map = {a.id: a for a in self.achievements}

        selected_positions = [pos_map[pid] for pid in variant.position_ids if pid in pos_map]

        experience = []
        for p in selected_positions:
            org = org_map.get(p.organization_id)
            highlights = []
            for aid in p.achievements:
                ach = ach_map.get(aid)
                if ach:
                    text = variant.wording_level == "brief" and ach.brief_text or ach.detailed_text
                    highlights.append(text or ach.text)
            experience.append({
                "company": org.name if org else "Unknown",
                "position": p.title,
                "start_date": p.start.to_iso().replace("-01", "") if p.start.month else str(p.start.year),
                "end_date": "present" if p.ongoing else (p.end.to_iso().replace("-01", "") if p.end and p.end.month else str(p.end.year) if p.end else ""),
                "location": f"{p.location or ''} — {p.work_model or ''}".strip(" —"),
                "summary": p.summary or "",
                "highlights": highlights,
            })

        education = []
        for e in self.education:
            org = org_map.get(e.organization_id)
            education.append({
                "institution": org.name if org else "Unknown",
                "area": e.degree,
                "degree": e.degree,
                "start_date": e.start.to_iso().replace("-01", "") if e.start.month else str(e.start.year),
                "end_date": "present" if e.ongoing else (e.end.to_iso().replace("-01", "") if e.end and e.end.month else str(e.end.year) if e.end else ""),
                "location": e.organization_id and org_map.get(e.organization_id) and org_map[e.organization_id].name or "",
                "highlights": (
                    ([f"GPA: {e.gpa}"] if e.gpa else [])
                    + ([f"Thesis: {e.thesis}"] if e.thesis else [])
                    + ([f"Coursework: {', '.join(e.coursework)}"] if e.coursework else [])
                ),
            })

        skills_dict = {}
        for s in self.skills:
            cat = {
                "language": "Programming",
                "ml_vision": "ML & Vision",
                "agentic": "Agentic AI & RAG",
                "llm_serving": "LLM Serving & GPU",
                "data_mlop": "Data & MLOps",
                "human": "Languages",
            }.get(s.category, s.category)
            skills_dict.setdefault(cat, []).append(s.name)

        return {
            "cv": {
                "name": self.profile.name,
                "headline": self.profile.headline,
                "location": self.profile.location,
                "email": self.profile.email,
                "phone": self.profile.phone or "",
                "website": self.profile.website or "",
                "social_networks": [
                    {"network": "LinkedIn", "username": "alinikkhah2001"},
                    {"network": "GitHub", "username": "AliNikkhah2001"},
                ],
                "sections": {
                    "summary": [self.profile.summary_brief or self.profile.summary],
                    "education": education,
                    "experience": experience,
                    "publications": [
                        {"title": pub.title, "authors": pub.authors, "journal": pub.venue or "", "date": str(pub.year)}
                        for pub in self.publications
                    ],
                    "teaching": [
                        {"name": t.course, "summary": f"{t.role} ({t.period})"}
                        for t in self.teaching
                    ],
                    "skills": [
                        {"label": cat, "details": ", ".join(names)}
                        for cat, names in skills_dict.items()
                    ],
                },
            },
            "design": {"theme": "classic"},
        }

    def to_linkedin_sections(self) -> dict:
        """Generate LinkedIn-style sections for copy-paste."""
        org_map = {o.id: o for o in self.organizations}
        pos_map = {p.id: p for p in self.positions}
        ach_map = {a.id: a for a in self.achievements}

        experience = []
        for p in self.positions:
            org = org_map.get(p.organization_id)
            bullets = []
            for aid in p.achievements:
                ach = ach_map.get(aid)
                if ach:
                    bullets.append(f"• {ach.text}")
            experience.append({
                "title": p.title,
                "company": org.name if org else "Unknown",
                "location": p.location or "",
                "duration": f"{p.start.to_iso()[:7]} – {'Present' if p.ongoing else (p.end.to_iso()[:7] if p.end else '')}",
                "description": (p.summary or "") + "\n\n" + "\n".join(bullets) if bullets else (p.summary or ""),
            })

        education = []
        for e in self.education:
            org = org_map.get(e.organization_id)
            education.append({
                "school": org.name if org else "Unknown",
                "degree": e.degree,
                "field": e.field or "",
                "dates": f"{e.start.year} – {'Present' if e.ongoing else (e.end.year if e.end else '')}",
                "description": f"GPA: {e.gpa}" if e.gpa else "",
            })

        skills = [s.name for s in self.skills if s.category != "human"]

        return {
            "headline": self.profile.headline,
            "about": self.profile.summary_brief or self.profile.summary,
            "experience": experience,
            "education": education,
            "skills": skills,
            "licenses": [],
        }

    def to_reactive_resume(self) -> dict:
        """Reactive Resume (rxresu.me) v3-compatible import document."""
        org_map = {o.id: o for o in self.organizations}
        ach_map = {a.id: a for a in self.achievements}

        def d2(d: Optional["DatePrecision"]) -> str:
            return d.to_iso()[:7] if d and d.year < 9999 else ""

        loc = [x.strip() for x in self.profile.location.split(",")]
        work, education, projects = [], [], []
        for p in self.positions_by_date():
            org = org_map.get(p.organization_id)
            work.append({
                "company": org.name if org else "Unknown",
                "position": p.title,
                "location": p.location or self.profile.location,
                "date": {"start": d2(p.start), "end": "present" if p.ongoing else d2(p.end)},
                "summary": p.summary or "",
                "highlights": [ach_map[a].text for a in p.achievements if a in ach_map],
            })
        for e in self.education:
            org = org_map.get(e.organization_id)
            education.append({
                "institution": org.name if org else "Unknown",
                "area": e.field or "",
                "studyType": e.degree,
                "date": {"start": d2(e.start), "end": "present" if e.ongoing else d2(e.end)},
                "score": e.gpa or "",
                "courses": e.coursework,
            })
        for prj in self.projects:
            projects.append({
                "name": prj.title,
                "description": prj.summary or "",
                "highlights": [prj.description] if prj.description else [],
                "date": {"start": d2(prj.start), "end": "present" if prj.ongoing else d2(prj.end)},
                "url": prj.url or "",
                "keywords": prj.skills,
            })

        cat_map = {
            "language": "Languages", "ml_vision": "ML & Vision", "agentic": "Agentic AI & RAG",
            "llm_serving": "LLM Serving & GPU", "data_mlop": "Data & MLOps", "human": "Human Languages",
        }
        grouped: dict[str, list[str]] = {}
        for s in self.skills:
            grouped.setdefault(cat_map.get(s.category, s.category), []).append(s.name)

        return {
            "basics": {
                "name": self.profile.name,
                "headline": self.profile.headline,
                "email": self.profile.email,
                "phone": self.profile.phone or "",
                "website": self.profile.website or "",
                "summary": self.profile.summary_brief or self.profile.summary,
                "location": {
                    "city": loc[0] if loc else "",
                    "region": loc[1] if len(loc) > 1 else "",
                    "country": loc[1] if len(loc) > 1 else "",
                },
                "profiles": [
                    {"network": "LinkedIn", "username": self.profile.linkedin or "", "url": self.profile.linkedin or ""},
                    {"network": "GitHub", "username": self.profile.github or "", "url": self.profile.github or ""},
                ],
            },
            "work": work,
            "education": education,
            "projects": projects,
            "skills": [
                {"name": name, "level": "Expert", "keywords": kws}
                for name, kws in grouped.items()
            ],
            "publications": [
                {"name": pub.title, "publisher": pub.venue or pub.status,
                 "releaseDate": str(pub.year), "url": pub.url or "", "summary": ", ".join(pub.authors)}
                for pub in self.publications
            ],
            "languages": [
                {"name": s.name, "level": s.proficiency or "Native"}
                for s in self.skills if s.category == "human"
            ],
            "meta": {"version": "v3", "generator": "career-dashboard", "source": "career_db"},
        }

    def to_jobops_rows(self) -> list[dict]:
        """Application-tracker rows for JobOps / Huntr / generic CSV trackers.

        Each employment position maps to one tracked application with
        outcome=hired (current roles: status=active).
        """
        org_map = {o.id: o for o in self.organizations}
        rows = []
        for p in self.positions_by_date():
            org = org_map.get(p.organization_id)
            rows.append({
                "company": org.name if org else "Unknown",
                "role": p.title,
                "status": "active" if p.ongoing else "hired",
                "outcome": "hired",
                "start": p.start.to_iso()[:7],
                "end": "present" if p.ongoing else (p.end.to_iso()[:7] if p.end else ""),
                "location": p.location or "",
                "type": p.employment_type,
                "work_model": p.work_model or ("remote" if p.remote else ""),
                "tech": ", ".join(p.tech_stack),
                "notes": p.concurrent_note or "",
                "url": (org.url if org else "") or "",
                "source": "career_db",
            })
        return rows