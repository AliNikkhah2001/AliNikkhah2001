# Career knowledge base and publishing pipeline

Research date: **5 October 2026**. This is a research/design document, not an
implemented dashboard or a connected publishing service.

## Recommendation

Build a small, purpose-specific **career database, timeline editor, variant
composer, and publishing coordinator**. Reuse RenderCV/LaTeX for documents and
JSON Resume for interoperability. Reactive Resume is the closest ready-made
application and a useful optional integration; it is not necessary to fork it.

The reviewed products cover substantial parts of the workflow. I did not find
a verified, drop-in solution combining shared career facts, independently
selectable brief/detailed descriptions, a career-history timeline, academic
LaTeX variants, and synchronized GitHub profile/Pages/LinkedIn profile editing.
That is a scoped finding from the products below, not a claim that no such
software exists anywhere.

The architectural rule is: **edit facts once; generate audience-specific views**.
A saved CV variant references career entries and achievements instead of copying
their dates, employers, and factual claims into a new editable document.

## 1. Existing tools

| Tool | Verified capabilities | Fit and missing pieces for this project |
|---|---|---|
| [Reactive Resume](https://github.com/reactive-resume/reactive-resume) | Self-hosted web editor, structured dates, multiple roles at a company, item visibility, public links, document versions, PDF/DOCX/Markdown/JSON exports, REST and MCP APIs, job applications and calendar | Closest complete product. Its job-tailoring flow makes an independent resume copy; its database stores each resume as a JSON document. Shared career-entry propagation, our academic LaTeX library, and GitHub/LinkedIn profile publishers would need additional integration. |
| [JSON Resume](https://github.com/jsonresume/jsonresume.org) | Open resume schema, validation, CLI, hosted registry, HTML themes, job-search tooling | Good interchange format. The core schema has work/projects/education and string highlights, but no standardized shared achievement IDs, brief/detailed variants, publishing state, or career-timeline editor. Extensions are allowed; other clients may drop them. |
| [RenderCV](https://github.com/rendercv/rendercv) | Validated YAML, reproducible typeset PDFs, customizable themes, localization | Strong document engine already present in this repo. Not the career database/editor or multi-platform publishing coordinator. Current RenderCV uses Typst; existing LaTeX templates require their own adapters. |
| [career-ops](https://github.com/career-ops-hq/career-ops) | Local-first job discovery, company/portal configuration, evaluation, application tracking, CV tailoring, LaTeX export, story bank, terminal dashboard and experimental web UI | Useful if the knowledge base includes future vacancies and hiring platforms. Its master-profile implementation explicitly covers schema/import/confirmation/validation only; the reviewed documentation says fact selection and PDF integration are not connected yet. It does not document our complete publishing workflow. |
| [JobOps](https://github.com/DaKheera47/job-ops) | Self-hosted job-board search, fit scoring, CV tailoring, local/Reactive Resume PDF export, application tracking, Gmail integration | Useful vacancy-ingestion/application subsystem. Not a shared career-content publishing system. License states AGPLv3 **plus Commons Clause**, so do not describe it as plain AGPL or MIT. |
| [Huntr](https://huntr.co/) | Hosted job/contact/interview tracking, tailored resumes, browser job clipper, PDF exports | Useful managed job-search workflow. The reviewed product pages do not establish a supported shared-facts API and GitHub/Pages/LinkedIn profile synchronization contract. |
| [Parametric Resume Builder](https://github.com/ConstanzaSchibber/parametric-resume-builder) | Role-focused LaTeX variants, selectable wording, local HTML configurator, application build log | Close to the selection concept. The configurator approximates LaTeX and generates compile commands; documentation asks users to mirror content into HTML, so it does not solve database editing or all-output synchronization. |

Teal's official builder/tracker pages returned HTTP 403 during this research, so
they are not used as verified evidence in the recommendation. Browser navigation
also failed in this session; findings come from official documentation, GitHub
release metadata, source files, and the publicly readable Huntr product page.
No hosted application was signed into or tested end-to-end.

### Reactive Resume version detail

GitHub reports **v6.0.0**, published **4 October 2026**, as a non-prerelease.
The default-branch README still describes v6 as upcoming; use the published tag
and that instance's OpenAPI specification when implementing an adapter.

The v6.0.0 schema supports nested roles, structured dates, and hidden items. Its
`resume` table contains an independent `data` JSONB document per resume. The
documented “Copy for a job” flow leaves the original unchanged. This establishes
the distinction between document versioning/copying and shared-fact propagation.

## 2. What synchronization can actually do

| Destination | Supported approach | Meaning of success |
|---|---|---|
| GitHub profile README | Generate Markdown and commit managed content through Git/GitHub API | Target branch contains the content generated from the intended source revision |
| GitHub Pages portfolio | Export public career data + documents; update the website repo; run its Pages workflow | Website deployment for that revision succeeds, not merely a successful Git push |
| PDF/LaTeX/RenderCV variants | Build from one versioned source snapshot and variant definitions | Artifact exists, compiler succeeded, content matches the snapshot, page checks passed |
| LinkedIn profile | Generate headline/about/experience/education text and a per-field update checklist; import the user's export for comparison when available | Distinguish “prepared” from “manually applied”; record the last confirmed revision |
| Job-search services | Optional import/export or documented API adapters | Imported records retain source IDs/URLs; exported documents retain their revision |

### LinkedIn limitation

LinkedIn's documented open permissions provide sign-in/profile information and
social posting. `w_member_social` publishes social content; it is **not** a
permission to edit the profile's Experience, Education or About fields.
The documented Profile API is restricted and describes profile retrieval.

There is no generally available profile-write permission established by these
sources. Therefore a normal personal developer app cannot honestly promise
fully automatic LinkedIn profile synchronization. A robust initial connector
prepares exact updates, tracks what was applied, and keeps the status visible.
An attended browser-editing integration would be a separate capability requiring
its own feasibility test, rather than a promised permanent unattended API.

### One source, asynchronous destinations

“Always updated” should mean automatic propagation of edits to supported outputs
while the service is running, with observable lag/failure. It cannot mean that
several independent services change atomically or remain reachable forever.

Use one database transaction/revision per edit, an outbox of publishing work,
and per-destination status: pending, building, published, failed, manual-action,
or conflict. Track intended revision, delivered revision, artifact hash, remote
commit/deployment ID, last attempt and last error. Retry safe/idempotent writes;
read back remote state before retrying an uncertain create operation.

The same facts should appear everywhere, but text length and emphasis can differ.
Previously submitted application PDFs stay frozen as historical records.

## 3. Existing workspace audit

### Reusable foundations

- `resume/data/cv.yaml`: 14 experience records, 2 education records, 3 research
  projects, a publication entry, teaching history, skills and 9 variant tags.
- `resume/scripts/build_tagged.py`: basic tag selection and generated fragments.
- `resume/scripts/generate_profile_readme.py`: profile Markdown projection.
- `resume/scripts/cv_to_rendercv.py`: an existing RenderCV export path.
- Academic/industrial LaTeX sources and the added template library.
- `archive/local-versions/`: original wording and conflicts with path provenance.

### Gaps to resolve during migration

- Variant tags select entire roles; individual bullets lack stable IDs and
  per-variant wording/visibility/order/length settings.
- Brief and detailed descriptions are not modeled as views of a shared fact.
- Education/contact data still appear in manually maintained LaTeX fragments.
- Every generated variant gets the same general summary/skills and all research
  projects rather than consistently applying audience-level selection.
- Page counts are intentions; the current generator does not enforce them.
- Some links in `concurrent_with` refer to missing IDs, including `trinity` and
  `l3s_tail`. Preserve and flag these during import rather than inventing records.
- The portfolio is a **separate repository**:
  `AliNikkhah2001/alinikkhah2001.github.io`, default branch **`Public`**.
  Its `index.md` loops over hard-coded `page.experience` and `page.education`.
  Copying `_data/cv_generated.yaml` alone will not update that homepage.
- The profile repo and portfolio repo need explicit cross-repository publishing
  credentials and a clear owner for each generated field/file.
- Current CI is not uniformly healthy: the latest main CV build succeeded, but
  the new gallery's Linux build failed for Simple-CV and Prometheus, despite all
  ten local MacTeX builds passing. Pages deployment failures are also present.
  Reproducible build environments and deployment status belong in the new system.

## 4. Proposed data model

Use a relational database with explicit IDs and searchable text. A vector
database or graph database is not required for the initial size of this corpus.

| Entity | Contents |
|---|---|
| Profile | Identity, contact fields, bios/headlines, links, language preferences |
| Organization | Employer/university/lab, canonical name and aliases, URLs |
| Position | Organization ID, actual title, start/end with date precision, ongoing flag, employment type, remote/location fields, related role/promotion IDs |
| Achievement | Position/project ID, canonical claim, structured metrics where useful, evidence/source references, skill tags |
| Wording | Achievement ID, language, brief/standard/detailed text, optional audience emphasis and source revision |
| Project/publication/education/teaching | Typed records with dates and explicit links to positions and organizations |
| Skill or technology platform | Canonical term, aliases, category, related achievements; distinguish tools such as Kubernetes from publishing platforms |
| Variant | Audience, length target, selected entity/bullet IDs, order, wording choice, template, sections, included fields |
| Destination | GitHub README, Pages, LinkedIn, PDF downloads; field mappings and last delivered revision |
| Source/revision | Original imported record/path, change history, immutable snapshots |
| Opportunity (optional) | Future vacancy, company, posting URL/text snapshot, source platform, requirements, dates and application stage |
| Application (optional) | Opportunity ID, events/notes, exact artifact/revision submitted |

“Positions” can mean roles already held or future vacancies; keep these as
separate types. Likewise, hiring platforms, technology platforms, and publishing
destinations should not share one ambiguous table.

### Selection example

```yaml
id: research-brief
audience: academic
length: brief
page_target: 2
template: academic-minimal
sections: [education, research, publications, selected_industry, skills]
positions:
  - id: ubc
    wording: brief
    achievements: [ubc-model-design, ubc-evaluation]
  - id: l3s
    wording: brief
    achievements: [l3s-motion-pipeline]
```

The example achievement IDs illustrate the proposed schema; they are not
existing records or newly asserted accomplishments. Different variants select
different references, not copied versions of the same employer/date/metric.
Dates and shared structured metrics always come from their canonical records.
If free-text wording depends on a changed fact, mark that wording stale rather
than silently claiming it has also been updated.

## 5. Dashboard

1. **Career timeline:** separate lanes for employment, research, education,
   teaching and projects; concurrent roles remain visible; clicking opens the
   record editor. Date-only/year-only precision remains explicit.
2. **Knowledge base:** searchable entries, reusable achievements, brief/detailed
   wording, linked skills and original-source references.
3. **Variant composer:** choose a target, select roles and bullets, switch
   brief/standard/detailed wording, reorder, choose a template, inspect the real
   compiled PDF and page count.
4. **Publishing status:** destination, latest intended/delivered revision,
   pending changes, errors, last successful deployment and LinkedIn copy blocks.
5. **Opportunities:** optional vacancy list/board and source-platform catalog,
   separate from the career-history timeline.

## 6. Implementation boundary

Recommended first deployment: **local-first, single-user**.

- **UI:** React/TypeScript, with an existing timeline component such as
  vis-timeline (component choice still needs a compatibility/accessibility check).
- **API/import/export:** FastAPI + Pydantic, reusing the Python generators.
- **Database:** SQLite with migrations and transactional edits; durable local
  storage plus portable versioned JSON/YAML export. Database is authoritative;
  exports are snapshots, not a second writable master.
- **Document engines:** one pinned RenderCV version plus one adapted LaTeX
  academic template first. Expand template adapters after the data contract works.
- **Publishing:** a background worker using GitHub APIs and a pinned CI toolchain.
  Private application notes/source evidence remain in the private database;
  public exports contain explicitly selected fields.
- **Optional integrations:** JSON Resume export and Reactive Resume import/export;
  job discovery from career-ops/JobOps later if needed.

GitHub Pages can host the public portfolio and PDFs. It is static hosting, not
the database/API. For editing from several devices and background publishing
without the laptop running, deploy the same dashboard/API on a server with
persistent storage and authentication; do not put write credentials in a Pages
JavaScript bundle.

## 7. Delivery sequence and acceptance criteria

### A. Canonical data and compatibility

- Import existing YAML and variant tags with IDs preserved.
- Preserve alternate local claims as source records; report unresolved references.
- Add stable achievement IDs and explicit wording/variant selections.
- Produce JSON Resume and existing CV-format exports from a single revision.
- Verify no source records disappear and every exported item can be traced back.

### B. Editable timeline and real document preview

- Create/edit a role and its brief/detailed wording in the browser.
- Change a date once and observe it in the timeline and every selected variant.
- Select individual bullets and compare a brief CV with a full record.
- Render a real PDF; fail the named page-limit check if it overflows.

### C. Publishing coordinator

- A saved edit queues versioned outputs for GitHub README and the Pages repo.
- Switch the portfolio's career sections to generated data.
- Display build/deployment failures and retain the last known good publication.
- Generate LinkedIn-ready text and track manual application separately.
- Verify the same source revision is represented in every automatically
  published destination; retain older application artifact snapshots.

### D. Optional opportunity knowledge base

- Save vacancies/platforms, snapshot descriptions, link requirements to evidence.
- Compose a role-specific variant from existing career facts.
- Record exactly which revision/PDF was used in each application.

## Sources and version evidence

1. [Reactive Resume v6.0.0 release](https://github.com/reactive-resume/reactive-resume/releases/tag/v6.0.0), commit `bc71f636c02a80ac6d731e17d2ee13501275295c`.
2. [Reactive Resume API guide at v6.0.0](https://github.com/reactive-resume/reactive-resume/blob/v6.0.0/docs/guides/using-the-api.mdx).
3. [Reactive Resume tailoring guide](https://github.com/reactive-resume/reactive-resume/blob/v6.0.0/docs/guides/tailoring-a-resume-for-a-job.mdx) and [database schema](https://github.com/reactive-resume/reactive-resume/blob/v6.0.0/packages/db/src/schema/resume.ts).
4. [JSON Resume schema](https://github.com/jsonresume/jsonresume.org/blob/dd0155358c8d85a134d434e49834705243b5eede/packages/schema/schema.json) and [monorepo](https://github.com/jsonresume/jsonresume.org).
5. [RenderCV](https://github.com/rendercv/rendercv) and [v2.8 release](https://github.com/rendercv/rendercv/releases/tag/v2.8).
6. [career-ops](https://github.com/career-ops-hq/career-ops/tree/b866e4b4be1223b27d078facacce7f073e90c31b) and [master-profile scope](https://github.com/career-ops-hq/career-ops/blob/b866e4b4be1223b27d078facacce7f073e90c31b/modes/master-profile.md).
7. [JobOps](https://github.com/DaKheera47/job-ops/tree/c28b90a5fba75f298cb1d6a49460ddf009808715).
8. [Huntr product site](https://huntr.co/).
9. [Parametric Resume Builder](https://github.com/ConstanzaSchibber/parametric-resume-builder).
10. [LinkedIn API access and open permissions](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access).
11. [LinkedIn Profile API](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api).
12. [GitHub repository contents API](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents).
13. [GitHub Pages hosting model](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages).
14. [Current portfolio homepage source](https://github.com/AliNikkhah2001/alinikkhah2001.github.io/blob/Public/index.md) and [deployment workflow](https://github.com/AliNikkhah2001/alinikkhah2001.github.io/blob/Public/.github/workflows/pages.yml).
15. [Gallery CI run inspected](https://github.com/AliNikkhah2001/AliNikkhah2001/actions/runs/37277763049).
