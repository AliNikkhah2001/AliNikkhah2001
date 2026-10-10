import { useEffect, useState } from 'react'
import { CareerDatabase, ValidationReport } from '../types'
import { api } from '../api'

interface AlertsPanelProps {
  db: CareerDatabase | null
}

const SEVERITY_ORDER: Record<string, number> = { error: 0, warning: 1, info: 2 }

export function AlertsPanel({ db }: AlertsPanelProps) {
  const [report, setReport] = useState<ValidationReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!db) return
    let mounted = true
    setLoading(true)
    setError(null)
    api
      .getValidation()
      .then((r) => {
        if (mounted) setReport(r)
      })
      .catch((e) => {
        if (mounted) setError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [db])

  if (error) {
    return (
      <div className="alerts-panel alerts-error" style={{ marginBottom: '0.75rem' }}>
        ⚠ Validation unavailable: {error}
      </div>
    )
  }
  if (loading && !report) {
    return (
      <div className="alerts-panel alerts-neutral" style={{ marginBottom: '0.75rem' }}>
        Checking for conflicts…
      </div>
    )
  }
  if (!report) return null

  const { counts, total } = report
  const problems = counts.error + counts.warning

  if (total === 0) {
    return (
      <div className="alerts-panel alerts-ok" style={{ marginBottom: '0.75rem' }}>
        ✓ No conflicts or ambiguities detected — all {db?.positions.length ?? 0} positions are consistent.
      </div>
    )
  }

  const sorted = [...report.issues].sort(
    (a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity]
  )

  return (
    <div className={`alerts-panel ${counts.error > 0 ? 'alerts-error' : 'alerts-warn'}`} style={{ marginBottom: '0.75rem' }}>
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer', flexWrap: 'wrap' }}
        onClick={() => setExpanded(!expanded)}
      >
        <strong>{counts.error > 0 ? '⚠' : '!'} Ambiguity alerts</strong>
        {counts.error > 0 && <span className="alert-chip alert-chip-error">{counts.error} error{counts.error !== 1 ? 's' : ''}</span>}
        {counts.warning > 0 && <span className="alert-chip alert-chip-warning">{counts.warning} warning{counts.warning !== 1 ? 's' : ''}</span>}
        <span className="alert-chip alert-chip-info">{counts.info} info</span>
        <span className="text-muted" style={{ fontSize: '0.78rem' }}>
          {problems === 0 ? 'no blocking issues — review below' : `${problems} issue${problems !== 1 ? 's' : ''} need review`}
        </span>
        <span style={{ marginLeft: 'auto', fontSize: '0.78rem' }}>{expanded ? 'Hide ▲' : 'Show ▼'}</span>
      </div>
      {expanded && (
        <ul className="alerts-list">
          {sorted.map((issue, i) => (
            <li key={i} className={`alerts-item alerts-item-${issue.severity}`}>
              <span className="alert-severity">{issue.severity}</span>
              <span className="alert-kind">{issue.kind.replace(/_/g, ' ')}</span>
              <span className="alert-message">{issue.message}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
