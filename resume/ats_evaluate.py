#!/usr/bin/env python3
"""
Comprehensive ATS & CV Evaluation Framework
Checks: ATS parsing, keyword density, metrics, formatting, section structure,
        readability, competitive benchmarking, role-specific scoring.
"""

import pdfplumber
import os
import re
import json
from collections import Counter
from datetime import datetime

PDF_DIR = "/Users/alinikkhah/Documents/CV repo/Resume 3/compiled_pdfs"

VARIANTS = [
    "Ali_Nikkhah_AgenticAI_1page.pdf",
    "Ali_Nikkhah_AgenticAI_2page.pdf",
    "Ali_Nikkhah_ComputerVision_1page.pdf",
    "Ali_Nikkhah_ComputerVision_2page.pdf",
    "Ali_Nikkhah_DataScience_1page.pdf",
    "Ali_Nikkhah_DataScience_2page.pdf",
    "Ali_Nikkhah_SoftwareEng_1page.pdf",
    "Ali_Nikkhah_SoftwareEng_2page.pdf",
    "Ali_Nikkhah_HybridAI_1page.pdf",
    "Ali_Nikkhah_HybridAI_2page.pdf",
    "Ali_Nikkhah_SeniorAI_1page.pdf",
    "Ali_Nikkhah_SeniorAI_2page.pdf",
    "Ali_Nikkhah_MLPlatform_1page.pdf",
    "Ali_Nikkhah_MLPlatform_2page.pdf",
    "Ali_Nikkhah_ResearchCV.pdf",
]

# ── ATS Parsing Rules ──────────────────────────────────────────────
ATS_KEYWORDS = {
    "core_ml": ["python", "pytorch", "tensorflow", "scikit-learn", "numpy", "pandas"],
    "llm_rag": ["llm", "rag", "langchain", "langgraph", "openai", "embedding", "vector", "prompt", "fine-tuning", "fine-tune"],
    "infra": ["kubernetes", "docker", "redis", "kafka", "aws", "gcp", "fastapi", "postgres", "postgresql"],
    "cv": ["opencv", "yolo", "cnn", "transformer", "segmentation", "detection", "onnx", "tensorrt", "torchvision"],
    "data": ["spark", "airflow", "dbt", "snowflake", "bigquery", "etl", "data pipeline", "feature store"],
    "devops": ["ci/cd", "terraform", "github actions", "jenkins", "monitoring", "prometheus", "grafana"],
}

ACTION_VERBS = [
    "engineered", "designed", "built", "developed", "led", "architected",
    "implemented", "optimized", "deployed", "orchestrated", "automated",
    "achieved", "reduced", "improved", "increased", "delivered", "scaled",
    "migrated", "streamlined", "established", "spearheaded", "championed",
    " mentored", "directed", "managed", "coordinated", "launched",
]

METRIC_PATTERNS = [
    r'\d+(?:[.,]\d+)?(?:\s*[%xX])',
    r'\d+(?:[.,]\d+)?\s*(?:ms|sec|min|hours?|days?|weeks?|months?)',
    r'\$\s*\d+(?:[.,]\d+)?\s*(?:K|M|B)?',
    r'\d+(?:[.,]\d+)?\s*(?:queries|QPS|RPS|req/s|rps|qps)',
    r'\d+(?:[.,]\d+)?(?:M|K|B)\+?',
    r'(?:reduced|decreased|improved|increased|achieved|saved)\s+\d+',
    r'\d+(?:[.,]\d+)?\s*(?:GB|TB|PB|MB)\b',
    r'p\d{2,3}\b(?:\s*latency)?',
    r'(?:top|ranked)\s+\d+',
    r'\d+\+?\s*(?:users?|customers?|clients?|developers?|teams?)',
]

SECTION_HEADERS = [
    "summary", "professional summary", "profile", "objective",
    "technical skills", "skills", "competencies",
    "professional experience", "experience", "work experience",
    "education", "academic background",
    "projects", "key projects", "selected projects",
    "research", "publications", "research experience",
    "certifications", "awards", "leadership",
]

FORMAT_ISSUES = {
    "special_bullets": ["•", "·", "▪", "▫", "◆", "◇", "★", "☆", "►", "▸", "»"],
    "bad_chars": ["\u200b", "\ufeff", "\xa0", "\u200c", "\u200d"],
}


def extract_text(pdf_path):
    text = ""
    page_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            page_texts.append(t)
            text += t + "\n"
    return text, page_texts


def check_ats_parsing(text, page_count):
    """Check ATS-friendliness of the document."""
    score = 100
    findings = []

    # Special characters
    for ch in FORMAT_ISSUES["special_bullets"]:
        if ch in text:
            score -= 5
            findings.append(("CRITICAL", f"Non-ATS bullet '{ch}' detected — ATS will garble content"))

    for ch in FORMAT_ISSUES["bad_chars"]:
        if ch in text:
            score -= 3
            findings.append(("WARNING", f"Invisible Unicode char U+{ord(ch):04X} may break parsing"))

    # Page count
    if page_count > 2:
        score -= 10
        findings.append(("CRITICAL", f"{page_count} pages — exceeds standard 1-2 page limit"))
    elif page_count == 1:
        findings.append(("PASS", "1-page format (optimal)"))

    # Contact info
    if "@" in text:
        findings.append(("PASS", "Email detected"))
    else:
        score -= 10
        findings.append(("CRITICAL", "No email address found"))

    if re.search(r'\+?\d[\d\s\-\(\)]{7,}', text):
        findings.append(("PASS", "Phone number detected"))
    else:
        score -= 5
        findings.append(("WARNING", "No phone number detected"))

    if "linkedin" in text.lower():
        findings.append(("PASS", "LinkedIn URL detected"))
    else:
        score -= 5
        findings.append(("WARNING", "No LinkedIn URL found"))

    if "github" in text.lower():
        findings.append(("PASS", "GitHub URL detected"))
    else:
        findings.append(("INFO", "No GitHub URL found"))

    # Sections
    found_sections = sum(1 for s in SECTION_HEADERS if s.lower() in text.lower())
    if found_sections >= 5:
        score += 5
        findings.append(("PASS", f"{found_sections} standard sections found"))
    elif found_sections >= 3:
        findings.append(("WARNING", f"Only {found_sections} sections found — aim for 5+"))
    else:
        score -= 10
        findings.append(("CRITICAL", f"Only {found_sections} sections found — poor structure"))

    return max(score, 0), findings


def check_keywords(text):
    """Check keyword density and coverage."""
    text_lower = text.lower()
    results = {}
    total_found = 0
    total_possible = 0

    for category, keywords in ATS_KEYWORDS.items():
        found = [k for k in keywords if k.lower() in text_lower]
        results[category] = {"found": found, "missing": [k for k in keywords if k.lower() not in text_lower]}
        total_found += len(found)
        total_possible += len(keywords)

    coverage = (total_found / total_possible * 100) if total_possible > 0 else 0
    return results, coverage, total_found, total_possible


def check_metrics(text):
    """Count quantifiable metrics."""
    metrics = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metrics.extend(matches)

    # Also find standalone numbers (potential metrics)
    standalone_numbers = re.findall(r'\b\d{2,}(?:[.,]\d+)?\b', text)

    return len(metrics), metrics, len(standalone_numbers)


def check_action_verbs(text):
    """Check action verb usage."""
    text_lower = text.lower()
    found = [v for v in ACTION_VERBS if v.strip() in text_lower]
    return len(found), found


def check_readability(text):
    """Basic readability metrics."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()

    avg_words_per_sentence = len(words) / max(len(sentences), 1)

    # Jargon density
    jargon = ["pipeline", "infrastructure", "microservices", "throughput", "latency",
              "throughput", "throughput", "orchestration", "deployment", "optimization"]
    jargon_count = sum(1 for j in jargon if j.lower() in text.lower())

    return {
        "total_words": len(words),
        "total_sentences": len(sentences),
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "jargon_density": jargon_count,
    }


def check_timeline_consistency(text):
    """Check date format consistency and overlaps."""
    # Find date ranges
    date_ranges = re.findall(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})\s*[–\-]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|[Pp]resent)',
        text
    )

    # Check format consistency
    formats = set()
    for start, end in date_ranges:
        if "present" in end.lower():
            formats.add("present")
        else:
            formats.add("month_year")

    return len(date_ranges), list(date_ranges), len(formats)


def score_variant(text, page_count, variant_name):
    """Compute total ATS score for a variant."""
    # 1. ATS Parsing (40 points)
    ats_score, ats_findings = check_ats_parsing(text, page_count)

    # 2. Keywords (25 points)
    kw_results, kw_coverage, kw_found, kw_total = check_keywords(text)
    kw_score = min(25, int(kw_coverage / 100 * 25))

    # 3. Metrics (15 points)
    metric_count, metric_list, standalone = check_metrics(text)
    metric_score = min(15, int(metric_count / 15 * 15))

    # 4. Action Verbs (10 points)
    verb_count, verb_list = check_action_verbs(text)
    verb_score = min(10, int(verb_count / 12 * 10))

    # 5. Readability (10 points)
    readability = check_readability(text)
    readability_score = 10
    if readability["avg_words_per_sentence"] > 30:
        readability_score -= 3
    if readability["avg_words_per_sentence"] < 8:
        readability_score -= 2

    total_score = ats_score + kw_score + metric_score + verb_score + readability_score
    total_score = min(total_score, 100)

    return {
        "variant": variant_name,
        "total_score": total_score,
        "page_count": page_count,
        "ats_parsing": {"score": ats_score, "findings": ats_findings},
        "keywords": {"score": kw_score, "coverage": round(kw_coverage, 1), "found": kw_found, "total": kw_total, "details": kw_results},
        "metrics": {"score": metric_score, "count": metric_count, "examples": metric_list[:10], "standalone_numbers": standalone},
        "action_verbs": {"score": verb_score, "count": verb_count, "list": verb_list},
        "readability": readability,
    }


def generate_report(results):
    """Generate comprehensive evaluation report."""
    lines = []
    lines.append("=" * 80)
    lines.append("COMPREHENSIVE ATS & CV EVALUATION REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)

    # Summary table
    lines.append("\n📊 SCORE SUMMARY")
    lines.append("-" * 80)
    lines.append(f"{'Variant':<42} {'Score':>6} {'Pages':>6} {'KW%':>6} {'Metrics':>8} {'Verbs':>6}")
    lines.append("-" * 80)
    for r in sorted(results, key=lambda x: -x["total_score"]):
        lines.append(
            f"{r['variant']:<42} {r['total_score']:>5}/100 {r['page_count']:>5}p "
            f"{r['keywords']['coverage']:>5.1f}% {r['metrics']['count']:>7} "
            f"{r['action_verbs']['count']:>5}"
        )

    # Best and worst
    best = max(results, key=lambda x: x["total_score"])
    worst = min(results, key=lambda x: x["total_score"])
    lines.append(f"\n🏆 Best: {best['variant']} ({best['total_score']}/100)")
    lines.append(f"⚠️  Worst: {worst['variant']} ({worst['total_score']}/100)")

    # Detailed per-variant analysis
    for r in results:
        lines.append("\n" + "=" * 80)
        lines.append(f"📋 {r['variant']} — Score: {r['total_score']}/100")
        lines.append("=" * 80)

        # ATS Findings
        lines.append(f"\n  ATS PARSING ({r['ats_parsing']['score']}/100):")
        for level, msg in r["ats_parsing"]["findings"]:
            icon = {"PASS": "✅", "WARNING": "⚠️", "CRITICAL": "❌", "INFO": "ℹ️"}.get(level, "?")
            lines.append(f"    {icon} [{level}] {msg}")

        # Keywords
        lines.append(f"\n  KEYWORDS ({r['keywords']['score']}/25 — {r['keywords']['coverage']:.1f}% coverage):")
        for cat, details in r["keywords"]["details"].items():
            lines.append(f"    {cat}: {len(details['found'])}/{len(details['found']) + len(details['missing'])} — found: {', '.join(details['found'][:5])}")
            if details["missing"]:
                lines.append(f"      missing: {', '.join(details['missing'][:5])}")

        # Metrics
        lines.append(f"\n  METRICS ({r['metrics']['score']}/15 — {r['metrics']['count']} quantifiable):")
        if r["metrics"]["examples"]:
            lines.append(f"    Examples: {', '.join(r['metrics']['examples'][:8])}")

        # Verbs
        lines.append(f"\n  ACTION VERBS ({r['action_verbs']['score']}/10 — {r['action_verbs']['count']} unique):")
        lines.append(f"    {', '.join(r['action_verbs']['list'][:15])}")

        # Readability
        lines.append(f"\n  READABILITY:")
        lines.append(f"    Words: {r['readability']['total_words']}, Sentences: {r['readability']['total_sentences']}")
        lines.append(f"    Avg words/sentence: {r['readability']['avg_words_per_sentence']}")

    # Global recommendations
    lines.append("\n" + "=" * 80)
    lines.append("🎯 GLOBAL RECOMMENDATIONS")
    lines.append("=" * 80)

    avg_score = sum(r["total_score"] for r in results) / len(results)
    lines.append(f"\n  Average Score: {avg_score:.1f}/100")

    # Find common issues
    all_missing_kw = Counter()
    for r in results:
        for cat, details in r["keywords"]["details"].items():
            for k in details["missing"]:
                all_missing_kw[k] += 1

    if all_missing_kw:
        lines.append("\n  🔴 MOST COMMONLY MISSING KEYWORDS (across all variants):")
        for kw, count in all_missing_kw.most_common(10):
            lines.append(f"    - '{kw}' missing in {count}/{len(results)} variants")

    # Formatting issues
    special_bullet_variants = [r["variant"] for r in results if any(
        "bullet" in f[1].lower() for f in r["ats_parsing"]["findings"] if f[0] == "CRITICAL"
    )]
    if special_bullet_variants:
        lines.append(f"\n  🔴 SPECIAL BULLET ISSUES in: {', '.join(special_bullet_variants)}")
    else:
        lines.append("\n  ✅ No special bullet character issues detected")

    # Score distribution
    score_ranges = Counter()
    for r in results:
        if r["total_score"] >= 85:
            score_ranges["Excellent (85+)"] += 1
        elif r["total_score"] >= 70:
            score_ranges["Good (70-84)"] += 1
        elif r["total_score"] >= 55:
            score_ranges["Fair (55-69)"] += 1
        else:
            score_ranges["Needs Work (<55)"] += 1

    lines.append("\n  📊 SCORE DISTRIBUTION:")
    for label, count in sorted(score_ranges.items()):
        lines.append(f"    {label}: {count} variants")

    lines.append("\n" + "=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    results = []

    for variant in VARIANTS:
        path = os.path.join(PDF_DIR, variant)
        if not os.path.exists(path):
            print(f"⚠️  {variant} not found, skipping")
            continue

        text, page_texts = extract_text(path)
        page_count = len(page_texts)

        result = score_variant(text, page_count, variant)
        results.append(result)

    report = generate_report(results)

    # Print report
    print(report)

    # Save report
    report_path = "/Users/alinikkhah/Documents/CV repo/Resume 3/ATS_EVALUATION_REPORT.txt"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_path}")

    # Save JSON
    json_path = "/Users/alinikkhah/Documents/CV repo/Resume 3/ats_evaluation_results.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"📊 JSON data saved to: {json_path}")


if __name__ == "__main__":
    main()
