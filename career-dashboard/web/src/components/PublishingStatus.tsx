import { useCallback, useEffect, useState } from 'react'
import { CareerDatabase, PublishingAudit } from '../types'
import { api } from '../api'

interface PublishingStatusProps {
  db: CareerDatabase | null
}

const STATUS_META: Record<string, { color: string; bg: string; label: string }> = {
  synced: { color: '#0f5132', bg: '#d1e7dd', label: 'in sync' },
  ready: { color: '#084298', bg: '#cfe2ff', label: 'ready' },
  stale: { color: '#997404', bg: '#fff3cd', label: 'stale' },
  missing: { color: '#58151c', bg: '#f8d7da', label: 'missing' },
  error: { color: '#58151c', bg: '#f8d7da', label: 'error' },
  external: { color: '#41464b', bg: '#e2e3e5', label: 'external' },
}

interface AdapterDef {
  id: string
  name: string
  what: string
  consumes: string
  url?: string
  endpoint?: string
  filename?: string
}

const ADAPTERS: AdapterDef[] = [
  {
    id: 'json-resume',
    name: 'JSON Resume',
    what: 'Community schema — themes, generators, online editors.',
    consumes: 'GET /api/export/json-resume',
    endpoint: '/api/export/json-resume',
    filename: 'resume.json',
    url: 'https://jsonresume.org',
  },
  {
    id: 'rendercv',
    name: 'RenderCV',
    what: 'Reproducible typst PDFs — 5 themes compiled live from career_db on the Templates tab.',
    consumes: 'engine integrated + GET /api/export/rendercv/{variant}',
    endpoint: '/api/export/rendercv/long',
    filename: 'rendercv_long.yaml',
    url: 'https://rendercv.com',
  },
  {
    id: 'reactive-resume',
    name: 'Reactive Resume',
    what: 'Open-source resume builder — import the JSON directly (Import → JSON).',
    consumes: 'GET /api/export/reactive-resume',
    endpoint: '/api/export/reactive-resume',
    filename: 'reactive-resume.json',
    url: 'https://rxresu.me',
  },
  {
    id: 'jobops',
    name: 'JobOps / Huntr',
    what: 'Job-application trackers — one CSV row per position (status, dates, tech, notes).',
    consumes: 'GET /api/export/jobops',
    endpoint: '/api/export/jobops',
    filename: 'jobops-applications.csv',
  },
  {
    id: 'career-ops',
    name: 'career-ops',
    what: 'Repo-style career data workflows — consumes the JSON Resume subset we export.',
    consumes: 'GET /api/export/json-resume (subset)',
    endpoint: '/api/export/json-resume',
    filename: 'career-ops-resume.json',
  },
  {
    id: 'github-readme',
    name: 'GitHub profile README',
    what: 'Generated markdown for AliNikkhah2001/AliNikkhah2001 (audited above).',
    consumes: 'GET /api/export/github-readme',
    endpoint: '/api/export/github-readme',
    filename: 'README.md',
    url: 'https://github.com/AliNikkhah2001/AliNikkhah2001',
  },
]

export function PublishingStatus({ db }: PublishingStatusProps) {
  const [audit, setAudit] = useState<PublishingAudit | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [exporting, setExporting] = useState<string | null>(null)
  const [note, setNote] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const a = await api.getPublishingAudit()
      setAudit(a)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh, db])

  const download = async (adapter: AdapterDef) => {
    setExporting(adapter.id)
    setNote(null)
    try {
      const res = await fetch(`/api${adapter.endpoint!.split('/api')[1]}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const isYaml = adapter.filename?.endsWith('.yaml')
      const isMd = adapter.filename?.endsWith('.md')
      const text = isYaml
        ? await res.text()
        : isMd
          ? ((await res.json()).content ?? '')
          : JSON.stringify(await res.json(), null, 2)
      const blob = new Blob([text], { type: isYaml ? 'text/yaml;charset=utf-8' : 'text/plain;charset=utf-8' })
      const href = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = href
      a.download = adapter.filename || `${adapter.id}.json`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(href)
      setNote(`Downloaded ${adapter.filename}`)
    } catch (e) {
      setNote(`Export failed: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setExporting(null)
    }
  }

  const downloadJobOps = async () => {
    setExporting('jobops')
    try {
      const content = await api.exportJobOps()
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8' })
      const href = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = href
      a.download = 'jobops-applications.csv'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(href)
      setNote('Downloaded jobops-applications.csv')
    } catch (e) {
      setNote(`Export failed: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h2 style={{ margin: 0 }}>Publishing Status</h2>
          <p className="text-muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
            Live audit of every publishing module — read-only, sync actions are dry-run only.
            {audit && <> · db <code>{audit.db_fingerprint}</code></>}
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={refresh} disabled={loading}>
          {loading ? 'Auditing…' : 'Re-audit'}
        </button>
      </div>

      {error && <div className="alerts-panel alerts-error">{error}</div>}
      {note && <div className="alerts-panel alerts-neutral" style={{ marginBottom: '0.75rem' }}>{note}</div>}

      {loading && !audit && <p className="text-muted">Running audit…</p>}

      {audit && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '0.75rem' }}>
            {audit.modules.map((m) => {
              const meta = STATUS_META[m.status] ?? STATUS_META.external
              return (
                <div key={m.id} className="card" style={{ borderLeft: `4px solid ${meta.bg}`, padding: '0.9rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                    <div>
                      <h4 style={{ margin: '0 0 0.25rem' }}>{m.name}</h4>
                      <span className="badge badge-secondary">{m.kind}</span>
                    </div>
                    <span className="badge" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span>
                  </div>
                  <p className="text-muted" style={{ fontSize: '0.78rem', margin: '0.5rem 0' }}>{m.detail}</p>
                  {m.last_sync && (
                    <p className="text-muted" style={{ fontSize: '0.72rem', margin: '0 0 0.5rem' }}>
                      last file change: {new Date(m.last_sync).toLocaleString()}
                    </p>
                  )}
                  {m.actions.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      {m.actions.map((a) => (
                        <code key={a} style={{ fontSize: '0.68rem', background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: 4, padding: '2px 6px' }}>
                          {a}
                        </code>
                      ))}
                    </div>
                  )}
                  {m.url && (
                    <a href={m.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.75rem' }}>
                      open ↗
                    </a>
                  )}
                </div>
              )
            })}
          </div>

          <details style={{ marginTop: '1rem' }}>
            <summary style={{ cursor: 'pointer', fontSize: '0.85rem' }}>Dry-run sync plan ({audit.dry_run.length} lines)</summary>
            <pre style={{ background: '#f8f9fa', padding: '0.75rem', borderRadius: 6, overflow: 'auto', fontSize: '0.75rem' }}>
{audit.dry_run.join('\n')}
            </pre>
          </details>
        </>
      )}

      <hr style={{ margin: '2rem 0' }} />

      <h3>Format adapters — one database, every tool</h3>
      <p className="text-muted" style={{ fontSize: '0.85rem' }}>
        Discovered OSS tools consume our exports instead of maintaining duplicate documents.
        Download a fresh export any time — everything derives from career_db.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '0.75rem' }}>
        {ADAPTERS.map((adapter) => (
          <div key={adapter.id} className="card" style={{ padding: '0.9rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4 style={{ margin: 0 }}>{adapter.name}</h4>
              {adapter.url && (
                <a href={adapter.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.75rem' }}>site ↗</a>
              )}
            </div>
            <p className="text-muted" style={{ fontSize: '0.78rem', margin: '0.4rem 0' }}>{adapter.what}</p>
            <code style={{ fontSize: '0.7rem', display: 'block', marginBottom: '0.5rem' }}>{adapter.consumes}</code>
            <button
              className="btn btn-outline btn-sm"
              disabled={exporting === adapter.id}
              onClick={() => (adapter.id === 'jobops' ? downloadJobOps() : download(adapter))}
            >
              {exporting === adapter.id ? 'Exporting…' : `Download ${adapter.filename}`}
            </button>
          </div>
        ))}
      </div>

      <hr style={{ margin: '2rem 0' }} />

      <h3>Export Commands</h3>
      <p className="text-muted">Run these from the project root:</p>
      <pre style={{ background: '#f8f9fa', padding: '1rem', borderRadius: 6, overflow: 'auto' }}>
{`# Profile README check (no write)
python3 resume/scripts/generate_profile_readme.py --check

# Structured exports
curl http://127.0.0.1:8000/api/export/json-resume > resume.json
curl http://127.0.0.1:8000/api/export/reactive-resume > reactive-resume.json
curl http://127.0.0.1:8000/api/export/jobops > jobops.csv
curl http://127.0.0.1:8000/api/export/rendercv/long > rendercv_long.yaml

# Compile every CV template + ATS score (Templates tab, or)
curl -X POST http://127.0.0.1:8000/api/templates/academic-01_classic/compile
curl http://127.0.0.1:8000/api/ats/academic-01_classic`}
      </pre>
    </div>
  )
}
