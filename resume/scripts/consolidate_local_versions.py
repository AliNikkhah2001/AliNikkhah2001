#!/usr/bin/env python3
"""Losslessly inventory/import the four local CV collections, without overwrites.

Run without --apply to preview. Archives are content-deduplicated; the manifest
can reconstruct every source collection, including PDFs and uncommitted edits.
Git internals, macOS metadata, and disposable TeX build files are excluded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "archive" / "local-versions"
VERSIONS = ["Resume 3", "Resume 3_v2_2026-08-14", "Resume_Detailed", "Resume"]
SLUGS = ["resume-3", "resume-3-v2-2026-08-14", "resume-detailed", "resume"]
BUILD_SUFFIXES = {".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk", ".synctex.gz"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored(path):
    if path.name == ".DS_Store" or path.name.startswith("._"):
        return "macOS metadata"
    if any(path.name.endswith(suffix) for suffix in BUILD_SUFFIXES):
        return "disposable TeX build output"
    if ".git" in path.parts or "__pycache__" in path.parts:
        return "Git/Python internal metadata"
    return None


def verify():
    manifest = json.loads((ARCHIVE / "manifest.json").read_text())
    checked = set()
    for entry in manifest["files"]:
        path = REPO / entry["stored_at"]
        if path not in checked:
            if digest(path) != entry["sha256"]:
                raise ValueError(f"Archive hash mismatch: {path}")
            checked.add(path)
    print(f"Verified {len(manifest['files'])} source files in {len(checked)} unique archived files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=REPO.parent)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    if (ARCHIVE / "manifest.json").exists():
        raise SystemExit("Archive already exists; use --verify instead of reimporting.")
    manifest = {
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "policy": "Keep GitHub working data; import missing Resume 3 files; archive all distinct local content.",
        "files": [], "excluded": [],
    }
    hashes = {}
    stats = []
    for name, slug in zip(VERSIONS, SLUGS):
        source = args.source_root / name
        if not source.is_dir():
            raise SystemExit(f"Missing source: {source}")
        count = unique = conflicts = imported = size = 0
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            reason = ignored(relative)
            if reason:
                if ".git" not in relative.parts:
                    manifest["excluded"].append({"source": name, "path": str(relative), "reason": reason})
                continue
            if path.is_symlink():
                raise ValueError(f"Review symlink before import: {path}")
            checksum = digest(path)
            target = REPO / "resume" / relative
            matching = target.is_file() and digest(target) == checksum
            # Only the most developed local version extends the live tree.
            # Earlier templates stay in reconstructable source archives.
            copy_live = name == "Resume 3" and not target.exists() and ".github" not in relative.parts
            status = "identical" if matching else "conflict" if target.exists() else "local-only"
            conflicts += status == "conflict"
            if checksum not in hashes:
                stored = ARCHIVE / slug / relative
                hashes[checksum] = str(stored.relative_to(REPO))
                unique += 1
                size += path.stat().st_size
                if args.apply:
                    stored.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, stored)
            if copy_live:
                imported += 1
                if args.apply:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
            manifest["files"].append({
                "source": name, "path": str(relative), "sha256": checksum,
                "stored_at": hashes[checksum], "status": status, "imported_to_live": copy_live,
            })
            count += 1
        stats.append((name, count, unique, conflicts, imported, size))
        print(f"{name}: {count} files, {unique} unique, {conflicts} differences, {imported} live additions, {size / 1e6:.2f} MB")
    if not args.apply:
        print("Dry run only. Re-run with --apply to consolidate.")
        return
    (ARCHIVE / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    lines = [
        "# Consolidated local CV versions", "",
        "The working CV lives in `resume/`. The GitHub version takes precedence for conflicting facts.",
        "This archive retains every distinct source document and PDF from the four local folders,",
        "including uncommitted work. Identical files are stored once. Original folders are untouched.", "",
        "| Source folder | Files | Unique files stored | Different from working tree | Live additions |",
        "|---|---:|---:|---:|---:|",
    ]
    lines += [f"| {n} | {c} | {u} | {d} | {i} |" for n, c, u, d, i, _ in stats]
    lines += ["", "## Finding an older version", "",
              "`manifest.json` maps **every original path** to its archived `stored_at` path and SHA-256.",
              "Folders are deduplicated, so an individual archive folder is not a standalone build.",
              "To reconstruct a complete version in a new directory:", "", "```bash",
              "python resume/scripts/restore_local_version.py 'Resume_Detailed' /tmp/restored-cv", "```", "",
              "Verify all stored content with:", "", "```bash",
              "python resume/scripts/consolidate_local_versions.py --verify", "```", "",
              "## Conflict policy", "",
              "Local wording, dates, metrics, projects, and templates remain available for the next content review.",
              "Conflicting facts are not silently combined. Local-only files from `Resume 3` extend the live tree.",
              "Older CI workflows are archived as reference rather than activated.",
              "Excluded OS metadata and disposable TeX artifacts are listed in the manifest; `.git` histories remain in the original folders.", ""]
    (ARCHIVE / "README.md").write_text("\n".join(lines))
    verify()


if __name__ == "__main__":
    main()
