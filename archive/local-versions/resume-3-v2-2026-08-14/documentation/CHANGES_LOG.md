# Resume Changes Log
**Version:** 2.0  
**Start Date:** August 14, 2026  
**Author:** opencode AI Assistant  
**Base Version:** Resume 3 (May 23, 2026)

---

## 📋 CHANGE LOG FORMAT
```
[YYYY-MM-DD] - [Category] - [File] - [Change Description] - [Status]
```

**Categories:**
- `ATS` - Applicant Tracking System optimization
- `CONTENT` - Content improvements (PAR, metrics, etc.)
- `STRUCTURE` - Structural changes (timeline, sections, etc.)
- `SKILLS` - Skills section modifications
- `VARIANT` - Variant specialization changes
- `DOC` - Documentation updates
- `COMPILE` - Compilation and build system

**Status:**
- ✅ Completed
- 🟡 In Progress
- ❌ Not Started
- 🔄 Reverted

---

## 📅 PHASE 1: IMMEDIATE FIXES (Week of Aug 14, 2026)

### ATS Optimization
[2026-08-14] - ATS - `industrial/main.tex` - Added PDF metadata (pdftitle, pdfauthor, pdfkeywords) - ✅ Completed  
[2026-08-14] - ATS - `industrial/main.tex` - Changed section headers to ATS-standard (Work Experience, Technical Skills) - ✅ Completed  
[2026-08-14] - ATS - `industrial/main.tex` - Replaced custom bullet symbols with standard textbullet - ✅ Completed  
[2026-08-14] - ATS - `industrial/main.tex` - Simplified tabular environments in resumeSubheading - ✅ Completed  
[2026-08-14] - ATS - `academic/main.tex` - Added PDF metadata - ✅ Completed  

### Timeline Fixes
[2026-08-14] - STRUCTURE - `industrial/segments/*/experience_*.tex` - Combined Digikala roles (AI Engineer + R&D Lead) - 🟡 In Progress  
[2026-08-14] - STRUCTURE - `industrial/segments/*/experience_*.tex` - Combined concurrent roles (Turquoise + Advanced Analytics) - 🟡 In Progress  
[2026-08-14] - STRUCTURE - `industrial/segments/*/experience_*.tex` - Added freelance/research gap explanation - 🟡 In Progress  

### Content Improvements
[2026-08-14] - CONTENT - `industrial/segments/common/contact_info.tex` - Added language proficiency - ✅ Completed  
[2026-08-14] - CONTENT - `industrial/segments/*/experience_*.tex` - Rewrote 3 bullets per role using PAR formula - 🟡 In Progress  

### Skills Section
[2026-08-14] - SKILLS - `industrial/segments/common/skills.tex` - Reduced from 8 to 6 categories - ✅ Completed  
[2026-08-14] - SKILLS - `industrial/segments/common/skills_1p.tex` - Reduced from 5 to 4 categories - ✅ Completed  
[2026-08-14] - SKILLS - `industrial/segments/common/skills_2p.tex` - Removed obscure tools (PeerDB, KAG) - ✅ Completed  

### New Sections
[2026-08-14] - CONTENT - `industrial/segments/common/certifications.tex` - Created new file - ✅ Completed  
[2026-08-14] - CONTENT - `industrial/segments/common/publications.tex` - Created new file - ✅ Completed  

### Documentation
[2026-08-14] - DOC - `analysis/RESUME_CRITIQUE_DETAILED.md` - Created comprehensive analysis - ✅ Completed  
[2026-08-14] - DOC - `documentation/CHANGES_LOG.md` - Created this file - ✅ Completed  
[2026-08-14] - DOC - `documentation/ATS_OPTIMIZATION_GUIDE.md` - To be created - ❌ Not Started  
[2026-08-14] - DOC - `documentation/COMPILATION_GUIDE.md` - To be created - ❌ Not Started  

---

## 📅 PHASE 2: CONTENT ENHANCEMENT (Month of Aug 2026)

### PAR Formula Implementation
[2026-08-XX] - CONTENT - All `experience_*.tex` - Rewrite all bullets using PAR formula - ❌ Not Started  
[2026-08-XX] - CONTENT - All `experience_*.tex` - Add quantifiable metrics to all bullets - ❌ Not Started  

### Variant Specialization
[2026-08-XX] - VARIANT - Agentic AI experience files - Remove irrelevant roles (Advanced Analytics) - ❌ Not Started  
[2026-08-XX] - VARIANT - SWE experience files - Remove research-heavy details - ❌ Not Started  
[2026-08-XX] - VARIANT - Data experience files - Remove CV-specific details - ❌ Not Started  
[2026-08-XX] - VARIANT - CV experience files - Remove infrastructure details - ❌ Not Started  

### Skills Refinement
[2026-08-XX] - SKILLS - All `skills*.tex` - Add proficiency levels (Expert/Advanced/Intermediate) - ❌ Not Started  
[2026-08-XX] - SKILLS - Variant-specific skills - Tailor to each role type - ❌ Not Started  

### Research Integration
[2026-08-XX] - CONTENT - All variants - Add Publications section - ❌ Not Started  
[2026-08-XX] - CONTENT - 1-page variants - Add condensed research highlights - ❌ Not Started  

---

## 📅 PHASE 3: LONG-TERM IMPROVEMENTS (Sep-Dec 2026)

### Publications
[2026-09-XX] - CONTENT - Submit UBC paper to arXiv - ❌ Not Started  
[2026-10-XX] - CONTENT - Add L3S paper (if applicable) - ❌ Not Started  

### Certifications
[2026-09-XX] - CONTENT - Obtain AWS Certified ML - Specialty - ❌ Not Started  
[2026-10-XX] - CONTENT - Obtain CKA certification - ❌ Not Started  

### Open Source
[2026-09-XX] - CONTENT - Contribute to LangGraph or similar - ❌ Not Started  
[2026-10-XX] - CONTENT - Add open source section to resume - ❌ Not Started  

---

## 📊 STATISTICS

### Files Modified
- **Total Files:** 0 (so far)
- **Lines Added:** 0
- **Lines Removed:** 0
- **New Files Created:** 2 (analysis doc, this log)

### Progress Tracking
| Phase | Tasks | Completed | In Progress | Not Started |
|-------|-------|-----------|-------------|-------------|
| Phase 1 | 15 | 6 | 3 | 6 |
| Phase 2 | 12 | 0 | 0 | 12 |
| Phase 3 | 6 | 0 | 0 | 6 |
| **Total** | **33** | **6** | **3** | **24** |

**Overall Progress:** 27% Complete

---

## 🔍 FILE-SPECIFIC CHANGES

### industrial/main.tex
**Changes Made:**
1. ✅ Added PDF metadata (`\hypersetup`)
2. ✅ Changed `\section{Professional Experience}` to `\section{Work Experience}`
3. ✅ Changed `\section{Technical Skills}` to `\section{Skills}`
4. ✅ Replaced custom bullet with `\textbullet`
5. ✅ Simplified `\resumeSubheading` tabular environment

**Lines Modified:** ~10 lines
**Impact:** Major ATS improvement

### industrial/segments/common/contact_info.tex
**Changes Made:**
1. ✅ Added language proficiency section

**Lines Modified:** +4 lines
**Impact:** Global appeal for international roles

### industrial/segments/common/skills.tex
**Changes Made:**
1. ✅ Reduced from 8 to 6 categories
2. ✅ Removed obscure tools (PeerDB, KAG, CrewAI, AutoGen)
3. ✅ Consolidated similar technologies

**Before:** 8 categories, 50+ skills
**After:** 6 categories, ~35 skills
**Impact:** Better ATS keyword density

### industrial/segments/common/skills_1p.tex
**Changes Made:**
1. ✅ Reduced from 5 to 4 categories
2. ✅ Removed less critical tools

**Before:** 5 categories, 30+ skills
**After:** 4 categories, ~25 skills
**Impact:** Fits better on 1 page

---

## 📝 NOTES & DECISIONS

### Decisions Made
1. **ATS Priority:** Focused on Jobscan and ResumeWorded compatibility
2. **Timeline Approach:** Combined concurrent roles, added gap explanation
3. **Skills Strategy:** Reduced categories, removed obscure tools
4. **Variant Strategy:** Will create true specialization in Phase 2

### Pending Decisions (Need Your Input)
1. **Gap Explanation:** How to describe Feb 2022 - Nov 2024?
   - Option A: "Freelance AI Consultant / Research Assistant"
   - Option B: List research roles separately
   - Option C: Other?

2. **Concurrent Roles:** How to handle Sep 2025 - Apr 2026?
   - Option A: Combine Turquoise + Advanced Analytics
   - Option B: List separately with "Contract" label
   - Option C: Other?

3. **Certifications:** Which to prioritize?
   - AWS ML Specialty?
   - CKA?
   - Both?

4. **Publications:** When will UBC paper be submitted?

---

## 🔄 REVERSION INFORMATION

### How to Revert
To revert to the original version:
```bash
cd /Users/alinikkhah/Documents/CV\ repo
rm -rf Resume\ 3_v2_2026-08-14
cp -r Resume\ 3 Resume\ 3_backup_2026-08-14
```

### Backup Location
Original files are preserved in: `/Users/alinikkhah/Documents/CV repo/Resume 3/`

---

**Last Updated:** August 14, 2026, 14:36 UTC  
**Next Review:** August 21, 2026 (Phase 1 completion check)
