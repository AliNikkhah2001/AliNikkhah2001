"""Template registry, career_db → LaTeX/RenderCV generation, compilation.

Build layout:
  career-dashboard/builds/<template-id>/out.pdf   — compiled artifact
  career-dashboard/builds/.cache/<family>-<hash>/ — regenerated sources

Template families:
  academic-*    9 academic themes  (live data, pdflatex)
  industrial-*  9 gallery preambles (live data, pdflatex)
  rendercv-*    5 RenderCV themes   (live data, rendercv/typst)
  upstream-*    10 open-source templates (sample data, latexmk)
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from models import CareerDatabase, DatePrecision, Position

ROOT = Path(__file__).resolve().parents[1]          # career-dashboard/
RESUME = ROOT.parent / "resume"                     # resume/
BUILD = ROOT / "builds"
RENDERCV = Path.home() / ".local" / "bin" / "rendercv"
RENDERCV_FALLBACK = Path("/opt/homebrew/bin/rendercv")
COMPILE_TIMEOUT = 300

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

ACADEMIC_THEMES = [
    ("01_classic", "Classic Serif", "lmodern + black rules", r"\usepackage{lmodern}"),
    ("02_awesome", "Awesome-CV Color", "teal accent #2A7F62",
     r"\usepackage{lmodern}\definecolor{awesome}{HTML}{2A7F62}\colorlet{sec}{awesome}"),
    ("03_modern", "ModernCV Blue", "ModernCV blue header + sans",
     r"\usepackage[default]{sourcesanspro}\definecolor{primary}{HTML}{0E6EB0}"),
    ("04_altacv", "AltaCV Sidebar", "sidebar color #1A3A4A",
     r"\usepackage{lmodern}\definecolor{sidebar}{HTML}{1A3A4A}"),
    ("05_deedy", "Deedy Tight", "tight Helvetica",
     r"\usepackage[scaled]{helvet}\renewcommand\familydefault{\sfdefault}"),
    ("06_plasmati", "Plasmati Grey", "grey/blue muted",
     r"\usepackage{lmodern}\definecolor{plas}{HTML}{4A6572}"),
    ("07_simple", "Simple Mono", "monochrome + Source Code Pro titles",
     r"\usepackage{sourcecodepro}\usepackage{lmodern}"),
    ("08_ieee", "IEEE Two-Column", "IEEEtran-inspired two-column",
     r"\usepackage{lmodern}"),
    ("09_clean", "Clean Margin", "Garamond",
     r"\usepackage{ebgaramond}\usepackage{lmodern}"),
]

INDUSTRIAL_PREAMBLES = [
    ("classic", "Classic"), ("teal", "Teal"), ("blue", "Blue"),
    ("slate", "Slate"), ("deedy", "Deedy"), ("plasmati", "Plasmati"),
    ("mono", "Mono"), ("ieee", "IEEE"), ("garamond", "Garamond"),
    ("executive", "Executive"),
]

RENDERCV_THEMES = [
    ("classic", "RenderCV Classic"),
    ("harvard", "RenderCV Harvard"),
    ("moderncv", "RenderCV ModernCV"),
    ("engineeringclassic", "RenderCV Engineering"),
    ("ink", "RenderCV Ink"),
]

SKILL_CATEGORIES = [
    ("language", "Languages"),
    ("ml_vision", "ML \\& Vision"),
    ("agentic", "Agentic AI \\& RAG"),
    ("llm_serving", "LLM Serving \\& GPU"),
    ("data_mlop", "Data \\& MLOps"),
    ("human", "Human Languages"),
]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def tex_esc(s: str | None) -> str:
    if not s:
        return ""
    out = str(s)
    for ch, repl in [
        ("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
        ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]:
        out = out.replace(ch, repl)
    return out


def fmt_date(d: DatePrecision | None) -> str:
    if d is None:
        return "?"
    if d.month:
        return f"{MONTHS[d.month - 1]} {d.year}"
    return str(d.year)


def date_range(start: DatePrecision, end: DatePrecision | None, ongoing: bool) -> str:
    if ongoing or end is None or end.year >= 9999:
        return f"{fmt_date(start)} -- Present"
    return f"{fmt_date(start)} -- {fmt_date(end)}"


def categorize(pos: Position) -> str:
    t = pos.title.lower()
    if "teaching assistant" in t or "instructor" in t:
        return "teaching"
    # Full-time industry roles (incl. R&D Lead) belong to Industry, not Research.
    if pos.employment_type == "full_time":
        return "full-time"
    if re.search(r"research|\br&d\b|scholar|fellow|collaborator", t):
        return "research"
    return "part-time"


def _by_start_desc(items, key=lambda x: x.start.year * 100 + (x.start.month or 1)):
    return sorted(items, key=key, reverse=True)


def db_hash(db: CareerDatabase, opts: dict | None = None) -> str:
    base = db.model_dump_json(exclude_none=True)
    if opts:
        base += "|" + json.dumps(opts, sort_keys=True, default=str)
    return hashlib.md5(base.encode()).hexdigest()[:12]


def _wording_text(ach, wording: str | None, compact: bool = False) -> str:
    if wording == "brief":
        return ach.brief_text or ach.text
    if wording == "detailed":
        return ach.detailed_text or ach.text
    if compact:  # legacy behavior: compact layout used brief wording
        return ach.brief_text or ach.text
    return ach.text


def _enabled(opts: dict | None, section: str) -> bool:
    """Section gate: no opts → everything on; otherwise membership in opts['sections']."""
    if not opts:
        return True
    return section in (opts.get("sections") or [])


def _org_map(db: CareerDatabase) -> dict:
    return {o.id: o for o in db.organizations}


def _ach_map(db: CareerDatabase) -> dict:
    return {a.id: a for a in db.achievements}


# --------------------------------------------------------------------------- #
# academic generator
# --------------------------------------------------------------------------- #
ACADEMIC_PREAMBLE = r"""\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[T1]{fontenc}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[dvipsnames]{xcolor}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{microtype}
\usepackage{lmodern}
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.0in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}
\urlstyle{same}
\raggedbottom
\raggedright
\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]
\newcommand{\resumeItem}[1]{\item\small{#1 \vspace{-2pt}}}
\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
  \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
    \textbf{#1} & \small #2 \\
    \textit{\small#3} & \textit{\small #4} \\
  \end{tabular*}\vspace{-7pt}
}
\newcommand{\pubItem}[4]{%
  \vspace{4pt}\item
  \begin{tabular*}{0.97\textwidth}[t]{p{0.85\textwidth}@{\extracolsep{\fill}}r}
    \small \textbf{#2} & \small #4 \\
    \small #1 & \\
    \small \textit{#3} & \\
  \end{tabular*}\vspace{-4pt}
}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}
\newenvironment{resumeSubHeadingList}{\begin{itemize}[leftmargin=0.15in, label={}]}{\end{itemize}}
\newenvironment{resumeItemList}{\begin{itemize}[leftmargin=0.2in]}{\end{itemize}\vspace{-5pt}}
"""


def _academic_header(db: CareerDatabase) -> str:
    p = db.profile
    links = []
    if p.website:
        links.append(f"\\href{{{p.website}}}{{{p.website.replace('https://', '').replace('http://', '')}}}")
    if p.linkedin:
        links.append(f"\\href{{{p.linkedin}}}{{{p.linkedin.replace('https://', '').replace('http://', '').replace('www.', '')}}}")
    contact = [f"\\href{{mailto:{p.email}}}{{{p.email}}}"]
    if p.phone:
        contact.append(tex_esc(p.phone))
    line1 = " $|$ ".join([tex_esc(p.location)] + contact)
    line2 = " $|$ ".join(links)
    return (
        "\\begin{center}\n"
        f"  \\Huge \\textsc{{{tex_esc(p.name)}}} \\\\ \\vspace{{2pt}}\n"
        f"  \\small {line1} \\\\\n"
        f"  {line2}\n"
        "\\end{center}\n"
    )


def _research_interests(db: CareerDatabase) -> str:
    text = db.profile.summary_brief or db.profile.summary or ""
    first = text.split(". ")[0].rstrip(".")
    return (
        "\\section{Research Interests}\n"
        f"\\small{{{tex_esc(first)}.}}\n\\vspace{{4pt}}\n"
    )


def _education_section(db: CareerDatabase) -> str:
    orgs = _org_map(db)
    out = ["\\section{Education}", "\\begin{resumeSubHeadingList}"]
    for e in _by_start_desc(db.education):
        org = orgs.get(e.organization_id)
        org_name = org.name if org else ""
        loc = "Tehran, Iran" if org and "Sharif" in org.name else ""
        degree = tex_esc(e.degree)
        if e.gpa:
            degree += f" \\quad GPA: {tex_esc(e.gpa)}"
        if e.ongoing:
            degree += " (ongoing)"
        out.append(
            f"  \\resumeSubheading\n    {{{tex_esc(org_name)}}}{{{loc}}}\n"
            f"    {{{degree}}}{{{date_range(e.start, e.end, e.ongoing)}}}"
        )
        items = []
        if e.thesis:
            items.append(f"    \\resumeItem{{Thesis: {tex_esc(e.thesis)}}}")
        if e.coursework:
            items.append(f"    \\resumeItem{{Relevant coursework: {tex_esc(', '.join(e.coursework))}.}}")
        if items:
            out.append("  \\begin{resumeItemList}")
            out.extend(items)
            out.append("  \\end{resumeItemList}")
    out.append("\\end{resumeSubHeadingList}\n")
    return "\n".join(out)


def _skills_section(db: CareerDatabase) -> str:
    grouped: dict[str, list[str]] = {}
    for s in db.skills:
        grouped.setdefault(s.category, []).append(s.name)
    out = ["\\section{Technical Skills}", "\\begin{itemize}[leftmargin=0.15in, label={}]", "  \\small{\\item{"]
    for key, label in SKILL_CATEGORIES:
        names = grouped.get(key)
        if names:
            out.append(f"    \\textbf{{{label}}}: {tex_esc(', '.join(names))} \\\\")
    # any unknown categories
    known = {k for k, _ in SKILL_CATEGORIES}
    for key, names in grouped.items():
        if key not in known:
            out.append(f"    \\textbf{{{tex_esc(key)}}}: {tex_esc(', '.join(names))} \\\\")
    out += ["  }}", "\\end{itemize}\n"]
    return "\n".join(out)


def _position_block(pos: Position, db: CareerDatabase, orgs: dict, achs: dict,
                    compact: bool = False, wording: str | None = None) -> str:
    org = orgs.get(pos.organization_id)
    org_name = tex_esc(org.name if org else "Unknown")
    loc = tex_esc(pos.location or "")
    title = tex_esc(pos.title)
    lines = [
        "\\resumeSubheading",
        f"  {{{org_name}}}{{{loc}}}",
        f"  {{{title}}}{{{date_range(pos.start, pos.end, pos.ongoing)}}}",
        "\\begin{resumeItemList}",
    ]
    texts = []
    for aid in pos.achievements:
        a = achs.get(aid)
        if a:
            texts.append(_wording_text(a, wording, compact))
    if not texts and pos.summary:
        texts.append(pos.summary)
    for t in texts:
        lines.append(f"  \\resumeItem{{{tex_esc(t)}}}")
    if pos.tech_stack and not compact:
        lines.append(f"  \\resumeItem{{\\textit{{Stack:}} {tex_esc(', '.join(pos.tech_stack))}}}")
    if len(lines) == 4:  # header only + begin + end
        lines.insert(4, "  \\resumeItem{}")
    lines.append("\\end{resumeItemList}")
    return "\n".join(lines)


def _has_items(segment: str) -> bool:
    """True if a generated segment contains real LaTeX content (not just comments)."""
    return any(
        ln.strip() and not ln.strip().startswith("%")
        for ln in segment.splitlines()
    )


def _teaching_segment(db: CareerDatabase, wording: str | None = None) -> str:
    orgs = _org_map(db)
    achs = _ach_map(db)
    out: list[str] = []
    for pos in _by_start_desc([p for p in db.positions if categorize(p) in ("education", "teaching")]):
        out.append(_position_block(pos, db, orgs, achs, wording=wording))
        out.append("")
    # group explicit teaching records by role+org
    groups: dict[tuple, list] = {}
    for t in db.teaching:
        groups.setdefault((t.role, t.organization_id), []).append(t)
    for (role, org_id), entries in groups.items():
        org = orgs.get(org_id) if org_id else None
        period = entries[0].period
        out.append("\\resumeSubheading")
        out.append(f"  {{{tex_esc(org.name if org else '')}}}{{}}")
        out.append(f"  {{{tex_esc(role)}}}{{{tex_esc(period)}}}")
        out.append("\\begin{resumeItemList}")
        courses = ", ".join(e.course for e in entries)
        out.append(f"  \\resumeItem{{Courses: {tex_esc(courses)}}}")
        students = [e.students for e in entries if e.students]
        if students:
            out.append(f"  \\resumeItem{{Cohorts of up to {max(students)} students; office hours, problem sets, grading, exam design.}}")
        out.append("\\end{resumeItemList}")
        out.append("")
    return "\n".join(out) if out else "% no teaching entries\n"


def _apply_style(tex: str, style: dict | None) -> str:
    """Override page margins / font size / line spacing on assembled LaTeX."""
    if not style:
        return tex
    margin = style.get("margin")
    if margin:
        m = f"{float(margin):g}"
        tex = tex.replace(
            r"\usepackage[empty]{fullpage}",
            rf"\usepackage[left={m}in,right={m}in,top={m}in,bottom={m}in]{{geometry}}",
        )
        tex = re.sub(
            r"^\\addtolength\{\\(?:oddsidemargin|evensidemargin|textwidth|topmargin|textheight)\}"
            r"\{[-+]?[.0-9]+in\}[ \t]*\n",
            "", tex, flags=re.M,
        )
    font_size = style.get("font_size")
    if font_size:
        tex = re.sub(r"(\\documentclass\[[^\]]*?)\d+pt", rf"\g<1>{int(font_size)}pt", tex, count=1)
    spacing = style.get("line_spacing")
    if spacing:
        tex = tex.replace(
            r"\begin{document}",
            "\\begin{document}\n" + rf"\linespread{{{float(spacing):g}}}\selectfont",
            1,
        )
    return tex


def generate_academic(db: CareerDatabase, cache: Path, opts: dict | None = None) -> None:
    """Write main.tex + segments/ + themes/*.tex into the cache tree."""
    orgs = _org_map(db)
    achs = _ach_map(db)
    wording = (opts or {}).get("wording_level")
    compact = bool(opts and opts.get("format") == "1page")
    (cache / "segments" / "publications").mkdir(parents=True, exist_ok=True)
    (cache / "segments" / "research_experience").mkdir(parents=True, exist_ok=True)
    (cache / "segments" / "teaching_mentoring").mkdir(parents=True, exist_ok=True)
    (cache / "themes").mkdir(parents=True, exist_ok=True)

    main = ACADEMIC_PREAMBLE + "\n% ==============================================================================\n\\begin{document}\n\n"
    main += "% --- HEADER ---\n" + _academic_header(db)
    if _enabled(opts, "summary"):
        main += "\n" + _research_interests(db)
    if _enabled(opts, "education"):
        main += _education_section(db)

    # publications segment (built before main so empty sections can be skipped)
    pubs = ["% generated from career_db", ""]
    status_map = {"published": "", "preprint": "arXiv preprint", "in_preparation": "in preparation",
                  "under_review": "under review"}
    for pub in db.publications:
        venue = tex_esc(pub.venue or status_map.get(pub.status, pub.status))
        pubs.append(
            "\\pubItem\n"
            f"  {{{tex_esc(', '.join(pub.authors))}}}\n"
            f"  {{{tex_esc(pub.title)}}}\n"
            f"  {{{venue}}}\n"
            f"  {{{pub.year}}}"
        )
    if len(pubs) == 2:
        pubs.append("% no publications yet")
    pubs_tex = "\n".join(pubs) + "\n"
    (cache / "segments" / "publications" / "list.tex").write_text(pubs_tex, encoding="utf-8")

    research = _by_start_desc([p for p in db.positions if categorize(p) == "research"])
    entries = "\n\n".join(_position_block(p, db, orgs, achs, compact=compact, wording=wording) for p in research) or "% no research positions"
    (cache / "segments" / "research_experience" / "entries.tex").write_text(entries + "\n", encoding="utf-8")

    industry = _by_start_desc([p for p in db.positions if categorize(p) in ("full-time", "part-time")])
    ind = "\n\n".join(_position_block(p, db, orgs, achs, compact=compact, wording=wording) for p in industry) or "% no industry positions"
    (cache / "segments" / "research_experience" / "industry.tex").write_text(ind + "\n", encoding="utf-8")

    teaching = _teaching_segment(db, wording=wording)
    (cache / "segments" / "teaching_mentoring" / "ta_history.tex").write_text(teaching + "\n", encoding="utf-8")

    # Sections gated by the resume config, then skipped when empty — an empty
    # itemize is a LaTeX fatal error. Research + industry are both "experience".
    if _enabled(opts, "publications") and _has_items(pubs_tex):
        main += (
            "\\section{Publications \\& Preprints}\n"
            "\\begin{itemize}[leftmargin=0.15in, label={}]\n"
            "  \\input{segments/publications/list.tex}\n"
            "\\end{itemize}\n\n"
        )
    if _enabled(opts, "experience") and _has_items(entries):
        main += (
            "\\section{Research Experience}\n\\begin{resumeSubHeadingList}\n"
            "  \\input{segments/research_experience/entries.tex}\n"
            "\\end{resumeSubHeadingList}\n\n"
        )
    if _enabled(opts, "teaching") and _has_items(teaching):
        main += (
            "\\section{Teaching \\& Mentoring}\n\\begin{resumeSubHeadingList}\n"
            "  \\input{segments/teaching_mentoring/ta_history.tex}\n"
            "\\end{resumeSubHeadingList}\n\n"
        )
    if _enabled(opts, "experience") and _has_items(ind):
        main += (
            "\\section{Industry Experience}\n\\begin{resumeSubHeadingList}\n"
            "  \\input{segments/research_experience/industry.tex}\n"
            "\\end{resumeSubHeadingList}\n\n"
        )
    if _enabled(opts, "skills"):
        main += _skills_section(db)
    main += "\\end{document}\n"
    main = _apply_style(main, (opts or {}).get("style"))
    (cache / "main.tex").write_text(main, encoding="utf-8")

    # themes: base = main.tex with segment inputs rewritten for themes/ cwd
    base = main.replace(r"\input{segments/", r"\input{../segments/")
    for slug, name, desc, pkg in ACADEMIC_THEMES:
        tex = base if pkg in base else base.replace(r"\usepackage{lmodern}", pkg, 1)
        if "awesome" in slug:
            tex = tex.replace(r"[\color{black}\titlerule", r"[\color{awesome}\titlerule")
        if "modern" in slug:
            tex = tex.replace(r"[\color{black}\titlerule", r"[\color{primary}\titlerule")
        tex = f"% THEME {slug}: {name} — {desc}\n% generated from career_db by career-dashboard/api/latex.py\n" + tex
        (cache / "themes" / f"theme_{slug}.tex").write_text(tex, encoding="utf-8")


# --------------------------------------------------------------------------- #
# industrial generator
# --------------------------------------------------------------------------- #
def _industrial_summary(db: CareerDatabase) -> str:
    text = db.profile.summary_brief or db.profile.summary or ""
    return f"% summary (generated)\n\\small{{{tex_esc(text)}}}\n"


def _industrial_skills(db: CareerDatabase) -> str:
    grouped: dict[str, list[str]] = {}
    for s in db.skills:
        grouped.setdefault(s.category, []).append(s.name)
    labels = {"language": "Languages", "ml_vision": "ML/Vision", "agentic": "Agentic",
              "llm_serving": "LLM Serving/GPU", "data_mlop": "Data/MLOps", "human": "Human Languages"}
    out = ["\\begin{itemize}[leftmargin=0.15in, label={}]", "\\small{\\item{"]
    for key, label in labels.items():
        if grouped.get(key):
            out.append(f"  \\textbf{{{label}}}: {tex_esc(', '.join(grouped[key]))} \\\\")
    out += ["}}", "\\end{itemize}"]
    return "\n".join(out) + "\n"


def _industrial_experience(db: CareerDatabase, compact: bool = False, wording: str | None = None) -> str:
    orgs = _org_map(db)
    achs = _ach_map(db)
    positions = _by_start_desc(db.positions)
    return "\n\n".join(_position_block(p, db, orgs, achs, compact=compact, wording=wording) for p in positions) + "\n"


def _industrial_projects(db: CareerDatabase) -> str:
    orgs = _org_map(db)
    out = []
    for prj in _by_start_desc(db.projects):
        org = orgs.get(prj.organization_id) if prj.organization_id else None
        loc = tex_esc(org.name if org else "")
        lines = [
            "\\resumeSubheading",
            f"  {{{tex_esc(prj.title)}}}{{{loc}}}",
            f"  {{{tex_esc(prj.summary or 'Selected project')}}}{{{date_range(prj.start, prj.end, prj.ongoing)}}}",
            "\\begin{resumeItemList}",
        ]
        if prj.description:
            lines.append(f"  \\resumeItem{{{tex_esc(prj.description)}}}")
        if prj.skills:
            lines.append(f"  \\resumeItem{{\\textit{{Stack:}} {tex_esc(', '.join(prj.skills))}}}")
        if len(lines) == 4:
            lines.insert(4, "  \\resumeItem{}")
        lines.append("\\end{resumeItemList}")
        out.append("\n".join(lines))
    return "\n\n".join(out) + "\n" if out else "\\item[] % no projects\n"


def _industrial_education(db: CareerDatabase) -> str:
    orgs = _org_map(db)
    out = []
    for e in _by_start_desc(db.education):
        org = orgs.get(e.organization_id)
        degree = tex_esc(e.degree)
        if e.gpa:
            degree += f" \\quad GPA: {tex_esc(e.gpa)}"
        out.append(
            "\\resumeSubheading\n"
            f"  {{{tex_esc(org.name if org else '')}}}{{}}\n"
            f"  {{{degree}}}{{{date_range(e.start, e.end, e.ongoing)}}}"
        )
    return "\n".join(out) + "\n"


INDUSTRIAL_SECTION_MAP = {
    "Summary": "summary",
    "Technical Skills": "skills",
    "Professional Experience": "experience",
    r"Selected Projects \& Research": "projects",
    "Education": "education",
}


def _filter_industrial_body(body: str, opts: dict | None) -> str:
    """Drop \section blocks whose wizard section is unchecked, keeping \end{document}."""
    if not opts:
        return body
    enabled = set(opts.get("sections") or [])
    out: list[str] = []
    keep = True
    for ln in body.splitlines(keepends=True):
        if ln.startswith("\\section{"):
            title = ln.split("{", 1)[1].rstrip("}\n")
            key = INDUSTRIAL_SECTION_MAP.get(title)
            keep = key is None or key in enabled
        elif ln.startswith("\\end{document}"):
            keep = True
        if keep:
            out.append(ln)
    return "".join(out)


def generate_industrial(db: CareerDatabase, cache: Path, compact: bool = False, opts: dict | None = None) -> None:
    gallery = RESUME / "industrial" / "theme-gallery"
    body = _filter_industrial_body((gallery / "body.tex").read_text(encoding="utf-8"), opts)
    wording = (opts or {}).get("wording_level")
    one_page = bool(opts and opts.get("format") == "1page")
    (cache / "segments" / "generated" / "live").mkdir(parents=True, exist_ok=True)
    (cache / "segments" / "common").mkdir(parents=True, exist_ok=True)

    gen = cache / "segments" / "generated" / "live"
    (gen / "summary.tex").write_text(_industrial_summary(db), encoding="utf-8")
    (gen / "skills.tex").write_text(_industrial_skills(db), encoding="utf-8")
    (gen / "experience.tex").write_text(_industrial_experience(db, wording=wording), encoding="utf-8")
    (gen / "experience-compact.tex").write_text(_industrial_experience(db, compact=True, wording=wording), encoding="utf-8")
    (gen / "projects.tex").write_text(_industrial_projects(db), encoding="utf-8")
    (cache / "segments" / "common" / "education.tex").write_text(_industrial_education(db), encoding="utf-8")
    body_compact = body.replace("experience.tex", "experience-compact.tex")
    (cache / "body-compact.tex").write_text(body_compact, encoding="utf-8")

    for slug, _name in INDUSTRIAL_PREAMBLES:
        preamble = (gallery / f"preamble-{_industrial_num(slug)}-{slug}.tex").read_text(encoding="utf-8")
        body_file = body_compact if (one_page or (compact and slug == "ieee")) else body
        assembled = (
            f"% assembled from theme-gallery/preamble-{slug} + generated career_db body\n"
            "\\newcommand{\\cvvariant}{live}\n"
            + preamble + "\n" + body_file
        )
        assembled = _apply_style(assembled, (opts or {}).get("style"))
        (cache / f"main-{slug}.tex").write_text(assembled, encoding="utf-8")


def _industrial_num(slug: str) -> str:
    order = [s for s, _ in INDUSTRIAL_PREAMBLES]
    return f"{order.index(slug) + 1:02d}"


# --------------------------------------------------------------------------- #
# rendercv generator
# --------------------------------------------------------------------------- #
def generate_rendercv(db: CareerDatabase, out_dir: Path, theme: str, variant_id: str = "long",
                      opts: dict | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = db.to_rendercv(
        variant_id,
        position_ids=(opts or {}).get("position_ids"),
        wording_level=(opts or {}).get("wording_level"),
        sections=(opts or {}).get("sections"),
    )
    # payload is a dict of cv: ... sections; build design block from theme + style
    payload.pop("design", None)
    design: dict = {"theme": theme}
    style = (opts or {}).get("style") or {}
    if style.get("margin"):
        m = f"{float(style['margin']):g}in"
        design["page"] = {
            "left_margin": m, "right_margin": m, "top_margin": m, "bottom_margin": m,
        }
    typography: dict = {}
    if style.get("font_size"):
        typography["font_size"] = {"body": f"{int(style['font_size'])}pt"}
    if style.get("line_spacing"):
        typography["line_spacing"] = f"{0.6 * float(style['line_spacing']):g}em"
    if typography:
        design["typography"] = typography
    payload["design"] = design
    import yaml as _yaml  # PyYAML installed alongside fastapi extras

    yaml_path = out_dir / "cv.yaml"
    yaml_path.write_text(_yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return yaml_path


def _rendercv_bin() -> Path:
    if RENDERCV.exists():
        return RENDERCV
    found = shutil.which("rendercv")
    return Path(found) if found else RENDERCV_FALLBACK


# --------------------------------------------------------------------------- #
# upstream templates
# --------------------------------------------------------------------------- #
def upstream_catalog() -> list[dict]:
    path = RESUME / "academic" / "template-library" / "catalog.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _compat() -> dict:
    path = RESUME / "academic" / "template-library" / "compatibility.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _build_results() -> dict:
    path = RESUME / "academic" / "template-library" / "build-results.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def prepare_upstream(entry_id: str, src_dir: Path) -> dict:
    """Copy upstream sources once, apply compatibility patches, return build info."""
    upstream = RESUME / "academic" / "template-library" / "upstream" / entry_id
    if not src_dir.exists():
        shutil.copytree(upstream, src_dir)
    patches = _compat().get(entry_id, {}).get("patches", {})
    for fname, subs in patches.items():
        target = src_dir / fname
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        for old, new in subs:
            text = text.replace(old, new)
        target.write_text(text, encoding="utf-8")
    results = _build_results().get(entry_id, {})
    entry = next((c for c in upstream_catalog() if c["id"] == entry_id), {})
    return {
        "entrypoint": entry.get("entrypoint", "main.tex"),
        "engine": results.get("engine") or entry.get("engine", "pdflatex"),
        "command": results.get("command"),
    }


# --------------------------------------------------------------------------- #
# compilation
# --------------------------------------------------------------------------- #
def _run(cmd: list[str], cwd: Path, timeout: int = COMPILE_TIMEOUT) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        )
        log = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode == 0, log
    except subprocess.TimeoutExpired:
        return False, f"compile timed out after {timeout}s"
    except FileNotFoundError as e:
        return False, f"engine not found: {e}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def _log_tail(log: str, n: int = 30) -> str:
    lines = [ln for ln in log.splitlines() if ln.strip()]
    return "\n".join(lines[-n:])


def _pdf_pages(pdf: Path) -> int | None:
    try:
        import pdfplumber

        with pdfplumber.open(pdf) as doc:
            return len(doc.pages)
    except Exception:  # noqa: BLE001
        return None


def _cache_dir(family: str, h: str) -> Path:
    return BUILD / ".cache" / f"{family}-{h}"


def pdf_path(template_id: str) -> Path:
    return BUILD / template_id / "out.pdf"


# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #
def registry(db: CareerDatabase) -> list[dict[str, Any]]:
    h = db_hash(db)
    db_mtime = (ROOT / "career_db.json").stat().st_mtime if (ROOT / "career_db.json").exists() else 0
    items: list[dict[str, Any]] = []

    def base_info(tid: str, name: str, family: str, engine: str, data: str, desc: str) -> dict:
        pdf = pdf_path(tid)
        compiled = pdf.exists()
        return {
            "id": tid,
            "name": name,
            "family": family,
            "engine": engine,
            "data_source": data,          # "live" = rendered from career_db, "sample" = upstream demo content
            "description": desc,
            "compiled": compiled,
            "stale": compiled and pdf.stat().st_mtime < db_mtime,
            "pages": _pdf_pages(pdf) if compiled else None,
            "pdf_url": f"/api/templates/{tid}/pdf" if compiled else None,
            "hash": h,
        }

    for slug, name, desc, _pkg in ACADEMIC_THEMES:
        items.append(base_info(
            f"academic-{slug}", name, "Academic themes", "pdflatex", "live",
            f"{desc} — academic CV, sections: research, teaching, publications.",
        ))

    for slug, name in INDUSTRIAL_PREAMBLES:
        items.append(base_info(
            f"industrial-{slug}", name, "Industrial gallery", "pdflatex", "live",
            "Industry CV (full career) — summary, skills, experience, projects, education.",
        ))

    for theme, name in RENDERCV_THEMES:
        items.append(base_info(
            f"rendercv-{theme}", name, "RenderCV", "rendercv (typst)", "live",
            "RenderCV reproducible PDF from the structured variant “long”.",
        ))

    for entry in upstream_catalog():
        results = _build_results().get(entry["id"], {})
        items.append(base_info(
            f"upstream-{entry['id']}", entry["name"], "Open-source upstream", results.get("engine", "latexmk"),
            "sample",
            f"{entry.get('description', '')} — {entry['repository']} ({entry.get('license', '')}); engine-verified.",
        ))

    return items


# --------------------------------------------------------------------------- #
# compile entry point
# --------------------------------------------------------------------------- #
def _flatten_tex(path: Path, depth: int = 0) -> str:
    """Inline \\input{...} references relative to the file's own directory."""
    text = path.read_text(encoding="utf-8")
    if depth > 3:
        return text

    def repl(m: "re.Match[str]") -> str:
        # body.tex references segments via the \cvvariant macro (always "live" here)
        rel = m.group(1).replace("\\cvvariant", "live")
        target = path.parent / rel
        if not target.suffix:
            target = target.with_suffix(".tex")
        if target.exists() and target.is_file():
            return _flatten_tex(target, depth + 1)
        return m.group(0)

    return re.sub(r"\\input\{([^}]+)\}", repl, text)


def _write_source_copy(entry: Path, target: Path) -> None:
    """Copy the generated entry file next to the output, inlining its segments."""
    try:
        content = _flatten_tex(entry)
    except OSError:
        content = entry.read_text(encoding="utf-8")
    target.with_suffix(entry.suffix or ".tex").write_text(content, encoding="utf-8")


def compile_template(db: CareerDatabase, template_id: str, force: bool = False,
                     opts: dict | None = None, out_pdf: Path | None = None) -> dict[str, Any]:
    start = time.time()
    known = {i["id"] for i in registry(db)}
    if template_id not in known:
        raise KeyError(f"unknown template: {template_id}")

    default_pdf = pdf_path(template_id)
    target = out_pdf or default_pdf
    if target == default_pdf and target.exists() and not force:
        item = next(i for i in registry(db) if i["id"] == template_id)
        if not item["stale"]:
            return {"ok": True, "cached": True, "pages": item["pages"], "duration": round(time.time() - start, 2)}

    target.parent.mkdir(parents=True, exist_ok=True)
    h = db_hash(db, opts)

    ok, log = False, ""
    family = template_id.split("-", 1)[0]

    try:
        if family == "academic":
            slug = template_id.split("-", 1)[1]
            cache = _cache_dir("academic", h)
            if not (cache / "themes" / f"theme_{slug}.tex").exists():
                generate_academic(db, cache, opts)
            cwd = cache / "themes"
            # keep the generated entry source (segments inlined) next to the output
            _write_source_copy(cwd / f"theme_{slug}.tex", target)
            ok, log = _run([
                "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                f"theme_{slug}.tex",
            ], cwd=cwd)
            produced = cwd / f"theme_{slug}.pdf"
            if ok and produced.exists():
                shutil.copy(produced, target)

        elif family == "industrial":
            slug = template_id.split("-", 1)[1]
            cache = _cache_dir("industrial", h)
            if not (cache / f"main-{slug}.tex").exists():
                generate_industrial(db, cache, compact=(slug == "ieee"), opts=opts)
            _write_source_copy(cache / f"main-{slug}.tex", target)
            ok, log = _run([
                "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                f"main-{slug}.tex",
            ], cwd=cache)
            produced = cache / f"main-{slug}.pdf"
            if ok and produced.exists():
                shutil.copy(produced, target)

        elif family == "rendercv":
            theme = template_id.split("-", 1)[1]
            work = BUILD / template_id / "src"
            yaml_path = generate_rendercv(db, work, theme, opts=opts)
            shutil.copy(yaml_path, target.with_suffix(".yaml"))
            bin_path = _rendercv_bin()
            ok, log = _run([
                str(bin_path), "render", "cv.yaml", "-o", "out", "-nomd", "-nopng",
                "-pdf", str(Path("out") / "cv.pdf"),
            ], cwd=work)
            produced = work / "out" / "cv.pdf"
            if ok and produced.exists():
                shutil.copy(produced, target)

        elif family == "upstream":
            entry_id = template_id.split("-", 1)[1]
            src = default_pdf.parent / "src"
            info = prepare_upstream(entry_id, src)
            out_dir = default_pdf.parent / "build"
            if out_dir.exists():
                shutil.rmtree(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            if info["command"]:
                cmd = [
                    c.replace("<build-directory>", str(out_dir)) for c in info["command"]
                ]
            else:
                engine = info["engine"]
                latexmk_mode = "-pdfxe" if engine in ("xelatex", "xdvipdfmx") else "-pdf"
                cmd = [
                    "latexmk", "-norc", latexmk_mode, "-interaction=nonstopmode",
                    "-halt-on-error", "-file-line-error", "-no-shell-escape",
                    f"-outdir={out_dir}", info["entrypoint"],
                ]
            ok, log = _run(cmd, cwd=src, timeout=420)
            pdfs = sorted(out_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
            if ok and pdfs:
                shutil.copy(pdfs[0], target)

    except KeyError as e:
        return {"ok": False, "error": str(e), "log": "", "duration": round(time.time() - start, 2)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "log": _log_tail(log),
                "duration": round(time.time() - start, 2)}

    duration = round(time.time() - start, 2)
    if ok and target.exists():
        return {"ok": True, "cached": False, "pages": _pdf_pages(target), "duration": duration}
    return {
        "ok": False,
        "error": "engine reported failure" if not ok else "engine succeeded but PDF missing",
        "log": _log_tail(log),
        "duration": duration,
    }
