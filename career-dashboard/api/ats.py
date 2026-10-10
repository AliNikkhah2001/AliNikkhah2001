"""ATS friendliness checker — scores a compiled CV PDF from 0 to 100.

Weights (100 total):
  contact info      10   email/phone/location/links present and machine-readable
  standard sections 15   Experience / Education / Skills headings
  keyword coverage  20   share of the career tech stack found in the text
  quantified impact 15   bullets containing hard numbers
  action verbs      10   strong verbs covering the experience section
  date hygiene      10   parseable Mon YYYY ranges for every role
  parse health      10   extractable text, no mojibake, role titles found
  length & density  10   page budget and readable text density
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from models import CareerDatabase

ACTION_VERBS = [
    "engineered", "designed", "built", "developed", "led", "architected",
    "implemented", "optimized", "deployed", "orchestrated", "automated",
    "achieved", "reduced", "improved", "increased", "delivered", "scaled",
    "migrated", "streamlined", "established", "spearheaded", "championed",
    "mentored", "directed", "managed", "coordinated", "launched", "shipped",
    "cut", "drove", "trained", "profiled", "integrated", "published",
]


def extract_text(pdf: Path) -> tuple[str, int | None]:
    """Extract UTF-8 text and page count from a PDF."""
    text = ""
    if shutil.which("pdftotext"):
        try:
            proc = subprocess.run(
                ["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                capture_output=True, text=True, timeout=60,
            )
            if proc.returncode == 0:
                text = proc.stdout
        except Exception:  # noqa: BLE001
            text = ""
    if not text.strip():
        try:
            import pdfplumber

            with pdfplumber.open(pdf) as doc:
                text = "\n".join((p.extract_text() or "") for p in doc.pages)
        except Exception:  # noqa: BLE001
            text = ""
    pages = None
    try:
        import pdfplumber

        with pdfplumber.open(pdf) as doc:
            pages = len(doc.pages)
    except Exception:  # noqa: BLE001
        pages = None
    return text, pages


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).lower()


def check_pdf(pdf: Path, db: CareerDatabase, family: str = "") -> dict[str, Any]:
    text, pages = extract_text(pdf)
    low = _norm(text)
    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    def record(key: str, label: str, weight: int, earned: float, detail: str, fix: str | None = None) -> None:
        earned = max(0.0, min(weight, earned))
        checks.append({
            "key": key, "label": label, "weight": weight,
            "score": round(earned, 1), "detail": detail,
        })
        if fix and earned < weight * 0.999:
            issues.append({"check": label, "lost": round(weight - earned, 1), "fix": fix})

    # 1. contact -------------------------------------------------------------
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    phone = re.search(r"\+?\d[\d\s().-]{7,}\d", text)
    link = "linkedin" in low or "github" in low or ".io" in low
    location = _norm(db.profile.location).split(",")[0]
    loc_found = location and location in low
    contact_parts = [bool(email), bool(phone), bool(link), bool(loc_found)]
    record(
        "contact", "Contact block", 10,
        10 * sum(contact_parts) / 4,
        f"email={bool(email)} phone={bool(phone)} links={link} location={loc_found}",
        "Add machine-readable email, phone, city and profile links at the top of the CV.",
    )

    # 2. sections ------------------------------------------------------------
    section_hits = {
        "experience": bool(re.search(r"(experience|employment|work history|professional background)", low)),
        "education": "education" in low or "academic background" in low,
        "skills": bool(re.search(r"(skills|technical skills|technologies|tech stack)", low)),
    }
    record(
        "sections", "Standard section headings", 15,
        15 * sum(section_hits.values()) / 3,
        ", ".join(f"{k}={'yes' if v else 'NO'}" for k, v in section_hits.items()),
        "Use standard headings: Experience, Education, Skills — ATS keyword routers look for them.",
    )

    # 3. keyword coverage ----------------------------------------------------
    wanted: set[str] = set()
    for p in db.positions:
        wanted.update(t.lower() for t in p.tech_stack if len(t) >= 3)
    wanted.update(s.name.lower() for s in db.skills if len(s.name) >= 3 and s.category != "human")
    present = {t for t in wanted if t in low}
    coverage = len(present) / len(wanted) if wanted else 1.0
    missing = sorted(wanted - present)
    record(
        "keywords", "Tech-stack keyword coverage", 20,
        20 * min(1.0, coverage / 0.6),
        f"{len(present)}/{len(wanted)} terms found ({coverage:.0%})",
        ("Missing high-value terms: " + ", ".join(missing[:12])) if missing else None,
    )

    # 4. quantified impact ---------------------------------------------------
    content_lines = [ln for ln in text.splitlines() if len(ln.strip()) > 40]
    quant = [ln for ln in content_lines if re.search(r"\d+(?:[.,]\d+)?\s*(?:%|x\b|ms\b|QPS|RPS|queries|models|students|pages)", ln, re.I)
             or re.search(r"\d+[.,]?\d*\s*(?:K|M|B)\+?", ln)]
    ratio = len(quant) / max(1, min(len(content_lines), 40))
    record(
        "metrics", "Quantified impact", 15,
        15 * min(1.0, ratio / 0.4),
        f"{len(quant)} quantified lines (target ≥40% of substantive lines)",
        "Add numbers to bullets: latency, %, scale, revenue, cohort sizes.",
    )

    # 5. action verbs --------------------------------------------------------
    verbs_found = sorted({v for v in ACTION_VERBS if re.search(rf"\b{v}\w*\b", low)})
    record(
        "verbs", "Strong action verbs", 10,
        10 * min(1.0, len(verbs_found) / 8),
        f"{len(verbs_found)} distinct verbs: {', '.join(verbs_found[:8])}",
        "Open bullets with action verbs (architected, reduced, shipped…), avoid 'responsible for'.",
    )

    # 6. dates ---------------------------------------------------------------
    date_hits = re.findall(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{4}\b|\b(?:19|20)\d{2}\b",
        low,
    )
    dated_roles = sum(
        1 for p in db.positions
        if str(p.start.year) in low and (not p.ongoing or "present" in low or "now" in low)
    )
    role_ratio = dated_roles / len(db.positions) if db.positions else 1.0
    record(
        "dates", "Date hygiene", 10,
        10 * min(1.0, role_ratio) * (0.7 + 0.3 * min(1.0, len(date_hits) / (4 * max(1, len(db.positions))))),
        f"{dated_roles}/{len(db.positions)} roles dated, {len(date_hits)} date tokens",
        "Every role needs a parseable date range (Mon YYYY – Mon YYYY / Present).",
    )

    # 7. parse health --------------------------------------------------------
    title_hits = sum(1 for p in db.positions if _norm(p.title)[:30] in low)
    title_ratio = title_hits / len(db.positions) if db.positions else 1.0
    mojibake = len(re.findall(r"[\ufffd]|Ã[\x80-\xbf]|â€", text))
    text_ok = len(text) > 1200
    health_parts = [text_ok, mojibake < 5, title_ratio >= 0.8]
    record(
        "parse", "Parse health", 10,
        10 * (0.4 * int(text_ok) + 0.3 * int(mojibake < 5) + 0.3 * min(1.0, title_ratio / 0.8)),
        f"chars={len(text)} mojibake={mojibake} role titles found={title_hits}/{len(db.positions)}",
        None if all(health_parts) else
        "Text extraction looks unhealthy — avoid glyphs/symbols ATS cannot decode; keep role titles verbatim.",
    )

    # 8. length & density ----------------------------------------------------
    page_limit = 4 if "academic" in family or (pages or 0) > 3 else 2
    if pages is None:
        length_score = 5.0
        pages_detail = "page count unavailable"
    else:
        over = max(0, pages - page_limit)
        length_score = max(0.0, 10 - over * 3)
        density = len(text) / pages
        if density < 800:
            length_score -= 2
        elif density > 7000:
            length_score -= 2
        pages_detail = f"{pages} pages (budget {page_limit}), {int(density)} chars/page"
    record(
        "length", "Length & density", 10, length_score, pages_detail,
        f"Trim to {page_limit} pages or split into a long academic + short industry variant.",
    )

    total = round(sum(c["score"] for c in checks), 1)
    if total >= 90:
        grade = "A"
    elif total >= 80:
        grade = "B"
    elif total >= 70:
        grade = "C"
    elif total >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": total,
        "grade": grade,
        "pages": pages,
        "checks": checks,
        "issues": issues,
        "summary": f"{total:.0f}/100 — grade {grade} ({len(issues)} improvement{'s' if len(issues) != 1 else ''} found)",
    }


def check_with_cache(pdf: Path, db: CareerDatabase, family: str = "") -> dict[str, Any]:
    cache_file = pdf.parent / "ats.json"
    try:
        pdf_mtime = pdf.stat().st_mtime
        if cache_file.exists():
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("_mtime") == pdf_mtime:
                cached.pop("_mtime", None)
                return cached
    except Exception:  # noqa: BLE001
        pass
    result = check_pdf(pdf, db, family)
    try:
        cache_file.write_text(
            json.dumps({**result, "_mtime": pdf.stat().st_mtime}), encoding="utf-8"
        )
    except Exception:  # noqa: BLE001
        pass
    return result
