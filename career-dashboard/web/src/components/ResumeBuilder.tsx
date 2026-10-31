import { useEffect, useMemo, useState } from 'react'
import { CareerDatabase, DatePrecision, Position, Project, ResumeConfig, ResumeCompileResult, ResumeStyle, TemplateInfo } from '../types'
import { api } from '../api'

interface ResumeBuilderProps {
  db: CareerDatabase | null
}

const SECTION_OPTIONS = [
  { id: 'summary', label: 'Summary' },
  { id: 'skills', label: 'Skills' },
  { id: 'experience', label: 'Experience' },
  { id: 'projects', label: 'Projects' },
  { id: 'education', label: 'Education' },
  { id: 'publications', label: 'Publications' },
  { id: 'teaching', label: 'Teaching' },
] as const

const FORMAT_OPTIONS = [
  { id: '1page', label: '1 Page' },
  { id: '2page', label: '2 Pages' },
  { id: 'long', label: 'Long / Full' },
] as const

const WORDING_OPTIONS = [
  { id: 'brief', label: 'Brief' },
  { id: 'standard', label: 'Standard' },
  { id: 'detailed', label: 'Detailed' },
] as const

const DEFAULT_SECTIONS = ['summary', 'skills', 'experience', 'projects', 'education']

const MARGIN_OPTIONS = [
  { v: 0.3, label: '0.3in (tight)' },
  { v: 0.4, label: '0.4in' },
  { v: 0.5, label: '0.5in (narrow)' },
  { v: 0.6, label: '0.6in' },
  { v: 0.75, label: '0.75in' },
  { v: 1, label: '1in (roomy)' },
]
const FONT_SIZE_OPTIONS = [
  { v: 10, label: '10pt (dense)' },
  { v: 11, label: '11pt' },
  { v: 12, label: '12pt (large)' },
]
const SPACING_OPTIONS = [
  { v: 0.9, label: 'Tight (0.9)' },
  { v: 1, label: 'Normal (1.0)' },
  { v: 1.08, label: 'Roomy (1.08)' },
  { v: 1.15, label: 'Airy (1.15)' },
]

function formatDate(d: { year: number; month?: number; day?: number }): string {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return d.month ? `${months[d.month - 1]} ${d.year}` : `${d.year}`
}

function dateRange(start: DatePrecision, end?: DatePrecision, ongoing?: boolean): string {
  const from = formatDate(start)
  const to = ongoing || !end ? 'Present' : formatDate(end)
  return `${from} – ${to}`
}

function employmentLabel(t: Position['employment_type']): string {
  switch (t) {
    case 'full_time': return 'Full-time'
    case 'part_time': return 'Part-time'
    case 'contract': return 'Contract'
    case 'internship': return 'Internship'
    case 'fellowship': return 'Fellowship'
  }
}

export function ResumeBuilder({ db }: ResumeBuilderProps) {
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [name, setName] = useState('')
  const [positionIds, setPositionIds] = useState<string[]>([])
  const [projectIds, setProjectIds] = useState<string[]>([])
  const [sections, setSections] = useState<string[]>(DEFAULT_SECTIONS)
  const [format, setFormat] = useState<ResumeConfig['format']>('2page')
  const [wordingLevel, setWordingLevel] = useState<ResumeConfig['wording_level']>('standard')
  const [style, setStyle] = useState<ResumeStyle>({})
  const [excludeIncomplete, setExcludeIncomplete] = useState(true)
  const [template, setTemplate] = useState<string | null>(null)
  const [templates, setTemplates] = useState<TemplateInfo[]>([])
  const [configId, setConfigId] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [compileResult, setCompileResult] = useState<ResumeCompileResult | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [source, setSource] = useState('')

  const positions = db?.positions || []
  const projects = db?.projects || []
  const orgName = (id?: string) => db?.organizations.find((o) => o.id === id)?.name || id || ''

  useEffect(() => {
    api.listTemplates()
      .then(setTemplates)
      .catch((e) => setError(`Failed to load templates: ${e.message}`))
  }, [])

  const fullTimePositions = useMemo(() => positions.filter((p) => p.employment_type === 'full_time'), [positions])
  const partTimePositions = useMemo(() => positions.filter((p) => p.employment_type !== 'full_time'), [positions])

  const toggleId = (list: string[], id: string, setter: (v: string[]) => void) => {
    setter(list.includes(id) ? list.filter((x) => x !== id) : [...list, id])
  }

  const toggleSection = (id: string) => {
    setSections(sections.includes(id) ? sections.filter((s) => s !== id) : [...sections, id])
  }

  const setStyleKey = (key: keyof ResumeStyle, value: number | undefined) => {
    setStyle((s) => {
      const next = { ...s }
      if (value === undefined) delete next[key]
      else next[key] = value
      return next
    })
  }

  const buildConfig = (): ResumeConfig => ({
    id: configId || `resume-${Date.now().toString(36)}`,
    name: name.trim() || 'Untitled Resume',
    position_ids: positionIds,
    project_ids: projectIds,
    sections,
    template: template || templates[0]?.id || 'industrial-classic',
    format,
    wording_level: wordingLevel,
    exclude_incomplete: excludeIncomplete,
    style: Object.keys(style).length ? style : undefined,
  })

  const persist = async (cfg: ResumeConfig, verb: 'POST' | 'PUT'): Promise<ResumeConfig> => {
    if (verb === 'POST') return api.createResumeConfig(cfg)
    return api.updateResumeConfig(cfg.id, cfg)
  }

  const handleNextFromStep1 = async () => {
    if (positions.length > 0 && positionIds.length === 0) {
      setError('Select at least one position, or clear this warning by selecting data.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const cfg = buildConfig()
      const saved = await persist(cfg, configId ? 'PUT' : 'POST')
      setConfigId(saved.id)
      setStep(2)
    } catch (e: any) {
      setError(e.message || 'Failed to save config')
    } finally {
      setBusy(false)
    }
  }

  const refreshPreview = async (cfgId: string) => {
    // Compile with the saved config (positions, sections, format, wording) and
    // point the preview at THIS config's PDF — not the global template output.
    let result: ResumeCompileResult
    try {
      result = await api.compileResumeConfig(cfgId)
    } catch (e: any) {
      const payload = e?.payload
      setCompileResult(payload && typeof payload === 'object'
        ? { ok: false, error: e.message, log: payload.log }
        : null)
      setPdfUrl(null)
      setSource('')
      setError(e.message || 'Compilation failed')
      return
    }
    setCompileResult(result)
    if (result.ok) {
      setPdfUrl(api.resumeConfigPdfUrl(cfgId, Date.now()))
      setSource(await api.resumeConfigSource(cfgId).catch(() => ''))
      setNotice(`Compiled — ${result.pages ?? '?'} page(s)${result.excluded_records?.length ? `, ${result.excluded_records.length} excluded` : ''}.`)
    } else {
      setPdfUrl(null)
      setSource('')
      setError(result.error || 'Compilation failed')
    }
  }

  const handleNextFromStep2 = async () => {
    if (!template) {
      setError('Select a template first.')
      return
    }
    if (!configId) {
      setError('Config is missing — go back and try again.')
      return
    }
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await api.updateResumeConfig(configId, buildConfig())
      setStep(3)
      await refreshPreview(configId)
    } catch (e: any) {
      setError(e.message || 'Failed to save template selection')
    } finally {
      setBusy(false)
    }
  }

  const handleCompile = async () => {
    if (!configId) return
    setBusy(true)
    setError(null)
    setNotice(null)
    setCompileResult(null)
    try {
      await api.updateResumeConfig(configId, buildConfig())
      await refreshPreview(configId)
    } catch (e: any) {
      setError(e.message || 'Compilation failed')
    } finally {
      setBusy(false)
    }
  }

  const handleSave = async () => {
    if (!configId) return
    setBusy(true)
    setError(null)
    try {
      await api.updateResumeConfig(configId, buildConfig())
      setNotice('Resume config saved.')
    } catch (e: any) {
      setError(e.message || 'Save failed')
    } finally {
      setBusy(false)
    }
  }

  const renderPositionGroup = (label: string, items: Position[]) => (
    <div className="mb-3">
      <div className="nav-section-title">{label} ({items.length})</div>
      <div className="rb-scrollbox">
        {items.length === 0 && <p className="text-muted" style={{ fontSize: '0.8rem', margin: 0 }}>None</p>}
        {items.map((pos) => (
          <label key={pos.id} className="check-row">
            <input
              type="checkbox"
              checked={positionIds.includes(pos.id)}
              onChange={() => toggleId(positionIds, pos.id, setPositionIds)}
            />
            <span style={{ flex: 1 }}>
              <strong>{pos.title}</strong> · {orgName(pos.organization_id)}
              <br />
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                {dateRange(pos.start, pos.end, pos.ongoing)} · {employmentLabel(pos.employment_type)}
              </span>
            </span>
          </label>
        ))}
      </div>
    </div>
  )

  return (
    <div className="card">
      <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
        <h2 style={{ margin: 0 }}>Resume Builder</h2>
        <div className="d-flex gap-2 align-items-center">
          <input
            className="form-control"
            style={{ width: 260 }}
            placeholder="Config name (e.g. ML Engineer @ Acme)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <span className="badge badge-secondary">Step {step} of 3</span>
        </div>
      </div>

      <div className="rb-steps mb-3">
        {['Data Selection', 'Template', 'Preview & Compile'].map((label, i) => (
          <div key={label} className={`rb-step ${step === i + 1 ? 'active' : ''} ${step > i + 1 ? 'done' : ''}`}>
            <span className="rb-step-num">{i + 1}</span> {label}
          </div>
        ))}
      </div>

      {error && <div className="alerts-panel alerts-error">{error}</div>}
      {notice && <div className="alerts-panel alerts-ok">{notice}</div>}

      {step === 1 && (
        <div className="rb-split">
          <div className="rb-pane">
            <h4>Positions ({positionIds.length} selected)</h4>
            {renderPositionGroup('Full-time', fullTimePositions)}
            {renderPositionGroup('Part-time / Other', partTimePositions)}

            <h4>Projects ({projectIds.length} selected)</h4>
            <div className="rb-scrollbox">
              {projects.length === 0 && <p className="text-muted" style={{ fontSize: '0.8rem', margin: 0 }}>No projects</p>}
              {projects.map((proj: Project) => (
                <label key={proj.id} className="check-row">
                  <input
                    type="checkbox"
                    checked={projectIds.includes(proj.id)}
                    onChange={() => toggleId(projectIds, proj.id, setProjectIds)}
                  />
                  <span style={{ flex: 1 }}>
                    <strong>{proj.title}</strong>
                    <br />
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                      {dateRange(proj.start, proj.end, proj.ongoing)}
                    </span>
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="rb-pane">
            <h4>Sections</h4>
            {SECTION_OPTIONS.map((s) => (
              <label key={s.id} className="check-row">
                <input type="checkbox" checked={sections.includes(s.id)} onChange={() => toggleSection(s.id)} />
                {s.label}
              </label>
            ))}

            <h4>Format</h4>
            <div className="d-flex gap-2 mb-3">
              {FORMAT_OPTIONS.map((f) => (
                <button
                  key={f.id}
                  className={`btn btn-sm ${format === f.id ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setFormat(f.id)}
                >
                  {f.label}
                </button>
              ))}
            </div>

            <h4>Wording Level</h4>
            <div className="d-flex gap-2 mb-3">
              {WORDING_OPTIONS.map((w) => (
                <button
                  key={w.id}
                  className={`btn btn-sm ${wordingLevel === w.id ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setWordingLevel(w.id)}
                >
                  {w.label}
                </button>
              ))}
            </div>

            <h4>Appearance</h4>
            <div className="mb-3" style={{ display: 'grid', gap: 8 }}>
              <label style={{ fontSize: '0.8rem' }}>
                <span className="text-muted">Margins</span>
                <select
                  className="form-control"
                  style={{ marginTop: 2 }}
                  value={style.margin ?? ''}
                  onChange={(e) => setStyleKey('margin', e.target.value === '' ? undefined : Number(e.target.value))}
                >
                  <option value="">Template default</option>
                  {MARGIN_OPTIONS.map((o) => <option key={o.v} value={o.v}>{o.label}</option>)}
                </select>
              </label>
              <label style={{ fontSize: '0.8rem' }}>
                <span className="text-muted">Font size</span>
                <select
                  className="form-control"
                  style={{ marginTop: 2 }}
                  value={style.font_size ?? ''}
                  onChange={(e) => setStyleKey('font_size', e.target.value === '' ? undefined : Number(e.target.value))}
                >
                  <option value="">Template default</option>
                  {FONT_SIZE_OPTIONS.map((o) => <option key={o.v} value={o.v}>{o.label}</option>)}
                </select>
              </label>
              <label style={{ fontSize: '0.8rem' }}>
                <span className="text-muted">Line spacing</span>
                <select
                  className="form-control"
                  style={{ marginTop: 2 }}
                  value={style.line_spacing ?? ''}
                  onChange={(e) => setStyleKey('line_spacing', e.target.value === '' ? undefined : Number(e.target.value))}
                >
                  <option value="">Template default</option>
                  {SPACING_OPTIONS.map((o) => <option key={o.v} value={o.v}>{o.label}</option>)}
                </select>
              </label>
            </div>

            <label className="check-row">
              <input type="checkbox" checked={excludeIncomplete} onChange={(e) => setExcludeIncomplete(e.target.checked)} />
              Exclude incomplete records
            </label>

            <div className="d-flex justify-content-end mt-3">
              <button className="btn btn-primary" onClick={handleNextFromStep1} disabled={busy}>
                {busy ? 'Saving…' : 'Next: Choose Template →'}
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <div className="stack-grid">
            {templates.map((t) => (
              <div key={t.id} className={`card template-card ${template === t.id ? 'rb-selected' : ''}`}>
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <strong>{t.name}</strong>
                  <span className="badge badge-bg">{t.family}</span>
                </div>
                <div className="text-muted" style={{ fontSize: '0.8rem' }}>
                  {t.pages != null ? `${t.pages} page(s)` : 'pages unknown'} · {t.engine}
                </div>
                {t.description && <div style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>{t.description}</div>}
                <div className="mt-2">
                  <button
                    className={`btn btn-sm ${template === t.id ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => setTemplate(t.id)}
                  >
                    {template === t.id ? 'Selected' : 'Select'}
                  </button>
                </div>
              </div>
            ))}
            {templates.length === 0 && <p className="text-muted">No templates available.</p>}
          </div>
          <div className="d-flex justify-content-between mt-3">
            <button className="btn btn-outline" onClick={() => setStep(1)} disabled={busy}>← Back</button>
            <button className="btn btn-primary" onClick={handleNextFromStep2} disabled={busy}>
              {busy ? 'Saving…' : 'Next: Preview & Compile →'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <div className="rb-split">
            <div className="rb-pane">
              <h4>PDF Preview {template && <span className="text-muted" style={{ fontWeight: 400, fontSize: '0.8rem' }}>({template})</span>}</h4>
              {pdfUrl ? (
                <iframe title="Resume PDF preview" src={pdfUrl} className="rb-pdf" />
              ) : (
                <div className="rb-pdf rb-pdf-empty">
                  {busy ? 'Compiling preview…' : 'Click "Compile" to generate the PDF preview.'}
                </div>
              )}
              {compileResult && (
                <div className={`alerts-panel mt-2 ${compileResult.ok ? 'alerts-ok' : 'alerts-error'}`} style={{ marginBottom: 0 }}>
                  {compileResult.ok
                    ? `OK — ${compileResult.pages ?? '?'} page(s)${compileResult.excluded_records?.length ? ` · excluded: ${compileResult.excluded_records.join(', ')}` : ''}`
                    : compileResult.error || 'Compilation failed'}
                </div>
              )}
            </div>

            <div className="rb-pane">
              <h4>{template?.startsWith('rendercv-') ? 'YAML Source' : 'LaTeX Source'}</h4>
              <textarea
                className="form-control rb-tex"
                readOnly
                placeholder="Source appears here after compiling"
                value={source}
              />
              <div className="d-flex gap-2 mt-3 flex-wrap">
                <button className="btn btn-primary" onClick={handleCompile} disabled={busy}>
                  {busy ? 'Compiling…' : 'Compile'}
                </button>
                <button className="btn btn-outline" onClick={handleSave} disabled={busy || !configId}>Save</button>
                <a
                  className="btn btn-outline"
                  href={pdfUrl || '#'}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open PDF
                </a>
              </div>
            </div>
          </div>
          <div className="d-flex justify-content-between mt-3">
            <button className="btn btn-outline" onClick={() => setStep(2)} disabled={busy}>← Back to Templates</button>
            <button className="btn btn-outline" onClick={() => setStep(1)} disabled={busy}>← Back to Data</button>
          </div>
        </div>
      )}
    </div>
  )
}
