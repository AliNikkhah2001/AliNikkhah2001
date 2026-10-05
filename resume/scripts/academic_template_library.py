#!/usr/bin/env python3
"""Import pinned, licensed upstream academic templates and build a PDF gallery.

Use --fetch once (requires gh), --build to compile locally, --verify to check
upstream hashes. Originals are kept verbatim under upstream/. Build products
live in .build/ and selected previews in the library's previews/ directory.
"""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

REPO = Path(__file__).resolve().parents[2]
LIBRARY = REPO / "resume/academic/template-library"
CATALOG = LIBRARY / "catalog.json"
SELECTION = [
    ("11-boeing", "Boeing academic CV", "gboeing/cv", "cv-gboeing.tex", "pdflatex", "Traditional single-column academic CV; understated rules and comprehensive scholarly sections."),
    ("12-simplecv", "Simple-CV", "dcetin/Simple-CV", "main.tex", "pdflatex", "Minimal sectioned CV with BibLaTeX publications and modular content files."),
    ("13-simple-resume", "Simple Resume / CV", "zachscrivena/simple-resume-cv", "CV.tex", "xelatex", "Monochrome academic CV with a narrow date column and bundled fonts."),
    ("14-pseudomanifold", "Pseudomanifold academic CV", "Pseudomanifold/latex-cv", "CV.tex", "lualatex", "Restrained typography and an academic publication list."),
    ("15-cleancv", "CleanCV", "giladturok/CleanCV", "main.tex", "pdflatex", "Modular, minimal academic CV with bibliography support and clear section hierarchy."),
    ("16-prometheus", "Prometheus CV", "chrisby/prometheusCV", "main.tex", "xelatex", "Research-focused modular layout with separate education, service and publications files."),
    ("17-phd-application", "PhD application CV", "salmanmaq/academic-cv-template", "example.tex", "pdflatex", "Compact graduate-application layout with academic sections and a dedicated class."),
    ("18-mcdowell", "McDowell CV", "dnl-blkv/mcdowell-cv", "McDowell_CV_Template.tex", "xelatex", "Black-and-white serif layout; a compact option for an academic/industry crossover CV."),
    ("19-uieda", "Uieda academic CV", "leouieda/cv", "cv.tex", "xelatex", "Long-form academic CV with a clean single-column structure and strong scholarly hierarchy."),
    ("20-academia", "Academia CV", "zhuokaizhao/academia_cv_template", "main.tex", "xelatex", "Academic section structure with restrained color and compact dated entries."),
]


def gh_json(endpoint):
    return json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch():
    if CATALOG.exists():
        raise SystemExit("Pinned catalog already exists; imports are intentionally immutable.")
    LIBRARY.mkdir(parents=True, exist_ok=True)
    catalog = []
    for slug, name, repository, entrypoint, engine, description in SELECTION:
        metadata = gh_json(f"repos/{repository}")
        license_info = metadata.get("license")
        if not license_info or license_info["spdx_id"] == "NOASSERTION":
            raise ValueError(f"Explicit license required: {repository}")
        revision = gh_json(f"repos/{repository}/commits/{metadata['default_branch']}")["sha"]
        destination = LIBRARY / "upstream" / slug
        if destination.exists():
            raise ValueError(f"Refusing to overwrite upstream source: {destination}")
        payload = subprocess.check_output(["gh", "api", f"repos/{repository}/tarball/{revision}"])
        files = {}
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                relative = PurePosixPath(*PurePosixPath(member.name).parts[1:])
                if not relative.parts or ".." in relative.parts or relative.is_absolute():
                    raise ValueError(f"Invalid archive path: {member.name}")
                if any(part.startswith(".") for part in relative.parts):
                    continue
                # Upstream compiled examples/screenshots are included as references;
                # our independently compiled previews are stored separately.
                if member.size > 20_000_000:
                    raise ValueError(f"Unexpected large upstream asset: {relative}")
                target = destination / str(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
                files[str(relative)] = sha256(target)
        if not (destination / entrypoint).is_file():
            raise ValueError(f"Missing entrypoint: {repository}/{entrypoint}")
        catalog.append({"id": slug, "name": name, "repository": repository,
                        "url": f"https://github.com/{repository}", "revision": revision,
                        "license": license_info["spdx_id"], "entrypoint": entrypoint,
                        "engine": engine, "description": description, "files": files})
        print(f"Imported {slug}: {len(files)} files, {license_info['spdx_id']}, {revision[:10]}", flush=True)
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    document(catalog)


def verify(catalog):
    count = 0
    for template in catalog:
        for relative, expected in template["files"].items():
            path = LIBRARY / "upstream" / template["id"] / relative
            if sha256(path) != expected:
                raise ValueError(f"Upstream file modified: {path}")
            count += 1
    print(f"Verified {count} original upstream files across {len(catalog)} templates.")
    results_path = LIBRARY / "build-results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text())
        if len(catalog) != 10:
            raise ValueError("Expected exactly ten additional templates")
        for template in catalog:
            result = results[template["id"]]
            if result["status"] != "success" or result["source_revision"] != template["revision"]:
                raise ValueError(f"Missing or stale successful build: {template['id']}")
            for extension, magic in (("pdf", b"%PDF-"), ("png", b"\x89PNG\r\n\x1a\n")):
                path = LIBRARY / "previews" / f"{template['id']}.{extension}"
                if not path.read_bytes().startswith(magic):
                    raise ValueError(f"Invalid preview: {path}")

        class Links(HTMLParser):
            def handle_starttag(self, tag, attrs):
                for key, value in attrs:
                    if key in ("href", "src") and value and not value.startswith(("https://", "http://", "#")):
                        if not (LIBRARY / value).is_file():
                            raise ValueError(f"Broken gallery link: {value}")

        Links().feed((LIBRARY / "index.html").read_text())
        print("Verified all ten successful builds, PDF/PNG previews, and local gallery links.")


def document(catalog, results=None):
    compatibility = json.loads((LIBRARY / "compatibility.json").read_text())
    lines = ["# Ten additional minimal academic LaTeX CV templates", "",
             "Templates **11–20** supplement the existing ten house themes in `../themes/`.",
             "These are actual upstream template sources, pinned to commits with their licenses retained.",
             "The previews show the upstream authors' **sample content**, not Ali's CV data.", "",
             "[Open the visual gallery](index.html) · [Build results](build-results.json)", "",
             "![Overview of all ten templates](previews/overview.png)", "",
             "| # | Template / source | Style | License | PDF |",
             "|---|---|---|---|---|"]
    cards = []
    for template in catalog:
        slug = template["id"]
        lines.append(f"| {slug.split('-')[0]} | [{template['name']}]({template['url']}) | {template['description']} | {template['license']} | [Preview](previews/{slug}.pdf) |")
        engine = compatibility.get(slug, {}).get("engine", template["engine"])
        note = compatibility.get(slug, {}).get("note", "")
        cards.append(f'<article><a href="previews/{slug}.pdf"><img loading="lazy" src="previews/{slug}.png" alt="{html.escape(template["name"])} first page"></a><h2>{html.escape(template["name"])}</h2><p>{html.escape(template["description"])}</p><p><a href="previews/{slug}.pdf">PDF preview</a> · <a href="{template["url"]}">Upstream source</a></p><small>{template["license"]} · {engine}</small><p><small>{html.escape(note)}</small></p></article>')
    lines += ["", "## Build all previews", "", "Run from the repository root:", "", "```bash",
              "python3 resume/scripts/academic_template_library.py --verify",
              "python3 resume/scripts/academic_template_library.py --build", "```", "",
              "Requires a full TeX Live installation (pdfLaTeX, XeLaTeX, LuaLaTeX, latexmk, biber),",
              "Poppler (`pdfinfo`, `pdftoppm`), and Pillow (`pip install Pillow`) for the overview image.",
              "The gallery uses free fonts available with TeX Live.",
              "See `build-results.json` for the exact build command and page count for each preview.",
              "Use `--only 11-boeing` to build one design.", "",
              "## Edit a template", "",
              "Copy its `upstream/<id>/` directory into your working area and edit the catalog's entrypoint.",
              "Keep the license and attribution with any derivative. The vendored originals stay immutable",
              "so the hash check can distinguish local adaptations from upstream code.",
              "`catalog.json` records source URL, exact commit, license, compiler, and SHA-256 hashes.",
              "The original house themes and `resume/data/cv.yaml` remain the working CV system.", ""]
    lines += ["## Portable build adjustments", "",
              "`compatibility.json` records small, reproducible changes applied only to build copies.",
              "Font substitutions affect preview typography; upstream source files remain byte-for-byte intact.",
              "The ready-to-edit portable sources are left in `.build/academic-templates/<id>/source/` after a build.", ""]
    lines += [f"- **{slug}:** {settings['note']}" for slug, settings in compatibility.items()]
    lines.append("")
    (LIBRARY / "README.md").write_text("\n".join(lines))
    (LIBRARY / "index.html").write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Minimal Academic CV Templates — 11–20</title><style>
body{font:16px/1.5 system-ui,sans-serif;margin:0;background:#f4f3ef;color:#202824}
header,main{max-width:1200px;margin:auto;padding:2rem}h1{font:2.2rem Georgia,serif;margin:0}header p{max-width:760px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;padding-top:0}
article{background:white;border:1px solid #d9ddd8;padding:1rem;border-radius:6px}h2{font:1.2rem Georgia,serif}
img{width:100%;aspect-ratio:0.77;object-fit:contain;object-position:top;background:#fafafa;border:1px solid #eee}
a{color:#245d49}small{color:#626a65}</style></head><body>
<header><h1>Minimal academic CVs</h1><p>Ten additional, licensed LaTeX templates. Previews use upstream sample content. Select a PDF to inspect its full layout; use the source link for attribution and documentation.</p></header><main>
""" + "\n".join(cards) + "\n</main></body></html>\n")
    if all((LIBRARY / "previews" / f"{item['id']}.png").exists() for item in catalog):
        from PIL import Image, ImageDraw
        sheet = Image.new("RGB", (1800, 1080), "#f4f3ef")
        draw = ImageDraw.Draw(sheet)
        for index, item in enumerate(catalog):
            x, y = (index % 5) * 360, (index // 5) * 540
            with Image.open(LIBRARY / "previews" / f"{item['id']}.png") as image:
                image.thumbnail((330, 475))
                sheet.paste(image, (x + (360 - image.width) // 2, y + 15))
            draw.text((x + 15, y + 500), f"{item['id'].split('-')[0]}  {item['name']}", fill="#202824", font_size=16)
        sheet.save(LIBRARY / "previews" / "overview.png")


def build(catalog, only=None):
    compatibility = json.loads((LIBRARY / "compatibility.json").read_text())
    previews = LIBRARY / "previews"
    previews.mkdir(exist_ok=True)
    results_path = LIBRARY / "build-results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else {}
    failed = []
    for template in catalog:
        slug = template["id"]
        if only and slug != only:
            continue
        source = REPO / ".build" / "academic-templates" / slug / "source"
        shutil.copytree(LIBRARY / "upstream" / slug, source, dirs_exist_ok=True)
        adjustments = compatibility.get(slug, {})
        for relative, replacements in adjustments.get("patches", {}).items():
            path = source / relative
            text = path.read_text()
            for old, new in replacements:
                if old not in text:
                    raise ValueError(f"Compatibility patch does not match {slug}/{relative}: {old}")
                text = text.replace(old, new)
            path.write_text(text)
        output = REPO / ".build" / "academic-templates" / slug / "output"
        output.mkdir(parents=True, exist_ok=True)
        engine = adjustments.get("engine", template["engine"])
        engine_flag = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}[engine]
        command = ["latexmk", "-norc", engine_flag, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", f"-outdir={output}", template["entrypoint"]]
        completed = subprocess.run(command, cwd=source, capture_output=True, text=True)
        (output / "build.log").write_text(completed.stdout + completed.stderr)
        pdf = output / Path(template["entrypoint"]).with_suffix(".pdf").name
        if completed.returncode or not pdf.exists():
            failed.append(slug)
            results[slug] = {"status": "failed", "engine": engine}
            print(f"FAILED {slug}: see {output / 'build.log'}", flush=True)
            continue
        shutil.copy2(pdf, previews / f"{slug}.pdf")
        info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
        pages = int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))
        subprocess.run(["pdftoppm", "-f", "1", "-singlefile", "-scale-to", "1000", "-png", str(pdf), str(previews / slug)], check=True)
        results[slug] = {"status": "success", "engine": engine, "pages": pages,
                         "command": [arg if not arg.startswith("-outdir=") else "-outdir=<build-directory>" for arg in command],
                         "source_revision": template["revision"], "adjustments": adjustments.get("note", "None")}
        print(f"Built {slug}: {pages} pages", flush=True)
    results_path.write_text(json.dumps(results, indent=2) + "\n")
    document(catalog, results)
    if failed:
        raise SystemExit(f"Templates needing build fixes: {', '.join(failed)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--only", choices=[row[0] for row in SELECTION])
    args = parser.parse_args()
    if args.fetch:
        fetch()
    catalog = json.loads(CATALOG.read_text())
    if args.verify:
        verify(catalog)
    if args.build:
        build(catalog, args.only)


if __name__ == "__main__":
    main()
