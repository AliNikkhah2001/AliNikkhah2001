# CV content consolidation

All four local collections have been imported into this repository. The working
data remains `resume/data/cv.yaml` as obtained from GitHub commit `3ff03f7`.
Every distinct older source document and PDF is preserved under
[`archive/local-versions/`](../../archive/local-versions/README.md).
The manifest maps all original paths, including identical files stored elsewhere.

## Facts that differ between sources

| Topic | Working GitHub source | Historical alternatives retained |
|---|---|---|
| Bachelor’s education | Sep 2020–Sep 2025; Electrical Engineering; GPA 3.65 | Sep 2020–Jul 2024; Digital Systems; 3.65 overall / 3.91 major |
| Master’s education | M.Sc. AI, Sep 2025–present; no thesis yet | M.Eng. AI, Sep 2026–present; research and coursework descriptions |
| Mapna dates | Jan–May 2021 | Nov 2022–Jan 2023 in `Resume_Detailed/industrial/segments/agentic_ai/experience.tex` |
| Turquoise start/title | Sep 2025; Senior Data Scientist & Data Engineer | Aug 2025; Senior Data Scientist & AI Engineer in the detailed variant |
| HomaCloud | Internship May–Aug 2021; engineer Aug 2021–Feb 2022 | Combined May 2021–Feb 2022 entry in the detailed variant |
| Achievements and metrics | Numerical, compressed YAML bullets | Longer descriptions and different technical emphasis across the LaTeX variants |

These alternatives are content sources for the upcoming review, not additional
jobs or credentials to append to the working CV. No conflicting factual claim
has been selected just because it appeared in a newer local file.

## Where to find all content

- `Resume 3`: master YAML, timeline drafts, evaluation notes, tagged variants,
  RenderCV sources, Markdown resumes, experience pool, and compiled PDFs.
- `Resume 3_v2_2026-08-14`: dated compact industrial and academic variants.
- `Resume_Detailed`: extended technical descriptions for each role focus.
- `Resume`: earlier role-specific content and layout experiments.

To restore a complete historical tree, run `restore_local_version.py` as documented
in the archive README. The original local folders were not changed.

## Working-source precedence

1. Keep the existing GitHub CV data as the working source.
2. Preserve all local alternatives verbatim with original-path provenance.
3. Generate the profile README from the working data, using the corrected root path.
4. Resolve factual differences and choose bullet wording during the CV discussion.

The ten added template previews contain their original upstream sample content.
They are a layout library and do not contribute biographical facts to this CV.
