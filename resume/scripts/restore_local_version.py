#!/usr/bin/env python3
"""Reconstruct a deduplicated local CV snapshot in a new directory."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    manifest = json.loads((REPO / "archive/local-versions/manifest.json").read_text())
    files = [entry for entry in manifest["files"] if entry["source"] == args.version]
    if not files:
        parser.error("Unknown version. See archive/local-versions/README.md.")
    if args.destination.exists():
        parser.error("Destination must be a new directory.")
    for entry in files:
        source = REPO / entry["stored_at"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Archive checksum mismatch: {source}")
    args.destination.mkdir(parents=True)
    for entry in files:
        destination = args.destination / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / entry["stored_at"], destination)
    print(f"Restored {len(files)} files into {args.destination}")


if __name__ == "__main__":
    main()
