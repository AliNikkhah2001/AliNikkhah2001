#!/usr/bin/env python3
"""Compile markdown resume -> LaTeX PDF in multiple pandoc/pdf theme styles."""
import pathlib, subprocess, shutil
ROOT = pathlib.Path(__file__).resolve().parents[1]
MD = ROOT / "markdown_resume" / "resume.md"
OUT = ROOT / "markdown_resume" / "pdf"
OUT.mkdir(exist_ok=True)

# Fallback templates if pandoc default not usable; work with pandoc built-in styles via -V geometry + fontfamily
# Pandoc can't do many "themes" natively; we emulate via geometry/font/linestretch variables + Eisvogel (if available).
def build(name, variables, extra=None):
    out = OUT / f"resume_{name}.pdf"
    cmd = ["pandoc", str(MD), "-o", str(out),
           "-V", "geometry:margin=1in"]
    for k, v in variables.items():
        cmd += ["-V", f"{k}={v}"]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = out.exists()
    print(f"[{name}] {'OK' if ok else 'FAIL'}: {r.stderr[:120] if r.returncode else ''}")
    return out

themes = {
    "classic":   {"fontfamily":"lmodern", "linestretch":1.15, "fontsize":"11pt"},
    "palatino":  {"fontfamily":"mathpazo", "linestretch":1.2, "fontsize":"11pt"},
    "garamond":  {"fontfamily":"ebgaramond", "linestretch":1.2, "fontsize":"11pt"},
    "libertine": {"fontfamily":"libertine", "linestretch":1.15, "fontsize":"11pt"},
    "helvet":    {"fontfamily":"helvet", "linestretch":1.1, "fontsize":"10pt"},
}
for name, vars in themes.items():
    build(name, vars)

print("done ->", OUT)
for p in sorted(OUT.glob("*.pdf")):
    print("  ", p.name, f"{p.stat().st_size//1024}K")
