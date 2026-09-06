#!/bin/bash
set -e
for f in theme_*.tex; do
  echo "Building $f"
  pdflatex -interaction=nonstopmode "$f" >/dev/null && echo " -> ${f%.tex}.pdf OK" || echo " -> $f FAILED"
done
ls -lh *.pdf 2>/dev/null
