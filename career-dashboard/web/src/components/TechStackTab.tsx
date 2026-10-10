import { useMemo, useState } from 'react'
import { CareerDatabase, Position } from '../types'
import { api } from '../api'

interface TechStackTabProps {
  db: CareerDatabase | null
  onUpdate: (db: CareerDatabase) => void
}

const CAT_META: Record<string, { label: string; color: string; bg: string }> = {
  language: { label: 'Programming', color: '#2563eb', bg: '#dbeafe' },
  ml_vision: { label: 'ML & Vision', color: '#c2410c', bg: '#ffedd5' },
  agentic: { label: 'Agentic AI & RAG', color: '#7c3aed', bg: '#ede9fe' },
  llm_serving: { label: 'LLM Serving & GPU', color: '#0f766e', bg: '#ccfbf1' },
  data_mlop: { label: 'Data & MLOps', color: '#0369a1', bg: '#e0f2fe' },
  human: { label: 'Languages', color: '#be185d', bg: '#fce7f3' },
}

interface StackEntry {
  name: string
  category?: string
  count: number
  positions: Position[]
}

export function TechStackTab({ db, onUpdate }: TechStackTabProps) {
  const [query, setQuery] = useState('')
  const [deriving, setDeriving] = useState(false)
  const [deriveMsg, setDeriveMsg] = useState<string | null>(null)

  const skillIndex = useMemo(() => {
    const map = new Map<string, { name: string; category?: string }>()
    for (const s of db?.skills ?? []) {
      map.set(s.name.toLowerCase(), { name: s.name, category: s.category })
      for (const a of s.aliases) map.set(a.toLowerCase(), { name: s.name, category: s.category })
    }
    return map
  }, [db])

  const { entries, untagged, taggedCount } = useMemo(() => {
    const agg = new Map<string, StackEntry>()
    const untagged: Position[] = []
    let taggedCount = 0

    for (const pos of db?.positions ?? []) {
      if (!pos.tech_stack || pos.tech_stack.length === 0) {
        untagged.push(pos)
        continue
      }
      taggedCount += 1
      for (const tech of pos.tech_stack) {
        const key = tech.trim().toLowerCase()
        if (!key) continue
        let entry = agg.get(key)
        if (!entry) {
          const known = skillIndex.get(key)
          entry = {
            name: known?.name ?? tech.trim(),
            category: known?.category,
            count: 0,
            positions: [],
          }
          agg.set(key, entry)
        }
        entry.count += 1
        entry.positions.push(pos)
      }
    }

    const entries = [...agg.values()].sort(
      (a, b) => b.count - a.count || a.name.localeCompare(b.name)
    )
    return { entries, untagged, taggedCount }
  }, [db, skillIndex])

  const filtered = query.trim()
    ? entries.filter((e) => e.name.toLowerCase().includes(query.trim().toLowerCase()))
    : entries

  const uniqueCount = entries.length

  const runDerive = async () => {
    setDeriving(true)
    setDeriveMsg(null)
    try {
      const res = await api.deriveTechStacks()
      const newDb = await api.getDatabase()
      onUpdate(newDb)
      setDeriveMsg(
        res.updated_positions === 0 && res.skills_added === 0
          ? 'Already up to date — every position already has its achievement skills.'
          : `Derived stacks: updated ${res.updated_positions} position(s), added ${res.skills_added} skill tag(s).`
      )
    } catch (err) {
      setDeriveMsg(`Derive failed: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setDeriving(false)
    }
  }

  if (!db) {
    return <div className="card"><p className="text-muted">Loading database…</p></div>
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <h2 style={{ margin: 0 }}>Tech Stack</h2>
          <div className="d-flex gap-2 align-items-center flex-wrap">
            <input
              className="form-control"
              placeholder="Filter tech…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ width: 200 }}
            />
            <button className="btn btn-outline" onClick={runDerive} disabled={deriving}>
              {deriving ? 'Deriving…' : 'Derive from achievements'}
            </button>
          </div>
        </div>

        {deriveMsg && (
          <div className="alert" style={{ background: '#e7f1ff', border: '1px solid #bad6ff', color: '#084298', padding: '0.6rem 0.9rem', borderRadius: 6, marginBottom: '1rem', fontSize: '0.875rem' }}>
            {deriveMsg}
          </div>
        )}

        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-value">{uniqueCount}</div>
            <div className="stat-label">unique tech</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{taggedCount}</div>
            <div className="stat-label">positions tagged</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{db.positions.length}</div>
            <div className="stat-label">total positions</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{db.achievements.reduce((n, a) => n + a.skills.length, 0)}</div>
            <div className="stat-label">skill mentions in bullets</div>
          </div>
        </div>

        {filtered.length === 0 ? (
          <p className="text-muted text-center py-4">
            {entries.length === 0
              ? 'No tech tagged yet. Open a position in the Timeline and add its stack, or hit “Derive from achievements”.'
              : 'No tech matches your filter.'}
          </p>
        ) : (
          <div className="stack-grid">
            {filtered.map((entry) => {
              const cat = entry.category ? CAT_META[entry.category] : undefined
              return (
                <div key={entry.name} className="stack-card">
                  <div className="stack-card-head">
                    <span className="stack-name">{entry.name}</span>
                    <span className="legend-count">{entry.count}</span>
                  </div>
                  {cat && (
                    <span className="tl-tag" style={{ background: cat.bg, color: cat.color, alignSelf: 'flex-start' }}>
                      {cat.label}
                    </span>
                  )}
                  <ul className="stack-positions">
                    {entry.positions.map((p) => (
                      <li key={`${entry.name}_${p.id}`} title={p.summary ?? p.title}>
                        {p.title}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {untagged.length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0, fontSize: '1rem' }}>Untagged positions ({untagged.length})</h3>
          <p className="text-muted" style={{ fontSize: '0.875rem' }}>
            These positions have an empty tech stack — edit them in the Timeline, or use “Derive from achievements” above.
          </p>
          <div className="d-flex gap-2 flex-wrap">
            {untagged.map((p) => (
              <span key={p.id} className="tech-chip" style={{ background: '#f1f3f5', color: '#495057' }}>
                {p.title}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
