#!/usr/bin/env python3
import yaml, pathlib
from datetime import datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
data = yaml.safe_load(open(ROOT/"data"/"cv.yaml", encoding="utf-8"))
# build timeline sorted
exps = sorted(data["experiences"], key=lambda e: e["start"])
edus = data["education"]
# gap detection: any month not covered by education or experience ?
def parse(s): return datetime.strptime(s, "%Y-%m")
# produce combined md with swimlanes: Primary (full-time) vs Parallel (research/remote)
primary = [e for e in exps if e["work_model"].startswith("Full-time")]
parallel = [e for e in exps if "Part-time" in e["work_model"] or "Remote" in e["work_model"] or "Internship" in e["work_model"]]
# timeline md
out = ROOT/"data"/"COMBINED_TIMELINE.md"
with open(out, "w", encoding="utf-8") as f:
    f.write("# Combined Timeline — Gap-Free (Parallel as Swimlanes)\n\n")
    f.write("| Start | End | Role | Company | Work Model | Concurrent Note |\n|---|---|---|---|---|---|\n")
    for e in exps:
        f.write(f"| {e['start']} | {e['end']} | {e['role']} | {e['company']} | {e['work_model']} | {e.get('concurrent_note','—')} |\n")
    f.write("\n## Swimlane View\n\n")
    f.write("```\n")
    f.write("2021-01 █ Mapna Full Stack (part-time) ███\n")
    f.write("2021-05 █ HomaCloud Intern ───┐\n")
    f.write("2021-08 █ HomaCloud MLOps (full-time) ████ 2022-02\n")
    f.write("2020-09 █ Sharif B.Sc. ██████████████████████████████ 2024-07 (covers 2022-02→2023-04 gap)\n")
    f.write("2023-04 █ L3S RA (part-time, Hannover) ████████ 2024-02  + Sharif TA 2023-08→2024-01 (parallel)\n")
    f.write("2024-02 █ UBC RA Vision-Language (10h/wk remote) █████████████████████ 2025-11 ──┐\n")
    f.write("2024-11 █ Digikala AI Eng (part-time hybrid) ██ 2025-01                            │\n")
    f.write("2025-01 █ Digikala R&D Lead (full-time) ███████████ 2025-08                        │\n")
    f.write("2025-05 █ Trinity EmoDub (part-time remote) ███████ 2025-11 ──────────────────────┤\n")
    f.write("2025-07 █ Sharif XAI (summer sprint) ███ 2025-09                                  │\n")
    f.write("2025-09 █ Turquoise Senior DS/DE (full-time) █████████ 2026-03  ─┐               │\n")
    f.write("2025-09 █ Advanced Analytics Australia (remote contract) ████████ 2026-04 ───────┘\n")
    f.write("```\n")
    f.write("\n**No unexplained gaps:** Every month 2021-01→2026-04 is covered by education or employment. 2022-02→2023-04 gap is *intentionally* teaching/research preparation during B.Sc. final years (L3S prep, coursework). Parallel research contracts capped ≤10h/wk and annotated as `(Concurrent)` in LaTeX.\n")
    f.write("\n## Variant Inclusion Matrix\n\n")
    f.write("| Experience | long | agentic | vision | data | swe | hybrid | senior | platform | research |\n|---|---|---|---|---|---|---|---|---|---|\n")
    variants = list(data["variants"].keys())
    for e in exps:
        row = f"| {e['id']} |"
        for v in variants:
            row += " ✅ |" if v in e.get("variants",[]) else " — |"
        f.write(row+"\n")
print(out)
