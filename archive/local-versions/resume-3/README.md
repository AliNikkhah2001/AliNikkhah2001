# Resume Build System — Ali Nikkhah

## Structure

```
Resume/
├── industrial/
│   ├── main.tex                        ← COMPILE THIS for all industrial variants
│   └── segments/
│       ├── common/
│       │   ├── contact_info.tex
│       │   ├── education.tex
│       │   └── skills.tex
│       ├── agentic_ai/
│       │   ├── summary.tex
│       │   ├── experience.tex
│       │   └── projects.tex
│       ├── computer_vision/
│       │   ├── summary.tex
│       │   ├── experience.tex
│       │   └── projects.tex
│       ├── data_roles/
│       │   ├── summary.tex
│       │   ├── experience.tex
│       │   └── projects.tex
│       └── software_engineering/
│           ├── summary.tex
│           ├── experience.tex
│           └── projects.tex
└── academic/
    ├── main.tex                        ← COMPILE THIS for the research CV
    └── segments/
        ├── publications/list.tex
        ├── research_experience/
        │   ├── entries.tex
        │   └── industry.tex
        └── teaching_mentoring/ta_history.tex
```

---

## How to Build

### Step 1 — Choose your variant in `industrial/main.tex`

Open `industrial/main.tex` and set **exactly one** role flag to `true`:

```latex
\newbool{isAgentic}  \setbool{isAgentic}{false}
\newbool{isVision}   \setbool{isVision}{true}   ← active variant
\newbool{isData}     \setbool{isData}{false}
\newbool{isSWE}      \setbool{isSWE}{false}
```

### Step 2 — Choose 1-page or 2-page

```latex
\newbool{onePage}    \setbool{onePage}{false}   ← false = 2-page, true = 1-page
```

For 1-page builds, the tighter geometry and 10pt font handle most of the compression.
Bullets marked with `% [1p-drop]` in each experience.tex can be commented out
if the content still overflows after geometry adjustment.

### Step 3 — Compile

```bash
cd industrial
pdflatex main.tex
```

### Academic CV

```bash
cd academic
pdflatex main.tex
```

---

## Variant Matrix

| Variant            | Flag        | 1-page | 2-page |
|--------------------|-------------|--------|--------|
| Agentic / AI Eng   | isAgentic   | ✓      | ✓      |
| Computer Vision    | isVision    | ✓      | ✓      |
| Data Sci / Eng     | isData      | ✓      | ✓      |
| Software Eng       | isSWE       | ✓      | ✓      |
| Research / Academic| (separate)  | —      | ✓      |

---

## Key Design Decisions

- **`% [1p-drop]` markers**: Lower-priority bullets in experience.tex files.
  Comment these out first when squeezing to 1 page.
- **Advanced Analytics Australia**: Listed as a parallel remote contract that
  overlapped with Digikala and Turquoise Digital roles. Each variant highlights
  its most relevant aspects (edge CV for vision, Kafka/async for SWE, etc.).
- **Academic CV**: Separates research experience from industry; industry is
  framed with research methodology language rather than business impact.
- **Publications**: Update `academic/segments/publications/list.tex` with
  real author list, title, and arXiv ID once the UBC preprint is posted.
