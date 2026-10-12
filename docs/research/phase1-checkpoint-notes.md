# Phase 1 Checkpoint — Review Notes for Human Confirmation

Generated 2026-10-11 after applying all three content patches. **59 notes** total.
Every note needs your decision: **confirm** (keep as-is), **fix** (tell me the correct fact), or **drop** (remove the item).

## Summary by type

- **MEMORY-CHECK**: 25
- **NEEDS-METRIC**: 19
- **SKILL-ORPHAN**: 9
- **CANDIDATE**: 5
- **SKILL-DUP**: 1

## New findings from integration (not from agents)

1. **industrial-ieee ATS 82.5 → 76.4 (C)**: template grew 2→3 pages; ATS page budget for industrial is 2 pages (ats.py:180). Fix = trim that template's content to 2 pages, or accept C.
2. **Academic templates 3→4 pages**: fine — academic budget is 4 pages (ats.py:180).
3. **Validation 10 → 5 issues**: the 5 remaining are the declared work/study overlaps you chose to keep (gate 1). To reach literally 0, add an 'acknowledged' mechanism — your call.
4. **Page growth cause**: 4 new bullets (mapna, homacloud_intern) + longer summaries. All 34 still compile.

## Full notes (verbatim from review agents)

### Batch 1 (2021–2025 research/TA roles)

- MEMORY-CHECK: pos_sharif_ta_history summary previously claimed 8 courses but listed only 6, and listed Generative Models which the teaching record dates Aug 2023 - Jan 2024 (after this role ended Aug 2023). New summary keeps the 8-course figure from the position title and drops Generative Models - confirm the true course count, list, and dates.
- MEMORY-CHECK: dates show pos_sharif_ta_history (Jan 2021 - Aug 2023) overlapping pos_mapna (Jan - May 2021), pos_homacloud_intern (May - Aug 2021) and pos_homacloud (Aug 2021 - Feb 2022), yet concurrent_with is empty on all of them - confirm whether the TA role really ran alongside those roles or one of the date ranges is wrong.
- MEMORY-CHECK: the same 30-80 students figure appears in both ach_sharif_ta_0 and ach_sharif_ta_history_0 - confirm both are accurate or identify which period the figure belongs to.
- MEMORY-CHECK: proposed tech stacks for the two empty positions - pos_mapna: React, Node.js, PostgreSQL, Docker (all taken verbatim from its summary); pos_homacloud_intern: Python, PyTorch, TensorFlow, Docker, FastAPI (PyTorch/TensorFlow from its summary, Docker/FastAPI inferred from the HomaCloud stack and its serving/API automation claim).
- MEMORY-CHECK: pos_ubc tech_stack trimmed LLaVA and PubMed as unreferenced in any bullet or summary; confirm MIMIC-CXR was actually used, since bullets only say de-identified QA corpora.
- MEMORY-CHECK: pos_l3s tech_stack dropped the vague entry 'Multimodal Models'; confirm PyTorch Lightning, OpenCV, PyAV, TensorBoard, scikit-learn is the correct set.
- MEMORY-CHECK: achievement.skills now list only terms that literally appear in each bullet, so the three teaching bullets (ach_sharif_ta_history_0, ach_sharif_ta_0, ach_sharif_ta_1) and ach_ubc_1 ended with empty skills - confirm or name the actual tools used.
- MEMORY-CHECK: all 7 position summaries rewritten as single 15-30 word sentences and pos_homacloud/pos_sharif_ta/pos_ubc concurrent_note text tightened to one sentence each - confirm wording matches reality.
- CANDIDATE: ach_mapna_0 (Mapna-MD2 dashboards/integrations on React/Node/PostgreSQL) is drafted only from the position summary and title - needs the human's memory confirmation before use.
- CANDIDATE: ach_mapna_1 (Docker + QA/deployment scripts) is drafted only from the position summary - needs the human's memory confirmation, plus a metric such as release/deploy cadence if known.
- CANDIDATE: ach_homacloud_intern_0 (evaluated PyTorch/TensorFlow multi-node training) is drafted only from the position summary and 2021 dates - needs the human's memory confirmation before use.
- CANDIDATE: ach_homacloud_intern_1 (serving/API automation for dataset prep and deployment) is drafted only from the position summary; FastAPI is inferred from the HomaCloud stack - needs the human's memory confirmation and a metric if known.
- NEEDS-METRIC: ach_homacloud_1 has no number in the source - suggest spot-instance cost savings or release frequency.
- NEEDS-METRIC: ach_l3s_0 has no number in the source - suggest dataset size or domain-shift accuracy gain.
- NEEDS-METRIC: ach_l3s_1 claims SOTA with no figures - suggest UCF-101/HMDB-51 accuracy percentages vs baselines.
- NEEDS-METRIC: ach_sharif_ta_1 has no number in the source - suggest capstones mentored or lab sessions delivered.
- NEEDS-METRIC: ach_ubc_0 has no number in the source - suggest training-set size or report-quality score.
- NEEDS-METRIC: ach_ubc_1 names BLEU/ROUGE-L but gives no values - suggest the actual scores vs prior art.
- NEEDS-METRIC: ach_ubc_2 is a publication bullet with no metric - add arXiv ID or accepted venue once available.
### Batch 2 (2024–2026 industry roles)

- MEMORY-CHECK: pos_advanced_analytics.concurrent_with listed 'trinity' while every other position uses 'trinity_emodub' — normalized to 'trinity_emodub'; the DB-wide convention is pos_-less ids (and pos_iran_credit_scoring points at education id 'sharif_masters'), so confirm the resolver's expected id form.
- MEMORY-CHECK: pos_iran_credit_scoring starts 2026-04 and pos_advanced_analytics ends 2026-04 — concurrent_with left as ['sharif_masters'] and the note claims only the Sharif M.Sc. overlaps; confirm there was no real April-2026 overlap.
- MEMORY-CHECK: dropped PyTorch from pos_iran_credit_scoring.tech_stack and TensorFlow from pos_trinity_emodub.tech_stack (untied to any summary/bullet); restore if they were genuinely used.
- MEMORY-CHECK: '<10h/wk' kept verbatim in pos_digikala_rd.concurrent_note — confirm whether that research budget was per commitment or combined across UBC/Trinity/Sharif XAI.
- MEMORY-CHECK: '5M queries' load-test (ach_digikala_ai_1) vs '5M+ queries/day' serving (pos_digikala_rd.summary) are two different claims, both kept verbatim; confirm the AI-role figure is a load-test ceiling, not production volume.
- MEMORY-CHECK: pos_digikala_ai -> pos_digikala_rd promotion is stated in summary + concurrent_note only; promotion_of left unset because all positions in the DB currently have promotion_of=None.
- MEMORY-CHECK: kept Prof. Siobhán Clarke attribution and the EmoDub GitHub URL verbatim in ach_trinity_emodub_2; EmotionNet/EmoDB stay in pos_trinity_emodub.tech_stack as corpus dependencies even though they are datasets, not tooling.
- MEMORY-CHECK: tech_stack additions are bullet-grounded only — Python + LangGraph added to pos_digikala_ai, Prometheus to pos_digikala_rd, XGBoost to pos_turquoise_senior; no stack item was removed unless it appeared in no summary or bullet.
- MEMORY-CHECK: all existing numbers kept verbatim (5TB/day, <60s, 60%, AUC 0.87, -22%, 50+, -78%, 94%, Sharpe +0.42, 99.2%, <50ms, 3.5x, 30 FPS, 100+, 12 sites, -35%, 5M, 5-person, +23%, -41%, p99 <200ms, 3.2x, 200 pods, <10h/wk); no number, date or fact was invented.
- MEMORY-CHECK: Digikala AI vs R&D bullets written as prototype -> production progression (AI: prototype RRF blend + 5M load-test; R&D: tuned retriever +23%/-41% and vLLM scale-out) — confirm the R&D gains were measured against the earlier AI-prototype baseline, not a pre-AI baseline.
- NEEDS-METRIC: ach_digikala_ai_0 — no number in source; suggest eval-pass or retrieval-quality delta vs the pre-prototype baseline.
- NEEDS-METRIC: ach_digikala_rd_3 — no number in source; suggest share of releases gated by the eval/canary pipeline.
- NEEDS-METRIC: ach_trinity_emodub_0 — no number in source; suggest SER F1 or emotion-consistency gain of the fusion model vs the SER-only baseline.
- NEEDS-METRIC: ach_trinity_emodub_1 — no number in source; suggest corpus size (hours/utterances) and per-emotion class balance.
- NEEDS-METRIC: ach_trinity_emodub_2 — no number in source; suggest reproduction signal (config runs, citations or forks).
- NEEDS-METRIC: ach_sharif_xai_0 — no number in source; suggest shift-suite size (attack/perturbation types) and measured robustness-accuracy drop.
- NEEDS-METRIC: ach_sharif_xai_1 — no number in source; suggest adoption signal for the guide (faculty sign-off, teams onboarded).
- NEEDS-METRIC: ach_advanced_analytics_1 — no number in source; suggest deployment success rate or rollback MTTR across the 12 sites.
- NEEDS-METRIC: ach_iran_credit_scoring_0 — no number in source; suggest analyst answer accuracy / citation-grounding rate vs the prior FAQ or SQL workflow.
- NEEDS-METRIC: ach_iran_credit_scoring_1 — no number in source; suggest before/after p99 token latency and GPU memory footprint for the vLLM/TGI tuning.
- NEEDS-METRIC: ach_iran_credit_scoring_2 — no number in source; suggest Cypher execution success rate or drop in unanswerable structured queries.
- NEEDS-METRIC: ach_iran_credit_scoring_3 — no number in source; suggest hallucination / unsupported-claim rate on an internal red-team set.
### Globals (profile/edu/projects/skills)

- CANDIDATE: coursework for sharif_masters = ['Advanced Machine Learning', 'Deep Learning', 'Advanced Computer Vision', 'Advanced Natural Language Processing', 'Optimization', 'Probabilistic Graphical Models', 'Reinforcement Learning'] — standard M.Sc. AI courses, verify against actual Sharif curriculum.
- MEMORY-CHECK: sharif_masters (M.Sc. AI) has no GPA, thesis, or expected end date recorded — add when available.
- MEMORY-CHECK: sharif_bsc GPA '3.65' has no scale recorded (presumed 4.00) — confirm scale.
- MEMORY-CHECK: publication ultrasound_preprint authors contain placeholders '[Co-authors TBD]' and 'A. Supervisor' — replace with real co-author and supervisor names.
- MEMORY-CHECK: publication ultrasound_preprint url is empty — add arXiv link once posted; venue says 'in preparation' but status is 'preprint' — set status to 'in_preparation' until the preprint is live.
- MEMORY-CHECK: teaching section has 6 entries covering 7 named courses (teach_5 combines 'Circuit Theory & Engineering Probability'), while pos_sharif_ta_history claims 8 courses — verify missing courses.
- MEMORY-CHECK: skill 'Librosa' registered with capital L but pos_trinity_emodub tech_stack and achievements use lowercase 'librosa' — align casing.
- MEMORY-CHECK: several skills referenced in positions/achievements are missing from the skills registry (e.g. FastAPI, Elasticsearch, Redis, Prometheus, Grafana, TensorRT, TFLite, Captum, SHAP, CLIP, LLaVA, scikit-learn, PyTorch Lightning, Trino, Great Expectations) — consider adding.
- SKILL-DUP: vLLM (id 1e1fd98c756d, llm_serving) -> merge into vLLM (id adaf2175726d, agentic)
- SKILL-ORPHAN: C++
- SKILL-ORPHAN: Go
- SKILL-ORPHAN: SQL
- SKILL-ORPHAN: R
- SKILL-ORPHAN: Bash
- SKILL-ORPHAN: TypeScript
- SKILL-ORPHAN: JAX
- SKILL-ORPHAN: TensorRT-LLM
- SKILL-ORPHAN: W&B

## What was changed (for the record)

- 14 positions: summaries rewritten (15–30 words), concurrent_note tightened, tech_stack pruned to role-relevant items
- 32 existing achievements rewritten to verb+scope+metric+stack; brief/detailed text regenerated; verified=true
- 4 new candidate achievements drafted for the 2 empty positions (mapna, homacloud_intern) — verified=false, need your memory
- Profile: 3 summary variants (recruiter/standard/detailed) rewritten
- Projects: 3 placeholder summaries/descriptions rewritten from linked position data; skills + position links filled
- Education: M.Sc. coursework drafted (candidate), B.Sc. thesis restructured
- Skills: 1 duplicate + 9 orphans flagged for your decision (not removed)
