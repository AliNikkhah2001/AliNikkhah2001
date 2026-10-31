# Experience Drafts — REVIEW REQUIRED (multi-agent pass)

> Status: **DRAFT, `verified=false`, NOT in the live DB.** Generated in parallel by
> 3 drafting agents (industry roles / research roles / TA+projects), each grounded
> only in that role's existing tech stack, summary, org and dates. **No new
> technology was invented.** Every number, metric, scale claim and scope statement
> is a **placeholder for you to confirm, correct or delete**. `[X]` / `[N]` /
> "placeholder" marks mean "fill in the real value".
> Reply per role with keep / edit / kill (e.g. "R2: keep 1,3,5; fix 2 to 4 nodes").
> Only approved bullets will be written into `career_db.json`.

How to read a sample: `[project / framework]` → draft bullet.

---

## R1 — MLOps Intern, HomaCloud (Aug–Nov 2021, full-time)
Stack: Python, PyTorch, TensorFlow, Docker, FastAPI

- [DRAFT-R1-1] [training-setup / Docker] Built Docker-based Python prototypes to stand up PyTorch and TensorFlow multi-node training jobs for initial feasibility testing.
- [DRAFT-R1-2] [dataset-automation / FastAPI] Built FastAPI endpoints in Python with Docker packaging to automate dataset preparation and trigger deployment jobs.
- [DRAFT-R1-3] [training-scale / PyTorch] Tuned data loading in Dockerized Python jobs to improve PyTorch and TensorFlow multi-node throughput by about 20% in test runs.
- [DRAFT-R1-4] [framework-eval / TensorFlow] Compared PyTorch versus TensorFlow runs on training time and accuracy to recommend serving and deployment options.
- [DRAFT-R1-5] [delivery-handoff / FastAPI] Shipped FastAPI automation for dataset preparation and Docker deployment steps with usage docs to support handoff to engineering.

## R2 — MLOps Engineer, HomaCloud (Nov 2021–Dec 2022, full-time)
Stack: Kubernetes, Docker, Ray, MLflow, Terraform, ArgoCD, FastAPI, Prometheus, Grafana, GitHub Actions

- [DRAFT-R2-1] [infra-setup / Terraform] Provisioned Kubernetes training environments with Terraform and Docker images to standardize prototyping across projects.
- [DRAFT-R2-2] [training-pipeline / Ray] Built Kubernetes-native training workflows on Ray with MLflow tracking and FastAPI serving endpoints for model deployment.
- [DRAFT-R2-3] [serving-scale / Kubernetes] Scaled model serving on Kubernetes with Ray replicas to sustain around 10k requests per day while tracking latency in Prometheus and Grafana.
- [DRAFT-R2-4] [quality-tracking / MLflow] Standardized MLflow evaluation logging with Prometheus metrics and Grafana dashboards to compare runs on latency and quality.
- [DRAFT-R2-5] [release-automation / ArgoCD] Automated delivery with GitHub Actions and ArgoCD for Docker builds and FastAPI releases to streamline collaboration with developers.

## R3 — AI Engineer, Digikala (Dec 2022–Dec 2023, full-time)
Stack: Python, LangChain, LlamaIndex, FAISS, Elasticsearch, LangGraph, FastAPI

- [DRAFT-R3-1] [assistant-prototype / LangChain] Prototyped marketplace listing assistant in Python with LangChain and FastAPI to scaffold RAG and MCP flows for early testing.
- [DRAFT-R3-2] [hybrid-retrieval / LlamaIndex] Built hybrid retrieval with LlamaIndex over FAISS and Elasticsearch to combine dense and keyword results for listings.
- [DRAFT-R3-3] [orchestration / LangGraph] Implemented orchestration in LangGraph with LangChain and FastAPI to route retrieval and generation steps with p95 under 2s in prototype tests.
- [DRAFT-R3-4] [eval-telemetry / FastAPI] Added Python eval telemetry in FastAPI to log retrieval hits and answer quality for review of prototype iterations.
- [DRAFT-R3-5] [delivery-handoff / FastAPI] Delivered FastAPI prototype endpoints with LangGraph flow docs to support collaboration with product and engineering.

## R4 — Machine Learning Engineer, Emotion-Aware Speech Translation, Trinity College Dublin (May 2023–Apr 2024, part-time remote)
Stack: PyTorch, Hugging Face, librosa, wav2vec2.0, Whisper, EmotionNet, EmoDB

- [DRAFT-R4-1] [EmoDub / librosa] Built librosa pipelines curating EmotionNet and EmoDB clips with denoising and prosody-preserving segmentation for translation training.
- [DRAFT-R4-2] [EmoDub / PyTorch] Developed PyTorch fusion model combining Hugging Face speech-emotion-recognition transformers with wav2vec2.0 and Whisper to preserve prosody in speech-to-speech translation.
- [DRAFT-R4-3] [EmoDub / EmoDB] Evaluated on EmoDB and EmotionNet splits with Hugging Face workflows, improving emotion preservation by a placeholder margin the user will verify.
- [DRAFT-R4-4] [EmoDub / wav2vec2.0] Analyzed wav2vec2.0 and Whisper embeddings against librosa prosody contours to diagnose emotion loss across EmotionNet categories.
- [DRAFT-R4-5] [EmoDub / Hugging Face] Released Hugging Face checkpoints and PyTorch inference demo for EmoDub emotion-aware translation for project handoff.

## R5 — Research Assistant, Video Motion Classification, L3S Hannover (May 2023–Feb 2024, part-time)
Stack: PyTorch Lightning, OpenCV, PyAV, TensorBoard, scikit-learn

- [DRAFT-R5-1] [L3S / PyAV] Built PyAV and OpenCV decoding pipelines generating texture-free optical-flow frames from raw video at placeholder scale for motion training.
- [DRAFT-R5-2] [L3S / PyTorch Lightning] Trained 3D CNN and transformer motion models in PyTorch Lightning on optical-flow inputs to isolate motion from appearance.
- [DRAFT-R5-3] [L3S / scikit-learn] Evaluated on UCF-101 and HMDB-51 with scikit-learn metrics and TensorBoard tracking, reaching placeholder state-of-the-art accuracy the user will verify.
- [DRAFT-R5-4] [L3S / TensorBoard] Analyzed errors with scikit-learn confusion analysis and TensorBoard traces with OpenCV flow overlays to localize motion-ambiguity failures.
- [DRAFT-R5-5] [L3S / OpenCV] Delivered reproducible PyTorch Lightning checkpoints with OpenCV and PyAV preprocessing and TensorBoard logs as publication artifact.

## R6 — Senior AI Engineer, Digikala (Dec 2023–May 2025, full-time) — NO team-leadership claims
Stack: Python, LangGraph, LangChain, LlamaIndex, FAISS, Elasticsearch, ChromaDB, HyDE, KAG, FastAPI, vLLM, Triton, Redis, Prometheus, Kubernetes, ArgoCD

- [DRAFT-R6-1] [control-pipeline / LangGraph] Prototyped MCP control pipelines in Python with LangGraph and FastAPI to scaffold tool routing for the agentic RAG platform.
- [DRAFT-R6-2] [hybrid-retrieval / LlamaIndex] Built hybrid retrieval with LlamaIndex, LangChain, FAISS, Elasticsearch and ChromaDB enhanced with HyDE and KAG for grounded answers.
- [DRAFT-R6-3] [llm-serving / vLLM] Operated LLM serving with vLLM and Triton on Kubernetes with Redis caching and FastAPI to sustain 5M+ queries per day at p95 under 800ms.
- [DRAFT-R6-4] [quality-eval / Prometheus] Improved answer quality with Prometheus telemetry tracking retrieval precision and latency across HyDE and KAG variants.
- [DRAFT-R6-5] [delivery-collab / ArgoCD] Shipped releases with ArgoCD on Kubernetes and shared Prometheus dashboards and FastAPI docs to support joint work with product and platform peers.

## R7 — Research Assistant, Vision-Language Medical Imaging, UBC (Feb 2024–Nov 2025, part-time)
Stack: PyTorch, ViT, BLIP, T5, CLIP, OpenCV, MIMIC-CXR, DICOM

- [DRAFT-R7-1] [UBC Ultrasound / OpenCV] Built OpenCV and PyTorch pipelines curating DICOM ultrasound frames paired with MIMIC-CXR reports for contrastive pretraining.
- [DRAFT-R7-2] [UBC Ultrasound / PyTorch] Developed ViT and BLIP encoders with T5 decoders in PyTorch using CLIP-style contrastive pretraining for ultrasound report generation.
- [DRAFT-R7-3] [UBC Ultrasound / MIMIC-CXR] Evaluated on held-out MIMIC-CXR and DICOM splits, improving report accuracy by a placeholder margin the user will verify.
- [DRAFT-R7-4] [UBC Ultrasound / CLIP] Integrated clinician-in-the-loop saliency review visualizing ViT and CLIP attention with OpenCV overlays to validate anatomical grounding.
- [DRAFT-R7-5] [UBC Ultrasound / DICOM] Delivered DICOM-compliant PyTorch inference pipeline with BLIP and T5 checkpoints for clinical collaborator testing.

## R8 — Computer Vision / ML Platform Engineer (Edge), Advanced Analytics Australia (Apr 2024–May 2025, part-time remote)
Stack: Python, OpenCV, YOLO, ViT, TensorRT, TFLite, Triton, Kafka, Docker, Kubernetes, Prometheus, Grafana, ONNX

- [DRAFT-R8-1] [Edge Platform / Kafka] Built Python with OpenCV and Kafka streaming pipelines ingesting 100+ cameras at 30 FPS across 12 retail sites into ONNX-standardized frames.
- [DRAFT-R8-2] [Edge Platform / Triton] Optimized YOLO and ViT detectors with TensorRT and TFLite quantization served on Triton for edge inference.
- [DRAFT-R8-3] [Edge Platform / ONNX] Benchmarked ONNX models for latency and accuracy with Prometheus tracking, achieving a placeholder FPS gain the user will verify.
- [DRAFT-R8-4] [Edge Platform / Grafana] Analyzed failures and drift with Grafana dashboards over Prometheus metrics correlating Triton latency with OpenCV video quality.
- [DRAFT-R8-5] [Edge Platform / Kubernetes] Shipped Dockerized Triton services on Kubernetes with Kafka integration and Grafana monitoring for production rollout.

## R9 — Senior Data Scientist & Data Engineer, Turquoise Digital (May 2025–Apr 2026, full-time)
Stack: Python, PyTorch, XGBoost, Spark, Trino, PeerDB, Airflow, Great Expectations, Prometheus, Grafana, Whisper, wav2vec2.0, LangGraph, LlamaIndex, ClickHouse, Metabase

- [DRAFT-R9-1] [data-lake-setup / Airflow] Set up centralized data lake ingestion with Airflow, PeerDB, Spark and Trino to prototype retailer analytics tables.
- [DRAFT-R9-2] [risk-reco-build / XGBoost] Built PyTorch multilingual recommendation features and XGBoost credit-risk ensemble for BNPL scoring reported at AUC 0.87.
- [DRAFT-R9-3] [chatbot-scale / LangGraph] Built agentic support chatbot with LangGraph and LlamaIndex using Whisper and wav2vec2.0 transcripts to handle around 5k chats per day with ClickHouse logging.
- [DRAFT-R9-4] [quality-eval / Great Expectations] Enforced data quality with Great Expectations checks in Airflow and Prometheus and Grafana alerts with Metabase views for review.
- [DRAFT-R9-5] [delivery-collab / Metabase] Delivered Metabase dashboards on ClickHouse and Trino with Airflow docs and Grafana monitors to support collaboration with retail stakeholders.

## R10 — Research Collaborator, Explainable & Robust AI, Sharif (Jun–Aug 2025, part-time)
Stack: PyTorch, MLflow, Captum, SHAP

- [DRAFT-R10-1] [RIML / PyTorch] Built PyTorch data pipelines stressing multimodal perception models under distribution shift with versioned runs in MLflow.
- [DRAFT-R10-2] [RIML / MLflow] Implemented PyTorch robustness harnesses for multimodal perception models with MLflow-tracked ablations across shift conditions.
- [DRAFT-R10-3] [RIML / PyTorch] Benchmarked robustness drops across shift splits logging placeholder accuracy gaps in MLflow for comparison.
- [DRAFT-R10-4] [RIML / Captum] Performed Captum and SHAP attribution analysis to localize brittle features driving failures under distribution shift.
- [DRAFT-R10-5] [RIML / MLflow] Delivered MLflow-tracked robustness toolkit with PyTorch harnesses and Captum and SHAP reports as lab publication artifact.

## R11 — ML Engineer (Graph RAG), Iran Credit Scoring Bureau (Apr 2026–present, full-time)
Stack: Python, Neo4j, Cypher, Graph RAG, LangGraph, LangChain, FAISS, vLLM, TGI, GPU Optimization, AWQ, GPTQ, FastAPI, Kubernetes

- [DRAFT-R11-1] [graph-setup / Neo4j] Prototyped Neo4j knowledge graph schema with Cypher loaders in Python to model credit-scoring entities for analyst search.
- [DRAFT-R11-2] [agent-build / LangGraph] Built tool-calling Graph RAG agent with LangGraph, LangChain and FAISS over Neo4j to return grounded citations.
- [DRAFT-R11-3] [gpu-runtime / vLLM] Optimized GPU-resident runtime with vLLM and TGI using AWQ and GPTQ quantization and GPU Optimization to cut latency by about 30% in test runs.
- [DRAFT-R11-4] [quality-eval / Cypher] Measured citation grounding with Cypher-based checks and FAISS retrieval scoring in Python to track answer quality.
- [DRAFT-R11-5] [delivery-collab / FastAPI] Shipped FastAPI assistant endpoints on Kubernetes with usage guides to support daily work with credit-scoring analysts.

---

## TA TEMPLATE — per-semester Teaching Assistant, Sharif (2021–2024)
Attach one set per semester as semesters are added. `[X]` / `[N]` / `[Y]` = fill in real values.
Courses on record: Circuit Theory & Engineering Probability, ML & Data Science, Analog Electronics, Deep Learning (grad), NLP (grad), Generative Models (grad).

- [DRAFT-TA-1] [lab sections] Led weekly lab/recitation sections for [X] students, demonstrating problem-solving workflows and guided practice exercises.
- [DRAFT-TA-2] [grading/problem sets] Graded [X] assignments and exams per term with structured feedback and consistent rubrics for [Y] submissions.
- [DRAFT-TA-3] [office hours] Held [N] office hours per week for [X] students, resolving conceptual questions and assignment clarifications.
- [DRAFT-TA-4] [course material] Prepared lab handouts and starter code plus drafted [X] problem sets with worked solutions per semester.
- [DRAFT-TA-5] [exams] Supported [X] exams per term including proctoring, drafting questions, and preparing grading keys for [Y] examinees.

---

## Linked projects — deliverable samples (parent role in brackets)

### P1 — Emotion-aware voice translation (part of TCD R4, May 2023–Apr 2024)
- [DRAFT-P1-1] Built PyTorch module coupling Whisper transcripts with wav2vec2.0 features for emotion-preserving translation on EmoDB.
- [DRAFT-P1-2] Benchmarked SER transformers vs. wav2vec2.0 baselines on EmoDB/EmotionNet across [X] emotion labels.
- [DRAFT-P1-3] Delivered demo translating [X] Whisper-decoded utterances while retaining source emotion tags from SER transformers.
- [DRAFT-P1-4] Packaged PyTorch training pipeline for wav2vec2.0 and Whisper fine-tuning on [X] hours of EmoDB/EmotionNet audio.
- [DRAFT-P1-5] Released evaluation module scoring translation quality and emotion retention on [X] held-out EmotionNet splits.

### P2 — Ultrasound report generation (part of UBC R7, Feb 2024–Nov 2025)
- [DRAFT-P2-1] Built ViT-BLIP encoding module generating T5 draft reports from DICOM inputs with CLIP pretraining.
- [DRAFT-P2-2] Benchmarked BLIP + T5 vs. ViT + T5 report quality on [X] MIMIC-CXR studies with CLIP pretraining ablations.
- [DRAFT-P2-3] Delivered demo generating T5 findings from [X] DICOM images with ViT attention overlays for review.
- [DRAFT-P2-4] Packaged DICOM-to-MIMIC-CXR preprocessing module feeding ViT-BLIP-T5 training with [X] curated cases.
- [DRAFT-P2-5] Released evaluation package scoring BLIP-T5 outputs with CLIP similarity on [X] held-out MIMIC-CXR reports.

### P3 — Texture-free motion intelligence (part of L3S R5, May 2023–Feb 2024)
- [DRAFT-P3-1] Built optical-flow input module for 3D CNNs and transformers isolating motion cues on UCF-101/HMDB-51.
- [DRAFT-P3-2] Benchmarked 3D CNNs vs. transformers on texture-free optical flow across [X] UCF-101/HMDB-51 classes.
- [DRAFT-P3-3] Delivered demo classifying [X] UCF-101 clips from optical flow alone with side-by-side RGB comparison.
- [DRAFT-P3-4] Packaged optical-flow extraction and 3D CNN training pipeline for [X] hours of UCF-101/HMDB-51 video.
- [DRAFT-P3-5] Released robustness benchmark reporting transformer accuracy drops on [X] texture-stripped HMDB-51 splits.
