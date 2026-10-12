"""Deterministic interview-prep question generation for the career dashboard.

Stdlib only; imports standalone (no main.py imports). Question ids are stable
in the form q_<category>_<n>, assigned during a deterministic traversal.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

VALID_STATUSES = ("unprepared", "drafted", "confident")
CATEGORIES = ("deep_dive", "project", "behavioral", "fundamentals")


def _get(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [v for v in value if v is not None]
    return [value]


def _text_of(item, keys=("text", "description", "summary", "detail", "content", "bullet", "title", "name")):
    if item is None:
        return ""
    if isinstance(item, str):
        return item.strip()
    for key in keys:
        value = _get(item, key, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _id_of(item):
    if item is None:
        return ""
    if isinstance(item, (str, int)):
        return str(item).strip()
    for key in ("id", "slug", "uuid", "key", "name", "title"):
        value = _get(item, key, None)
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return ""


def _section(db, *keys):
    for key in keys:
        value = _get(db, key, None)
        if isinstance(value, list):
            return value
    return []


def _tokens(text):
    stop = {"pos", "org", "ach", "teach", "the", "of", "and", "for", "a", "an"}
    return {t for t in re.split(r"[^a-z0-9]+", str(text or "").lower()) if t and t not in stop}


def _stack_of(item):
    for key in ("tech_stack", "stack", "technologies", "technology", "tools", "tech", "tech_used", "skills"):
        value = _get(item, key, None)
        if not value:
            continue
        names = []
        for entry in _as_list(value):
            name = _text_of(entry, keys=("name", "title", "label", "skill", "technology"))
            if name:
                names.append(name)
        if names:
            return names
    return []


_KNOWN_TECH = {
    "react": "React", "node": "Node", "postgres": "Postgres", "docker": "Docker",
    "pytorch": "PyTorch", "tensorflow": "TensorFlow", "numpy": "NumPy", "fastapi": "FastAPI",
    "kubernetes": "Kubernetes", "spark": "Spark", "airflow": "Airflow", "opencv": "OpenCV",
    "python": "Python", "typescript": "TypeScript", "redis": "Redis",
    "elasticsearch": "Elasticsearch", "grafana": "Grafana", "prometheus": "Prometheus",
    "mlflow": "MLflow", "ray": "Ray", "terraform": "Terraform", "kafka": "Kafka",
    "scikit-learn": "scikit-learn", "hugging face": "Hugging Face", "llm": "LLM",
    "ci/cd": "CI/CD", "qa": "QA",
}


def _stack_hint(pos):
    stack = _stack_of(pos)
    if stack:
        return stack, False
    raw = " ".join(str(_get(pos, key) or "") for key in ("summary", "description_md", "description"))
    found = [
        display for token, display in _KNOWN_TECH.items()
        if re.search(r"(?<![a-z0-9-])" + re.escape(token) + r"(?![a-z0-9-])", raw, re.I)
    ]
    if re.search(r"(?<![A-Za-z])TF(?![A-Za-z])", raw) and "TensorFlow" not in found:
        found.append("TensorFlow")
    return found, True


def _org_names(db):
    mapping = {}
    for org in _section(db, "organizations", "orgs", "companies"):
        name = _text_of(org, keys=("name", "title", "label", "organization"))
        oid = _id_of(org)
        if oid and name:
            mapping[oid] = name
    return mapping


def _position_org(item, orgs_by_id):
    for key in ("organization", "organization_name", "org", "company", "employer"):
        value = _get(item, key, None)
        if isinstance(value, str) and value.strip():
            raw = value.strip()
            return orgs_by_id.get(raw, raw)
        if value is not None and not isinstance(value, str):
            name = _text_of(value, keys=("name", "title", "label"))
            if name:
                return name
    for key in ("organization_id", "org_id", "company_id"):
        value = _get(item, key, None)
        if isinstance(value, (str, int)) and str(value).strip():
            return orgs_by_id.get(str(value), str(value))
    return ""


def _full_title(item):
    return _text_of(item, keys=("title", "role", "position_title", "name")) or "this role"


def _short_title(item):
    title = _full_title(item)
    for sep in ("\u2014", "\u2013", " - "):
        if sep in title:
            title = title.split(sep)[0].strip()
    return title or "this role"


def _role_phrase(item, orgs_by_id, short=True):
    title = _short_title(item) if short else _full_title(item)
    org = _position_org(item, orgs_by_id)
    return f"{title} at {org}" if org else title


def _snippet(text, limit=170):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:-\u2014")
    return cut + "..."


def _enum(items, max_items=6):
    items = [str(i) for i in items if str(i).strip()][:max_items]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_MEASURE_RE = re.compile(r"\d{2,}|\d+(?:\.\d+)?\s*(?:%|x\b|TB\b|GB\b|M\b|h\b)")
_METRIC_TERM_RE = re.compile(
    r"\b(?:BLEU|ROUGE|F1|MOS|AUC|accuracy|precision|recall|Sharpe|p99|uplift|latency|freshness|uptime|speedup)\b",
    re.I,
)
_PROTECTED_DOT_RE = re.compile(r"(?<=\d)\.(?=\d)")


def _clauses(text):
    protected = _PROTECTED_DOT_RE.sub("\u0001", text or "")
    clauses = []
    for part in re.split(r"[.!?]+", protected):
        part = re.sub(r"\s+", " ", part.replace("\u0001", ".")).strip(" -\u2022\t")
        if len(part) >= 15:
            clauses.append(part)
    return clauses


def _metric_claims(texts, limit=2):
    claims = []
    for text in texts:
        for clause in _clauses(text):
            if _MEASURE_RE.search(_YEAR_RE.sub("", clause)) or _METRIC_TERM_RE.search(clause):
                claims.append(_snippet(clause, 200))
                break
        if len(claims) >= limit:
            break
    return claims


def _find_position(positions, needle):
    needle = str(needle or "").strip()
    if not needle:
        return None
    for pos in positions:
        if _id_of(pos) == needle:
            return pos
    return None


def _resolve_reference(ref, db, positions, orgs_by_id):
    if ref is None:
        return None
    if isinstance(ref, dict):
        return _role_phrase(ref, orgs_by_id)
    ref = str(ref).strip()
    if not ref:
        return None
    match = _find_position(positions, ref)
    if match is not None:
        return _role_phrase(match, orgs_by_id)
    for edu in _section(db, "education"):
        if _id_of(edu) == ref:
            degree = _text_of(edu, keys=("degree", "title", "name")) or "graduate studies"
            org = _position_org(edu, orgs_by_id)
            return f"{degree} at {org}" if org else degree
    for proj in _section(db, "projects"):
        if _id_of(proj) == ref:
            return f"the {_text_of(proj, keys=('name', 'title')) or ref} project"
    ref_tokens = _tokens(ref)
    best, best_score = None, 0
    for pos in positions:
        score = len(ref_tokens & _tokens(_id_of(pos)))
        if score > best_score:
            best, best_score = pos, score
    if best is not None and best_score >= 1:
        return _role_phrase(best, orgs_by_id)
    return re.sub(r"^pos_", "", ref).replace("_", " ").strip() or None


def _position_achievements(pos, pid, all_achievements):
    result = []
    seen = set()

    def push(item):
        marker = _id_of(item) or _text_of(item)[:40]
        if marker and marker not in seen:
            seen.add(marker)
            result.append(item)

    for embedded in _as_list(_get(pos, "achievements", None)):
        if isinstance(embedded, dict):
            push(embedded)
        elif embedded is not None:
            wanted = str(embedded).strip()
            for achievement in all_achievements:
                if _id_of(achievement) == wanted:
                    push(achievement)
    for achievement in all_achievements:
        pids = [str(v) for v in _as_list(_get(achievement, "position_ids", None))]
        if not pids:
            pids = [str(v) for v in _as_list(_get(achievement, "position_id", None))]
        if pid and pid in pids:
            push(achievement)
    return result


def _concurrent_context(pos, db, positions, orgs_by_id):
    raw = _get(pos, "concurrent_with", None)
    if not raw:
        return None, None
    parts = []
    for entry in _as_list(raw):
        phrase = _resolve_reference(entry, db, positions, orgs_by_id)
        if phrase and phrase not in parts:
            parts.append(phrase)
    if not parts:
        return None, None
    note = _get(pos, "concurrent_note", None)
    return _enum(parts), (str(note).strip() if isinstance(note, str) and note.strip() else None)


def _project_links(proj, positions, achievements, orgs_by_id):
    proj_org_id = _get(proj, "organization_id", None)
    proj_org_tokens = _tokens(_position_org(proj, orgs_by_id))
    name = _text_of(proj, keys=("name", "title"))
    name_tokens = _tokens(name)
    explicit = {str(v).strip() for v in _as_list(_get(proj, "position_ids", None))}
    linked_positions = []
    for pos in positions:
        pid = _id_of(pos)
        pos_org_id = _get(pos, "organization_id", None)
        pos_org_tokens = _tokens(_position_org(pos, orgs_by_id))
        hit = pid in explicit
        if not hit and proj_org_id and pos_org_id == proj_org_id:
            hit = True
        if not hit and proj_org_tokens and pos_org_tokens:
            shared = proj_org_tokens & pos_org_tokens
            if proj_org_tokens <= pos_org_tokens or pos_org_tokens <= proj_org_tokens or len(shared) >= 2:
                hit = True
        if not hit and name_tokens:
            if len(name_tokens & pos_org_tokens) >= 2 or name_tokens <= _tokens(_full_title(pos)):
                hit = True
        if hit:
            linked_positions.append(pos)
    linked_pids = {_id_of(p) for p in linked_positions}
    linked_achievements = []
    for achievement in achievements:
        a_pids = [str(v) for v in _as_list(_get(achievement, "position_ids", None))]
        if not a_pids:
            a_pids = [str(v) for v in _as_list(_get(achievement, "position_id", None))]
        hit = bool(linked_pids.intersection(a_pids))
        if not hit and str(_get(achievement, "project_id") or "") == _id_of(proj):
            hit = True
        if not hit and name_tokens and len(name_tokens & _tokens(_text_of(achievement))) >= 2:
            hit = True
        if hit:
            linked_achievements.append(achievement)
    linked_orgs = []
    linked_stack = []
    for pos in linked_positions:
        org = _position_org(pos, orgs_by_id)
        if org and org not in linked_orgs:
            linked_orgs.append(org)
        for tech in _stack_of(pos):
            if tech not in linked_stack:
                linked_stack.append(tech)
    return linked_positions, linked_achievements, _enum(linked_orgs), linked_stack


_FUNDAMENTAL_TEMPLATES = (
    ("Graph RAG", ("graph rag", "neo4j", "cypher", "langgraph", "retrieval"), "hard",
     "You built Graph RAG on Neo4j. Walk me through its failure modes - broken entity resolution, stale or wrong edges, retrieval that is topically correct but useless - and the regression set you would freeze to catch each one.",
     ("Name at least two retrieval-level failure modes.", "Describe the golden set you would freeze before shipping.")),
    ("Vector search", ("faiss", "chromadb", "vector", "elasticsearch", "ann"), "hard",
     "Compare HNSW and IVF-PQ style indexes against brute-force search: recall, latency, and memory - and when brute force actually wins.",
     ("Give the tradeoff in one sentence each.", "Name a dataset size where brute force is correct.")),
    ("LLM serving", ("vllm", "pagedattention", "kv-cache", "kv cache", "tgi", "tensorrt-llm"), "hard",
     "How do paged KV-cache and continuous batching in vLLM change the latency-throughput tradeoff versus naive HuggingFace generate(), and where does that approach break down?",
     ("Explain paging in one sentence.", "Name a workload where it does not help.")),
    ("Agentic workflows", ("langgraph", "langchain", "llamaindex", "llama index", "hyde", "kag"), "hard",
     "How do you debug an agent graph that loops, stalls, or silently degrades - state management, cycle guards, health checks, and when to fall back to a deterministic path?",
     ("Name the three ways a cyclic graph fails.", "Say what forces the deterministic fallback.")),
    ("Prompt engineering", ("prompt", "hyde", "instruction", "llm"), "medium",
     "How do you debug a prompt that succeeds only 80% of the time - variance sources, deterministic decoding, and enforcing structured output?",
     ("Fix temperature and seeds first.", "Describe a schema-constrained decode.")),
    ("Quantization", ("awq", "gptq", "onnx", "tensorrt", "int8", "int4"), "hard",
     "Walk through post-training quantization for an inference service: granularity, calibration data, per-channel effects, and how you verify quality did not regress.",
     ("Mention calibration-set representativeness.", "Say what you measure beyond perplexity.")),
    ("Evaluation design", ("mlflow", "w&b", "wandb", "eval", "benchmark"), "hard",
     "Design an offline evaluation suite for a generative model: golden sets, proxies, statistical checks, and how you stop the team from gaming the metric.",
     ("Separate proxy metrics from user outcomes.", "Say how you would detect metric gaming.")),
    ("Overfitting", ("pytorch", "tensorflow", "scikit-learn", "jax", "numpy"), "medium",
     "You train a model that looks excellent offline. Give me the ordered checklist you run before trusting it: overfitting, leakage, shift, and sampling artifacts.",
     ("Order checks by how often they are the real cause.", "Explain one leakage path concretely.")),
    ("Data leakage", ("airflow", "spark", "trino", "peerdb", "cdc", "great expectations"), "hard",
     "Name three classic ways data leakage creeps into a training pipeline fed by CDC and batch jobs, and the specific guard that catches each one.",
     ("Think temporal, group-wise, and target-derived leakage.", "Say which guard runs in CI.")),
    ("Data contracts", ("great expectations", "clickhouse", "trino", "peerdb", "airflow"), "medium",
     "What belongs in a data-quality gate for a high-volume lake - schema, distributions, freshness - and what does a gate like that still miss?",
     ("Cover schema, distribution, and freshness.", "Name a bug a gate will not catch.")),
    ("MLOps", ("docker", "kubernetes", "argocd", "github actions", "terraform", "ci/cd"), "hard",
     "What must a CI/CD pipeline for a model change verify that a normal service pipeline does not?",
     ("Cover data, model, and code gates.", "Mention rollback for model artifacts.")),
    ("Experiment design", ("kafka", "clickhouse", "metabase", "streaming", "prometheus"), "hard",
     "How do you run an online experiment for a model change when you already stream signals and ship canaries - randomization unit, guardrails, and early stopping?",
     ("Name the guardrail metrics you would not trade.", "Explain why peeking breaks the test.")),
    ("Vision transformers", ("vit", "blip", "clip", "llava", "image"), "hard",
     "When does a vision transformer beat a CNN at equal compute, and what makes small-data ViT training so brittle?",
     ("Discuss inductive bias and data hunger.", "Mention positional embeddings.")),
    ("Self-supervised learning", ("wav2vec", "contrastive", "self-supervised", "librosa"), "hard",
     "Explain how wav2vec 2.0's contrastive self-supervised objective works, where its negatives come from, and what happens if the quantizer collapses.",
     ("Describe the masked prediction setup.", "Say what collapse looks like in curves.")),
    ("Speech & audio", ("whisper", "wav2vec", "librosa", "ser", "emotionnet", "emodb"), "hard",
     "How do you evaluate a speech-emotion recognition model when the labels themselves are subjective?",
     ("Use inter-annotator agreement.", "Separate speaker and corpus effects.")),
    ("Report generation", ("t5", "blip", "dicom", "ultrasound", "llava"), "hard",
     "For medical-style report generation, how do you prevent fluent hallucination that a reviewer would only catch on a bad day?",
     ("Ground every sentence in findings.", "Describe a claim-verification step.")),
    ("Class imbalance", ("credit", "scoring", "risk", "default"), "hard",
     "For a credit-scoring style problem with heavy class imbalance, what is your metrics strategy - PR-AUC, calibration, cost matrix - and why is accuracy meaningless here?",
     ("Tie thresholds to business cost.", "Explain why calibration matters for risk.")),
    ("Transfer learning", ("hugging face", "whisper", "tensorflow", "jax", "pytorch"), "medium",
     "Fine-tune, freeze, or prompt: how do you decide for a pretrained model, and what evidence would push you to full fine-tuning?",
     ["Connect the size of the task delta to the choice.", "Name one signal that freezing failed."]),
    ("Transformers", ("attention", "vit", "t5", "whisper", "wav2vec"), "medium",
     "Walk me through multi-head self-attention and its complexity, then your options for long documents without giving up quality.",
     ("State the quadratic term plainly.", "Compare windows, retrieval, and efficient attention.")),
    ("Databases", ("sql", "elasticsearch", "clickhouse", "postgres"), "medium",
     "A database-backed endpoint is suddenly slow. Show me your diagnosis path: query plan, indexes, N+1 queries, and connection pool saturation.",
     ("Start with the query plan.", "Separate storage time from application time.")),
    ("Async Python", ("fastapi", "asyncio", "python"), "medium",
     "Explain asyncio event-loop starvation in a FastAPI service: blocking calls, CPU-bound work, and how the threadpool changes the picture.",
     ("Name one blocking call people forget.", "Say when to move work off the loop.")),
    ("Frontend state", ("typescript", "react", "node", "javascript"), "medium",
     "In a React + TypeScript app, how do you decide what lives in server state versus client state, and how do you keep cached server state honest?",
     ("Distinguish cache from source of truth.", "Describe invalidation after mutations.")),
    ("Caching", ("redis", "kv-cache", "cache"), "medium",
     "What are your invalidation rules for a Redis cache in front of a rarely-changing but correctness-critical dataset?",
     ("Pick TTL, versioned keys, or pub/sub.", "Describe a stampede and its fix.")),
    ("Containers", ("docker", "kubernetes", "k8s"), "medium",
     "For an inference service, what is the difference between scaling replicas and scaling resources, and how do you set requests and limits?",
     ("Connect limits to tail latency.", "Mention bin-packing effects.")),
    ("Observability", ("prometheus", "grafana", "logging", "elk", "sentry"), "medium",
     "Which five signals tell you an ML feature is silently rotting in production?",
     ("Include data drift and prediction drift.", "Say who gets paged and when.")),
    ("Testing", ("great expectations", "pytest", "test", "qa"), "medium",
     "What does a meaningful unit test look like for a data or ML pipeline, and what should stay out of unit tests?",
     ("Pin inputs and expected outputs.", "Push heavy fixtures to integration tests.")),
    ("Explainability", ("shap", "captum", "saliency", "interpret"), "hard",
     "SHAP says one feature drives the model's decisions. What can still be wrong with that story?",
     ("Correlated features split credit.", "Explain off-manifold explanations.")),
    ("GPU serving", ("gpu optimization", "triton", "ray", "mig", "tf serving"), "hard",
     "How do you pack several models onto shared GPUs without letting one tenant's tail latency poison another's?",
     ("Compare MIG slicing vs time-sharing.", "Name the interference signal you monitor.")),
    ("Reproducibility", ("mlflow", "lineage", "registry", "dvc", "w&b"), "medium",
     "How do you reproduce a training run from six months ago - data, code, environment, and hyperparameters?",
     ("Version data and config, not just code.", "Name the artifact registry you would use.")),
    ("Streaming", ("kafka", "airflow", "spark", "cdc"), "hard",
     "Design an exactly-once style pipeline over a stream: where duplicates come from and how you make consumers idempotent.",
     ("Separate delivery guarantees from effect idempotency.", "Describe offset commit ordering.")),
    ("Distributed training", ("ray", "pytorch lightning", "multi-node", "kubernetes"), "hard",
     "Data, model, and tensor parallelism: how do you choose, and how do you debug a multi-node run that scales poorly?",
     ("Match the parallelism to model size.", "Say what you measure before scaling nodes.")),
    ("Search ranking", ("elasticsearch", "bm25", "retrieval", "rrf"), "hard",
     "How do you fuse BM25 keyword scores with dense retrieval scores, and how do you evaluate the fusion itself?",
     ("Describe score normalization or RRF.", "Hold out a labeled query set.")),
)

_ACADEMIC_RE = re.compile(r"university|sharif|institute|polytechnic|college|school|research center", re.I)


def _fundamental_corpus(db, skills, positions, projects, orgs_by_id):
    parts = []
    for skill in skills:
        for key in ("name", "category", "label", "skill"):
            value = _get(skill, key, None)
            if isinstance(value, str) and value.strip():
                parts.append(value)
        for alias in _as_list(_get(skill, "aliases", None)):
            if isinstance(alias, str):
                parts.append(alias)
    for item in list(positions) + list(projects):
        parts.extend(_stack_of(item))
        for key in ("summary", "description_md", "description"):
            value = _get(item, key, None)
            if isinstance(value, str):
                parts.append(value)
        title = _full_title(item) if _get(item, "organization_id", None) else _text_of(item, keys=("title", "name"))
        if title:
            parts.append(title)
    parts.extend(orgs_by_id.values())
    profile = _get(db, "profile", None)
    if profile is not None:
        for key in ("summary", "headline", "summary_brief"):
            value = _get(profile, key, None)
            if isinstance(value, str):
                parts.append(value)
    return " | ".join(parts).lower()


def _academic_orgs(orgs_by_id, positions=()):
    counts = Counter()
    for pos in positions:
        org = _position_org(pos, orgs_by_id)
        if org:
            counts[org] += 1
    names = sorted({n for n in orgs_by_id.values() if _ACADEMIC_RE.search(n)},
                   key=lambda n: (-counts[n], n))
    deduped = []
    for name in names:
        tokens = _tokens(name)
        if any(tokens <= _tokens(other) or _tokens(other) <= tokens for other in deduped):
            continue
        deduped.append(name)
    return deduped


def _industry_orgs(db, positions, orgs_by_id):
    full_time = []
    others = []
    for pos in positions:
        org = _position_org(pos, orgs_by_id)
        if not org:
            continue
        if _get(pos, "employment_type", None) == "full_time":
            if org not in full_time:
                full_time.append(org)
        elif org not in others:
            others.append(org)
    academic = _academic_orgs(orgs_by_id, positions)
    picked = [org for org in sorted(full_time) if org not in academic]
    if not picked:
        picked = [org for org in sorted(others) if org not in academic]
    return picked


def _title_hits(positions, orgs_by_id, pattern):
    regex = re.compile(pattern, re.I)
    hits = []
    for pos in positions:
        if regex.search(_full_title(pos)):
            hits.append(_role_phrase(pos, orgs_by_id))
    return hits


def generate_questions(db):
    """Build the full deterministic question list from the career database."""
    positions = _section(db, "positions", "roles", "experience")
    achievements = _section(db, "achievements", "bullets")
    projects = _section(db, "projects")
    skills = _section(db, "skills")
    orgs_by_id = _org_names(db)

    questions = []
    counters = {category: 0 for category in CATEGORIES}

    def add(category, difficulty, question, hints, why, scope=None):
        counters[category] += 1
        item = {"id": f"q_{category}_{counters[category]}", "category": category, "difficulty": difficulty}
        if scope:
            item.update(scope)
        item["question"] = question
        item["hints"] = [str(h) for h in list(hints)[:2]]
        item["why"] = why
        questions.append(item)

    for pos in positions:
        pid = _id_of(pos)
        title = _short_title(pos)
        org = _position_org(pos, orgs_by_id) or "this team"
        role = f"{title} at {org}" if org else title
        stack, stack_inferred = _stack_hint(pos)
        stack_phrase = _enum(stack)
        summary = _text_of(pos, keys=("summary", "description_md", "description"))
        texts = [t for t in (_text_of(a) for a in _position_achievements(pos, pid, achievements)) if t]
        scope = {"position_id": pid} if pid else {}
        other, note = _concurrent_context(pos, db, positions, orgs_by_id)

        if texts:
            add("deep_dive", "hard",
                f'Walk me through the end-to-end architecture behind the flagship item of your {role} role: "{_snippet(texts[0])}". What were the components, the data flow, and where were the hard integration points?',
                ["Sketch the moving parts before naming technologies.", "Call out one integration point that almost derailed you."],
                "Architecture walkthrough of this role's flagship achievement, grounded in its real bullet text.",
                scope)
        elif summary:
            add("deep_dive", "hard",
                f'Your {org} role is summarized as "{_snippet(summary, 200)}". Walk me through what you actually built there: the architecture, the data flow, and the hardest integration point.',
                ["Sketch the moving parts before naming technologies.", "Call out one integration point that almost derailed you."],
                "Architecture walkthrough grounded in this role's summary.",
                scope)
        else:
            add("deep_dive", "hard",
                f"As {role} you owned a system end to end. Describe its architecture, the data flow, and the hardest integration point you hit.",
                ["Sketch the moving parts before naming technologies.", "Call out one integration point that almost derailed you."],
                "Architecture walkthrough anchored to this role.",
                scope)

        if stack and stack_inferred:
            add("deep_dive", "medium",
                f"Your summary for the {org} role mentions {stack_phrase}. Which of those did you actually standardize on as {title}, and which alternatives did you reject?",
                ["Name at least one runner-up technology you rejected.", "Tie each choice to a real constraint you had."],
                "Tech-choice justification built from this role's summary.",
                scope)
        elif stack:
            add("deep_dive", "medium",
                f"As {role} you built with {stack_phrase}. Why those choices over the alternatives, and what would you replace first if you started over today?",
                ["Name at least one runner-up technology you rejected.", "Tie each choice to a real constraint you had."],
                "Tech-choice justification using this role's actual stack.",
                scope)
        else:
            add("deep_dive", "medium",
                f"Which technologies did you standardize on as {role}, and which ones did you explicitly reject?",
                ["Name at least one runner-up technology you rejected.", "Tie each choice to a real constraint you had."],
                "Tech-choice justification for this role.",
                scope)

        claims = _metric_claims(texts)
        if claims:
            add("deep_dive", "hard",
                f'Your {org} role claims "{_snippet(claims[0], 200)}". How exactly was that measured - baseline, instrumentation, time window - and what result would have falsified the claim?',
                ["Describe the measurement setup, not the outcome.", "State what would have proven the claim wrong."],
                "Metrics question grounded in what this role's bullets actually claim.",
                scope)
        else:
            add("deep_dive", "medium",
                f"How did you measure impact as {role}? Define the metric you would defend in a design review, including its baseline and its failure modes.",
                ["Name a baseline you can actually reproduce.", "Say how the metric can be gamed."],
                "Measurement thinking for this role.",
                scope)

        add("deep_dive", "hard",
            f"What was the hardest technical problem you solved as {role}? Give the constraints, the options you weighed, the tradeoff you accepted, and what you would do differently now.",
            ["Lead with the constraint that made it hard.", "Name one tradeoff you knowingly accepted."],
            "Hardest-problem and tradeoff articulation anchored to this role.",
            scope)

        if len(texts) >= 2:
            add("deep_dive", "hard",
                f'Deep-dive "{_snippet(texts[1], 180)}" from your {org} time: implementation choices, the bottleneck you hit, and how you verified it actually worked.',
                ["Explain how you proved it worked, not just that it shipped.", "Name the bottleneck and its fix."],
                "Second-achievement interrogation from this role's real bullets.",
                scope)
        else:
            add("deep_dive", "hard",
                f"If you had to take what you built as {role} to ten times the load, what breaks first, and how would you harden it?",
                ["Rank the first three failure points.", "Separate capacity limits from correctness limits."],
                "Scale and hardening follow-up for this role.",
                scope)

        if other:
            context = f' - your CV notes: "{_snippet(note, 220)}"' if note else ""
            add("deep_dive", "medium",
                f"Your {role} work overlapped with {other}{context}. Take me through a week where both demanded you: how did you prioritize, what did you defer, and how did you keep both sides informed?",
                ["Describe an actual collision, not a philosophy.", "Say what you gave up to keep both moving."],
                "Concurrency prioritization (STAR) for overlapping roles.",
                scope)

    for proj in projects:
        proj_id = _id_of(proj)
        name = _text_of(proj, keys=("name", "title")) or "this project"
        summary = _text_of(proj, keys=("summary", "description"))
        if summary.strip().lower() == name.strip().lower():
            summary = _text_of(proj, keys=("description",)) or ""
        scope = {"project_id": proj_id} if proj_id else {}
        linked_positions, linked_achievements, linked_org, linked_stack = _project_links(
            proj, positions, achievements, orgs_by_id)
        linked_texts = [t for t in (_text_of(a) for a in linked_achievements) if t]
        where = f"your {linked_org} work" if linked_org else "your linked role"

        if summary and linked_texts:
            add("project", "hard",
                f'Give me the architecture walkthrough of {name}: "{_snippet(summary, 160)}". Your linked work at {linked_org} includes "{_snippet(linked_texts[0], 150)}" - what were the components, the data flow, and the riskiest stage?',
                ["Name the components and the data flow.", "Identify the riskiest stage."],
                "Project interrogation built from this project's description plus linked position achievements.",
                scope)
        elif linked_texts:
            add("project", "hard",
                f'Give me the architecture walkthrough of {name}, built in your {linked_org} role - for example "{_snippet(linked_texts[0], 170)}". What were the components, the data flow, and the riskiest stage?',
                ["Name the components and the data flow.", "Identify the riskiest stage."],
                "Project interrogation built from linked position achievements.",
                scope)
        elif summary:
            add("project", "hard",
                f'Give me the architecture walkthrough of {name}: "{_snippet(summary, 170)}" - components, data flow, and the riskiest stage.',
                ["Name the components and the data flow.", "Identify the riskiest stage."],
                "Project interrogation built from this project's own summary.",
                scope)
        else:
            add("project", "hard",
                f"Give me the architecture walkthrough of {name}: components, data flow, and the riskiest stage.",
                ["Name the components and the data flow.", "Identify the riskiest stage."],
                "Project interrogation anchored to this project.",
                scope)

        claim_src = None
        project_claims = []
        for idx, text in enumerate(linked_texts):
            found = _metric_claims([text], limit=1)
            if found:
                project_claims.append(found[0])
                claim_src = idx
                break
        if project_claims:
            add("project", "hard",
                f'How did you evaluate {name}? Your linked work claims "{_snippet(project_claims[0], 200)}" - reconstruct the eval suite: metrics, baselines, test-set hygiene, and one silent failure it would miss.',
                ["Separate offline metrics from real acceptance.", "Name one failure your eval would not catch."],
                "Evaluation question grounded in a real claim from linked achievements.",
                scope)
        else:
            add("project", "hard",
                f"How did you evaluate {name}? Define the metrics, the baseline, test-set hygiene, and one silent failure your eval would miss.",
                ["Separate offline metrics from real acceptance.", "Name one failure your eval would not catch."],
                "Evaluation design question for this project.",
                scope)

        used = {claim_src, 0} if linked_texts else set()
        next_text = next((t for idx, t in enumerate(linked_texts) if idx not in used), None)
        if next_text:
            add("project", "medium",
                f'{name} also rests on "{_snippet(next_text, 170)}" from {where}. Deep-dive that part: what you tried, what failed, and how you verified it worked.',
                ["Show how you proved it worked.", "Name the attempt that failed first."],
                "Further linked-achievement interrogation for this project.",
                scope)
        elif linked_stack:
            add("project", "medium",
                f"{name} shipped with {_enum(linked_stack)}. Why those choices over the alternatives, and what would you replace first?",
                ["Name a runner-up you rejected.", "Tie the choice to a real constraint."],
                "Tech-choice question using the linked position stack.",
                scope)
        else:
            add("project", "medium",
                f"If you rebuilt {name} today with a fresh team, what would you change first and why?",
                ["Change the riskiest design decision first.", "Tie the change to a lesson you learned."],
                "Retrospective design question for this project.",
                scope)

    concurrent_story = None
    best_note_len = -1
    for pos in positions:
        other, note = _concurrent_context(pos, db, positions, orgs_by_id)
        if not other:
            continue
        score = len(note or "")
        if score > best_note_len:
            best_note_len = score
            concurrent_story = (pos, other, note)
    if concurrent_story:
        pos, other, note = concurrent_story
        role = _role_phrase(pos, orgs_by_id)
        note_part = f' Your CV notes: "{_snippet(note, 220)}".' if note else ""
        add("behavioral", "medium",
            f"You held {role} alongside {other}.{note_part} Tell me about a specific week when both demanded you: what you prioritized, what slipped, and how each side experienced it.",
            ["Use a real week, with real dates of pressure.", "Explain how each stakeholder experienced your choice."],
            "Concurrency story required by overlapping roles in the database.")
    else:
        add("behavioral", "medium",
            "Tell me about a period when you were juggling two demanding commitments at once: what you prioritized, what slipped, and how you communicated it.",
            ["Use a real period, with real dates of pressure.", "Explain how each stakeholder experienced your choice."],
            "Concurrency and prioritization reflection.")

    academic = _academic_orgs(orgs_by_id, positions)
    industry = _industry_orgs(db, positions, orgs_by_id)
    if academic and industry:
        add("behavioral", "hard",
            f'You split your time between industry work (for example {industry[0]}) and academic work including {_enum(academic[:2])}. Tell me about a time the part-time research and industry sides blurred - how you set boundaries, and what each side misunderstood about the other.',
            ["Give a concrete moment of ambiguity.", "Say what boundary you put in place afterwards."],
            "Part-time research versus industry ambiguity present in the database's orgs.")
    else:
        add("behavioral", "hard",
            "Tell me about a time your part-time research work and your industry role blurred together: the ambiguity, how you set boundaries, and what each side misunderstood about the other.",
            ["Give a concrete moment of ambiguity.", "Say what boundary you put in place afterwards."],
            "Part-time research versus industry ambiguity reflection.")

    founding = _title_hits(positions, orgs_by_id, r"founding|founder")
    if founding:
        add("behavioral", "medium",
            f"As {founding[0]}, you had to define what the engineering culture would be before there was any process. Tell me about the first hiring or technical decision that set the tone - and the one you would take back.",
            ["Describe the decision and its ripple effect.", "Name one decision you would reverse."],
            "Leadership anchor: founding role exists in the database.")
    else:
        add("behavioral", "medium",
            "Tell me about the first time you set the technical direction for a team rather than executing someone else's - and the decision you would now take back.",
            ["Describe the decision and its ripple effect.", "Name one decision you would reverse."],
            "Leadership reflection.")

    leads = _title_hits(positions, orgs_by_id, r"\blead\b|\bmanager\b|\bhead of\b|\bfounding\b")
    tas = _title_hits(positions, orgs_by_id, r"teaching assistant|\binstructor\b|\btutor\b")
    lead_part = f"You have been {leads[0]}" if leads else "You have had to lead without authority"
    ta_part = f", and you have also been {tas[0]}" if tas else " and you have also taught"
    add("behavioral", "medium",
        f"{lead_part}{ta_part}. Describe a moment you had to bring a struggling teammate or student up to speed under time pressure - what you changed about how you explain technical work.",
        ["Show how you diagnosed the gap first.", "Say what you changed in your own communication."],
        "Leadership and mentorship anchors (R&D lead / teaching) from the database.")

    conflict_anchor = _text_of(projects[0], keys=("name", "title")) if projects else (sorted(orgs_by_id.values())[0] if orgs_by_id else "a recent project")
    add("behavioral", "hard",
        f"Tell me about a serious disagreement with a teammate or stakeholder during {conflict_anchor}. What was your position, what did you get wrong first, and how was it resolved?",
        ["Own your part in the conflict before describing theirs.", "State what you would do differently now."],
        "Conflict reflection anchored to a real project or org from the database.")

    failure_anchor = _text_of(projects[-1], keys=("name", "title")) if projects else "a recent project"
    add("behavioral", "hard",
        f"Tell me about something that failed or badly underdelivered - ideally around {failure_anchor}. What did you miss, what did it cost, and what changed in how you work afterwards?",
        ["Describe the failure without blaming environment or people.", "Name the concrete process change that followed."],
        "Failure reflection anchored to a real project from the database.")

    corpus = _fundamental_corpus(db, skills, positions, projects, orgs_by_id)
    for tag, keywords, difficulty, question, hints in _FUNDAMENTAL_TEMPLATES:
        if any(keyword in corpus for keyword in keywords):
            add("fundamentals", difficulty, question, hints,
                f"Indexed to your DB skill set: matches '{tag}'.", {"skill": tag})

    return questions


def get_questions(db, position_id=None, category=None):
    """Generate questions and merge persisted interview_prep state into them."""
    prep = _get(db, "interview_prep", None) or {}
    answers = _get(prep, "answers", None) or {}
    if not isinstance(answers, dict):
        answers = {}
    merged = []
    for question in generate_questions(db):
        if position_id is not None and question.get("position_id") != position_id:
            continue
        if category is not None and question.get("category") != category:
            continue
        entry = answers.get(question["id"], None) or {}
        item = dict(question)
        item["status"] = entry.get("status", "unprepared") if isinstance(entry, dict) else "unprepared"
        item["answer"] = entry.get("answer", "") if isinstance(entry, dict) else ""
        merged.append(item)
    return merged


def submit_answer(db, qid, status, answer):
    """Validate and persist one answer; returns the stored entry (no filesystem I/O)."""
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}; expected one of {', '.join(VALID_STATUSES)}")
    valid_ids = {q["id"] for q in generate_questions(db)}
    if qid not in valid_ids:
        raise ValueError(f"unknown question id: {qid!r}")
    prep = _get(db, "interview_prep", None)
    if not isinstance(prep, dict):
        prep = {}
        try:
            if isinstance(db, dict):
                db["interview_prep"] = prep
            else:
                setattr(db, "interview_prep", prep)
        except Exception as exc:
            raise ValueError(
                "career database has no interview_prep field; add "
                "`interview_prep: dict = Field(default_factory=dict)` to CareerDatabase"
            ) from exc
    answers = prep.get("answers")
    if not isinstance(answers, dict):
        answers = {}
        prep["answers"] = answers
    entry = {
        "status": status,
        "answer": answer if isinstance(answer, str) else ("" if answer is None else str(answer)),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    answers[qid] = entry
    return entry


if __name__ == "__main__":
    db_path = Path(__file__).resolve().parents[1] / "career_db.json"
    data = json.loads(db_path.read_text(encoding="utf-8"))
    questions = generate_questions(data)
    counts = Counter(q["category"] for q in questions)
    print(f"loaded {db_path}")
    for category in CATEGORIES:
        print(f"  {category}: {counts.get(category, 0)}")
    print(f"  total: {len(questions)}")
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "duplicate question ids"
    assert counts.get("deep_dive", 0) >= 70, counts
    assert counts.get("project", 0) >= 9, counts
    assert counts.get("behavioral", 0) >= 5, counts
    assert counts.get("fundamentals", 0) >= 20, counts
    assert all(q["difficulty"] in ("medium", "hard") for q in questions)
    assert all(len(q["hints"]) == 2 for q in questions)
    per_position = Counter(q.get("position_id") for q in questions if q["category"] == "deep_dive")
    for pos in data["positions"]:
        assert per_position.get(pos["id"], 0) >= 5, (pos["id"], per_position.get(pos["id"], 0))
    per_project = Counter(q.get("project_id") for q in questions if q["category"] == "project")
    for proj in data["projects"]:
        assert per_project.get(proj["id"], 0) >= 3, (proj["id"], per_project.get(proj["id"], 0))
    sample = questions[0]
    entry = submit_answer(data, sample["id"], "drafted", "self-test answer")
    restored = {q["id"]: q for q in get_questions(data)}
    assert restored[sample["id"]]["status"] == "drafted"
    assert restored[sample["id"]]["answer"] == "self-test answer"
    assert entry["updated_at"]
    try:
        submit_answer(data, "q_nope_1", "drafted", "x")
        raise AssertionError("bad qid accepted")
    except ValueError:
        pass
    try:
        submit_answer(data, sample["id"], "sure", "x")
        raise AssertionError("bad status accepted")
    except ValueError:
        pass
    print("  self-test: OK (>=5 deep_dive/position, >=3 project/project)")
    for question in questions[:5]:
        print(json.dumps(question, ensure_ascii=False, indent=2))
