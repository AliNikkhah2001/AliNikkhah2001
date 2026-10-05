# CV Improvement Questions — Ali Nikkhah

Based on reviewing all LaTeX segments across industrial and academic variants, here are targeted questions to strengthen your CV.

---

## 1. Quantifiable Impact & Metrics (High Priority)

**For every role, can you add or refine specific numbers?**

| Role | Current Metrics | Missing/Could Improve |
|------|-----------------|----------------------|
| **Digikala AI R&D Lead** | 5M+ daily queries | • Query latency improvement (p50/p99 before→after) <br>• Cost reduction per 1K queries <br>• Hallucination rate reduction % with KAG <br>• Team size managed <br>• Revenue/GMV impact of search improvements |
| **Turquoise Digital** | BNPL platform, real-time A/B | • $ volume processed through credit risk model <br>• Default rate reduction % <br>• A/B test velocity (tests/month) <br>• Portfolio allocation AUM influenced <br>• Call center ticket reduction % from voice bot |
| **Advanced Analytics Australia** | Multi-site edge deployment | • Sites deployed to <br>• False positive/negative rates <br>• Edge inference latency (ms) <br>• Bandwidth savings vs cloud <br>• Incidents detected/prevented |
| **HomaCloud MLOps** | Sub-10-min deployments | • Models in production <br>• Deployment frequency (weekly/daily) <br>• Incident rollback time <br>• GPU utilization improvement % |

---

## 2. Timeline Consistency Check (Critical)

**Several date ranges overlap or appear adjacent — please verify:**

| Role | Stated Range | Concern |
|------|-------------|---------|
| Digikala AI Engineer | Nov 2024 – Jan 2025 | 3 months, immediately before R&D Lead |
| Digikala R&D Lead | Jan 2025 – Aug 2025 | 7 months |
| Turquoise Senior Data Eng | Sep 2025 – Mar 2026 | 6 months — overlaps with Digikala? |
| Turquoise Data Scientist | Aug 2025 – Sep 2025 | 1 month — overlaps above? |
| Advanced Analytics | Sep 2025 – Apr 2026 | 7 months — overlaps Turquoise? |
| UBC Research | Feb 2024 – Nov 2025 | 21 months — overlaps Digikala? |
| L3S Research | Apr 2023 – Feb 2024 | 10 months |
| Sharif XAI | Jul 2025 – Sep 2025 | 3 months — overlaps Turquoise/Digikala? |
| HomaCloud | Aug 2021 – Feb 2022 | 6 months |

**Questions:**
1. Were Digikala and Turquoise truly concurrent (contract vs full-time)?
2. Was Advanced Analytics a part-time remote contract alongside Turquoise?
3. Was UBC research part-time alongside Digikala (Nov 2024 – Nov 2025)?
4. Should overlapping roles be labeled "Concurrent" or "Parallel" for transparency?

---

## 3. Title Accuracy & Seniority Signaling

**Current titles may undersell scope — consider:**

| Current | Suggested Alternative | Rationale |
|---------|----------------------|-----------|
| "AI Engineering R&D Lead" (7 months) | "Senior AI Engineer / Tech Lead, Search & Knowledge" | "Lead" implies team management; clarify if you managed people or technical direction |
| "Senior Data Engineer & Data Scientist" | Split into two entries or "Senior ML Engineer" | Dual title dilutes focus; pick primary identity per variant |
| "MLOps Engineer" (HomaCloud) | "Founding MLOps Engineer" or "ML Platform Engineer" | If first hire / built from scratch, say so |
| "Research Assistant" (UBC/L3S) | "Graduate Researcher" or "Research Associate" | RA can sound junior; you led SOTA work |

---

## 4. Technology Specificity Gaps

**Add version/ecosystem details where it strengthens credibility:**

| Area | Current | Could Add |
|------|---------|-----------|
| **LLM Serving** | vLLM, Triton | vLLM version, PagedAttention config (block size, max num seqs), tensor parallelism degree |
| **Vector Search** | FAISS, Elasticsearch, OpenSearch | Index type (HNSW, IVF), embedding dims, sharding strategy, QPS at scale |
| **Kubernetes** | Ray, ArgoCD, multi-tenant | Cluster size (nodes, GPUs), CNI, GPU scheduling (NVIDIA device plugin, MIG), cost optimization (spot/preemptible) |
| **Data Lake** | Trino, PeerDB, Parquet/ORC | Table format (Iceberg/Delta/Hudi), partition strategy, CDC latency (ms), data volume (TB/day) |
| **Observability** | Prometheus, Grafana, ELK | Custom metrics cardinality, alerting rules, SLO/SLI definitions, on-call rotation |

---

## 5. Project Descriptions — Make Them Punchier

**Current projects are solid but could lead with outcomes:**

| Project | Current Lead | Stronger Lead |
|---------|--------------|---------------|
| AI Portfolio Allocation | "Designed end-to-end asset recommendation system..." | "Built automated trading engine managing $X AUM; time-series transformers + sentiment fusion reduced portfolio drawdown by Y% vs benchmark" |
| Forex Heuristic Engine | "Formalized professional trader chart-reading heuristics..." | "Encoded expert technical analysis (trendlines, S/R, microstructure) as inductive biases for seq2seq models; backtested Sharpe improvement of X over buy-and-hold" |
| Ultrasound Reports | "Developed vision-language architectures... SOTA BLEU/ROUGE-L" | "First to achieve SOTA on DICOM-compliant ultrasound report generation; ViT+BLIP+T5 with contrastive learning beat prior best by X BLEU points" |
| Texture-Free Motion | "Designed pipelines using 3D CNNs + transformers over optical flow..." | "Proved texture-agnostic flow representations generalize better: SOTA on UCF-101/HMDB-51, +X% cross-dataset transfer vs RGB baselines" |

---

## 6. Academic CV Specific Questions

| Section | Question |
|---------|----------|
| **Publications** | The UBC preprint is "in preparation" — what's the realistic submission timeline? Should it be listed as "Under Review" or "Preprint (arXiv:XXXX)" once submitted? |
| **Research Interests** | Current list is broad. Should you prioritize 2-3 areas matching target labs (e.g., "Vision-Language Models for Healthcare" + "Agentic RAG Systems")? |
| **Teaching** | 3 years / 8 courses is strong. Can you add: course enrollment sizes, any curriculum development, student evaluation scores? |
| **Industry Experience** | Framed well for academia. Consider adding: "Collaborated with Prof. X on Y" or "Open-sourced Z library used in production" to bridge industry/academia. |

---

## 7. Variant-Specific Polish

### Agentic AI Variant
- Summary mentions "stateful LangGraph multi-agent pipelines" — can you name the specific agent patterns (ReAct, Plan-and-Execute, Reflection)?
- KAG is a differentiator — consider a 1-line footnote or parenthetical: "Knowledge-Augmented Generation: symbolic constraints on structured catalog data"

### Computer Vision Variant
- Edge deployment (TensorRT, TF Lite, Triton) is a superpower — emphasize: "Sub-50ms inference on Jetson Orin / AXIS ARTPEC-8"
- Multimodal retrieval (ViT + BLIP) at Digikala — add index scale: "10M+ product embeddings, 500 QPS"

### Data Roles Variant
- PeerDB CDC + Trino is a modern stack — highlight: "Sub-minute CDC latency from PostgreSQL to Trino"
- A/B testing engine — specify: "Sequential testing (mSPRT), 50+ concurrent experiments, automated power analysis"

### Software Engineering Variant
- Async FastAPI at 5M QPS — add: "p99 < 200ms, 99.9% uptime, horizontal scaling to 200 pods"
- Kafka + edge streaming — add: "100+ camera streams, 30 FPS each, exactly-once processing semantics"

---

## 8. Formatting & Presentation

| Issue | Recommendation |
|-------|----------------|
| **Font warning** | `\scshape` with bold not available in CM; switch to `\textsc` or use `lmodern` package |
| **1-page density** | Agentic 1p experience is tight; consider dropping HomaCloud or condensing to 1 bullet |
| **Date format** | Standardize: "Jan 2025 – Aug 2025" vs "2025-01 – 2025-08" — pick one |
| **Location consistency** | "Tehran, Iran" vs "Remote Contract" vs "Remote" — standardize format |
| **Bullet consistency** | Some bullets end with periods, others don't — standardize |

---

## 9. Missing Sections to Consider

- **Open Source / Community**: Any GitHub repos with stars, PyPI packages, conference talks?
- **Certifications**: AWS/Azure/GCP, CKAD, TensorFlow Developer, etc.?
- **Languages**: Persian (native), English (IELTS 8.0), Arabic (professional), French (beginner) — move to industrial CV footer?
- **Security Clearance / Visa Status**: If applying to US/EU, add "Eligible for TN/H-1B" or "EU Blue Card eligible"

---

## 10. Quick Wins (Do This Week)

1. **Fix overlapping dates** — add "Concurrent" labels or adjust months
2. **Add 2-3 hard numbers per role** — latency, cost, scale, revenue, error reduction
3. **Clarify Digikala title** — Tech Lead vs People Lead
4. **Submit UBC preprint to arXiv** — even as "v1" to get a citeable ID
5. **Standardize date/location format** across all segments
6. **Add `\usepackage{lmodern}`** to fix font warning

---

## Next Steps

Please answer the **Timeline Consistency** questions (Section 2) first — they affect every variant. Then we can prioritize metric additions per target role.

Would you like me to:
1. Create a "master experience timeline" to resolve overlaps?
2. Draft metric-infused bullet rewrites for a specific variant?
3. Add an Open Source / Publications section to industrial CVs?
4. Build a LaTeX command to auto-generate all 8 PDFs at once?