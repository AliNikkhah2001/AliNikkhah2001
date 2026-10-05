#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/alinikkhah/Documents/CV repo/Resume 3/industrial")

variants = [
    ("isAgentic", "AgenticAI"),
    ("isVision", "ComputerVision"),
    ("isData", "DataScience"),
    ("isSWE", "SoftwareEng"),
    ("isHybrid", "HybridAI"),
    ("isSenior", "SeniorAI"),
    ("isMLPlatform", "MLPlatform"),
]

for flag, name in variants:
    with open("main.tex", "r") as f:
        content = f.read()
    
    for f in ["isAgentic", "isVision", "isData", "isSWE", "isHybrid", "isSenior", "isMLPlatform"]:
        content = content.replace(f"\\setbool{{{f}}}{{true}}", f"\\setbool{{{f}}}{{false}}")
    
    content = content.replace(f"\\setbool{{{flag}}}{{false}}", f"\\setbool{{{flag}}}{{true}}")
    content = content.replace(r"\setbool{onePage}{true}", r"\setbool{onePage}{false}")
    
    with open("main.tex", "w") as f:
        f.write(content)
    
    result = subprocess.run(["pdflatex", "main.tex"], capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.run(["cp", "main.pdf", f"/Users/alinikkhah/Documents/CV repo/Resume 3/compiled_pdfs/Ali_Nikkhah_{name}_2page.pdf"])
        print(f"✅ {name} 2-page compiled")
    else:
        print(f"❌ {name} 2-page failed:")
        print(result.stdout[-3000:])

# Now compile 1-page versions
for flag, name in variants:
    with open("main.tex", "r") as f:
        content = f.read()
    
    for f in ["isAgentic", "isVision", "isData", "isSWE", "isHybrid", "isSenior", "isMLPlatform"]:
        content = content.replace(f"\\setbool{{{f}}}{{true}}", f"\\setbool{{{f}}}{{false}}")
    
    content = content.replace(f"\\setbool{{{flag}}}{{false}}", f"\\setbool{{{flag}}}{{true}}")
    content = content.replace(r"\setbool{onePage}{false}", r"\setbool{onePage}{true}")
    
    with open("main.tex", "w") as f:
        f.write(content)
    
    result = subprocess.run(["pdflatex", "main.tex"], capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.run(["cp", "main.pdf", f"/Users/alinikkhah/Documents/CV repo/Resume 3/compiled_pdfs/Ali_Nikkhah_{name}_1page.pdf"])
        print(f"✅ {name} 1-page compiled")
    else:
        print(f"❌ {name} 1-page failed:")
        print(result.stdout[-3000:])

# Restore Agentic 1-page as default
with open("main.tex", "r") as f:
    content = f.read()
content = content.replace(r"\setbool{isAgentic}{false}", r"\setbool{isAgentic}{true}")
content = content.replace(r"\setbool{onePage}{false}", r"\setbool{onePage}{true}")
with open("main.tex", "w") as f:
    f.write(content)

print("\nDone! All variants compiled.")