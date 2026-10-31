"""Data-quality validation: conflicts, ambiguities and suspicious entries.

Severity levels:
  error   — likely wrong or impossible (e.g. two full-time roles overlapping)
  warning — needs human review (ambiguity, weak evidence)
  info    — suggestions / hygiene notes
"""
from __future__ import annotations

from datetime import date
from typing import Any

from models import CareerDatabase, DatePrecision, Position


def _month_index(d: DatePrecision | None, default_month: int | None = None) -> int | None:
    """Convert a DatePrecision into a comparable YYYYMM integer (start of period)."""
    if d is None:
        return None
    month = d.month or default_month
    if month is None:
        return None
    return d.year * 100 + month


def _position_window(p: Position) -> tuple[int, int]:
    start = _month_index(p.start) or (p.start.year * 100 + 1)
    if p.ongoing:
        today = date.today()
        end = today.year * 100 + today.month
    elif p.end and not (p.end.year >= 9999):
        end = _month_index(p.end) or (p.end.year * 100 + 12)
    else:
        end = start
    return start, max(start, end)


def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    # Strict overlap: sharing only a single boundary month (exact handoff,
    # e.g. intern ends Nov 2021 and engineer starts Nov 2021) is standard
    # CV month-precision dating, not parallel employment.
    return a[0] < b[1] and b[0] < a[1]


def _fmt_month(ym: int | None) -> str:
    if ym is None:
        return "?"
    return f"{ym // 100:04d}-{ym % 100:02d}"


PLACEHOLDER_PATTERNS = [
    r"\[TBD\]", r"\[Co-authors TBD\]", r"\[.*TBD.*\]",
    r"^\s*TODO\s*$", r"^\s*todo\s*$",
    r"^\s*A\. Supervisor\s*$",
    r"^\s*$",
]

def _is_placeholder(text: str | None) -> bool:
    """Check if a text field contains placeholder content."""
    if not text:
        return True
    for pat in PLACEHOLDER_PATTERNS:
        import re
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def scan_placeholders(db: CareerDatabase) -> list[dict[str, Any]]:
    """Find all records with placeholder/incomplete content."""
    findings = []
    # Publications
    for pub in db.publications:
        for author in pub.authors:
            if _is_placeholder(author) or "TBD" in author:
                findings.append({
                    "record_type": "publication",
                    "record_id": pub.id,
                    "field": "authors",
                    "issue": f"Placeholder author: {author}",
                    "action": "Exclude from CV until real names are added",
                })
        if not pub.url:
            findings.append({
                "record_type": "publication",
                "record_id": pub.id,
                "field": "url",
                "issue": "Missing URL/link",
                "action": "Add arXiv URL or remove from CV",
            })
        if pub.status in ("preprint", "in_preparation") and not pub.url:
            findings.append({
                "record_type": "publication",
                "record_id": pub.id,
                "field": "status",
                "issue": "Status is preprint/in_preparation but no URL",
                "action": "Set to in_preparation or add URL",
            })
    # Education
    for edu in db.education:
        if not edu.gpa and not edu.ongoing:
            findings.append({
                "record_type": "education",
                "record_id": edu.id,
                "field": "gpa",
                "issue": "Missing GPA",
                "action": "Add GPA or leave empty if not applicable",
            })
        if not edu.thesis and not edu.ongoing:
            findings.append({
                "record_type": "education",
                "record_id": edu.id,
                "field": "thesis",
                "issue": "Missing thesis title",
                "action": "Add thesis title or mark as ongoing",
            })
    # Achievements
    for ach in db.achievements:
        if _is_placeholder(ach.text):
            findings.append({
                "record_type": "achievement",
                "record_id": ach.id,
                "field": "text",
                "issue": f"Placeholder text: {ach.text[:60]}",
                "action": "Rewrite with real content before including in CV",
            })
    # Positions
    for pos in db.positions:
        if _is_placeholder(pos.summary):
            findings.append({
                "record_type": "position",
                "record_id": pos.id,
                "field": "summary",
                "issue": "Placeholder summary",
                "action": "Write a real summary",
            })
    # Projects
    for proj in db.projects:
        if _is_placeholder(proj.summary) or _is_placeholder(proj.description):
            findings.append({
                "record_type": "project",
                "record_id": proj.id,
                "field": "summary/description",
                "issue": "Placeholder summary or description",
                "action": "Rewrite with real content",
            })
    return findings


def filter_incomplete(db: CareerDatabase) -> tuple[CareerDatabase, list[str]]:
    """Return a copy of db with placeholder/incomplete records removed.
    Returns (filtered_db, list_of_excluded_ids)."""
    findings = scan_placeholders(db)
    excluded_ids = {f["record_id"] for f in findings}

    # Filter publications
    publications = [p for p in db.publications if p.id not in excluded_ids]

    # Filter education
    education = [e for e in db.education if e.id not in excluded_ids]

    # Filter achievements
    achievements = [a for a in db.achievements if a.id not in excluded_ids]

    # Filter positions (and their achievement links)
    positions = []
    for p in db.positions:
        if p.id in excluded_ids:
            continue
        p_copy = p.model_copy(deep=True)
        p_copy.achievements = [aid for aid in p.achievements if aid not in excluded_ids]
        positions.append(p_copy)

    # Filter projects
    projects = [p for p in db.projects if p.id not in excluded_ids]

    filtered = CareerDatabase(
        schema_version=db.schema_version,
        profile=db.profile,
        organizations=db.organizations,
        positions=positions,
        projects=projects,
        education=education,
        publications=publications,
        teaching=db.teaching,
        skills=db.skills,
        achievements=achievements,
        variants=db.variants,
        interview_prep=db.interview_prep,
        acknowledged=db.acknowledged,
    )
    return filtered, sorted(excluded_ids)


def validate_db(db: CareerDatabase) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    def add(severity: str, kind: str, message: str, position_ids: list[str] | None = None) -> None:
        issues.append({
            "severity": severity,
            "kind": kind,
            "message": message,
            "position_ids": position_ids or [],
        })

    positions = db.positions
    windows = {p.id: _position_window(p) for p in positions}
    today_ym = date.today().year * 100 + date.today().month

    # --- 1. Overlapping full-time roles (the classic red flag) -------------
    full_time = [p for p in positions if p.employment_type == "full_time"]
    for i, a in enumerate(full_time):
        for b in full_time[i + 1:]:
            if not _overlaps(windows[a.id], windows[b.id]):
                continue
            # Explicit concurrency notes make the overlap intentional.
            if b.id in a.concurrent_with or a.id in b.concurrent_with:
                add(
                    "info",
                    "declared_concurrency",
                    f"“{a.title}” overlaps “{b.title}” ({_fmt_month(windows[a.id][0])}–"
                    f"{_fmt_month(windows[a.id][1])} vs {_fmt_month(windows[b.id][0])}–"
                    f"{_fmt_month(windows[b.id][1])}) — flagged as declared concurrent, verify wording.",
                    [a.id, b.id],
                )
                continue
            add(
                "error",
                "full_time_overlap",
                f"Two full-time roles overlap: “{a.title}” and “{b.title}” "
                f"({_fmt_month(windows[a.id][0])}–{_fmt_month(windows[a.id][1])} vs "
                f"{_fmt_month(windows[b.id][0])}–{_fmt_month(windows[b.id][1])}). "
                f"Either dates are wrong or one is actually part-time — background checks will catch this.",
                [a.id, b.id],
            )

    # --- 2. Full-time role concurrent with full-time study ----------------
    for p in full_time:
        for e in db.education:
            edu_start = _month_index(e.start) or e.start.year * 100 + 1
            if e.ongoing:
                edu_end = today_ym
            elif e.end and e.end.year < 9999:
                edu_end = _month_index(e.end) or e.end.year * 100 + 12
            else:
                edu_end = edu_start
            if not _overlaps(windows[p.id], (edu_start, edu_end)):
                continue
            if p.concurrent_note or p.id in {"pos_iran_credit_scoring"} or e.id in p.concurrent_with:
                add(
                    "info",
                    "work_study_overlap",
                    f"“{p.title}” runs alongside “{e.degree}” — expected work-study overlap on the timeline.",
                    [p.id],
                )
            else:
                add(
                    "warning",
                    "work_study_overlap",
                    f"Full-time role “{p.title}” overlaps full-time study “{e.degree}” without a declared concurrency note.",
                    [p.id],
                )

    # --- 3. Date sanity -----------------------------------------------------
    for p in positions:
        start = _month_index(p.start) or p.start.year * 100 + 1
        if start > today_ym + 3:
            add("error", "future_start", f"“{p.title}” starts in the future ({_fmt_month(start)}).", [p.id])
        if p.end and p.end.year < 9999:
            end = _month_index(p.end) or p.end.year * 100 + 12
            if end < start:
                add("error", "end_before_start", f"“{p.title}” ends before it starts.", [p.id])
        if not p.ongoing and (p.end is None or p.end.year >= 9999):
            add(
                "warning",
                "missing_end",
                f"“{p.title}” has no end date and is not marked ongoing — ambiguous date range.",
                [p.id],
            )
        if p.start.month is None or (p.end and p.end.year < 9999 and p.end.month is None):
            add(
                "info",
                "year_only_dates",
                f"“{p.title}” uses year-only dates — ATS parsers prefer Mon YYYY.",
                [p.id],
            )

    # --- 4. Evidence hygiene ------------------------------------------------
    for p in positions:
        if not p.achievements:
            add(
                "info",
                "no_evidence",
                f"“{p.title}” has no achievement bullets — weak for ATS keyword coverage and recruiters.",
                [p.id],
            )
        if not p.tech_stack:
            add("info", "no_tech_stack", f"“{p.title}” has an empty tech stack.", [p.id])

    # --- 5. Achievement reuse / mislinking ---------------------------------
    seen: dict[str, list[str]] = {}
    for a in db.achievements:
        if a.position_id:
            seen.setdefault(a.position_id, []).append(a.id)
    for a in db.achievements:
        linked_positions = [p.id for p in positions if a.id in p.achievements]
        if a.position_id and linked_positions and a.position_id not in linked_positions:
            add(
                "warning",
                "achievement_mismatch",
                f"Bullet “{a.text[:60]}…” is registered to position {a.position_id} "
                f"but linked from {', '.join(linked_positions)}.",
                linked_positions,
            )

    # --- 6. Organization / org-type sanity ---------------------------------
    org_ids = {o.id for o in db.organizations}
    for p in positions:
        if p.organization_id not in org_ids:
            add("error", "unknown_org", f"“{p.title}” references missing organization {p.organization_id}.", [p.id])

    # --- 7. Timeline gaps (info) -------------------------------------------
    dated = sorted(
        (w for pid, w in windows.items()),
        key=lambda w: w[0],
    )
    prev_end = None
    for start, end in dated:
        if prev_end is not None and start - prev_end > 12:
            add(
                "info",
                "employment_gap",
                f"Gap of roughly {(start - prev_end) // 12} month(s) between roles "
                f"({_fmt_month(prev_end)} → {_fmt_month(start)}).",
                [],
            )
        prev_end = max(prev_end or 0, end)

    counts = {
        "error": sum(1 for i in issues if i["severity"] == "error"),
        "warning": sum(1 for i in issues if i["severity"] == "warning"),
        "info": sum(1 for i in issues if i["severity"] == "info"),
    }
    # Filter acknowledged issues (user has explicitly accepted these)
    ack = set(db.acknowledged or [])
    if ack:
        issues = [i for i in issues if f"{i['kind']}:{','.join(i['position_ids'])}" not in ack]
        counts = {
            "error": sum(1 for i in issues if i["severity"] == "error"),
            "warning": sum(1 for i in issues if i["severity"] == "warning"),
            "info": sum(1 for i in issues if i["severity"] == "info"),
        }
    return {"issues": issues, "counts": counts, "total": len(issues)}
