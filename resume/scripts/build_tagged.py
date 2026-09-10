#!/usr/bin/env python3
"""
Tag-driven builder: data/cv.yaml -> LaTeX fragments + JSON + Jekyll data
Usage:
  python scripts/build_tagged.py --variant all
  python scripts/build_tagged.py --variant agentic --pages 2
Generates: industrial/segments/generated/<variant>/experience.tex etc.
           compiled long union timeline -> data/timeline.md
"""
import argparse, pathlib, yaml, re, os, textwrap
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cv.yaml"
GEN_ROOT = ROOT / "industrial" / "segments" / "generated"
JEKYLL_DATA = ROOT.parents[1] / "alinikkhah2001.github.io" / "_data" / "cv_generated.yaml"
LONG_TEX = ROOT / "industrial" / "long_union.tex"

def load():
    with open(DATA, encoding="utf-8") as f: return yaml.safe_load(f)

def tex_escape(s): return s.replace("&", r"\&").replace("%", r"\%")

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def fmt_period(start, end):
    def f(s):
        if s == "present": return "Present"
        y, m = s.split("-")
        return f"{MONTHS[int(m)-1]} {y}"
    return f"{f(start)} == {f(end)}"

def render_experience(exp):
    period = fmt_period(exp['start'], exp['end'])
    # concurrent note as small italic
    concurrent = exp.get("concurrent_note", "")
    role = tex_escape(exp["role"])
    if concurrent:
        role += r" \textit{\scriptsize (Concurrent)}"
    skills = ", ".join(exp.get("skills", [])[:8])
    lines = []
    lines.append(f"\\resumeSubheading")
    lines.append(f"  {{{tex_escape(exp['company'])}}}{{{tex_escape(exp['location'])}}}")
    lines.append(f"  {{{role}}}{{{period}}}")
    bullets = exp.get("bullets", [])
    if bullets or skills or concurrent:
        lines.append(r"\begin{resumeItemList}")
        for b in bullets:
            lines.append(f"  \\resumeItem{{{tex_escape(b)}}}")
        if skills:
            lines.append(f"  \\resumeItem{{\\textit{{Stack:}} {tex_escape(skills)}}}")
        if concurrent:
            lines.append(f"  \\resumeItem{{\\textit{{{tex_escape(concurrent)}}}}}")
        lines.append(r"\end{resumeItemList}")
    lines.append("")
    return "\n".join(lines)

def build_variant(data, variant):
    vinfo = data["variants"][variant]
    exps = [e for e in data["experiences"] if variant in e.get("variants", []) or variant=="long" and "long" in e.get("variants",[])]
    # sort newest first
    exps.sort(key=lambda e: e["start"], reverse=True)
    out_dir = GEN_ROOT / variant
    out_dir.mkdir(parents=True, exist_ok=True)
    # experience
    with open(out_dir / "experience.tex", "w", encoding="utf-8") as f:
        f.write(f"% AUTO-GENERATED from data/cv.yaml variant={variant} — do not edit manually\n")
        for e in exps: f.write(render_experience(e)+"\n")
    # summary
    name = vinfo["label"]
    with open(out_dir / "summary.tex", "w", encoding="utf-8") as f:
        f.write(f"% summary for {variant}\n")
        f.write(f"\\small{{{tex_escape(data['basics']['summary'])} — Variant: {tex_escape(name)}}}\n")
    # skills
    with open(out_dir / "skills.tex", "w", encoding="utf-8") as f:
        s=data["skills"]
        f.write("\\small{\\item{\n")
        f.write(f"  \\textbf{{Languages}}: {', '.join(s['languages'])} \\\\\n")
        f.write(f"  \\textbf{{ML/Vision}}: {', '.join(s['ml_vision'][:8])} \\\\\n")
        f.write(f"  \\textbf{{Agentic}}: {', '.join(s['agentic'][:6])} \\\\\n")
        if 'llm_serving' in s:
            f.write(f"  \\textbf{{LLM Serving/GPU}}: {', '.join(s['llm_serving'][:5])} \\\\\n")
        f.write(f"  \\textbf{{Data/MLOps}}: {', '.join(s['data_mlop'][:6])}\n}}\n")
    # projects + publications (single source: data/cv.yaml research_projects)
    with open(out_dir / "projects.tex", "w", encoding="utf-8") as f:
        f.write(f"% AUTO-GENERATED from data/cv.yaml variant={variant} — do not edit manually\n")
        for rp in data.get("research_projects", []):
            f.write("\\resumeSubheading\n")
            f.write(f"  {{{tex_escape(rp['org'])}}}{{{tex_escape(rp['period'])}}}\n")
            f.write(f"  {{{tex_escape(rp['title'])}}}{{ }}\n")
            bullets = rp.get("bullets", [])
            if bullets:
                f.write("\\begin{resumeItemList}\n")
                for b in bullets:
                    f.write(f"  \\resumeItem{{{tex_escape(b)}}}\n")
                f.write("\\end{resumeItemList}\n")
            f.write("\n")
        for pub in data.get("publications", []):
            f.write(f"\\resumeItem{{{tex_escape(pub['title'])} — \\textit{{{tex_escape(pub['venue'])}}}, {pub['year']}}}\n")
    print(f"[build] {variant}: {len(exps)} experiences -> {out_dir}")

def build_all(data):
    for v in data["variants"]: build_variant(data, v)
    # also export Jekyll data copy
    try:
        JEKYLL_DATA.parent.mkdir(parents=True, exist_ok=True)
        import shutil; shutil.copy(DATA, JEKYLL_DATA)
        print(f"[jekyll] copied to {JEKYLL_DATA}")
    except Exception as e: print(f"[jekyll] skip {e}")
    # generate long markdown timeline
    tl = ROOT / "data" / "timeline_gapfree.md"
    with open(tl, "w", encoding="utf-8") as f:
        f.write("# Gap-free Combined Timeline (parallel shown as swimlanes)\n\n")
        f.write("| Period | Role | Org | Concurrency |\n|---|---|---|---|\n")
        for e in sorted(data["experiences"], key=lambda x: x["start"]):
            conc = "—"
            if e.get("concurrent_with"): conc = ", ".join(e["concurrent_with"])
            f.write(f"| {e['start']} – {e['end']} | {e['role']} | {e['company']} | {conc} |\n")
        f.write("\n> Parallel remote contracts (UBC, Trinity, Sharif XAI, Advanced Analytics) shown with concurrency notes; no unexplained gaps.\n")
    print(f"[timeline] {tl}")
    # long union tex stub
    LONG_TEX.write_text(textwrap.dedent(r"""
    % Long Union CV — includes all tagged experiences (10 pages)
    % Build: pdflatex long_union.tex
    \documentclass[letterpaper,11pt]{article}
    \usepackage[empty]{fullpage}\usepackage{titlesec}\usepackage{hyperref}\usepackage{enumitem}\usepackage{tabularx}\usepackage{etoolbox}\usepackage{microtype}\usepackage{lmodern}
    \addtolength{\oddsidemargin}{-0.5in}\addtolength{\evensidemargin}{-0.5in}\addtolength{\textwidth}{1.0in}\addtolength{\topmargin}{-.5in}\addtolength{\textheight}{1.0in}
    \titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\titlerule \vspace{-5pt}]
    \newcommand{\resumeItem}[1]{\item\small{#1 \vspace{-1pt}}}
    \newcommand{\resumeSubheading}[4]{\vspace{-2pt}\item\begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}\textbf{#1} & \small #2 \\ \textit{\small#3} & \textit{\small #4} \\\end{tabular*}\vspace{-7pt}}
    \newenvironment{resumeSubHeadingList}{\begin{itemize}[leftmargin=0.15in, label={}]}{\end{itemize}}
    \newenvironment{resumeItemList}{\begin{itemize}[leftmargin=0.2in, topsep=2pt, itemsep=1pt, parsep=0pt]}{\end{itemize}\vspace{-3pt}}
    \renewcommand\labelitemii{--}
    \begin{document}
    \begin{center}\Huge\textsc{Ali Nikkhah} \\ \small Tehran | alinkkh9@gmail.com | +98 991 296 3951 | alinikkhah2001.github.io\end{center}
    \section{Summary}\small{Union 10-page CV — all experiences, gap-free timeline with parallel annotations.}\vspace{4pt}
    \section{Professional Experience (Union)}\begin{itemize}[leftmargin=0.15in,label={}]
    \input{segments/generated/long/experience.tex}
    \end{itemize}
    \section{Education}\begin{resumeSubHeadingList}\input{segments/common/education.tex}\end{resumeSubHeadingList}
    \end{document}
    """).strip())
    print(f"[long] stub at {LONG_TEX}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="all", help="variant name or all")
    args = ap.parse_args()
    data = load()
    if args.variant == "all": build_all(data)
    else: build_variant(data, args.variant)
