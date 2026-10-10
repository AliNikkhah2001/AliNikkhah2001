# Career Dashboard

Local-first career database and publishing dashboard. Edit your career history, achievements, and technologies once; compose targeted CV variants; export to multiple formats and platforms.

## Architecture

```
career-dashboard/
├── api/                 # FastAPI backend
│   ├── main.py         # REST endpoints
│   └── models.py       # Pydantic models
├── web/                # React + TypeScript frontend (Vite)
│   └── src/
│       ├── components/ # Timeline, KnowledgeBase, VariantComposer, PublishingStatus, LinkedInExport
│       ├── api.ts      # API client
│       └── types.ts    # TypeScript interfaces
├── scripts/
│   └── import_cv.py    # cv.yaml → career_db.json importer
├── career_db.json      # Local database (SQLite alternative supported)
└── README.md
```

## Quick Start

```bash
# 1. Import your cv.yaml into the local database
cd /Users/alinikkhah/Documents/CV\ repo/AliNikkhah2001/career-dashboard
python3 scripts/import_cv.py

# 2. Start the API server (port 8000)
cd api
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000

# 3. Start the dashboard (port 3000)
cd ../web
npm install   # first time only
npm run dev

# 4. Open http://localhost:3000 in your browser
```

## Features

### 1. Career Timeline (vis-timeline)
- Visual timeline with separate lanes for positions, education, and projects
- Concurrent roles shown clearly
- Click any entry to view details

### 2. Knowledge Base
- Searchable, editable tables for all entity types:
  - Positions (with achievements)
  - Achievements (with metrics, skills, wording variants)
  - Organizations
  - Skills (categorized)
  - Education, Projects, Publications, Teaching
- Inline editing with JSON validation
- CRUD operations via API

### 3. CV Variant Composer
- Define variants by audience (industry/academic/research), length, template
- Select specific positions and achievements per variant
- Choose wording level: brief / standard / detailed
- Preview page count target

### 4. Publishing Status & Exports
One-click export to:
- **GitHub README** — Markdown for profile repo
- **RenderCV** — YAML per variant for PDF generation
- **JSON Resume** — Standard schema for themes and registry
- **LinkedIn sections** — Formatted copy-paste blocks (headline, about, experience, education, skills)
- **Reactive Resume** — Import via their API

### 5. LinkedIn Export
- Generates LinkedIn-style cards for each section
- One-click copy to clipboard for manual paste
- Full profile text dump available

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/db` | Full database |
| `POST /api/db/reload` | Re-import from cv.yaml |
| `GET /api/profile` | Profile info |
| `GET /api/positions` | All positions (chronological) |
| `GET /api/achievements` | All achievements |
| `GET /api/organizations` | All organizations |
| `GET /api/projects` | All projects |
| `GET /api/education` | All education |
| `GET /api/publications` | All publications |
| `GET /api/teaching` | All teaching |
| `GET /api/skills` | All skills |
| `GET /api/variants` | All CV variants |
| `GET /api/export/json-resume` | JSON Resume format |
| `GET /api/export/rendercv/{variant}` | RenderCV YAML for variant |
| `GET /api/export/linkedin` | LinkedIn-formatted sections |
| `GET /api/export/github-readme` | GitHub profile README markdown |
| `GET /api/search?q=...` | Full-text search across entities |

All entities support CRUD: `POST`, `PUT /{id}`, `DELETE /{id}`

## Data Model

Key entities (defined in `api/models.py`):

- **Profile** — Identity, contact, summaries (brief/detailed)
- **Organization** — Employer/university/lab with type
- **Position** — Role at organization, dates, employment type, achievements[]
- **Achievement** — Canonical claim with brief/detailed wording, metrics, skills
- **Project** — Research/portfolio projects
- **Education** — Degrees with coursework, thesis
- **Publication** — Papers, preprints
- **Teaching** — Courses, periods
- **Skill** — Categorized technologies
- **Variant** — CV variant definition (audience, length, template, selected positions)

Achievements are the atomic unit of reuse. A position references achievement IDs; variants select positions and choose wording level.

## Integrations

| Tool | Role | How we use it |
|------|------|---------------|
| **JSON Resume** | Interchange format | `GET /api/export/json-resume` → use with 50+ community themes, registry |
| **RenderCV** | PDF generation | `GET /api/export/rendercv/{variant}` → `rendercv render` → PDF/HTML/Typst |
| **Reactive Resume** | Web editor + job tracking | Export JSON Resume → import via their API; optional web UI for applications |
| **career-ops** | Job discovery & tailoring | Optional: feed evaluated job postings into opportunity board |
| **JobOps / Huntr** | Job boards & tracking | Optional: import vacancies, export tailored CVs |

## GitHub Pages Publishing

The dashboard generates content for two GitHub repositories:

1. **Profile README** (`AliNikkhah2001/AliNikkhah2001`)
   ```bash
   curl http://127.0.0.1:8000/api/export/github-readme | jq -r .content > README.md
   git add README.md && git commit -m "Update profile" && git push
   ```

2. **Portfolio site** (`AliNikkhah2001/alinikkhah2001.github.io`)
   - Replace hard-coded `index.md` experience/education with generated data
   - Push to `Public` branch → GitHub Actions builds Jekyll site

## Development

### Adding a new entity type
1. Add Pydantic model in `api/models.py`
2. Add CRUD endpoints in `api/main.py`
3. Add TypeScript interface in `web/src/types.ts`
4. Add API method in `web/src/api.ts`
5. Add KnowledgeBase tab in `web/src/components/KnowledgeBase.tsx`

### Switching to SQLite
The current JSON file storage is simple but not concurrent-safe. To use SQLite:

```python
# In api/main.py, replace load_db/save_db:
from sqlmodel import SQLModel, create_engine, Session, select

engine = create_engine("sqlite:///career.db")
SQLModel.metadata.create_all(engine)

def load_db():
    with Session(engine) as s:
        return s.exec(select(CareerDatabase)).first() or CareerDatabase()
```

### RenderCV PDF Generation

```bash
# Install
pip install "rendercv[full]"

# Generate PDF for a variant
cd /Users/alinikkhah/Documents/CV\ repo/AliNikkhah2001/resume
curl http://127.0.0.1:8000/api/export/rendercv/long -o rendercv/long.yaml
rendercv render rendercv/long.yaml -o rendercv_output/long
# Output: rendercv_output/long/*.pdf, *.html, *.md, *.typst
```

## Project Structure Details

```
career-dashboard/
├── api/
│   ├── main.py              # FastAPI app with all endpoints
│   └── models.py            # Pydantic models (Profile, Position, Achievement, etc.)
├── web/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.tsx           # Navigation + stats
│   │   │   ├── TimelineView.tsx      # vis-timeline visualization
│   │   │   ├── KnowledgeBase.tsx     # Searchable editable tables
│   │   │   ├── VariantComposer.tsx   # Define CV variants
│   │   │   ├── PublishingStatus.tsx  # Export status + one-click sync
│   │   │   └── LinkedInExport.tsx    # Copy-paste LinkedIn sections
│   │   ├── api.ts             # Typed fetch wrappers
│   │   ├── types.ts           # TypeScript interfaces matching Pydantic
│   │   ├── App.tsx            # Main layout with tabs
│   │   ├── main.tsx           # React entry
│   │   └── index.css          # Global styles
│   ├── package.json
│   ├── vite.config.ts         # Proxy to API on 8000
│   └── tsconfig.json
├── scripts/
│   └── import_cv.py           # cv.yaml → career_db.json
├── career_db.json             # Local database (gitignored in production)
└── README.md
```

## Extending for Job Search (Future)

The dashboard is designed to accept an **Opportunities** module:

```python
# In models.py (future)
class Opportunity(BaseModel):
    id: str
    company: str
    title: str
    url: str
    platform: str  # linkedin, indeed, greenhouse, lever, etc.
    description: str
    requirements: list[str]
    posted_date: DatePrecision
    status: Literal['new', 'evaluating', 'tailoring', 'applied', 'interview', 'offer', 'rejected']
    tailored_variant_id: Optional[str]
    tailored_cv_path: Optional[str]
```

This would live in a separate `opportunities` table, keeping career history separate from future vacancies.

## License

MIT — use freely for your own career management.