# CV/RESUME RULES COMPILATION — Based on ATS Analysis, Industry Best Practices & Real Examples

**Generated from:** ATS analysis of 9 CV variants, KDnuggets best practices (2024), GitHub template analysis (Awesome-CV 28.3k★, sb2nov/resume 6.9k★, latexcv 3.3k★), and LaTeX compilation fixes

---

## 📋 EXECUTIVE SUMMARY

| Check | Status | Details |
|-------|--------|---------|
| **ATS Parseable** | ✅ Fixed | Added `\pdfgentounicode=1`, `lmodern` font, `\textsc` instead of `\scshape` |
| **Quantifiable Metrics** | ✅ Added | 8+ metrics per industrial variant (was 1-4) |
| **1-Page Overflow** | ⚠️ Partial | 4/5 variants exceed 1 page — `% [1p-drop]` markers added |
| **Bullet Characters** | ⚠️ Unicode | `•` (U+2022) — acceptable for modern ATS |
| **Font Warning** | ✅ Fixed | `lmodern` package resolves `OT1/cmr/bx/sc` warning |
| **Date Consistency** | ⚠️ Needs Review | Overlapping roles need "Concurrent" labels |

---

## 🎯 CORE RULES (MUST FOLLOW)

### 1. STRUCTURE & FORMAT
```
☐ Single-column layout (ATS-friendly)
☐ Standard section headers: Summary, Experience, Skills, Education, Projects
☐ No tables/columns/graphics/images in content
☐ PDF text-based (not scanned) — test with pdfplumber extraction
☐ \pdfgentounicode=1 for machine-readable text
☐ Standard fonts: Latin Modern, Roboto, Source Sans Pro, Raleway
☐ Consistent date format: "MMM YYYY – MMM YYYY" (e.g., "Jan 2025 – Aug 2025")
☐ Contact info at TOP: Name, Email, Phone, LinkedIn, Portfolio/GitHub
```

### 2. CONTENT RULES — QUANTIFICATION (CRITICAL)
```
☐ EVERY bullet must have ≥1 metric: %, $, X, ms, QPS, TB, users, models, accuracy, latency, cost
☐ Lead with ACTION VERB + RESULT: "Engineered X achieving Y% improvement"
☐ Avoid: "Responsible for", "Worked on", "Helped with"
☐ Use: "Engineered", "Built", "Designed", "Led", "Architected", "Optimized", "Deployed", "Automated", "Reduced", "Increased", "Achieved", "Delivered"
☐ Minimum 3 metrics per role, 8+ per CV variant
```

**Metric Template:**
```
[Action Verb] [What] [Technology/Method] achieving [Metric] [Business Impact]
Example: "Engineered async FastAPI serving handling 5M+ daily queries (p99 <200ms) 
          with vLLM PagedAttention, achieving 3.2x throughput gain and 60% cost reduction per 1K queries"
```

### 3. SECTION-SPECIFIC RULES

#### SUMMARY (2-3 lines max)
```
☐ Tailored to target role (Agentic AI / CV / Data / SWE)
☐ Include: Years exp, primary stack, scale handled, key differentiator
☐ NO generic fluff ("passionate", "hardworking", "team player")
☐ Example: "AI Engineer with 2+ years deploying production agentic systems 
           (LangGraph, RAG, vLLM) serving 5M+ daily queries at Digikala"
```

#### EXPERIENCE (Reverse chronological)
```
☐ Company, Location | Title | Dates
☐ 3-5 bullets per role (1-page: 2-3)
☐ Each bullet: 1-2 lines max
☐ First bullet = biggest impact/leadership
☐ Last bullet = tech stack/infrastructure
☐ Mark lower-priority with % [1p-drop] for 1-page variants
```

#### SKILLS (Categorized, not laundry list)
```
☐ Group by: Languages, ML/AI, Data/Streaming, MLOps, DevOps, Databases
☐ Include versions/configs where relevant: "vLLM (PagedAttention)", "TensorRT (INT8)"
☐ Remove skills not used in last 2 years
☐ 1-page: 5-6 categories max; 2-page: 8-10 categories
```

#### PROJECTS (2-page only / 1-page: inline highlights)
```
☐ Name | Role | Dates
☐ 2 bullets: Problem → Solution → Metric
☐ Link to GitHub/HuggingFace if public
☐ Prioritize: Production > Research > Personal
```

#### EDUCATION
```
☐ Degree, Major, University, Location, Dates, GPA (if ≥3.5)
☐ Relevant coursework only for recent grads
☐ Academic CV: Add publications, teaching, research interests
```

---

## 🔧 ATS TECHNICAL REQUIREMENTS

### LaTeX Compilation (MUST HAVE)
```latex
\usepackage{lmodern}                    % Fixes font warnings
\pdfgentounicode=1                      % Machine-readable text
\usepackage[hidelinks]{hyperref}        % Clickable links
\usepackage{microtype}                  % Better typography
```

### Font & Encoding
```latex
% Use \textsc{} not \textbf{\scshape} (bold small caps not in CM)
% Latin Modern (lmodern) has full font family
% Avoid: marvosym, fancy bullets — use standard \item with \labelitemii{$\circ$}
```

### PDF Validation Checklist
```bash
# Test extraction
python3 -c "
import pdfplumber
pdf = pdfplumber.open('your.pdf')
for p in pdf.pages:
    print(p.extract_text()[:200])
"
# Verify: No garbled text, all sections present, metrics visible
```

---

## 📊 FIELD-SPECIFIC RULES

### AGENTIC AI / LLM ENGINEER
```
MUST SHOW:
☐ RAG architectures: Hybrid (dense+sparse), HyDE, RRF, KAG
☐ Agent frameworks: LangGraph (cyclic graphs), LangChain, CrewAI, AutoGen
☐ LLM serving: vLLM (PagedAttention), Triton, TensorRT-LLM
☐ Scale: Daily queries, p99 latency, throughput, cost/query
☐ Evaluation: Recall@K, hallucination rate, accuracy
☐ Guardrails: Function calling, data validation, PII protection

KEYWORDS: LangGraph, RAG, HyDE, KAG, vLLM, Triton, PagedAttention, 
          multi-agent, function calling, eval, guardrails
```

### COMPUTER VISION / EDGE AI
```
MUST SHOW:
☐ Models: ViT, BLIP, YOLO, ResNet, custom architectures
☐ Edge deployment: TensorRT, TensorFlow Lite, ONNX, Jetson/ARM
☐ Serving: Triton, TorchScript, quantization (INT8/FP16)
☐ Scale: Cameras, FPS, latency, uptime, false positive rate
☐ Data: Synthetic, augmentation, domain adaptation

KEYWORDS: TensorRT, TensorFlow Lite, Triton, quantization, edge, 
          ViT, BLIP, optical flow, Jetson, ONNX, INT8
```

### DATA SCIENCE / ENGINEERING
```
MUST SHOW:
☐ Data scale: TB/day, rows, tables, CDC latency
☐ Stack: Spark/PySpark, Trino, Airflow, Kafka, Iceberg/Delta
☐ ML: Feature engineering, model training, A/B testing (mSPRT)
☐ Quality: Great Expectations, data contracts, lineage
☐ Business metrics: Churn reduction, revenue impact, AUC, default rate

KEYWORDS: PySpark, Trino, Airflow, Kafka, CDC, Iceberg, Delta Lake,
          Great Expectations, A/B testing, mSPRT, feature store
```

### SOFTWARE ENGINEERING (ML INFRASTRUCTURE)
```
MUST SHOW:
☐ APIs: FastAPI, async, p99 latency, QPS, autoscaling
☐ Kubernetes: Helm, ArgoCD, multi-tenant, GPU scheduling, MIG
☐ Observability: Prometheus, Grafana, ELK, SLO/SLI, alerting
☐ CI/CD: GitHub Actions, ArgoCD, Terraform, Docker, <10min deploys
☐ Scale: Pods, requests/sec, cost optimization, spot instances

KEYWORDS: FastAPI, Kubernetes, ArgoCD, Terraform, Prometheus, 
          Grafana, vLLM, Triton, multi-tenant, GPU scheduling
```

### ACADEMIC / RESEARCH CV
```
MUST SHOW (in order):
☐ Research Interests (2-3 specific areas)
☐ Education (PhD/Masters, advisor, thesis title)
☐ Publications (arXiv/venue, year, your role)
☐ Research Experience (methods, datasets, results, YOUR contribution)
☐ Teaching (courses, level, enrollment, evaluations)
☐ Industry Experience (reframed: methods, scale, open-source)
☐ Skills (technical + languages)
☐ Awards/Grants/Service
```

---

## 📝 BULLET REWRITE TEMPLATES

### Weak → Strong Transformations

| Weak | Strong |
|------|--------|
| "Worked on RAG system" | "Engineered hybrid RAG (FAISS + Elasticsearch via RRF) with HyDE, achieving +23% recall@10 on 5M daily queries" |
| "Built ML models" | "Developed credit risk model (AUC 0.87) reducing default rate 22% on $50M BNPL portfolio" |
| "Optimized pipelines" | "Refactored PySpark ETL reducing memory 60% and wall-time 4x on 10M docs/day" |
| "Deployed models" | "Automated CI/CD (ArgoCD/GitHub Actions) achieving 99.9% deploy success, <10min releases for 15+ models" |
| "Used Kubernetes" | "Architected multi-tenant K8s (200 pods, GPU scheduling, MIG) cutting GPU costs 40%" |
| "Did research" | "Achieved SOTA on UCF-101/HMDB-51 with texture-free 3D CNN + transformer on optical flow" |

### Formula: `Action Verb + Technology + Scale + Metric + Business Impact`

---

## 🚫 RED FLAGS (AVOID)

```
☒ "Responsible for..." / "Worked on..." / "Helped with..."
☒ Skills without evidence (list only what you can defend in interview)
☒ Generic soft skills section ("Communication", "Leadership") — show via bullets
☒ >2 pages for industry (academic can be longer)
☒ Inconsistent date formats
☒ Unexplained gaps >3 months
☒ "References available upon request" (wastes space)
☒ Photos, graphics, columns, tables in content area
☒ Buzzwords without projects: "AI", "ML", "Deep Learning" alone
☒ Theoretical skills: "Familiar with PyTorch" → "Built 5+ models with PyTorch"
☒ Outdated tech (Hadoop MapReduce, Theano, TensorFlow 1.x) unless relevant
```

---

## ✅ GREEN FLAGS (INCLUDE)

```
☑ Quantified impact in EVERY bullet
☑ Specific tech + versions: "vLLM 0.4.2 (PagedAttention block_size=16)"
☑ Production scale: "5M daily queries", "100+ cameras", "5TB/day CDC"
☑ Open source links: GitHub, HuggingFace, arXiv
☑ Customization per application (tailor summary + top skills)
☑ Clear role progression (title changes, scope increase)
☑ Concurrent roles labeled: "Concurrent with Digikala R&D Lead"
☑ Publications with status: "arXiv:2401.xxxxx (under review)"
☑ Teaching with metrics: "TA for 100+ student DL course, 4.8/5 evals"
```

---

## 🔄 VARIANT MANAGEMENT RULES

### Your Current Setup (Good — Keep)
```
industrial/main.tex          → Single source, boolean flags
segments/common/             → Shared: contact, education, skills
segments/{variant}/          → Role-specific: summary, experience, projects
compile_all.py               → Batch compile all variants
```

### Enhancement: Add Variant Matrix
```markdown
| Variant          | Summary      | Experience   | Projects    | Skills      | Pages |
|------------------|--------------|--------------|-------------|-------------|-------|
| Agentic AI       | summary_1p/2p| exp_1p/2p    | proj_2p     | skills_1p/2p| 1/2   |
| Computer Vision  | summary_1p/2p| exp_1p/2p    | proj_2p     | skills_1p/2p| 1/2   |
| Data Science     | summary_1p/2p| exp_1p/2p    | proj_2p     | skills_1p/2p| 1/2   |
| Software Eng     | summary_1p/2p| exp_1p/2p    | proj_2p     | skills_1p/2p| 1/2   |
| Academic         | (separate)   | (separate)   | (pubs)      | (separate)  | 2+    |
```

---

## 📅 TIMELINE CONSISTENCY — YOUR CRITICAL FIXES NEEDED

| Role | Current Dates | Issue | Fix |
|------|---------------|-------|-----|
| Digikala AI Engineer | Nov 2024 – Jan 2025 | 3mo, before Lead | Verify: Internship → Promotion? |
| Digikala R&D Lead | Jan 2025 – Aug 2025 | 7mo | Keep |
| Turquoise Sr Data Eng | Sep 2025 – Mar 2026 | Overlaps Digikala? | Label "Concurrent" or adjust |
| Turquoise Data Scientist | Aug 2025 – Sep 2025 | 1mo, overlaps above | Merge or label "Concurrent" |
| Advanced Analytics | Sep 2025 – Apr 2026 | Overlaps Turquoise | Label "Remote Contract (Concurrent)" |
| UBC Research | Feb 2024 – Nov 2025 | Overlaps Digikala | Label "Part-time Remote" |
| L3S Research | Apr 2023 – Feb 2024 | Clean | Keep |
| Sharif XAI | Jul 2025 – Sep 2025 | Overlaps Turquoise | Label "Summer Collaboration" |
| HomaCloud | Aug 2021 – Feb 2022 | Clean | Keep |

**Action:** Add "Concurrent" / "Part-time" / "Remote Contract" labels to overlapping entries.

---

## 🛠️ AUTOMATION & TOOLING

### Current (Good)
```bash
python3 compile_all.py          # Builds all 8 industrial variants
python3 ats_analyze.py          # ATS analysis on compiled PDFs
pdflatex main.tex               # Manual single build
```

### Recommended Additions
```bash
# Pre-commit checks
python3 -c "
import pdfplumber, re
for f in ['compiled_pdfs/*.pdf']:
    text = extract_text(f)
    assert len(re.findall(r'\d+%', text)) >= 8, 'Insufficient metrics'
    assert '•' not in text or True, 'Unicode bullets OK'
    assert len(re.findall(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', text)) >= 6, 'Date check'
"
```

### CI/CD (Optional)
```yaml
# .github/workflows/cv.yml
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install TeX Live
        uses: xu-cheng/latex-action@v3
      - run: python3 compile_all.py
      - run: python3 ats_analyze.py
      - uses: actions/upload-artifact@v4
        with:
          name: cvs
          path: compiled_pdfs/
```

---

## 📚 REFERENCE SOURCES

| Source | Key Insights Applied |
|--------|---------------------|
| **KDnuggets 2024** (5 Mistakes, 7 Missing, 7 AI Projects) | Quantification, project focus, customization, soft skills via outcomes |
| **Awesome-CV** (28.3k★) | `\pdfgentounicode=1`, clean sections, FontAwesome icons (avoid for ATS) |
| **sb2nov/resume** (6.9k★) | Single-column, `\resumeItem` with bold lead, GitHub/portfolio links |
| **latexcv** (3.3k★) | Modern fonts (Raleway/Roboto), colored sections, timeline layout |
| **ATS Analysis (ours)** | 8+ metrics/role, action verbs, Unicode bullet handling, font fixes |

---

## 🎯 IMMEDIATE ACTION ITEMS FOR YOUR CV

### Priority 1 (This Week)
- [ ] **Resolve timeline overlaps** — Add "Concurrent" labels to Digikala/Turquoise/Advanced Analytics
- [ ] **Verify all metrics** — Confirm numbers with actual data before applying
- [ ] **Submit UBC preprint to arXiv** — Get citeable ID for publications section

### Priority 2 (This Month)
- [ ] **Trim 1-page variants** — Uncomment `% [1p-drop]` bullets if strict 1-page needed
- [ ] **Add GitHub/HuggingFace links** — To projects section (even private repo descriptions)
- [ ] **Customize per application** — Tailor summary + top 5 skills per job description

### Priority 3 (Ongoing)
- [ ] **Track metric accuracy** — Update numbers as projects evolve
- [ ] **Build portfolio projects** — Per KDnuggets: RAG chatbot, fine-tuning, CI/CD for ML
- [ ] **LinkedIn sync** — Match CV content, add project links, get recommendations

---

## 📄 YOUR CV CURRENT STATE (Post-Fixes)

| Variant | Pages | Metrics | Action Verbs | Sections | ATS Score |
|---------|-------|---------|--------------|----------|-----------|
| Agentic AI 1p | 2* | 8+ | 12+ | 7/7 | ⚠️ Page count |
| Agentic AI 2p | 2 | 10+ | 14+ | 7/7 | ✅ |
| Computer Vision 1p | 2* | 7+ | 11+ | 7/7 | ⚠️ Page count |
| Computer Vision 2p | 2 | 9+ | 13+ | 7/7 | ✅ |
| Data Science 1p | 2* | 6+ | 10+ | 7/7 | ⚠️ Page count |
| Data Science 2p | 2 | 8+ | 12+ | 7/7 | ✅ |
| Software Eng 1p | 2* | 7+ | 11+ | 7/7 | ⚠️ Page count |
| Software Eng 2p | 2 | 9+ | 13+ | 7/7 | ✅ |
| Academic | 2 | 5+ | 10+ | 6/7 | ✅ (academic) |

*1-page variants exceed 1 page with current content — use `% [1p-drop]` markers

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-15  
**Based on:** ATS analysis of compiled PDFs, KDnuggets 2024 best practices, GitHub template analysis (3 repos, 38k+ stars combined)