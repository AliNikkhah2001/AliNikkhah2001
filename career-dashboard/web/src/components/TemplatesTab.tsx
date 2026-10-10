import { useCallback, useEffect, useRef, useState } from 'react'
import { AtsResult, CareerDatabase, TemplateInfo } from '../types'
import { api } from '../api'

interface TemplatesTabProps {
  db: CareerDatabase | null
}

type FamilyFilter = 'all' | 'Academic themes' | 'Industrial gallery' | 'RenderCV' | 'Open-source upstream'

const FAMILY_ORDER = ['Academic themes', 'Industrial gallery', 'RenderCV', 'Open-source upstream']

function gradeColor(grade: string): string {
  if (grade === 'A') return '#198754'
  if (grade === 'B') return '#0d6efd'
  if (grade === 'C') return '#fd7e14'
  return '#dc3545'
}

export function TemplatesTab({ db }: TemplatesTabProps) {
  const [templates, setTemplates] = useState<TemplateInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<FamilyFilter>('all')
  const [compiling, setCompiling] = useState<Record<string, boolean>>({})
  const [results, setResults] = useState<Record<string, { ok: boolean; message: string }>>({})
  const [ats, setAts] = useState<Record<string, AtsResult | null>>({})
  const [atsLoading, setAtsLoading] = useState<Record<string, boolean>>({})
  const [batch, setBatch] = useState<{ running: boolean; done: number; total: number; current: string }>({
    running: false, done: 0, total: 0, current: '',
  })
  const batchRef = useRef(false)

  const refresh = useCallback(async () => {
    try {
      const list = await api.listTemplates()
      setTemplates(list)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh, db])

  const compileOne = async (id: string, force = false) => {
    setCompiling((c) => ({ ...c, [id]: true }))
    setResults((r) => ({ ...r, [id]: undefined as any }))
    try {
      const res = await api.compileTemplate(id, force)
      setResults((r) => ({
        ...r,
        [id]: { ok: true, message: `${res.pages ?? '?'} pages · ${res.duration ?? 0}s${res.cached ? ' (cached)' : ''}` },
      }))
      await refresh()
      return true
    } catch (e: any) {
      const payload = e?.payload
      const logTail = payload?.log ? String(payload.log).split('\n').slice(-6).join('\n') : ''
      setResults((r) => ({
        ...r,
        [id]: { ok: false, message: `${payload?.error || e.message}${logTail ? '\n' + logTail : ''}` },
      }))
      return false
    } finally {
      setCompiling((c) => ({ ...c, [id]: false }))
    }
  }

  const compileAll = async (force: boolean) => {
    if (batchRef.current) return
    batchRef.current = true
    const targets = templates
      .filter((t) => force || !t.compiled || t.stale)
      .map((t) => t.id)
    setBatch({ running: true, done: 0, total: targets.length, current: '' })
    let failed = 0
    for (const id of targets) {
      setBatch((b) => ({ ...b, current: id }))
      const ok = await compileOne(id, force)
      if (!ok) failed += 1
      setBatch((b) => ({ ...b, done: b.done + 1 }))
    }
    setBatch({ running: false, done: targets.length, total: targets.length, current: '' })
    batchRef.current = false
    await refresh()
    if (failed > 0) alert(`${failed} of ${targets.length} compilations failed — see card logs.`)
  }

  const loadAts = async (id: string) => {
    setAtsLoading((s) => ({ ...s, [id]: true }))
    try {
      const res = await api.getAts(id)
      setAts((s) => ({ ...s, [id]: res }))
    } catch (e: any) {
      setAts((s) => ({ ...s, [id]: null }))
      setResults((r) => ({ ...r, [id]: { ok: false, message: `ATS failed: ${e.message}` } }))
    } finally {
      setAtsLoading((s) => ({ ...s, [id]: false }))
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: '1rem' }}>CV Templates</h2>
        <p className="text-muted">Loading template registry…</p>
      </div>
    )
  }

  const families = FAMILY_ORDER.filter((f) => templates.some((t) => t.family === f))
  const visible = filter === 'all' ? templates : templates.filter((t) => t.family === filter)
  const compiledCount = templates.filter((t) => t.compiled).length
  const staleCount = templates.filter((t) => t.stale).length

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h2 style={{ margin: 0 }}>CV Templates</h2>
          <p className="text-muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
            {templates.length} engines · {compiledCount} compiled{staleCount > 0 ? ` · ${staleCount} stale` : ''} ·
            {' '}live = rendered from career_db, sample = upstream demo content
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button className="btn btn-primary btn-sm" onClick={() => compileAll(false)} disabled={batch.running}>
            {batch.running ? `Compiling ${batch.done}/${batch.total}…` : 'Compile missing / stale'}
          </button>
          <button className="btn btn-outline btn-sm" onClick={() => compileAll(true)} disabled={batch.running}>
            Force recompile all
          </button>
        </div>
      </div>

      {batch.running && (
        <div style={{ marginBottom: '0.75rem' }}>
          <div className="progress" style={{ height: 8, background: '#e9ecef', borderRadius: 4, overflow: 'hidden' }}>
            <div style={{ width: `${(batch.done / Math.max(1, batch.total)) * 100}%`, background: '#0d6efd', height: '100%', transition: 'width 0.3s' }} />
          </div>
          <div className="text-muted" style={{ fontSize: '0.75rem', marginTop: 4 }}>current: {batch.current}</div>
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        {(['all', ...families] as FamilyFilter[]).map((f) => (
          <button
            key={f}
            className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setFilter(f)}
          >
            {f === 'all' ? `All (${templates.length})` : `${f} (${templates.filter((t) => t.family === f).length})`}
          </button>
        ))}
      </div>

      {error && <div className="alerts-panel alerts-error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '0.75rem' }}>
        {visible.map((t) => {
          const res = results[t.id]
          const score = ats[t.id]
          const isCompiling = compiling[t.id]
          return (
            <div
              key={t.id}
              className="card template-card"
              style={{ borderLeft: `4px solid ${t.compiled ? (t.stale ? '#fd7e14' : '#198754') : '#6c757d'}` }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                <div>
                  <h4 style={{ margin: '0 0 0.25rem' }}>{t.name}</h4>
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    <span className="badge badge-secondary">{t.family}</span>
                    <span className="badge badge-bg">{t.engine}</span>
                    <span
                      className="badge"
                      style={t.data_source === 'live'
                        ? { background: '#d1e7dd', color: '#0f5132' }
                        : { background: '#e2e3e5', color: '#41464b' }}
                    >
                      {t.data_source}
                    </span>
                    {t.compiled && !t.stale && <span className="badge badge-success">PDF{t.pages ? ` · ${t.pages}p` : ''}</span>}
                    {t.stale && <span className="badge" style={{ background: '#fff3cd', color: '#997404' }}>stale</span>}
                    {!t.compiled && <span className="badge badge-secondary">not compiled</span>}
                  </div>
                </div>
                {score && (
                  <div style={{ textAlign: 'center', minWidth: 54 }}>
                    <div style={{ fontSize: '1.4rem', fontWeight: 700, color: gradeColor(score.grade), lineHeight: 1 }}>
                      {Math.round(score.score)}
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#6c757d' }}>ATS {score.grade}</div>
                  </div>
                )}
              </div>

              <p className="text-muted" style={{ fontSize: '0.75rem', margin: '0.5rem 0' }}>{t.description}</p>

              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                <button
                  className="btn btn-primary btn-sm"
                  disabled={isCompiling || batch.running}
                  onClick={() => compileOne(t.id, t.compiled)}
                >
                  {isCompiling ? 'Compiling…' : t.compiled ? 'Recompile' : 'Compile'}
                </button>
                {t.compiled && (
                  <a className="btn btn-outline btn-sm" href={`/api/templates/${encodeURIComponent(t.id)}/pdf`} target="_blank" rel="noopener noreferrer">
                    View PDF
                  </a>
                )}
                {t.compiled && (
                  <button
                    className="btn btn-outline btn-sm"
                    disabled={atsLoading[t.id] || isCompiling}
                    onClick={() => loadAts(t.id)}
                    title="ATS friendliness score of the compiled PDF"
                  >
                    {atsLoading[t.id] ? 'Scoring…' : score ? 'Re-score' : 'ATS score'}
                  </button>
                )}
              </div>

              {res && (
                <pre
                  className="template-log"
                  style={{
                    margin: '0.5rem 0 0',
                    padding: '0.5rem',
                    fontSize: '0.7rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    background: res.ok ? '#f6ffed' : '#fff5f5',
                    border: `1px solid ${res.ok ? '#b7eb8f' : '#ffccc7'}`,
                    borderRadius: 4,
                    maxHeight: 140,
                    overflow: 'auto',
                  }}
                >
                  {res.ok ? `✓ ${res.message}` : `✗ ${res.message}`}
                </pre>
              )}

              {score && (
                <details style={{ marginTop: '0.5rem' }}>
                  <summary style={{ fontSize: '0.78rem', cursor: 'pointer', color: '#6c757d' }}>
                    ATS breakdown ({score.issues.length} improvements)
                  </summary>
                  <ul style={{ margin: '0.4rem 0 0', paddingLeft: '1.1rem', fontSize: '0.74rem' }}>
                    {score.checks.map((c) => (
                      <li key={c.key} style={{ marginBottom: 2 }}>
                        <strong>{c.label}</strong>: {c.score}/{c.weight} — <span className="text-muted">{c.detail}</span>
                      </li>
                    ))}
                  </ul>
                  {score.issues.length > 0 && (
                    <ul style={{ margin: '0.4rem 0 0', paddingLeft: '1.1rem', fontSize: '0.74rem', color: '#997404' }}>
                      {score.issues.map((i, idx) => (
                        <li key={idx}>{i.fix}</li>
                      ))}
                    </ul>
                  )}
                </details>
              )}
            </div>
          )
        })}
      </div>

      <p className="text-muted" style={{ fontSize: '0.75rem', marginTop: '1rem' }}>
        Sources: academic themes generated from career_db (pdflatex) · industrial gallery assembled from theme-gallery
        preambles + live segments · RenderCV themes via rendercv v2.8 (typst) · upstream templates compiled with their
        own latexmk commands (sample data).
      </p>
    </div>
  )
}
