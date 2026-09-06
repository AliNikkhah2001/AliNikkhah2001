#!/usr/bin/env python3
import pdfplumber
import os

pdf_dir = "/Users/alinikkhah/Documents/CV repo/Resume 3/compiled_pdfs"
variants = [
    "Ali_Nikkhah_AgenticAI_1page.pdf",
    "Ali_Nikkhah_AgenticAI_2page.pdf",
    "Ali_Nikkhah_ComputerVision_1page.pdf",
    "Ali_Nikkhah_ComputerVision_2page.pdf",
    "Ali_Nikkhah_DataScience_1page.pdf",
    "Ali_Nikkhah_DataScience_2page.pdf",
    "Ali_Nikkhah_SoftwareEng_1page.pdf",
    "Ali_Nikkhah_SoftwareEng_2page.pdf",
    "Ali_Nikkhah_ResearchCV.pdf",
]

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def analyze_ats(text, name, pdf_path):
    issues = []
    warnings = []
    
    # Check for contact info
    if "email" not in text.lower() and "@" not in text:
        issues.append("No email found")
    if "phone" not in text.lower() and "+" not in text:
        warnings.append("No phone number found")
    if "linkedin" not in text.lower():
        warnings.append("No LinkedIn URL found")
    
    # Check for keywords density
    keywords = ["python", "fastapi", "kubernetes", "docker", "redis", "kafka", "pytorch", "tensorflow", "llm", "rag", "langgraph", "triton", "vllm"]
    found = sum(1 for k in keywords if k.lower() in text.lower())
    if found < 8:
        warnings.append(f"Only {found}/12 core keywords found")
    
    # Check for quantifiable metrics
    import re
    numbers = re.findall(r'\d+(?:[.,]\d+)?\s*(?:million|M|K|k|%|percent|ms|latency|throughput|queries|daily|QPS|RPS)', text, re.IGNORECASE)
    if len(numbers) < 5:
        warnings.append(f"Only {len(numbers)} quantifiable metrics found")
    
    # Check for action verbs
    action_verbs = ["engineered", "designed", "built", "developed", "led", "architected", "implemented", "optimized", "deployed", "orchestrated", "automated", "achieved", "reduced", "improved", "increased", "delivered"]
    found_verbs = sum(1 for v in action_verbs if v in text.lower())
    if found_verbs < 8:
        warnings.append(f"Only {found_verbs}/15 action verbs found")
    
    # Check for dates format consistency
    date_patterns = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–-]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}', text)
    if len(date_patterns) < 3:
        warnings.append("Date format may be inconsistent or sparse")
    
    # Check page count
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
    
    # Check for section headers
    sections = ["summary", "technical skills", "professional experience", "experience", "education", "projects", "research"]
    found_sections = sum(1 for s in sections if s.lower() in text.lower())
    if found_sections < 5:
        warnings.append(f"Only {found_sections}/7 standard sections found")
    
    # Check for special characters that might break ATS
    special_chars = ['•', '·', '▪', '▫', '◆', '◇', '★', '☆']
    for ch in special_chars:
        if ch in text:
            warnings.append(f"Special bullet character '{ch}' may not parse correctly")
            break
    
    return issues, warnings, page_count

print("=" * 80)
print("ATS ANALYSIS REPORT")
print("=" * 80)

for variant in variants:
    path = os.path.join(pdf_dir, variant)
    if os.path.exists(path):
        text = extract_text(path)
        issues, warnings, page_count = analyze_ats(text, variant, path)
        
        print(f"\n📄 {variant}")
        print(f"   Pages: {page_count}")
        print(f"   Chars: {len(text)}, Words: {len(text.split())}")
        
        if issues:
            for i in issues:
                print(f"   ❌ ISSUE: {i}")
        if warnings:
            for w in warnings:
                print(f"   ⚠️  WARNING: {w}")
        if not issues and not warnings:
            print(f"   ✅ No major issues detected")
    else:
        print(f"\n📄 {variant} - FILE NOT FOUND")

print("\n" + "=" * 80)
print("COMMON ATS BEST PRACTICES CHECKLIST")
print("=" * 80)
checklist = [
    ("Standard section headers", "Summary, Experience, Education, Skills, Projects"),
    ("No columns/tables", "Single-column layout preferred"),
    ("Standard fonts", "Arial, Calibri, Helvetica - avoid fancy fonts"),
    ("No graphics/images", "ATS cannot read images, charts, logos"),
    ("Keywords from job description", "Match exact terms: 'Python' not 'Python3'"),
    ("Quantifiable achievements", "Numbers, percentages, scale metrics"),
    ("Action verbs first", "Start bullets with: Engineered, Built, Led, etc."),
    ("Consistent date format", "MMM YYYY – MMM YYYY"),
    ("Contact info at top", "Name, email, phone, LinkedIn, portfolio"),
    ("File format", "PDF (text-based) or DOCX"),
    ("No headers/footers", "ATS may skip header/footer content"),
    ("Standard bullet points", "Use simple • or - not special chars"),
]
for item, desc in checklist:
    print(f"   ☐ {item}: {desc}")