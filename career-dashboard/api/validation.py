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
    return a[0] <= b[1] and b[0] <= a[1]


def _fmt_month(ym: int | None) -> str:
    if ym is None:
        return "?"
    return f"{ym // 100:04d}-{ym % 100:02d}"


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
                    f"“{p.title}” runs alongside “{e.degree}” — declared in the CV, keep the phrasing explicit.",
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
        if p.start.month is None or (p.end and p.end.month is None):
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
    return {"issues": issues, "counts": counts, "total": len(issues)}
