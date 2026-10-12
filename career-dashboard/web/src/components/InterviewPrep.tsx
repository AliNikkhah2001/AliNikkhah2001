import { useCallback, useEffect, useState } from 'react'
import { CareerDatabase, InterviewQuestion, InterviewStatus } from '../types'
import { api } from '../api'

interface InterviewPrepProps {
  db: CareerDatabase | null
}

type CategoryFilter = 'all' | 'deep_dive' | 'project' | 'behavioral' | 'fundamentals'

const CATEGORIES: { id: CategoryFilter; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'deep_dive', label: 'Deep Dive' },
  { id: 'project', label: 'Project' },
  { id: 'behavioral', label: 'Behavioral' },
  { id: 'fundamentals', label: 'Fundamentals' },
]

const STATUSES: { id: InterviewStatus; label: string }[] = [
  { id: 'unprepared', label: 'Unprepared' },
  { id: 'drafted', label: 'Drafted' },
  { id: 'confident', label: 'Confident' },
]

function statusBadge(status: InterviewStatus): string {
  if (status === 'confident') return 'badge badge-success'
  if (status === 'drafted') return 'badge badge-warning'
  return 'badge badge-secondary'
}

export function InterviewPrep({ db }: InterviewPrepProps) {
  const [questions, setQuestions] = useState<InterviewQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [category, setCategory] = useState<CategoryFilter>('all')
  const [positionId, setPositionId] = useState('all')
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState<Record<string, boolean>>({})
  const [savedId, setSavedId] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<Record<string, string | undefined>>({})

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.listInterviewQuestions({
        position_id: positionId === 'all' ? undefined : positionId,
        category: category === 'all' ? undefined : category,
      })
      const list = res?.questions ?? []
      setQuestions(list)
      const next: Record<string, string> = {}
      for (const q of list) next[q.id] = q.answer ?? ''
      setDrafts(next)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }, [category, positionId])

  useEffect(() => {
    load()
  }, [load])

  const save = async (q: InterviewQuestion, status: InterviewStatus, answer: string) => {
    setSaving((s) => ({ ...s, [q.id]: true }))
    setSaveError((s) => ({ ...s, [q.id]: undefined }))
    setQuestions((qs) => qs.map((x) => (x.id === q.id ? { ...x, status, answer } : x)))
    try {
      const updated = await api.saveInterviewAnswer(q.id, { status, answer })
      if (updated && typeof updated === 'object' && 'id' in updated) {
        setQuestions((qs) => qs.map((x) => (x.id === q.id ? { ...x, ...updated } : x)))
      }
      setSavedId(q.id)
      window.setTimeout(() => setSavedId((s) => (s === q.id ? null : s)), 1500)
    } catch (e) {
      setSaveError((s) => ({ ...s, [q.id]: e instanceof Error ? e.message : String(e) }))
    } finally {
      setSaving((s) => ({ ...s, [q.id]: false }))
    }
  }

  const positions = db?.positions ?? []
  const confident = questions.filter((q) => q.status === 'confident').length
  const drafted = questions.filter((q) => q.status === 'drafted').length
  const unprepared = questions.filter((q) => q.status === 'unprepared').length

  return (
    <div className="card">
      <h2 style={{ marginTop: 0 }}>Interview Prep</h2>
      <p className="text-muted" style={{ margin: '0 0 0.75rem', fontSize: '0.85rem' }}>
        Practice questions generated from your positions, projects and skills. Draft answers, track confidence,
        walk into the interview prepared.
      </p>

      <div className="interview-toolbar">
        {CATEGORIES.map((c) => (
          <button
            key={c.id}
            className={`btn btn-sm ${category === c.id ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setCategory(c.id)}
          >
            {c.label}
          </button>
        ))}
        <select
          className="form-control"
          style={{ width: 'auto', fontSize: '0.85rem', marginLeft: 'auto' }}
          value={positionId}
          onChange={(e) => setPositionId(e.target.value)}
        >
          <option value="all">All positions ({positions.length})</option>
          {positions.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title}
            </option>
          ))}
        </select>
      </div>

      {!loading && !error && questions.length > 0 && (
        <div className="interview-progress">
          {confident} confident · {drafted} drafted · {unprepared} unprepared · total {questions.length}
        </div>
      )}

      {error && (
        <div
          className="alerts-panel alerts-error"
          style={{ marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}
        >
          <span>⚠ Interview questions unavailable: {error}</span>
          <button className="btn btn-outline btn-sm" onClick={load}>Retry</button>
        </div>
      )}

      {loading && (
        <div>
          {[0, 1, 2].map((i) => (
            <div key={i} className="qa-skeleton" />
          ))}
        </div>
      )}

      {!loading && !error && questions.length === 0 && (
        <p className="text-muted" style={{ fontSize: '0.85rem' }}>
          No questions for this filter yet — pick another category or position, or generate questions on the backend.
        </p>
      )}

      {!loading && questions.map((q) => (
        <div key={q.id} className="qa-card">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
            <span className="badge badge-bg">{q.category.replace(/_/g, ' ')}</span>
            <div className="d-flex gap-2 align-items-center">
              {q.difficulty && <span className="badge badge-secondary">{q.difficulty}</span>}
              <span className={statusBadge(q.status)}>{q.status}</span>
            </div>
          </div>

          <div className="qa-question" onClick={() => setExpanded((e) => ({ ...e, [q.id]: !e[q.id] }))}>
            {expanded[q.id] ? '▾' : '▸'} {q.question}
          </div>

          {expanded[q.id] && (
            <div className="qa-detail">
              {q.hints && q.hints.length > 0 && (
                <>
                  <div className="qa-detail-title">Hints</div>
                  <ul>
                    {q.hints.map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                </>
              )}
              {q.why && (
                <>
                  <div className="qa-detail-title">Why this matters</div>
                  <p style={{ margin: '0.2rem 0 0' }}>{q.why}</p>
                </>
              )}
            </div>
          )}

          <div className="qa-status-group">
            {STATUSES.map((s) => (
              <button
                key={s.id}
                className={`qa-status-btn ${q.status === s.id ? 'active' : ''}`}
                disabled={saving[q.id]}
                onClick={() => {
                  if (q.status !== s.id) save(q, s.id, drafts[q.id] ?? q.answer ?? '')
                }}
              >
                {s.label}
              </button>
            ))}
          </div>

          <textarea
            className="form-control"
            rows={3}
            style={{ marginTop: '0.35rem', fontSize: '0.85rem' }}
            placeholder="Draft your answer…"
            value={drafts[q.id] ?? ''}
            onChange={(e) => setDrafts((d) => ({ ...d, [q.id]: e.target.value }))}
          />

          <div className="d-flex align-items-center gap-2" style={{ marginTop: '0.4rem' }}>
            <button
              className="btn btn-primary btn-sm"
              disabled={saving[q.id]}
              onClick={() => save(q, q.status, drafts[q.id] ?? q.answer ?? '')}
            >
              {saving[q.id] ? 'Saving…' : 'Save'}
            </button>
            {savedId === q.id && <span className="qa-saved">✓ Saved</span>}
            {saveError[q.id] && (
              <span className="text-danger" style={{ fontSize: '0.75rem' }}>
                Save failed: {saveError[q.id]}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
