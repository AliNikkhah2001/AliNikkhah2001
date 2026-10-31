# Experience Drafts — REVIEW REQUIRED

> Status: **DRAFT, `verified=false`, NOT in the live DB.** Every bullet below is a
> writing sample grounded only in the role's existing tech stack, summary, org and
> dates. **No new technology was invented.** Every number, metric, scale claim and
> scope statement is a **placeholder for you to confirm, correct or delete**.
> Reply per role with keep / edit / kill (e.g. "R2: keep 1,3,5; fix 2 to 4 nodes").
> Only approved bullets will be written into `career_db.json`.

How to read a sample: `[project / framework]` → draft bullet.

---

## R1 — MLOps Intern, HomaCloud (Aug–Nov 2021, full-time)
Stack: Python, PyTorch, TensorFlow, Docker, FastAPI

- [DRAFT-R1-1] [Multi-node training eval / PyTorch DDP vs TF]: Benchmarked PyTorch
  distributed-data-parallel against TensorFlow multi-worker training on the same
  workload, comparing throughput scaling and time-to-accuracy; wrote up the
  comparison that informed the platform's framework choice.
- [DRAFT-R1-2] [Dataset-prep automation / FastAPI]: Built FastAPI endpoints that
  automated dataset preparation and validation steps, replacing manual
  preprocessing runs before training jobs.
- [DRAFT-R1-3] [Serving prototype / FastAPI + Docker]: Containerized a model-serving
  prototype behind a FastAPI API with health checks, covering the path from
  trained checkpoint to queryable endpoint.
- [DRAFT-R1-4] [Reproducible training images / Docker]: Produced pinned Docker
  images (CUDA, cuDNN, PyTorch/TensorFlow versions) so training jobs ran
  identically across machines.
- [DRAFT-R1-5] [Deployment automation / FastAPI]: Automated parts of the model
  deployment flow (packaging, config, rollout triggers) via internal APIs,
  cutting manual release steps.

## R2 — MLOps Engineer, HomaCloud (Nov 2021–Dec 2022, full-time)
Stack: Kubernetes, Docker, Ray, MLflow, Terraform, ArgoCD, FastAPI, Prometheus, Grafana, GitHub Actions

- [DRAFT-R2-1] [GPU cluster provisioning / Terraform + Kubernetes]: Provisioned
  multi-node Kubernetes GPU clusters with Terraform (networking, node pools,
  GPU drivers), giving training workloads a reproducible home.
- [DRAFT-R2-2] [Distributed training pipelines / Ray + MLflow]: Built Ray-based
  distributed training pipelines with MLflow experiment tracking, so runs,
  params, metrics and artifacts were comparable across experiments.
- [DRAFT-R2-3] [GitOps delivery / ArgoCD + GitHub Actions]: Operationalized
  GitOps delivery — CI on GitHub Actions, canary rollouts via ArgoCD — for
  training and serving components.
- [DRAFT-R2-4] [Model-serving layer / FastAPI + Kubernetes]: Ran the FastAPI
  model-serving layer on Kubernetes with autoscaling, serving team models behind
  a stable internal API.
- [DRAFT-R2-5] [Observability + cost / Prometheus + Grafana]: Built
  Prometheus/Grafana dashboards for GPU utilization, serving latency and
  pipeline health; tuned workloads toward spot instances to cut compute spend.

## R3 — AI Engineer, Digikala (Dec 2022–Dec 2023, full-time)
Stack: Python, LangChain, LlamaIndex, FAISS, Elasticsearch, LangGraph, FastAPI

- [DRAFT-R3-1] [Agent orchestration prototype / LangGraph]: Prototyped LangGraph
  orchestration with health-checked steps for the marketplace listing assistant,
  making multi-step agent runs observable and restartable.
- [DRAFT-R3-2] [Hybrid retrieval prototype / FAISS + Elasticsearch]: Blended FAISS
  dense vectors with Elasticsearch keyword hits for listing search, establishing
  the hybrid retrieval pattern the platform later adopted.
- [DRAFT-R3-3] [Ingestion pipelines / LlamaIndex + LangChain]: Built LlamaIndex
  ingestion pipelines (chunking, embeddings, indexing) over marketplace listing
  catalogs feeding the assistant prototype.
- [DRAFT-R3-4] [Eval telemetry / FastAPI + retrieval metrics]: Instrumented the
  prototype with eval telemetry — retrieval quality plus latency tracking — so
  iterations were measured, not vibes.
- [DRAFT-R3-5] [Prototype-to-platform handoff / FastAPI service]: Shipped the
  FastAPI prototype service with a handoff design that grew into the org-wide
  platform mandate (continued as Senior AI Engineer).

## R4 — Machine Learning Engineer (EmoDub), Trinity College Dublin (May 2023–Apr 2024, part-time remote)
Stack: PyTorch, Hugging Face, librosa, wav2vec2.0, Whisper, EmotionNet, EmoDB

- [DRAFT-R4-1] [SER front-end / PyTorch + wav2vec2.0]: Trained a transformer
  speech-emotion-recognition head over wav2vec2.0 representations emitting
  affect logits per utterance.
- [DRAFT-R4-2] [Prosody-consistent translation / Whisper fusion]: Fused SER
  affect signals with Whisper-based speech translation so translated output
  preserved the speaker's prosody and emotional tone.
- [DRAFT-R4-3] [Emotion corpora / EmoDB + EmotionNet + librosa]: Curated and
  preprocessed EmoDB and EmotionNet corpora (librosa feature pipelines,
  balanced splits) for SER training and evaluation.
- [DRAFT-R4-4] [Reproducibility / Hugging Face + PyTorch]: Published
  reproducible training and evaluation scripts with versioned checkpoints for
  the EmoDub pipeline.
- [DRAFT-R4-5] [Research delivery / TCD collaboration]: Delivered a working
  emotion-aware speech-to-speech demo with Trinity collaborators, reporting
  emotion-retention scores on held-out clips.

## R5 — Research Assistant (Video Motion Classification), L3S Hannover (May 2023–Feb 2024, part-time)
Stack: PyTorch Lightning, OpenCV, PyAV, TensorBoard, scikit-learn

- [DRAFT-R5-1] [Flow dataset pipeline / OpenCV + PyAV]: Engineered an
  optical-flow-centric video data pipeline (decoding with PyAV, flow
  extraction with OpenCV, temporal sampling and augmentation).
- [DRAFT-R5-2] [3D CNN baselines / PyTorch Lightning]: Trained 3D CNN baselines
  in PyTorch Lightning with TensorBoard tracking, establishing the reference
  numbers for texture-free motion classification.
- [DRAFT-R5-3] [Transformer hybrids / UCF-101 + HMDB-51]: Benchmarked
  transformer-hybrid architectures against the CNN baselines on UCF-101 and
  HMDB-51, reaching state-of-the-art results.
- [DRAFT-R5-4] [Attention analysis / interpretability]: Analyzed attention maps
  to show which motion cues (vs static texture) drove predictions, supporting
  the texture-free claim.
- [DRAFT-R5-5] [Eval harness / scikit-learn]: Built the ablation and evaluation
  harness (cross-val splits, metric aggregation) used across all reported
  experiments.

## R6 — Senior AI Engineer, Digikala (Dec 2023–May 2025, full-time)
Stack: Python, LangGraph, LangChain, LlamaIndex, FAISS, Elasticsearch, ChromaDB, HyDE, KAG, FastAPI, vLLM, Triton, Redis, Prometheus, Kubernetes, ArgoCD

- [DRAFT-R6-1] [Agent platform + MCP control plane / LangGraph]: Drove the agent
  platform roadmap and SLOs, shipping an MCP control plane with LangGraph
  cyclic graphs, zero-downtime hot-swapping and health-checked agent
  composition.
- [DRAFT-R6-2] [Hybrid retriever / FAISS + Elasticsearch + HyDE + KAG]: Tuned
  the production hybrid retriever — FAISS vectors fused with Elasticsearch
  keyword hits via RRF, plus HyDE and KAG — lifting recall@10 and cutting
  hallucinations.
- [DRAFT-R6-3] [LLM serving at scale / vLLM + Triton + Kubernetes]: Scaled LLM
  inference on vLLM (PagedAttention) and Triton across the Kubernetes fleet,
  multiplying throughput while cutting cost per query.
- [DRAFT-R6-4] [Latency envelope / Redis caching]: Backed the serving path with
  multi-tier Redis caching to hold p99 latency inside budget at 5M+ queries/day.
- [DRAFT-R6-5] [Quality gates / eval + A/B + ArgoCD canary]: Partnered with
  infrastructure and product teams on shared eval pipelines, A/B guardrails and
  ArgoCD canary rollouts; used ChromaDB-backed memory for agent context.

## R7 — Research Assistant (Ultrasound Report Generation), UBC (Feb 2024–Nov 2025, part-time)
Stack: PyTorch, ViT, BLIP, T5, CLIP, OpenCV, MIMIC-CXR, DICOM

- [DRAFT-R7-1] [Report-generation architecture / ViT + BLIP + T5]: Designed
  ViT/BLIP visual encoders paired with a T5 report generator for ultrasound
  images.
- [DRAFT-R7-2] [Contrastive pretraining / CLIP-style + MIMIC-CXR]: Pretrained
  image-text representations with contrastive objectives on MIMIC-CXR and
  DICOM ultrasound data before report-generation fine-tuning.
- [DRAFT-R7-3] [Clinician-facing interpretability / saliency overlays]: Deployed
  attention and saliency overlays (OpenCV visualization) so generated findings
  could be traced back to image regions.
- [DRAFT-R7-4] [Benchmarking / BLEU + ROUGE-L + clinical accuracy]: Benchmarked
  generated reports on BLEU/ROUGE-L plus clinical accuracy checks against
  reference reports.
- [DRAFT-R7-5] [Manuscript / DICOM-compliant generation]: Drafted the manuscript
  on automated DICOM-compliant ultrasound report generation via contrastive
  vision-language modeling.

## R8 — Computer Vision / ML Platform Engineer (Edge), Advanced Analytics Australia (Apr 2024–May 2025, part-time remote)
Stack: Python, OpenCV, YOLO, ViT, TensorRT, TFLite, Triton, Kafka, Docker, Kubernetes, Prometheus, Grafana, ONNX

- [DRAFT-R8-1] [Edge model optimization / TensorRT + TFLite + ONNX]: Converted
  YOLO and ViT detectors through ONNX into quantized TensorRT/TF Lite engines
  meeting per-camera frame budgets.
- [DRAFT-R8-2] [Fleet serving / Triton model repository]: Served the quantized
  models from a Triton model repository with rolling updates and no service
  interruption across 12 retail sites and 100+ camera streams.
- [DRAFT-R8-3] [Streaming ingestion / Kafka + OpenCV]: Built Kafka-based frame
  ingestion sustaining 30 FPS per stream from acquisition through inference.
- [DRAFT-R8-4] [Detection quality / attention-guided NMS]: Cut YOLO false
  positives by combining attention-guided NMS with SNR monitoring on difficult
  in-store scenes.
- [DRAFT-R8-5] [Edge observability / Prometheus + Grafana + Docker]: Ran the
  edge fleet in containers with Prometheus/Grafana observability (device
  health, inference latency, stream drops).

## R9 — Senior Data Scientist & Data Engineer, Turquoise Digital (May 2025–Apr 2026, full-time)
Stack: Python, PyTorch, XGBoost, Spark, Trino, PeerDB, Airflow, Great Expectations, Prometheus, Grafana, Whisper, wav2vec2.0, LangGraph, LlamaIndex, ClickHouse, Metabase

- [DRAFT-R9-1] [Lakehouse / PeerDB + Trino + Airflow + Great Expectations]:
  Consolidated raw CDC streams via PeerDB into Trino/Parquet lake storage at
  5TB/day, orchestrated with Airflow and guarded by Great Expectations data
  checks.
- [DRAFT-R9-2] [BNPL credit risk / XGBoost + PyTorch Transformers]: Shipped a
  BNPL default-risk ensemble (XGBoost plus PyTorch time-series Transformers)
  reaching AUC 0.87 in production scoring.
- [DRAFT-R9-3] [Support chatbot / Whisper + wav2vec2.0 + LangGraph]: Launched an
  agentic support chatbot on speech models plus LangGraph dialogue control,
  cutting ticket volume.
- [DRAFT-R9-4] [Product discovery / LlamaIndex retrieval]: Built LlamaIndex
  retrieval over product catalogs powering multilingual recommendation and
  search for regional retailers.
- [DRAFT-R9-5] [Risk engine + BI / ClickHouse + Metabase + Spark]: Directed a
  portfolio allocation and risk engine on streaming ClickHouse features with
  Metabase dashboards and Spark batch layers; Prometheus/Grafana observability
  throughout.

## R10 — Research Collaborator (Explainable & Robust AI), Sharif (Jun–Aug 2025, part-time)
Stack: PyTorch, MLflow, Captum, SHAP

- [DRAFT-R10-1] [Shift suites / PyTorch multimodal]: Constructed adversarial and
  natural distribution-shift suites over PyTorch multimodal perception models.
- [DRAFT-R10-2] [Attribution analysis / Captum + SHAP]: Ran Captum and SHAP
  attribution analyses to compare explanation stability between in-distribution
  and shifted inputs.
- [DRAFT-R10-3] [Experiment tracking / MLflow]: Tracked all shift-benchmark
  runs in MLflow for apples-to-apples comparison across model variants.
- [DRAFT-R10-4] [Robustness leaderboard / benchmark report]: Produced a
  robustness ranking across model variants under each shift type, with failure
  cases documented.
- [DRAFT-R10-5] [Deployment guide / regulated industry]: Authored a deployment
  guide with lab faculty codifying evaluation and monitoring practice for
  regulated-industry use.

## R11 — ML Engineer (Graph RAG), Iran Credit Scoring Bureau (Apr 2026–present, full-time)
Stack: Python, Neo4j, Cypher, Graph RAG, LangGraph, LangChain, FAISS, vLLM, TGI, GPU Optimization, AWQ, GPTQ, FastAPI, Kubernetes

- [DRAFT-R11-1] [Knowledge graph / Neo4j + Cypher]: Designed the Neo4j credit
  domain graph (schema, ingest, Cypher access patterns) grounding the
  assistant's answers in bureau data.
- [DRAFT-R11-2] [Tool-calling agent / LangGraph + LangChain]: Implemented
  Neo4j tool calls inside the LangGraph agent — schema-aware Cypher generation
  with FAISS vector retrieval as fallback.
- [DRAFT-R11-3] [GPU runtime / vLLM + TGI + AWQ + GPTQ]: Ran open-weight LLMs on
  GPU via vLLM and TGI, profiling KV-cache and batching with AWQ/GPTQ
  quantization for fit and throughput.
- [DRAFT-R11-4] [Trust + compliance / grounded citations]: Hardened the
  assistant for regulated financial use with retrieval grounding, citations on
  every claim and refusal paths for low-evidence answers.
- [DRAFT-R11-5] [Analyst service / FastAPI + Kubernetes]: Shipped the assistant
  as a FastAPI service on Kubernetes for credit-scoring analysts.

---

## TA TEMPLATE — per-semester Teaching Assistant entries (attach as semesters are added)
Usage: one position per semester, e.g. "Teaching Assistant — <Course> (<Term> <Year>)".

- [DRAFT-TA-1] [Lab sections]: Led weekly lab/recitation sections, walking
  students through problem sets and live coding exercises.
- [DRAFT-TA-2] [Grading + problem sets]: Graded assignments and exams; drafted
  and vetted problem-set questions with the lecturer.
- [DRAFT-TA-3] [Office hours]: Held office hours answering conceptual and
  debugging questions one-on-one.
- [DRAFT-TA-4] [Course material]: Prepared lab handouts, starter code and
  reference solutions for weekly topics.
- [DRAFT-TA-5] [Exams]: Proctored and graded midterms/finals; calibrated
  partial-credit rubrics with the teaching team.

---

## Linked projects — deliverable samples (parent role in brackets)

### P1 — Emotion-aware voice translation (part of TCD, May 2023–Apr 2024)
- [DRAFT-P1-1] Affect-logit SER module over wav2vec2.0 features.
- [DRAFT-P1-2] Prosody-fusion decoder preserving speaker emotion in translation.
- [DRAFT-P1-3] EmoDB/EmotionNet benchmark pack with balanced splits.
- [DRAFT-P1-4] Live speech-to-speech demo system.
- [DRAFT-P1-5] Reproducibility package (scripts, configs, checkpoints).

### P2 — Ultrasound report generation (part of UBC, Feb 2024–Nov 2025)
- [DRAFT-P2-1] ViT/BLIP encoder plus T5 generator training setup.
- [DRAFT-P2-2] Contrastive pretraining run on MIMIC-CXR/DICOM pairs.
- [DRAFT-P2-3] Saliency-overlay visualization for clinician review.
- [DRAFT-P2-4] BLEU/ROUGE-L plus clinical-accuracy benchmark.
- [DRAFT-P2-5] Manuscript draft on DICOM-compliant generation.

### P3 — Texture-free motion intelligence (part of L3S, May 2023–Feb 2024)
- [DRAFT-P3-1] Optical-flow video pipeline with temporal sampling.
- [DRAFT-P3-2] 3D CNN baselines in PyTorch Lightning.
- [DRAFT-P3-3] Transformer-hybrid models beating baselines on UCF-101/HMDB-51.
- [DRAFT-P3-4] Attention-map study of motion-vs-texture cues.
- [DRAFT-P3-5] Ablation harness and results report.
