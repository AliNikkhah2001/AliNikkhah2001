"""FastAPI backend for career dashboard."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

from models import CareerDatabase, Organization, Position, Project, Education, Achievement, Variant
import ats as ats_mod
import latex as latex_mod
import validation as validation_mod

DB_PATH = Path(__file__).resolve().parents[1] / "career_db.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "resume" / "scripts"))
import generate_profile_readme as readme_mod

app = FastAPI(title="Career Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_db() -> CareerDatabase:
    if not DB_PATH.exists():
        raise HTTPException(500, "Database not found. Run import first.")
    with open(DB_PATH, encoding="utf-8") as f:
        return CareerDatabase.model_validate_json(f.read())


def save_db(db: CareerDatabase) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        f.write(db.model_dump_json(indent=2, exclude_none=True))


@app.get("/api/health")
async def health():
    return {"status": "ok", "db_exists": DB_PATH.exists()}


@app.get("/api/db")
async def get_database():
    return load_db()


@app.post("/api/db/reload")
async def reload_database():
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/import_cv.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(500, f"Import failed: {result.stderr}")
    return {"status": "reloaded", "output": result.stdout}


# Profile
@app.get("/api/profile")
async def get_profile():
    return load_db().profile


@app.put("/api/profile")
async def update_profile(profile_data: dict):
    db = load_db()
    db.profile = db.profile.model_validate(profile_data)
    save_db(db)
    return db.profile


# Organizations
@app.get("/api/organizations")
async def list_organizations():
    return load_db().organizations


@app.post("/api/organizations")
async def create_organization(org: Organization):
    db = load_db()
    if any(o.id == org.id for o in db.organizations):
        raise HTTPException(409, "Organization ID exists")
    db.organizations.append(org)
    save_db(db)
    return org


@app.put("/api/organizations/{org_id}")
async def update_organization(org_id: str, org: Organization):
    db = load_db()
    for i, o in enumerate(db.organizations):
        if o.id == org_id:
            db.organizations[i] = org
            save_db(db)
            return org
    raise HTTPException(404, "Organization not found")


@app.delete("/api/organizations/{org_id}")
async def delete_organization(org_id: str):
    db = load_db()
    db.organizations = [o for o in db.organizations if o.id != org_id]
    save_db(db)
    return {"deleted": org_id}


# Positions
@app.get("/api/positions")
async def list_positions():
    db = load_db()
    return db.positions_by_date()


@app.post("/api/positions")
async def create_position(pos: Position):
    db = load_db()
    if any(p.id == pos.id for p in db.positions):
        raise HTTPException(409, "Position ID exists")
    db.positions.append(pos)
    save_db(db)
    return pos


@app.put("/api/positions/{pos_id}")
async def update_position(pos_id: str, pos: Position):
    db = load_db()
    for i, p in enumerate(db.positions):
        if p.id == pos_id:
            db.positions[i] = pos
            save_db(db)
            return pos
    raise HTTPException(404, "Position not found")


@app.delete("/api/positions/{pos_id}")
async def delete_position(pos_id: str):
    db = load_db()
    db.positions = [p for p in db.positions if p.id != pos_id]
    save_db(db)
    return {"deleted": pos_id}


# Achievements
@app.get("/api/achievements")
async def list_achievements():
    return load_db().achievements


@app.post("/api/achievements")
async def create_achievement(ach: Achievement):
    db = load_db()
    if any(a.id == ach.id for a in db.achievements):
        raise HTTPException(409, "Achievement ID exists")
    db.achievements.append(ach)
    save_db(db)
    return ach


@app.put("/api/achievements/{ach_id}")
async def update_achievement(ach_id: str, ach: Achievement):
    db = load_db()
    for i, a in enumerate(db.achievements):
        if a.id == ach_id:
            db.achievements[i] = ach
            save_db(db)
            return ach
    raise HTTPException(404, "Achievement not found")


@app.delete("/api/achievements/{ach_id}")
async def delete_achievement(ach_id: str):
    db = load_db()
    db.achievements = [a for a in db.achievements if a.id != ach_id]
    save_db(db)
    return {"deleted": ach_id}


# Projects
@app.get("/api/projects")
async def list_projects():
    return load_db().projects


@app.post("/api/projects")
async def create_project(proj: Project):
    db = load_db()
    db.projects.append(proj)
    save_db(db)
    return proj


@app.put("/api/projects/{proj_id}")
async def update_project(proj_id: str, proj: Project):
    db = load_db()
    for i, p in enumerate(db.projects):
        if p.id == proj_id:
            db.projects[i] = proj
            save_db(db)
            return proj
    raise HTTPException(404, "Project not found")


@app.post("/api/positions/tech-stack/derive")
async def derive_tech_stacks():
    """Union achievement skills into each position's tech_stack (case-insensitive merge)."""
    db = load_db()
    updated = 0
    added = 0
    for pos in db.positions:
        derived: dict[str, str] = {s.lower(): s for s in pos.tech_stack}
        linked = [a for a in db.achievements if a.position_id == pos.id or a.id in pos.achievements]
        for ach in linked:
            for skill in ach.skills:
                if skill.lower() not in derived:
                    derived[skill.lower()] = skill
                    added += 1
        new_stack = list(derived.values())
        if new_stack != pos.tech_stack:
            pos.tech_stack = new_stack
            updated += 1
    if updated:
        save_db(db)
    return {"updated_positions": updated, "skills_added": added}


# Education
@app.get("/api/education")
async def list_education():
    return load_db().education


# Publications
@app.get("/api/publications")
async def list_publications():
    return load_db().publications


# Teaching
@app.get("/api/teaching")
async def list_teaching():
    return load_db().teaching


# Skills
@app.get("/api/skills")
async def list_skills():
    return load_db().skills


# Variants
@app.get("/api/variants")
async def list_variants():
    return load_db().variants


@app.post("/api/variants")
async def create_variant(variant: Variant):
    db = load_db()
    if any(v.id == variant.id for v in db.variants):
        raise HTTPException(409, "Variant ID exists")
    db.variants.append(variant)
    save_db(db)
    return variant


# Exports
@app.get("/api/export/json-resume")
async def export_json_resume():
    return load_db().to_json_resume()


@app.get("/api/export/rendercv/{variant_id}")
async def export_rendercv(variant_id: str):
    try:
        data = load_db().to_rendercv(variant_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    text = (
        "# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json\n"
        + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    )
    return Response(content=text, media_type="text/yaml")


@app.get("/api/export/linkedin")
async def export_linkedin():
    return load_db().to_linkedin_sections()


@app.get("/api/export/reactive-resume")
async def export_reactive_resume():
    return load_db().to_reactive_resume()


@app.get("/api/export/jobops")
async def export_jobops():
    import csv
    import io

    rows = load_db().to_jobops_rows()
    if not rows:
        return Response(content="", media_type="text/csv")
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return Response(content=buf.getvalue(), media_type="text/csv")


@app.get("/api/export/github-readme")
async def export_github_readme():
    db = load_db()
    return {"content": readme_mod.generate_readme(db.model_dump()), "format": "markdown"}


# Validation — conflicts & ambiguities
@app.get("/api/validation")
async def get_validation():
    return validation_mod.validate_db(load_db())


# Templates — registry, compile, PDF
class CompileRequest(BaseModel):
    force: bool = False


@app.get("/api/templates")
async def list_templates():
    return latex_mod.registry(load_db())


@app.post("/api/templates/{template_id}/compile")
async def compile_template(template_id: str, body: CompileRequest | None = None):
    try:
        result = latex_mod.compile_template(
            load_db(), template_id, force=bool(body and body.force)
        )
    except KeyError as e:
        raise HTTPException(404, str(e))
    return JSONResponse(content=result, status_code=200 if result.get("ok") else 500)


@app.get("/api/templates/{template_id}/pdf")
async def template_pdf(template_id: str):
    pdf = latex_mod.pdf_path(template_id)
    if not pdf.exists():
        raise HTTPException(404, "Not compiled yet — POST /api/templates/{id}/compile first")
    return FileResponse(pdf, media_type="application/pdf", filename=f"{template_id}.pdf")


# ATS — friendliness score of a compiled template
@app.get("/api/ats/{template_id}")
async def ats_score(template_id: str, compile_if_missing: bool = True):
    db = load_db()
    pdf = latex_mod.pdf_path(template_id)
    if not pdf.exists():
        if not compile_if_missing:
            raise HTTPException(404, "Not compiled yet")
        result = latex_mod.compile_template(db, template_id)
        if not result.get("ok"):
            return JSONResponse(
                status_code=500,
                content={"error": "compile failed before ATS check", "compile": result},
            )
    family = template_id.split("-", 1)[0]
    return ats_mod.check_with_cache(pdf, db, family)


# Publishing — real status audit (read-only, dry-run by default)
@app.get("/api/publishing/audit")
async def publishing_audit():
    import subprocess
    import sys
    from datetime import datetime, timezone

    REPO = Path(__file__).resolve().parents[2]
    RESUME = REPO / "resume"
    BUILD = latex_mod.BUILD
    db = load_db()
    db_mtime = DB_PATH.stat().st_mtime if DB_PATH.exists() else 0

    def iso(ts: float) -> str:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")

    def git(*args: str) -> str | None:
        try:
            r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, timeout=15)
            return (r.stdout or "").strip() if r.returncode == 0 else None
        except Exception:  # noqa: BLE001
            return None

    def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
        try:
            r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=60)
            return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
        except Exception as e:  # noqa: BLE001
            return -1, f"{type(e).__name__}: {e}"

    modules: list[dict] = []

    # 1. profile README vs generator (--check, no write)
    code, out = run([sys.executable, "generate_profile_readme.py", "--check"], RESUME / "scripts")
    readme = REPO / "README.md"
    if code == 0:
        m_status, m_detail = "synced", "README matches generator output"
    elif code == 1:
        m_status, m_detail = "stale", f"drift detected ({out.splitlines()[0] if out else 'differs'})"
    else:
        m_status, m_detail = "error", out[-200:] or "check failed"
    modules.append({
        "id": "profile-readme",
        "name": "GitHub profile README",
        "kind": "markdown",
        "status": m_status,
        "detail": m_detail,
        "last_sync": iso(readme.stat().st_mtime) if readme.exists() else None,
        "url": "https://github.com/AliNikkhah2001/AliNikkhah2001",
        "actions": ["python3 resume/scripts/generate_profile_readme.py"] if m_status != "synced" else [],
    })

    # 2. compiled CV PDFs (Templates tab outputs)
    pdfs = sorted(p for p in BUILD.glob("*/out.pdf") if p.is_file())
    stale_pdfs = [p for p in pdfs if p.stat().st_mtime < db_mtime]
    if not pdfs:
        p_status, p_detail = "missing", "0 templates compiled"
    elif stale_pdfs:
        p_status = "stale"
        p_detail = f"{len(pdfs)} compiled, {len(stale_pdfs)} older than the last career_db edit"
    else:
        p_status, p_detail = "synced", f"{len(pdfs)} compiled PDFs, all newer than career_db"
    modules.append({
        "id": "cv-pdfs",
        "name": "Compiled CV PDFs",
        "kind": "pdf",
        "status": p_status,
        "detail": p_detail,
        "last_sync": iso(max((p.stat().st_mtime for p in pdfs), default=0)) if pdfs else None,
        "url": None,
        "actions": ["Templates tab → Compile missing / stale"] if p_status != "synced" else [],
    })

    # 3. rendercv variant YAMLs (legacy inputs for standalone rendercv usage)
    yamls = sorted((RESUME / "rendercv").glob("*.yaml"))
    stale_yamls = [y for y in yamls if y.stat().st_mtime < db_mtime]
    if not yamls:
        y_status, y_detail = "missing", "no variant YAMLs in resume/rendercv/"
    elif stale_yamls:
        y_status = "stale"
        y_detail = f"{len(yamls)} YAMLs, {len(stale_yamls)} older than career_db (dashboard edits not regenerated)"
    else:
        y_status, y_detail = "synced", f"{len(yamls)} variant YAMLs up to date"
    modules.append({
        "id": "rendercv-yamls",
        "name": "RenderCV variant YAMLs",
        "kind": "yaml",
        "status": y_status,
        "detail": y_detail,
        "last_sync": iso(max((y.stat().st_mtime for y in yamls), default=0)) if yamls else None,
        "url": None,
        "actions": ["python3 resume/scripts/cv_to_rendercv.py"] if y_status == "stale" else [],
    })

    # 4. structured API exporters
    modules.append({
        "id": "api-exports",
        "name": "Structured exports",
        "kind": "json/csv",
        "status": "ready",
        "detail": "JSON Resume · RenderCV · GitHub README · LinkedIn · Reactive Resume · JobOps CSV",
        "last_sync": None,
        "url": None,
        "actions": ["GET /api/export/json-resume", "GET /api/export/reactive-resume", "GET /api/export/jobops"],
    })

    # 5. CI workflows
    wf_dir = REPO / ".github" / "workflows"
    wfs = sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml"))
    wf_parts = []
    for wf in wfs:
        stamp = git("log", "-1", "--format=%cI", "--", str(wf.relative_to(REPO)))
        wf_parts.append(f"{wf.name} (last change {stamp[:10] if stamp else 'unknown'})")
    modules.append({
        "id": "ci-workflows",
        "name": "GitHub Actions CV builds",
        "kind": "ci",
        "status": "ready" if wfs else "missing",
        "detail": "; ".join(wf_parts) if wf_parts else "no workflows found",
        "last_sync": None,
        "url": "https://github.com/AliNikkhah2001/AliNikkhah2001/actions",
        "actions": [],
    })

    # 6. git working tree
    porcelain = git("status", "--porcelain")
    dirty = len([ln for ln in (porcelain or "").splitlines() if ln.strip()]) if porcelain is not None else None
    unpushed = git("rev-list", "--count", "@{u}..HEAD")
    if dirty is None:
        g_status, g_detail = "error", "git status failed"
    elif dirty or (unpushed and unpushed.isdigit() and int(unpushed) > 0):
        g_status = "stale"
        bits = [f"{dirty} uncommitted files" if dirty else None]
        if unpushed and unpushed.isdigit() and int(unpushed) > 0:
            bits.append(f"{unpushed} unpushed commits")
        g_detail = ", ".join(b for b in bits if b)
    else:
        g_status, g_detail = "synced", "clean working tree, everything pushed"
    modules.append({
        "id": "git-state",
        "name": "Git working tree",
        "kind": "git",
        "status": g_status,
        "detail": g_detail,
        "last_sync": None,
        "url": "https://github.com/AliNikkhah2001/AliNikkhah2001",
        "actions": ["git status", "git add -A && git commit -m '...'", "git push"] if g_status == "stale" else [],
    })

    # 7. GitHub Pages (external repository)
    modules.append({
        "id": "github-pages",
        "name": "GitHub Pages portfolio",
        "kind": "site",
        "status": "external",
        "detail": "separate repository (alinikkhah2001.github.io) — not audited from this repo",
        "last_sync": None,
        "url": "https://alinikkhah2001.github.io",
        "actions": [],
    })

    dry_run = [
        "# DRY RUN — planned sync actions, nothing was executed:",
        *[f"  {a}" for m in modules for a in m["actions"]],
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "db_fingerprint": latex_mod.db_hash(db),
        "modules": modules,
        "dry_run": dry_run,
    }


# Search
@app.get("/api/search")
async def search(q: str = ""):
    db = load_db()
    q = q.lower()
    results = {"positions": [], "achievements": [], "organizations": [], "skills": [], "projects": []}

    for p in db.positions:
        if q in p.title.lower() or q in (p.summary or "").lower():
            results["positions"].append(p)

    for a in db.achievements:
        if q in a.text.lower():
            results["achievements"].append(a)

    for o in db.organizations:
        if q in o.name.lower():
            results["organizations"].append(o)

    for s in db.skills:
        if q in s.name.lower():
            results["skills"].append(s)

    for pr in db.projects:
        if q in pr.title.lower() or q in (pr.description or "").lower():
            results["projects"].append(pr)

    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)