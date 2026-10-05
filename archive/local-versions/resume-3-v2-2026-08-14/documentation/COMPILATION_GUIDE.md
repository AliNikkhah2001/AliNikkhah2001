# Resume Compilation Guide
**Version:** 1.0  
**Date:** August 14, 2026  
**Author:** opencode AI Assistant

---

## 📋 QUICK START

### Prerequisites
1. **LaTeX Distribution:** TeX Live 2024 (confirmed working on your system)
2. **pdflatex:** Available at `/Library/TeX/texbin/pdflatex`
3. **Working Directory:** `/Users/alinikkhah/Documents/CV repo/Resume 3_v2_2026-08-14/`

### Verify Installation
```bash
which pdflatex
pdflatex --version
```

---

## 🏗️ DIRECTORY STRUCTURE

```
Resume 3_v2_2026-08-14/
├── industrial/
│   ├── main.tex                             # Main LaTeX file
│   ├── segments/
│   │   ├── common/                          # Shared segments
│   │   │   ├── contact_info.tex
│   │   │   ├── education.tex
│   │   │   ├── skills.tex
│   │   │   ├── skills_1p.tex
│   │   │   └── research_2p.tex
│   │   ├── agentic_ai/                      # Agentic AI variant
│   │   │   ├── summary_1p.tex
│   │   │   ├── summary_2p.tex
│   │   │   ├── experience_1p.tex
│   │   │   ├── experience_2p.tex
│   │   │   └── projects_2p.tex
│   │   ├── computer_vision/                 # Computer Vision variant
│   │   │   ├── summary_1p.tex
│   │   │   ├── summary_2p.tex
│   │   │   ├── experience_1p.tex
│   │   │   ├── experience_2p.tex
│   │   │   └── projects_2p.tex
│   │   ├── data_roles/                       # Data Science variant
│   │   │   ├── summary_1p.tex
│   │   │   ├── summary_2p.tex
│   │   │   ├── experience_1p.tex
│   │   │   ├── experience_2p.tex
│   │   │   └── projects_2p.tex
│   │   └── software_engineering/            # Software Engineering variant
│   │       ├── summary_1p.tex
│   │       ├── summary_2p.tex
│   │       ├── experience_1p.tex
│   │       ├── experience_2p.tex
│   │       └── projects_2p.tex
│   └── compiled_pdfs/                        # Output directory
└── academic/
    ├── main.tex
    └── segments/
        ├── publications/
        │   └── list.tex
        ├── research_experience/
        │   ├── entries.tex
        │   └── industry.tex
        └── teaching_mentoring/
            └── ta_history.tex
```

---

## 🎯 COMPILATION COMMANDS

### Industrial Variants

The industrial variants use a **modular system** where you set flags in `main.tex` to select:
1. **Role variant:** Agentic AI, Computer Vision, Data Science, or Software Engineering
2. **Page length:** 1-page or 2-page

#### Step 1: Choose Variant in main.tex

Open `industrial/main.tex` and set the flags:

```latex
% Set exactly ONE role flag to true
\newbool{isAgentic}  \setbool{isAgentic}{true}    % Agentic AI
\newbool{isVision}   \setbool{isVision}{false}   % Computer Vision
\newbool{isData}     \setbool{isData}{false}     % Data Science
\newbool{isSWE}      \setbool{isSWE}{false}      % Software Engineering

% Set page length
\newbool{onePage}    \setbool{onePage}{true}     % false = 2-page
```

#### Step 2: Compile

```bash
cd /Users/alinikkhah/Documents/CV\ repo/Resume\ 3_v2_2026-08-14/industrial

# Compile (creates main.pdf)
pdflatex main.tex

# For clean compilation (removes auxiliary files)
pdflatex main.tex && rm -f *.aux *.log *.out
```

#### Step 3: Rename Output

```bash
# Agentic AI - 1 Page
cp main.pdf ../compiled_pdfs/Ali_Nikkhah_AgenticAI_1page.pdf

# Agentic AI - 2 Pages
cp main.pdf ../compiled_pdfs/Ali_Nikkhah_AgenticAI_2page.pdf

# And so on for other variants...
```

### Quick Compile Script

Create `compile_all.sh` in the industrial directory:

```bash
#!/bin/bash

# Create output directory
mkdir -p ../compiled_pdfs

# Compile all variants
for variant in "AgenticAI" "ComputerVision" "DataScience" "SWE"; do
  for pages in "1page" "2page"; do
    # Set flags based on variant
    case $variant in
      "AgenticAI") role="isAgentic" ;;
      "ComputerVision") role="isVision" ;;
      "DataScience") role="isData" ;;
      "SWE") role="isSWE" ;;
    esac
    
    # Set page flag
    if [ "$pages" = "1page" ]; then
      page="true"
    else
      page="false"
    fi
    
    # Create temporary main.tex with correct flags
    sed "s/\\setbool{isAgentic}{.*}/\\setbool{isAgentic}{false}/" main.tex | \
    sed "s/\\setbool{isVision}{.*}/\\setbool{isVision}{false}/" | \
    sed "s/\\setbool{isData}{.*}/\\setbool{isData}{false}/" | \
    sed "s/\\setbool{isSWE}{.*}/\\setbool{isSWE}{false}/" | \
    sed "s/\\setbool{$role}{.*}/\\setbool{$role}{true}/" | \
    sed "s/\\setbool{onePage}{.*}/\\setbool{onePage}{$page}/" > main_temp.tex
    
    # Compile
    pdflatex main_temp.tex > /dev/null 2>&1
    
    # Move output
    mv main_temp.pdf ../compiled_pdfs/Ali_Nikkhah_${variant}_${pages}.pdf
    
    # Cleanup
    rm -f main_temp.*
  done
done

echo "All variants compiled successfully!"
```

Make it executable:
```bash
chmod +x compile_all.sh
```

Run it:
```bash
./compile_all.sh
```

### Academic CV

```bash
cd /Users/alinikkhah/Documents/CV\ repo/Resume\ 3_v2_2026-08-14/academic

# Compile
pdflatex main.tex

# Move output
mv main.pdf ../compiled_pdfs/Ali_Nikkhah_ResearchCV.pdf

# Cleanup
rm -f *.aux *.log *.out
```

---

## 🐍 PYTHON COMPILATION SCRIPT

For more advanced compilation, create `compile_all.py`:

```python
#!/usr/bin/env python3
import os
import subprocess
import shutil

# Configuration
INDUSTRIAL_DIR = "/Users/alinikkhah/Documents/CV repo/Resume 3_v2_2026-08-14/industrial"
ACADEMIC_DIR = "/Users/alinikkhah/Documents/CV repo/Resume 3_v2_2026-08-14/academic"
OUTPUT_DIR = "/Users/alinikkhah/Documents/CV repo/Resume 3_v2_2026-08-14/compiled_pdfs"

# Variants
VARIANTS = {
    "AgenticAI": "isAgentic",
    "ComputerVision": "isVision",
    "DataScience": "isData",
    "SWE": "isSWE"
}

PAGE_LENGTHS = {
    "1page": "true",
    "2page": "false"
}

def compile_variant(variant_name, variant_flag, page_length, page_flag):
    """Compile a single variant"""
    print(f"Compiling {variant_name} - {page_length}...")
    
    # Read main.tex
    with open(os.path.join(INDUSTRIAL_DIR, "main.tex"), "r") as f:
        content = f.read()
    
    # Replace flags
    for v, flag in VARIANTS.items():
        content = content.replace(f"\\setbool{{{flag}}}{{true}}", f"\\setbool{{{flag}}}{{false}}")
        content = content.replace(f"\\setbool{{{flag}}}{{false}}", f"\\setbool{{{flag}}}{{false}}")
    
    content = content.replace(f"\\setbool{{{variant_flag}}}{{false}}", f"\\setbool{{{variant_flag}}}{{true}}")
    content = content.replace(f"\\setbool{{onePage}}{{true}}", f"\\setbool{{onePage}}{{{page_flag}}}")
    content = content.replace(f"\\setbool{{onePage}}{{false}}", f"\\setbool{{onePage}}{{{page_flag}}}")
    
    # Write temporary file
    temp_file = os.path.join(INDUSTRIAL_DIR, "main_temp.tex")
    with open(temp_file, "w") as f:
        f.write(content)
    
    # Compile
    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "main_temp.tex"], 
                      cwd=INDUSTRIAL_DIR, check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Move output
        src_pdf = os.path.join(INDUSTRIAL_DIR, "main_temp.pdf")
        dst_pdf = os.path.join(OUTPUT_DIR, f"Ali_Nikkhah_{variant_name}_{page_length}.pdf")
        shutil.move(src_pdf, dst_pdf)
        
        # Cleanup
        for ext in ["aux", "log", "out", "toc", "lot", "lof"]:
            temp_file_ext = os.path.join(INDUSTRIAL_DIR, f"main_temp.{ext}")
            if os.path.exists(temp_file_ext):
                os.remove(temp_file_ext)
        
        print(f"  ✓ Success: {dst_pdf}")
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to compile {variant_name} - {page_length}")
        print(f"    Error: {e}")

def compile_academic():
    """Compile academic CV"""
    print("Compiling Academic CV...")
    
    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], 
                      cwd=ACADEMIC_DIR, check=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Move output
        src_pdf = os.path.join(ACADEMIC_DIR, "main.pdf")
        dst_pdf = os.path.join(OUTPUT_DIR, "Ali_Nikkhah_ResearchCV.pdf")
        shutil.move(src_pdf, dst_pdf)
        
        # Cleanup
        for ext in ["aux", "log", "out", "toc", "lot", "lof"]:
            main_ext = os.path.join(ACADEMIC_DIR, f"main.{ext}")
            if os.path.exists(main_ext):
                os.remove(main_ext)
        
        print(f"  ✓ Success: {dst_pdf}")
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to compile Academic CV")
        print(f"    Error: {e}")

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Compile industrial variants
    for variant_name, variant_flag in VARIANTS.items():
        for page_length, page_flag in PAGE_LENGTHS.items():
            compile_variant(variant_name, variant_flag, page_length, page_flag)
    
    # Compile academic CV
    compile_academic()
    
    print("\n✅ All resumes compiled successfully!")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
```

Run it:
```bash
python3 compile_all.py
```

---

## 🔧 TROUBLESHOOTING

### Common Issues

#### 1. pdflatex Not Found
**Error:** `command not found: pdflatex`
**Solution:** Install TeX Live or ensure it's in your PATH

#### 2. Missing Packages
**Error:** `! LaTeX Error: File 'xxx.sty' not found.`
**Solution:** Install the missing package:
```bash
# For TeX Live on macOS
sudo tlmgr install <package-name>
```

#### 3. Compilation Errors
**Error:** Various LaTeX errors
**Solution:** Check the `.log` file for details

#### 4. Output Not Generated
**Solution:** Check if `main.pdf` exists in the directory

#### 5. Permission Issues
**Error:** `Permission denied`
**Solution:** Ensure you have write permissions:
```bash
chmod -R u+w /Users/alinikkhah/Documents/CV\ repo/Resume\ 3_v2_2026-08-14/
```

### Debug Mode

To see compilation output:
```bash
cd /Users/alinikkhah/Documents/CV\ repo/Resume\ 3_v2_2026-08-14/industrial
pdflatex main.tex  # Without redirecting output
```

---

## 📊 COMPILATION TIME ESTIMATES

| Task | Time | Notes |
|------|------|-------|
| Single variant | 5-10 seconds | Depends on complexity |
| All industrial variants (8) | 40-80 seconds | 4 variants × 2 page lengths |
| Academic CV | 5-10 seconds | Simpler document |
| All variants | 45-90 seconds | Total compilation time |

---

## 🎯 BEST PRACTICES

### 1. Always Compile Before Submitting
```bash
# Quick check
cd industrial && pdflatex main.tex && open main.pdf
```

### 2. Clean Up Auxiliary Files
```bash
rm -f *.aux *.log *.out *.toc
```

### 3. Verify Output
```bash
# Check file size (should be 100-300KB)
ls -lh main.pdf

# Check page count
pdfinfo main.pdf | grep Pages
```

### 4. Test on Multiple Devices
- Open on desktop
- Open on mobile (some ATS use mobile parsing)
- Check text selectability

### 5. Version Control
```bash
# Before making changes
git add .
git commit -m "Before ATS optimization"

# After changes
git add .
git commit -m "ATS optimization - Phase 1"
```

---

## 📚 ADDITIONAL RESOURCES

### LaTeX Guides
- [Overleaf Documentation](https://www.overleaf.com/learn)
- [LaTeX Wikibook](https://en.wikibooks.org/wiki/LaTeX)
- [TeX Live Guide](https://tug.org/texlive/)

### Resume-Specific LaTeX
- [Awesome CV](https://github.com/posquit0/awesome-cv)
- [Modern CV](https://github.com/moderncv/moderncv)
- [ATS-Friendly Resume](https://github.com/georgehawkins/ats-resume-latex)

---

**Document Version:** 1.0  
**Last Updated:** August 14, 2026  
**Next Review:** After Phase 1 completion
