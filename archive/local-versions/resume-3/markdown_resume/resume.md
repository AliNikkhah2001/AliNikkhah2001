# Ali Nikkhah

**Machine Learning Engineer / Researcher**  
Tehran, Iran · Remote-friendly · Open to Relocation | alinkkh9@gmail.com | +98 991 296 3951
[Website](https://alinikkhah2001.github.io) | [LinkedIn](https://linkedin.com/in/alinikkhah2001) | [GitHub](https://github.com/AliNikkhah2001)

## Summary
Applied ML researcher & engineer (Sharif B.Sc. EE 2020-2024, GPA 3.65/3.91; M.Eng. AI from Sep 2026) specialising in agentic RAG, multimodal vision-language, self-hosted LLM serving, and GPU runtime optimisation. Shipped LLM + CV pipelines at marketplace scale, self-hosted Graph RAG assistant for a national credit bureau, and BNPL risk platforms. Research focus: LLM reasoning and hallucination mitigation.


## Education
- **Sharif University of Technology** — M.Eng. Artificial Intelligence (2026-09 — present)  
  Thesis: LLM reasoning and hallucination mitigation
  Coursework: LLM Reasoning, Hallucination Mitigation, Multimodal Learning, Representation Learning
- **Sharif University of Technology** — B.Sc. Electrical & Electronics Engineering — Digital Systems (2020-09 — 2024-07)  
  GPA: 3.65 overall, 3.91 major
  Coursework: Deep Learning, Machine Learning, DSP, Linear Algebra, Probability & Statistics, Algorithm Design, Digital Systems Design
- **Atomic Energy High School** — Mathematics Diploma (2017-09 — 2019-06)  

## Experience
### ML Engineer — Self-Hosted Graph RAG Assistant — Iran Credit Scoring Bureau
*Tehran, Iran · Full-time · On-site · 2026-04 — Present*  
Self-hosted Graph RAG company assistant for national credit scoring — Neo4j knowledge graph, self-hosted LLM runtime on GPU, tool-calling agent.
- Architected self-hosted Graph RAG assistant: Neo4j knowledge graph + vector retrieval fused into an agent that answers analyst queries over credit-scoring domain data with grounded citations.
- Ran self-hosted open-weight LLMs (vLLM/TGI) on GPU; profiled and optimised GPU runtime — KV-cache, batching, quantization (AWQ/GPTQ) — cutting per-token latency and GPU memory footprint.
- Implemented Neo4j tool-calls (Cypher generation + schema-aware retrieval) so the assistant executes graph traversals instead of hallucinating structured facts.
- Added hallucination guardrails — retrieval grounding, citation enforcement, deterministic fallback — for a regulated financial environment.
  **Stack:** Python, Neo4j, Cypher, Graph RAG, LangGraph, LangChain, FAISS, vLLM, TGI, PyTorch, GPU Optimization, AWQ, GPTQ, FastAPI, Kubernetes

### Senior Data Scientist & Data Engineer — Turquoise Digital
*Tehran, Iran · Full-time · On-site · 2025-09 — 2026-03*  
Directed AI for regional retailers — multilingual reco, BNPL credit-risk ensemble (AUC 0.87), agentic support chatbot, centralized data lake + observability.
- Centralized lake from raw CDC via PeerDB + Trino/Parquet on 5TB/day, <60s freshness; Airflow + PySpark DAGs cut memory 60%, governed by Great Expectations + Prometheus/Grafana.
- Built default-risk ensemble (XGBoost + time-series Transformers) — AUC 0.87, -22% defaults; 50+ concurrent mSPRT A/B tests with canary & auto-rollback, presented to C-suite.
- Shipped Whisper/wav2vec2.0 + LangGraph agentic chatbot — -78% ticket volume, 94% intent accuracy; deterministic fallback + policy guardrails for auditability.
- Drove portfolio allocation & risk engine (Sharpe +0.42) with streaming ClickHouse signals; LlamaIndex retrieval graph for ranking features.
  **Stack:** Python, PyTorch, Spark, Trino, PeerDB, Airflow, Great Expectations, Prometheus, Grafana, Whisper, wav2vec2.0, LangGraph, LlamaIndex, ClickHouse, Metabase

### Computer Vision / ML Platform Engineer (Edge) — Advanced Analytics Australia
*Remote · Australia (Tehran-based) · Remote Contract · 2025-09 — 2026-04*  
Edge CV platform across 12 retail sites, 100+ cameras @30 FPS, Kafka streaming, quantized TensorRT/TF Lite + Triton serving.
- Deployed YOLO + ViT quantized (TensorRT/TF Lite) on Triton — 99.2% uptime <50ms p99, 3.5x speedup, exactly-once Kafka, 30 FPS over 100+ streams.
- Built edge MLOps with Triton model repository, zero-downtime rolling updates, automated rollback, Prometheus/Grafana per-site health.
- Cut false positives -35% via attention-guided NMS + SNR monitoring; broker architecture for 12 distributed sites.
  **Stack:** Python, OpenCV, YOLO, ViT, TensorRT, TFLite, Triton, Kafka, Docker, Kubernetes, Prometheus, Grafana, ONNX

### Machine Learning Researcher — Emotion-Aware Speech Translation — Trinity College Dublin — EmoDub Project
*Dublin, Ireland · Part-time · Remote Collaboration · 2025-05 — 2025-11*  
Fusion of SER transformers + wav2vec2.0 for prosody-preserving S2S translation; cross-modal acoustic+semantic transformer.
- Trained SER front-end (transformer + wav2vec2.0 + Whisper) for affect logits; cross-modal fusion transformer for emotion-consistent decoding.
- Curated emotion-annotated corpora (EmotionNet/EmoDB) with balanced cultural representation; evaluated BLEU, Emotion F1, MOS.
- Collab. with Prof. Siobhán Clarke; reproducible codebase https://github.com/AliNikkhah2001/emodub-emotion-translation.
  **Stack:** PyTorch, TensorFlow, Hugging Face, librosa, wav2vec2.0, Whisper, EmotionNet, EmoDB

### Research Collaborator — Explainable & Robust AI — Sharif University — Robust & Interpretable ML Lab
*Tehran, Iran · Part-time · On-site · 2025-07 — 2025-09*  
Robustness & interpretability harnesses for multimodal perception under distribution shift.
- Benchmarked adversarial + natural shift suites; notebooks surfacing Captum/SHAP attributions, saliency, counterfactuals.
- Documented deploy best-practices for regulated industries with faculty.
  **Stack:** PyTorch, MLflow, Captum, SHAP

### AI Engineering R&D Lead — Digikala
*Tehran, Iran · Full-time · On-site · 2025-01 — 2025-08*  
Owned agentic RAG platform for marketplace listing intelligence — modular control pipelines (MCP), hybrid retrieval, LLM serving at 5M+ queries/day.
- Led team of 5 defining R&D roadmap + SLOs; shipped MCP with LangGraph cyclic graphs, zero-downtime hot-swapping, health-checked agent composition with deterministic fallback.
- Hybrid retrieval FAISS + Elasticsearch RRF + HyDE + KAG — +23% recall@10, -41% hallucination; multi-tier Redis caching, p99 <200ms.
- LLM serving on vLLM (PagedAttention) + Triton — 3.2x throughput, 60% cost reduction; 200 pods, MIG/HPA/VPA, Prometheus KV-cache dashboards.
- Partnered with infra/product establishing eval pipelines, A/B guardrails, canary rollouts.
  **Stack:** Python, LangGraph, LangChain, LlamaIndex, FAISS, Elasticsearch, ChromaDB, HyDE, KAG, FastAPI, vLLM, Triton, Redis, Kubernetes, ArgoCD

### AI Engineer — Digikala
*Tehran, Iran · Part-time · Hybrid · 2024-11 — 2025-01*  
Prototyped MCP + RAG scaffolding that scaled to org-wide mandate.
- Implemented LangGraph orchestration layers with health monitoring; hybrid retrieval with RRF + deterministic fallbacks for auditability.
- Embedded eval telemetry, memory-efficient indexing, response caching; load-tested to 5M queries.
  **Stack:** LangChain, LlamaIndex, FAISS, Elasticsearch, FastAPI

### Research Assistant — Vision-Language Medical Imaging (Ultrasound Report Generation) — University of British Columbia
*Remote · Vancouver, Canada (Tehran-based) · Part-time · Remote Internship (10h/wk) · 2024-02 — 2025-11*  
ViT/BLIP + T5 for DICOM-compliant ultrasound reporting with contrastive pretraining and clinician-in-the-loop saliency.
- Designed ViT/BLIP encoders + T5 generator with contrastive/self-supervised alignment; curated DICOM, de-identified QA corpora.
- Deployed attention/saliency overlays for interpretability; benchmarked BLEU/ROUGE-L + clinical efficacy with radiologists; SOTA on in-house split.
- Preprint in prep: Automated DICOM-Compliant Ultrasound Report Generation via Contrastive Vision-Language Learning (2025).
  **Stack:** PyTorch, ViT, BLIP, T5, LLaVA, CLIP, OpenCV, MIMIC-CXR, PubMed, DICOM

### Research Assistant — Video Motion Classification — L3S Research Center — Leibniz University Hannover
*Hannover, Germany · Part-time · Remote/On-site · 2023-04 — 2024-02*  
Texture-free motion models via optical flow + 3D CNNs + transformers; SOTA on UCF-101/HMDB-51.
- Engineered optical-flow-centric datasets with temporal sampling/augmentation; improved domain generalization across lighting/texture/camera shift.
- Benchmarked 3D CNN + transformer hybrids vs baselines; analyzed attention maps; reduced overfitting, SOTA accuracy.
  **Stack:** PyTorch Lightning, OpenCV, PyAV, TensorBoard, scikit-learn, Multimodal Models

### Teaching Assistant — NLP, Generative Models, Deep Learning — Sharif University of Technology
*Tehran, Iran · Part-time · On-site · 2023-08 — 2024-01*  
Led labs/seminars for graduate NLP/GenAI/DL; mentored capstones.
- Facilitated seminars, office hours (30-80 students), problem-set design/grading, exam design for DL/NLP.
- Developed lab material for Deep Learning, Analog Electronics, foundational ML; mentored undergrad capstones.
  **Stack:** PyTorch, TensorFlow, NumPy, scikit-learn

### Teaching Assistant — History (8 courses, 2021-2023) — Sharif University of Technology
*Tehran, Iran · Part-time · 2021-01 — 2023-08*  
Three-year TA service across 8 courses — Deep Learning, ML & Data Science, Generative Models, Engineering Prob & Stats, Analog Electronics, Circuit Theory.
- Graded problem sets, ran tutorials, held office hours; supported 30-80 students per term.
  **Stack:** PyTorch, TensorFlow, NumPy

### MLOps Engineer (Founding) — HomaCloud
*Tehran, Iran · Full-time · On-site · 2021-08 — 2022-02*  
Built K8s-native training, CI/CD, and serving infra from scratch — Docker/K8s, Ray, MLflow, FastAPI/TF Serving, Terraform, ArgoCD.
- Provisioned multi-node K8s via Terraform; Ray + MLflow training pipelines, TF Serving + FastAPI — <10 min releases, 99.9% deploy success, 15+ models.
- GitOps with GitHub Actions, canary, spot-instance optimization; Prometheus/Grafana + ELK observability; registry + lineage.
  **Stack:** Kubernetes, Docker, Ray, MLflow, Terraform, ArgoCD, FastAPI, Prometheus, Grafana, GitHub Actions

### MLOps Intern — HomaCloud
*Tehran, Iran · Internship · 2021-05 — 2021-08*  
Evaluated PyTorch/TF + multi-node training; built serving/API automation for dataset prep & deployment.

### Full Stack Engineer — Mapna-MD2
*Tehran, Iran · Part-time · 2021-01 — 2021-05*  
Dashboards + partner integrations (React/Node/Postgres/Docker); QA/deployment scripts.
  **Stack:** React, Node.js, PostgreSQL, Docker

## Skills
- **languages:** Python, C++, Go, SQL, R, Bash, TypeScript
- **ml_vision:** PyTorch, TensorFlow, JAX, Hugging Face, ViT, BLIP, T5, Whisper, wav2vec2.0, Librosa, OpenCV, YOLO, ONNX
- **agentic:** LangGraph, LangChain, LlamaIndex, FAISS, ChromaDB, HyDE, KAG, Graph RAG, vLLM, Triton, Neo4j, Cypher
- **llm_serving:** vLLM, TGI, AWQ, GPTQ, KV-cache, GPU Optimization, PagedAttention, TensorRT-LLM
- **data_mlop:** Spark, Airflow, Kafka, Docker, Kubernetes, Ray, MLflow, W&B, ArgoCD, Terraform
- **human:** Persian (Native), English (C2 IELTS 8.0), Arabic (Professional), French (Limited), German (Limited)

## Research Projects
- **Emotion-aware voice translation** — Trinity College Dublin · EmoDub (May 2025 – Nov 2025)
- **Ultrasound report generation** — University of British Columbia (Feb 2024 – Nov 2025)
- **Texture-free motion intelligence** — L3S Research Center (Apr 2023 – Feb 2024)

## Publications
- Automated DICOM-Compliant Ultrasound Report Generation via Contrastive Vision-Language Learning — Ali Nikkhah, [Co-authors TBD], A. Supervisor — *arXiv preprint — in preparation* (2025)

## Teaching
- Natural Language Processing (Graduate) — TA · Sharif (Aug 2023 – Jan 2024)
- Generative Models (Graduate) — TA · Sharif (Aug 2023 – Jan 2024)
- Deep Learning (Graduate) — TA · Sharif (Jan 2023 – Aug 2023)
- Analog Electronics — TA · Sharif (Aug 2022 – Jan 2023)
- Machine Learning & Data Science — TA · Sharif (Jan 2022 – Aug 2022)
- Circuit Theory & Engineering Probability — TA · Sharif (Jan 2021 – Aug 2021)

## Honors
- Iran University entrance exam distinction
- IELTS Academic (Computer) — Band 8

## Certifications
- Intro to ML in Production
- Building Systems with ChatGPT API
- ChatGPT Prompt Engineering
- Diffusion Models
- Web Dev with PHP