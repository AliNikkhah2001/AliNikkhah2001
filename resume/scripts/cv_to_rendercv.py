#!/usr/bin/env python3
"""Regenerate resume/rendercv/Ali_Nikkhah_<variant>.yaml from career_db.json.

Single source of truth is career-dashboard/career_db.json (edited via the
dashboard). This script delegates to the API's CareerDatabase.to_rendercv()
so the standalone YAMLs always match the live /api/export/rendercv/{variant}
output (RenderCV v2 schema).
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "career-dashboard" / "api"))

import yaml  # noqa: E402

from models import CareerDatabase  # noqa: E402

OUT_DIR = REPO / "resume" / "rendercv"
OUT_DIR.mkdir(exist_ok=True)
SCHEMA_LINE = "# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json\n"


def main() -> None:
    db_path = REPO / "career-dashboard" / "career_db.json"
    db = CareerDatabase.model_validate_json(db_path.read_text(encoding="utf-8"))
    for variant in db.variants:
        rc = db.to_rendercv(variant.id)
        out = OUT_DIR / f"Ali_Nikkhah_{variant.id}.yaml"
        with open(out, "w", encoding="utf-8") as f:
            f.write(SCHEMA_LINE)
            yaml.dump(rc, f, sort_keys=False, allow_unicode=True)
        n_exp = len(rc["cv"]["sections"].get("experience", []))
        print(f"[rendercv] {variant.id} -> {out} ({n_exp} exps)")
    print("done rendercv conversion")


if __name__ == "__main__":
    main()
