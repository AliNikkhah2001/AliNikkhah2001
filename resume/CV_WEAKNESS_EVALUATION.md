# CV WEAKNESS EVALUATION & IMPROVEMENT ROADMAP

**Candidate:** Ali Nikkhah  
**Date:** 2026-08-15  
**Based on:** ATS analysis of 14 CV variants, KDnuggets 2024 best practices, timeline audit, LaTeX compilation logs, industry benchmarking

---

## 🔴 CRITICAL WEAKNESSES (Fix This Week)

### 1. Timeline Inconsistencies — **Major Red Flag**

| Role | Stated Dates | Overlap Conflict | Severity |
|------|--------------|------------------|----------|
| Digikala AI Engineer | Nov 2024 – Jan 2025 | Precedes Lead role by 3 months | ⚠️ Medium |
| Digikala R&D Lead | Jan 2025 – Aug 2025 | — | OK |
| Turquoise Sr Data Eng | Sep 2025 – Mar 2026 | Overlaps Digikala Lead (Jan-Aug 2025)? | 🔴 Critical |
| Turquoise Data Scientist | Aug 2025 – Sep 2025 | 1 month, overlaps above | 🔴 Critical |
| Advanced Analytics | Sep 2025 – Apr 2026 | Overlaps Turquoise (Sep-Mar 2026) | 🔴 Critical |
| UBC Research | Feb 2024 – Nov 2025 | Overlaps Digikala (Nov 2024+) | 🔴 Critical |
| L3S Research | Apr 2023 – Feb 2024 | Clean | ✅ |
| Sharif XAI | Jul 2025 – Sep 2025 | Overlaps Turquoise/Digikala | ⚠️ Medium |
| HomaCloud | Aug 2021 – Feb 2022 | Clean | ✅ |

**Required Fix:** Add explicit concurrency labels:
- "Concurrent with Digikala R&D Lead" / "Part-time remote"
- "Concurrent with Turquoise" / "Evening/weekend contract"
- Clarify: Were these full-time overlapping, or part-time/contract?

### 2. Title Inflation Risk — **Seniority Signaling**

| Current Title | Duration | Risk | Recommended |
|---------------|----------|------|-------------|
| "AI Engineering R&D Lead" | 7 months | "Lead" implies team management; did you manage people or tech? | "Senior AI Engineer / Tech Lead, Search & Knowledge" |
| "Senior Data Engineer & Data Scientist" | 6 months | Dual title dilutes focus | Split into two entries or "Senior ML Engineer" |
| "MLOps Engineer" (HomaCloud) | 6 months | If first hire, say so | "Founding MLOps Engineer" or "ML Platform Engineer" |
| "Research Assistant" (UBC/L3S) | 21/10 months | Sounds junior for SOTA work | "Graduate Researcher" or "Research Associate" |

### 3. 1-Page Variants Don't Fit — **Format Issue**

All 4 original 1-page variants render as **2 pages** with current content.
- **Root cause:** Too many roles + dense metrics for 1-page margins
- **Fix:** Either (a) use `% [1p-drop]` markers aggressively, or (b) accept 2-page for industry

---

## 🟠 HIGH PRIORITY WEAKNESSES (Fix This Month)

### 4. Metric Verification Needed

**Every metric must be defensible in interview.** Flag for verification:

| Metric | Source | Verification Status |
|--------|--------|---------------------|
| "5M+ daily queries" | Digikala | ❓ Verify |
| "p99 <200ms" | Digikala | ❓ Verify |
| "+23% recall@10" | Digikala RAG | ❓ Verify |
| "-41% hallucinations" | KAG | ❓ Verify |
| "3.2x throughput, 60% cost reduction" | vLLM | ❓ Verify |
| "12 sites, 100+ cameras" | Advanced Analytics | ❓ Verify |
| "<50ms inference, 99.2% uptime" | Edge CV | ❓ Verify |
| "-35% false positives" | Calibration | ❓ Verify |
| "-78% ticket volume, 94% accuracy" | Turquoise chatbot | ❓ Verify |
| "Sharpe +0.42" | Portfolio allocation | ❓ Verify |
| "<60s CDC latency, 5TB/day" | PeerDB/Trino | ❓ Verify |
| "AUC 0.87, -22% default rate" | BNPL model | ❓ Verify |
| "60% memory reduction" | PySpark | ❓ Verify |
| "15+ models, 99.9% deploy success" | HomaCloud | ❓ Verify |

**Action:** Create a "metric evidence" document with screenshots/logs/dashboard links for each.

### 5. Missing Quantification in Key Areas

| Area | Current | Needed |
|------|---------|--------|
| HomaCloud MLOps | "15+ models" | Training time reduction, GPU cost savings, incident MTTR |
| L3S Research | SOTA on UCF-101/HMDB-51 | Exact accuracy numbers, improvement over prior SOTA |
| UBC Research | SOTA BLEU/ROUGE-L | Exact scores, baseline comparison |
| Sharif XAI | "Investigated XAI" | Publications? Metrics? Open-source? |
| Teaching | "3 years, 8 courses" | Class sizes, evaluation scores, curriculum development |

### 6. Skills Section — Laundry List Problem

**Current:** 8-10 categories with 50+ technologies
**Issue:** ATS can't differentiate proficiency levels
**Fix:** Tier skills by proficiency:
```
EXPERT (production): Python, PyTorch, FastAPI, Kubernetes, Docker, Redis, Kafka, vLLM, Triton
ADVANCED: LangGraph, TensorRT, TensorFlow, Spark, Airflow, Prometheus, Terraform
WORKING: Go, C++, JAX, ClickHouse, Ray, MLflow, ArgoCD
LEARNING: Rust, eBPF, WebAssembly
```

---

## 🟡 MEDIUM PRIORITY WEAKNESSES (Fix This Quarter)

### 7. Story Coherence — "Why This Path?"

**Current narrative:** CV Engineer → MLOps → Data Eng → AI Eng → R&D Lead → Senior/Lead
**Missing:** Connective tissue explaining *strategic* choices
- Why MLOps first? (Foundation for production ML)
- Why Data Eng at Turquoise? (Needed to own data for ML)
- Why edge CV at Advanced Analytics? (Deployment expertise)
- Why Agentic AI at Digikala? (Next frontier after RAG)

**Fix:** Craft a 60-second narrative: "I started in MLOps because I realized models don't matter if they can't serve reliably. Then I moved to data engineering to own the fuel for ML. Then edge CV taught me deployment under constraints. Now I build agentic systems that combine all three: reliable serving, data quality, and constrained deployment."

### 8. Missing Portfolio Evidence

| Project | GitHub/HF Link | Demo | Paper |
|---------|----------------|------|-------|
| Agentic RAG (Digikala) | ❌ Private | ❌ | ❌ |
| Edge CV (Advanced Analytics) | ❌ Private | ❌ | ❌ |
| BNPL Credit Risk (Turquoise) | ❌ Private | ❌ | ❌ |
| Financial Chatbot (Turquoise) | ❌ Private | ❌ | ❌ |
| Ultrasound Reports (UBC) | ❌ | ❌ | ⏳ "In preparation" |
| Texture-Free Motion (L3S) | ❌ | ❌ | ❓ |
| Forex Heuristic Engine | ❓ Personal | ❓ | ❓ |

**Fix:** Even for private work, create **sanitized case studies** (1-pagers) for portfolio.

### 9. Academic CV Gaps

| Section | Issue |
|---------|-------|
| Publications | Only 1 "in preparation" — need arXiv submission |
| Research Interests | Too broad — focus on 2-3 areas matching target labs |
| Teaching | No evaluation scores, no curriculum development |
| Awards/Grants | None listed |
| Service | No conference reviewing, no community involvement |

### 10. Contact & Branding

- **Email:** `alinkkh9@gmail.com` — consider professional alias
- **Phone:** +98 (Iran) — add WhatsApp/Telegram for international
- **Portfolio:** `alinikkhah2001.github.io` — ensure it exists and is polished
- **LinkedIn:** Verify matches CV exactly

---

## 📋 QUESTIONS YOU MUST ANSWER

### Timeline & Role Clarity
1. **Digikala:** Were "AI Engineer" (Nov-Jan) and "R&D Lead" (Jan-Aug) a promotion? Same team?
2. **Turquoise:** "Senior Data Engineer" (Sep-Mar) AND "Data Scientist" (Aug-Sep) — sequential or concurrent? Why title change?
3. **Advanced Analytics:** Contract concurrent with Turquoise? Part-time? Remote from Iran?
4. **UBC Research:** Part-time during Digikala? How many hours/week?
5. **Sharif XAI:** Summer internship? Concurrent with Turquoise?
6. **HomaCloud:** Why only 6 months? Contract ended? Layoff?

### Metric Ownership
7. Which metrics did **you personally own** vs. team achievements?
8. For each metric: What was the baseline? What was your specific contribution?
9. Any metrics from A/B tests vs. before/after comparisons?

### Technical Depth
10. **LangGraph:** What specific patterns? (ReAct, Plan-and-Execute, Reflection, custom cycles?)
11. **KAG:** Symbolic reasoning implementation details? Open-source component?
12. **vLLM:** What PagedAttention config? (block_size, max_num_seqs, tensor_parallel_size?)
13. **TensorRT:** INT8/FP16 calibration? ONNX parser version? Dynamic shapes?
14. **PeerDB CDC:** Slot configuration? Lag monitoring? Schema evolution handling?

### Career Direction
15. **Target role:** Staff AI Engineer? AI Engineering Manager? ML Platform Lead? Research Scientist?
16. **Target geography:** Iran remote? EU (Germany/Netherlands)? Canada? US?
17. **Visa status:** Eligible for EU Blue Card? US TN/H-1B? Canada PR?
18. **Salary expectations:** Market rate for target role/location?

---

## 🎯 ACTION PLAN

### Week 1 (Critical)
- [ ] Resolve all timeline overlaps with "Concurrent" labels
- [ ] Verify/defend top 10 metrics with evidence
- [ ] Fix 1-page variants (use `% [1p-drop]` or accept 2-page)
- [ ] Submit UBC preprint to arXiv (get citeable ID)

### Week 2-3 (High Priority)
- [ ] Tier skills by proficiency (Expert/Advanced/Working)
- [ ] Create metric evidence document
- [ ] Write 60-second career narrative
- [ ] Sanitize 3 case studies for portfolio

### Week 4 (Medium Priority)
- [ ] Refine academic CV: research interests, teaching metrics, awards
- [ ] Polish GitHub portfolio page
- [ ] LinkedIn sync with CV
- [ ] Prepare STAR stories for each metric

### Ongoing
- [ ] Customize per application (summary + top 5 skills)
- [ ] Track metric accuracy as projects evolve
- [ ] Build public portfolio projects per KDnuggets recommendations

---

## 📊 COMPETITIVE BENCHMARKING

| Dimension | Your Level | Target (Staff/Lead) | Gap |
|-----------|------------|---------------------|-----|
| **Production Scale** | 5M queries/day | 100M+ | 20x |
| **Team Leadership** | Mentored 3-5 | Managed 10+ | Title vs. reality |
| **Open Source** | Private only | Significant OSS | Major |
| **Publications** | 1 in prep | 3+ top-tier | Major |
| **Speaking** | None listed | Conference talks | Medium |
| **Patents** | None | 1-2 | Minor |
| **Geographic Mobility** | Iran remote | EU/US/Canada | Visa/relocation |

---

## 🏁 FINAL RECOMMENDATION

**Your CV is technically strong** — metrics, stack, and variant system are excellent. The **three blockers** are:

1. **Timeline credibility** — Fix overlaps transparently
2. **Metric defensibility** — Evidence for every number
3. **Story coherence** — Connect the dots strategically

**Once fixed:** You're competitive for **Staff AI Engineer / ML Platform Lead / AI Engineering Manager** roles at Series B+ startups and Big Tech (EU/Canada/US remote).

**Timeline:** 2-3 weeks of focused work to make it bulletproof.