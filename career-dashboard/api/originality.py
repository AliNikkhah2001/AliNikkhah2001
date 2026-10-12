"""Originality checker — duplication, cliché density and an AI-content heuristic.

Local-only screening signal (stdlib + ats.py's PDF extraction). No network calls,
no API keys, nothing external. Every AI-related number ships with a disclaimer:
this is a screening signal, NOT a verdict.

Mirrors ats.py conventions:
  * PDF discovery      career-dashboard/builds/<template-id>/out.pdf
  * text extraction    ats.extract_text() when importable, else pdftotext/pdfplumber
  * cache              builds/<template-id>/originality.json with "_mtime" staleness

Weights — AI subscores (0-100 each, higher = more templated/AI-like):
  burstiness            35   stdev/mean of sentence lengths (low variance = templated)
  first_word_diversity  20   distinct sentence-opening words / sentences
  hedge_ratio           20   filler & hedge words per total words
  ai_phrases            25   AI-pattern phrase hits + em-dash density

Return shape (frontend contract):
  {
    "template_id": str,
    "generated_at": str,
    "duplication": {"score": float, "findings": [{"shared": str, "between": [i, j]}]},
    "cliches":     {"count": int, "phrases": [{"phrase": str, "sentence": str}]},
    "ai":          {"band": "low|medium|high", "score": float,
                    "signals": {"burstiness", "first_word_diversity",
                                "hedge_ratio", "ai_phrases"},
                    "disclaimer": str}
  }
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # reuse ats.py's extraction; never import main.py (FastAPI app)
    from ats import extract_text as _ats_extract_text
except Exception:  # noqa: BLE001 — module must import without the app
    _ats_extract_text = None

ROOT = Path(__file__).resolve().parents[1]          # career-dashboard/
BUILD = ROOT / "builds"                             # mirrors latex.py BUILD
N_GRAM = 5
DISCLAIMER = (
    "Heuristic screening signal only — not a reliable verdict. "
    "Do not use as sole evidence."
)

# (phrase, only_a_cliche_without_a_metric) — ~46 corporate / AI-boilerplate phrases
CLICHES: list[tuple[str, bool]] = [
    ("responsible for", False),
    ("team player", False),
    ("proven track record", False),
    ("results-driven", False),
    ("results oriented", False),
    ("synergy", False),
    ("leverage", False),
    ("leveraging", False),
    ("cutting-edge", False),
    ("passionate about", False),
    ("detail-oriented", False),
    ("fast-paced environment", False),
    ("hit the ground running", False),
    ("go-getter", False),
    ("dynamic", False),
    ("spearheaded", True),              # only a cliché when the sentence has no metric
    ("think outside the box", False),
    ("go the extra mile", False),
    ("worn many hats", False),
    ("wears many hats", False),
    ("excellent communication skills", False),
    ("strong communication skills", False),
    ("self-motivated", False),
    ("self-starter", False),
    ("proactive", False),
    ("innovative solutions", False),
    ("best practices", False),
    ("cross-functional", False),
    ("stakeholder", False),
    ("mission-critical", False),
    ("game-changer", False),
    ("streamlined", False),
    ("utilized", False),
    ("seamless", False),
    ("robust", False),
    ("holistic", False),
    ("in today's fast-paced world", False),
    ("hard-working", False),
    ("go-to person", False),
    ("eager to learn", False),
    ("work well under pressure", False),
    ("strong work ethic", False),
    ("people person", False),
    ("a passion for", False),
    ("end-to-end", False),
    ("value-added", False),
    ("delve", False),
    ("tapestry", False),
    ("testament to", False),
    ("multifaceted", False),
    ("ever-evolving", False),
]

FILLERS = [
    "additionally", "moreover", "furthermore", "in conclusion",
    "it is important to note", "it is worth noting", "in summary",
    "to summarize", "overall", "importantly", "notably", "needless to say",
    "as a matter of fact", "certainly", "undoubtedly", "truly", "basically",
    "actually", "arguably", "in today's fast-paced world",
]

AI_PHRASE_PATTERNS = [
    r"\bnot only\b.{0,80}?\bbut also\b",
    r"\bcomprehensive understanding\b",
    r"\bproficient in\b",
    r"\bin order to\b",
    r"\ba wide range of\b",
    r"\bdelve into\b",
    r"\bdelves into\b",
    r"\btestament to\b",
    r"\bseamlessly\b",
    r"\bnavigate the (?:complexities|landscape)\b",
    r"\bunlock the (?:potential|power)\b",
    r"\bleverage the power of\b",
    r"\bever-evolving\b",
    r"\brich tapestry\b",
    r"\bit is worth noting\b",
]

_SENT_RX = re.compile(r"(?<=[.!?])\s+")
_ID_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _words(text: str) -> list[str]:
    """Lowercased, punctuation-stripped word tokens."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).split()


def _sentences(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        for part in _SENT_RX.split(line):
            part = re.sub(r"\s+", " ", part).strip()
            if part:
                out.append(part)
    return out


# --------------------------------------------------------------------------- #
# duplication — cross-text word 5-gram overlap
# --------------------------------------------------------------------------- #
def _duplication(texts: list[str]) -> dict[str, Any]:
    tokens = [_words(t) for t in texts]
    grams: dict[tuple[str, ...], dict[int, list[int]]] = {}
    for i, toks in enumerate(tokens):
        for p in range(len(toks) - N_GRAM + 1):
            g = tuple(toks[p:p + N_GRAM])
            grams.setdefault(g, {}).setdefault(i, []).append(p)

    shared = {g: w for g, w in grams.items() if len(w) > 1}
    score = 100.0 * len(shared) / len(grams) if grams else 0.0

    # group overlapping shared n-grams per text-pair into longer snippets
    pair_runs: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for g, where in shared.items():
        idxs = sorted(where)
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                pair_runs.setdefault((i, j), []).append(where[i][0])

    candidates: list[tuple[int, int, int, int]] = []  # (len, i, j, start)
    for (i, j), positions in pair_runs.items():
        runs: list[list[int]] = []  # [start, end) in token space
        for pos in sorted(set(positions)):
            if runs and pos == runs[-1][1] - (N_GRAM - 1):
                runs[-1][1] = pos + N_GRAM
            else:
                runs.append([pos, pos + N_GRAM])
        for start, end in runs:
            candidates.append((end - start, i, j, start))

    candidates.sort(key=lambda c: (-c[0], c[1], c[2], c[3]))
    findings: list[dict[str, Any]] = []
    seen_snippets: set[str] = set()
    for length, i, j, start in candidates:
        snippet = " ".join(tokens[i][start:start + length])
        if snippet in seen_snippets:
            continue
        seen_snippets.add(snippet)
        findings.append({"shared": snippet, "between": [i, j]})
        if len(findings) >= 10:
            break

    return {"score": round(score, 1), "findings": findings}


# --------------------------------------------------------------------------- #
# clichés — corporate / AI boilerplate dictionary
# --------------------------------------------------------------------------- #
_CLICHE_RX = {
    phrase: re.compile(r"\b" + re.escape(phrase) + r"\b", re.I)
    for phrase, _ in CLICHES
}


def _cliches(texts: list[str]) -> dict[str, Any]:
    matched: list[dict[str, str]] = []
    for text in texts:
        for sentence in _sentences(text):
            for phrase, no_metric in CLICHES:
                if no_metric and re.search(r"\d", sentence):
                    continue  # "spearheaded X by 40%" is evidence, not boilerplate
                for _ in _CLICHE_RX[phrase].finditer(sentence):
                    matched.append({"phrase": phrase, "sentence": sentence})
    return {"count": len(matched), "phrases": matched}


# --------------------------------------------------------------------------- #
# ai — heuristic subscores, weighted overall score, mandatory disclaimer
# --------------------------------------------------------------------------- #
def _ai_signals(texts: list[str]) -> dict[str, Any]:
    text = "\n".join(texts)
    sentences = [s for t in texts for s in _sentences(t)]
    words = _words(text)
    n_words, n_sent = len(words), len(sentences)
    lengths = [len(_words(s)) for s in sentences]

    # 1. burstiness — low stdev/mean = uniform, templated sentence rhythm
    if n_sent >= 3:
        mean = sum(lengths) / len(lengths)
        var = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        cv = math.sqrt(var) / mean if mean else 0.0
        burstiness = _clamp(100.0 * (1.0 - min(1.0, cv / 0.6)))
    else:
        burstiness = 0.0  # too few sentences to judge

    # 2. first-word diversity — every sentence opening the same = templated
    if n_sent >= 2:
        firsts = [_words(s)[0] for s in sentences if _words(s)]
        diversity = len(set(firsts)) / len(firsts) if firsts else 1.0
        first_word_diversity = _clamp(100.0 * (0.9 - diversity) / 0.9)
    else:
        first_word_diversity = 0.0

    # 3. filler / hedge word ratio
    low = text.lower()
    filler_hits = sum(len(re.findall(r"\b" + re.escape(f) + r"\b", low)) for f in FILLERS)
    filler_ratio = filler_hits / n_words if n_words else 0.0
    hedge_ratio = _clamp(100.0 * min(1.0, filler_ratio / 0.015))

    # 4. AI-pattern phrases + em-dash density
    phrase_hits = sum(len(re.findall(p, low)) for p in AI_PHRASE_PATTERNS)
    phrase_score = 100.0 * min(1.0, phrase_hits / 4.0)
    em_dashes = text.count("—")
    em_per_100w = 100.0 * em_dashes / n_words if n_words else 0.0
    em_score = 100.0 * min(1.0, em_per_100w / 2.5)
    ai_phrases = 0.65 * phrase_score + 0.35 * em_score

    signals = {
        "burstiness": round(burstiness, 1),
        "first_word_diversity": round(first_word_diversity, 1),
        "hedge_ratio": round(hedge_ratio, 1),
        "ai_phrases": round(ai_phrases, 1),
    }
    score = round(
        0.35 * signals["burstiness"]
        + 0.20 * signals["first_word_diversity"]
        + 0.20 * signals["hedge_ratio"]
        + 0.25 * signals["ai_phrases"],
        1,
    )
    if score < 35:
        band = "low"
    elif score <= 65:
        band = "medium"
    else:
        band = "high"

    return {
        "band": band,
        "score": score,
        "signals": signals,
        "disclaimer": DISCLAIMER,
    }


def analyze_texts(texts: list[str]) -> dict[str, Any]:
    """Pure, unit-testable analysis of 2+ text segments (paragraphs/sentences)."""
    texts = [t for t in (texts or []) if t and t.strip()]
    if not texts:
        return {
            "duplication": {"score": 0.0, "findings": []},
            "cliches": {"count": 0, "phrases": []},
            "ai": {
                "band": "low", "score": 0.0,
                "signals": {
                    "burstiness": 0.0, "first_word_diversity": 0.0,
                    "hedge_ratio": 0.0, "ai_phrases": 0.0,
                },
                "disclaimer": DISCLAIMER,
            },
        }
    return {
        "duplication": _duplication(texts),
        "cliches": _cliches(texts),
        "ai": _ai_signals(texts),
    }


# --------------------------------------------------------------------------- #
# PDF plumbing — ats.py conventions
# --------------------------------------------------------------------------- #
def _pdf_text(pdf: Path) -> str:
    """Extract text from a compiled PDF (ats.extract_text when available)."""
    if _ats_extract_text is not None:
        try:
            text, _pages = _ats_extract_text(pdf)
            if text and text.strip():
                return text
        except Exception:  # noqa: BLE001
            pass
    text = ""
    if shutil.which("pdftotext"):  # same fallback chain as ats.extract_text
        try:
            proc = subprocess.run(
                ["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                capture_output=True, text=True, timeout=60,
            )
            if proc.returncode == 0:
                text = proc.stdout
        except Exception:  # noqa: BLE001
            text = ""
    if not text.strip():
        try:
            import pdfplumber

            with pdfplumber.open(pdf) as doc:
                text = "\n".join((p.extract_text() or "") for p in doc.pages)
        except Exception:  # noqa: BLE001
            text = ""
    return text


def _segments(text: str) -> list[str]:
    """Blank-line paragraphs when there are ≥2, else sentences (never both:
    sentences are substrings of their paragraph and would fake duplication)."""
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    paras = [p for p in paras if len(_words(p)) >= N_GRAM]
    if len(paras) >= 2:
        return paras
    sents = [s for s in _sentences(text) if len(_words(s)) >= N_GRAM]
    if len(sents) >= 2:
        return sents
    return paras or sents or [text.strip()]


def check_template(template_id: str) -> dict[str, Any]:
    """Originality report for builds/<template_id>/out.pdf (cached with _mtime).

    Raises FileNotFoundError (→ HTTP 404) when the build/PDF is missing and
    RuntimeError (→ HTTP 503) when the PDF cannot be read as text.
    """
    if not template_id or not _ID_RX.match(template_id) or ".." in template_id:
        raise FileNotFoundError(f"invalid template id: {template_id!r}")
    build_dir = BUILD / template_id
    if not build_dir.is_dir():
        raise FileNotFoundError(
            f"no build directory for template '{template_id}' ({build_dir}) — "
            "compile it first via POST /api/templates/{template_id}/compile"
        )
    pdf = build_dir / "out.pdf"
    if not pdf.exists():
        raise FileNotFoundError(
            f"no compiled PDF for template '{template_id}' ({pdf}) — "
            "compile it first via POST /api/templates/{template_id}/compile"
        )

    cache_file = build_dir / "originality.json"
    try:
        pdf_mtime = pdf.stat().st_mtime
        if cache_file.exists():
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("_mtime") == pdf_mtime:
                cached.pop("_mtime", None)
                return cached
    except Exception:  # noqa: BLE001
        pass

    text = _pdf_text(pdf)
    if not text or not text.strip():
        raise RuntimeError(
            f"no extractable text in {pdf} — PDF may be image-only or corrupt"
        )

    result: dict[str, Any] = {
        "template_id": template_id,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **analyze_texts(_segments(text)),
    }
    try:
        cache_file.write_text(
            json.dumps({**result, "_mtime": pdf.stat().st_mtime}, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:  # noqa: BLE001
        pass
    return result


if __name__ == "__main__":
    shared_line = (
        "Spearheaded the migration to a cutting-edge ingestion platform, "
        "responsible for mentoring five engineers in a fast-paced environment."
    )
    dup_a = shared_line + " Results-driven engineer and team player."
    dup_b = shared_line + " Detail-oriented go-getter with synergy."
    human = (
        "I rewrote the ingestion service in Rust after the Python worker kept "
        "timing out at 40k events per second, dropping p99 latency from 900ms "
        "to 120ms. On-call taught me to stop guessing: we added tracing before "
        "touching the scheduler. The team shipped the fix on a Thursday, "
        "because Friday deploys are how you lose a weekend."
    )

    out = analyze_texts([dup_a, dup_b])
    print("=== duplicated + cliché samples ===")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    assert out["duplication"]["score"] > 0, "expected cross-text 5-gram overlap"
    assert out["duplication"]["findings"], "expected duplication findings"
    assert out["cliches"]["count"] >= 5, "expected cliché hits"
    assert out["ai"]["disclaimer"] == DISCLAIMER

    out2 = analyze_texts([human])
    print("\n=== human-voice sample ===")
    print(json.dumps(out2, indent=2, ensure_ascii=False))
    print("\nOK — self-test passed")
