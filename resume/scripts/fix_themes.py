import pathlib
ROOT = pathlib.Path("/Users/alinikkhah/Documents/CV repo/Resume 3/academic/themes")
for p in ROOT.glob("theme_*.tex"):
    t = p.read_text()
    t = t.replace(r"\usepackage[usenames,dvipsnames]{color}", r"\usepackage[usenames,dvipsnames,table,HTML]{xcolor}")
    t = t.replace(r"\input{segments/", r"\input{../segments/")
    p.write_text(t)
    print(p.name)

# also create build shell
(ROOT / "build_all.sh").write_text("""#!/bin/bash
set -e
for f in theme_*.tex; do
  echo "Building $f"
  pdflatex -interaction=nonstopmode "$f" >/dev/null && echo " -> ${f%.tex}.pdf OK" || echo " -> $f FAILED"
done
ls -lh *.pdf 2>/dev/null
""")
print("fixed")
