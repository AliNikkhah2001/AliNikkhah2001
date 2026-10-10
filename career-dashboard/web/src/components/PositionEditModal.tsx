import { useMemo, useState, type ReactNode } from 'react'
import { Achievement, CareerDatabase, DatePrecision, Position, Project } from '../types'
import { api } from '../api'
import { categorizePosition, CATEGORY_META } from '../categories'
import { MarkdownEditor } from './MarkdownEditor'

interface PositionEditModalProps {
  position: Position
  db: CareerDatabase
  onClose: () => void
  onUpdate: (db: CareerDatabase) => void
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

function DateField({ label, value, disabled, onChange }: {
  label: string
  value: DatePrecision
  disabled?: boolean
  onChange: (d: DatePrecision) => void
}) {
  return (
    <div>
      <label className="form-label">{label}</label>
      <div className="d-flex gap-2">
        <input
          type="number"
          className="form-control"
          style={{ width: 90 }}
          min={1900}
          max={9999}
          disabled={disabled}
          value={value.year > 0 ? value.year : ''}
          onChange={(e) => onChange({ ...value, year: e.target.value === '' ? 0 : parseInt(e.target.value, 10) || 0 })}
        />
        <select
          className="form-control"
          disabled={disabled}
          value={value.month ?? ''}
          onChange={(e) => onChange({
            ...value,
            month: e.target.value === '' ? undefined : parseInt(e.target.value, 10),
          })}
        >
          <option value="">— year only</option>
          {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
        </select>
      </div>
    </div>
  )
}

function SectionTitle({ children, hint }: { children: ReactNode; hint?: string }) {
  return (
    <div className="edit-section-title">
      <h4>{children}</h4>
      {hint && <span className="text-muted">{hint}</span>}
    </div>
  )
}

export function PositionEditModal({ position, db, onClose, onUpdate }: PositionEditModalProps) {
  const [form, setForm] = useState<Position>({ ...position, tech_stack: [...(position.tech_stack ?? [])] })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Deferred sub-entity edits, applied on Save
  const [achievementEdits, setAchievementEdits] = useState<Record<string, string>>({})
  const [newBullets, setNewBullets] = useState<string[]>([])
  const [bulletDraft, setBulletDraft] = useState('')
  const [projectLinks, setProjectLinks] = useState<Record<string, boolean>>({})
  const [newProjects, setNewProjects] = useState<string[]>([])
  const [projectDraft, setProjectDraft] = useState('')
  const [techDraft, setTechDraft] = useState('')

  const set = <K extends keyof Position>(key: K, value: Position[K]) =>
    setForm((f) => ({ ...f, [key]: value }))

  const category = categorizePosition(form)
  const meta = CATEGORY_META[category]

  const achMap = useMemo(() => new Map(db.achievements.map((a) => [a.id, a])), [db.achievements])

  const techSuggestions = useMemo(() => {
    const names = new Set<string>()
    for (const s of db.skills) {
      names.add(s.name)
      for (const a of s.aliases) names.add(a)
    }
    return [...names].sort((a, b) => a.localeCompare(b))
  }, [db.skills])

  const addTech = (raw: string) => {
    const name = raw.trim()
    if (!name) return
    if (form.tech_stack.some((t) => t.toLowerCase() === name.toLowerCase())) {
      setTechDraft('')
      return
    }
    set('tech_stack', [...form.tech_stack, name])
    setTechDraft('')
  }

  const removeTech = (name: string) =>
    set('tech_stack', form.tech_stack.filter((t) => t !== name))

  const unlinkBullet = (id: string) =>
    set('achievements', form.achievements.filter((a) => a !== id))

  const isProjectLinked = (p: Project) =>
    projectLinks[p.id] ?? p.position_ids.includes(position.id)

  const toggleProject = (p: Project) =>
    setProjectLinks((l) => ({ ...l, [p.id]: !isProjectLinked(p) }))

  const handleSave = async () => {
    setError(null)
    if (!form.title.trim()) return setError('Title is required')
    if (!form.organization_id) return setError('Organization is required')
    if (!form.start.year || form.start.year < 1900) return setError('Start year is required')

    setSaving(true)
    try {
      // 1. Create new achievement bullets
      const createdIds: string[] = []
      for (const text of newBullets.filter((t) => t.trim())) {
        const ach = await api.createAchievement({
          id: `ach_${position.id}_${Date.now().toString(36)}_${createdIds.length}`,
          position_id: position.id,
          text: text.trim(),
          metrics: {},
          skills: [],
          source_refs: [],
          verified: false,
        } as Achievement)
        createdIds.push(ach.id)
      }

      // 2. Save edited bullet text (keep brief/detailed in sync)
      for (const [id, text] of Object.entries(achievementEdits)) {
        const orig = achMap.get(id)
        if (!orig || !text.trim() || text === orig.text) continue
        const trimmed = text.trim()
        await api.updateAchievement(id, {
          ...orig,
          text: trimmed,
          brief_text: trimmed.slice(0, 160) + (trimmed.length > 160 ? '…' : ''),
          detailed_text: trimmed,
        })
      }

      // 3. Unlink removed bullets from their achievement records
      const finalAchIds = [...form.achievements, ...createdIds]
      const unlinked = position.achievements.filter((id) => !finalAchIds.includes(id))
      for (const id of unlinked) {
        const orig = achMap.get(id)
        if (orig && orig.position_id === position.id) {
          await api.updateAchievement(id, { ...orig, position_id: undefined })
        }
      }

      // 4. Save the position itself
      const payload: Position = {
        ...form,
        achievements: finalAchIds,
        tech_stack: form.tech_stack,
      }
      if (payload.ongoing || !payload.end || payload.end.year < 1900) payload.end = undefined
      await api.updatePosition(position.id, payload)

      // 5. Apply project link toggles + create quick-added projects
      for (const p of db.projects) {
        const linked = isProjectLinked(p)
        const wasLinked = p.position_ids.includes(position.id)
        if (linked === wasLinked) continue
        const position_ids = linked
          ? [...p.position_ids, position.id]
          : p.position_ids.filter((i) => i !== position.id)
        await api.updateProject(p.id, { ...p, position_ids })
      }
      for (const title of newProjects.filter((t) => t.trim())) {
        await api.createProject({
          id: `prj_${position.id}_${Date.now().toString(36)}`,
          title: title.trim(),
          organization_id: position.organization_id,
          start: position.start,
          ongoing: position.ongoing,
          skills: [],
          achievements: [],
          position_ids: [position.id],
        } as Project)
      }

      const newDb = await api.getDatabase()
      onUpdate(newDb)
      onClose()
    } catch (err) {
      console.error('Save failed:', err)
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSaving(false)
    }
  }

  const bullets = form.achievements.map((id) => ({ id, ach: achMap.get(id) }))

  return (
    <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose() }}>
      <div className="modal modal-wide">
        <div className="modal-header">
          <div className="d-flex align-items-center gap-2" style={{ flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Edit Position</h3>
            <span className="tl-tag" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span>
          </div>
          <button className="btn btn-outline btn-sm" onClick={onClose}>Close</button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="alert" style={{ background: '#f8d7da', border: '1px solid #f5c6cb', color: '#721c24', padding: '0.75rem', borderRadius: 6, marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          <SectionTitle>Basics</SectionTitle>
          <div className="mb-3">
            <label className="form-label">Title</label>
            <input
              className="form-control"
              value={form.title}
              onChange={(e) => set('title', e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Organization</label>
            <select
              className="form-control"
              value={form.organization_id}
              onChange={(e) => set('organization_id', e.target.value)}
            >
              {db.organizations.map((org) => (
                <option key={org.id} value={org.id}>{org.name}</option>
              ))}
            </select>
          </div>

          <div className="d-flex gap-3 mb-3" style={{ flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 200px' }}>
              <DateField label="Start" value={form.start} onChange={(d) => set('start', d)} />
            </div>
            <div style={{ flex: '1 1 200px' }}>
              <DateField
                label="End"
                value={form.end ?? { year: 0 }}
                disabled={form.ongoing}
                onChange={(d) => set('end', d)}
              />
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8, fontSize: '0.875rem' }}>
                <input
                  type="checkbox"
                  checked={form.ongoing}
                  onChange={(e) => set('ongoing', e.target.checked)}
                />
                Ongoing (present)
              </label>
            </div>
          </div>

          <div className="d-flex gap-3 mb-3" style={{ flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 200px' }}>
              <label className="form-label">Employment type</label>
              <select
                className="form-control"
                value={form.employment_type}
                onChange={(e) => set('employment_type', e.target.value as Position['employment_type'])}
              >
                <option value="full_time">Full-time</option>
                <option value="part_time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
                <option value="fellowship">Fellowship</option>
              </select>
            </div>
            <div style={{ flex: '1 1 200px' }}>
              <label className="form-label">Work model</label>
              <input
                className="form-control"
                placeholder="e.g. Full-time · On-site"
                value={form.work_model ?? ''}
                onChange={(e) => set('work_model', e.target.value || undefined)}
              />
            </div>
          </div>

          <div className="d-flex gap-3 mb-3" style={{ flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 200px' }}>
              <label className="form-label">Location</label>
              <input
                className="form-control"
                value={form.location ?? ''}
                onChange={(e) => set('location', e.target.value || undefined)}
              />
            </div>
            <div style={{ flex: '1 1 200px' }}>
              <label className="form-label">Remote</label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4, fontSize: '0.875rem' }}>
                <input
                  type="checkbox"
                  checked={form.remote}
                  onChange={(e) => set('remote', e.target.checked)}
                />
                Remote position
              </label>
            </div>
          </div>

          <SectionTitle hint="One or two lines, used as the headline blurb">Short summary</SectionTitle>
          <div className="mb-3">
            <textarea
              className="form-control"
              rows={2}
              placeholder="e.g. Self-hosted Graph RAG company assistant for national credit scoring…"
              value={form.summary ?? ''}
              onChange={(e) => set('summary', e.target.value || undefined)}
            />
          </div>

          <SectionTitle hint="Full write-up — supports markdown (headings, lists, bold, links, code)">Detailed description</SectionTitle>
          <div className="mb-3">
            <MarkdownEditor
              value={form.description_md ?? ''}
              onChange={(v) => set('description_md', v || undefined)}
              placeholder={'## What I did\n\n- Shipped …\n- Cut latency by **40%** using …\n\n> Architecture notes, links, metrics…'}
              minHeight={200}
            />
          </div>

          <SectionTitle hint={`${form.achievements.length + newBullets.length} bullets · saved with the position`}>Achievement bullets</SectionTitle>
          <div className="mb-3">
            {bullets.map(({ id, ach }) => (
              <div key={id} className="bullet-row">
                <span className="bullet-marker">•</span>
                <textarea
                  className="form-control"
                  rows={2}
                  value={achievementEdits[id] ?? ach?.text ?? id}
                  onChange={(e) => setAchievementEdits((ed) => ({ ...ed, [id]: e.target.value }))}
                />
                <button
                  type="button"
                  className="md-btn"
                  title="Remove bullet"
                  onClick={() => unlinkBullet(id)}
                >
                  ✕
                </button>
              </div>
            ))}

            {newBullets.map((text, i) => (
              <div key={`new_${i}`} className="bullet-row">
                <span className="bullet-marker">•</span>
                <textarea
                  className="form-control"
                  rows={2}
                  value={text}
                  onChange={(e) => setNewBullets((nb) => nb.map((t, j) => (j === i ? e.target.value : t)))}
                />
                <button
                  type="button"
                  className="md-btn"
                  title="Remove bullet"
                  onClick={() => setNewBullets((nb) => nb.filter((_, j) => j !== i))}
                >
                  ✕
                </button>
              </div>
            ))}

            <div className="d-flex gap-2">
              <input
                className="form-control"
                placeholder="Add a new achievement bullet…"
                value={bulletDraft}
                onChange={(e) => setBulletDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && bulletDraft.trim()) {
                    e.preventDefault()
                    setNewBullets((nb) => [...nb, bulletDraft.trim()])
                    setBulletDraft('')
                  }
                }}
              />
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => {
                  if (!bulletDraft.trim()) return
                  setNewBullets((nb) => [...nb, bulletDraft.trim()])
                  setBulletDraft('')
                }}
              >
                Add bullet
              </button>
            </div>
          </div>

          <SectionTitle hint="Link existing projects or quick-create new ones">Projects</SectionTitle>
          <div className="mb-3">
            {db.projects.map((p) => (
              <label key={p.id} className="check-row">
                <input
                  type="checkbox"
                  checked={isProjectLinked(p)}
                  onChange={() => toggleProject(p)}
                />
                <span>{p.title}</span>
                <span className="text-muted" style={{ fontSize: '0.8rem' }}>
                  {p.start.year}{p.end && !p.ongoing ? `–${p.end.year}` : p.ongoing ? '–present' : ''}
                </span>
              </label>
            ))}

            {newProjects.map((title, i) => (
              <div key={`nprj_${i}`} className="bullet-row">
                <span className="bullet-marker">▸</span>
                <input
                  className="form-control"
                  value={title}
                  onChange={(e) => setNewProjects((np) => np.map((t, j) => (j === i ? e.target.value : t)))}
                />
                <button
                  type="button"
                  className="md-btn"
                  title="Remove project"
                  onClick={() => setNewProjects((np) => np.filter((_, j) => j !== i))}
                >
                  ✕
                </button>
              </div>
            ))}

            <div className="d-flex gap-2 mt-2">
              <input
                className="form-control"
                placeholder="New project started during this position…"
                value={projectDraft}
                onChange={(e) => setProjectDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && projectDraft.trim()) {
                    e.preventDefault()
                    setNewProjects((np) => [...np, projectDraft.trim()])
                    setProjectDraft('')
                  }
                }}
              />
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => {
                  if (!projectDraft.trim()) return
                  setNewProjects((np) => [...np, projectDraft.trim()])
                  setProjectDraft('')
                }}
              >
                Add project
              </button>
            </div>
          </div>

          <SectionTitle hint="Tech used in this role — feeds the Tech Stack tab">Tech stack</SectionTitle>
          <div className="mb-3">
            <div className="chip-editor">
              {form.tech_stack.map((t) => (
                <span key={t} className="tech-chip">
                  {t}
                  <button type="button" onClick={() => removeTech(t)} title={`Remove ${t}`}>×</button>
                </span>
              ))}
              {form.tech_stack.length === 0 && (
                <span className="text-muted" style={{ fontSize: '0.8rem' }}>
                  Empty — type below, or use “Derive from achievements” in the Tech Stack tab.
                </span>
              )}
            </div>
            <div className="d-flex gap-2 mt-2">
              <input
                className="form-control"
                list="tech-suggestions"
                placeholder="Add technology (Enter)…"
                value={techDraft}
                onChange={(e) => setTechDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addTech(techDraft)
                  }
                }}
              />
              <button type="button" className="btn btn-outline" onClick={() => addTech(techDraft)}>
                Add
              </button>
            </div>
            <datalist id="tech-suggestions">
              {techSuggestions.map((s) => <option key={s} value={s} />)}
            </datalist>
          </div>
        </div>

        <div className="modal-footer">
          <span className="text-muted" style={{ marginRight: 'auto', fontSize: '0.8rem' }}>
            {newBullets.length > 0 && `${newBullets.length} new bullet(s) · `}
            {newProjects.length > 0 && `${newProjects.length} new project(s) · `}
            saves everything at once
          </span>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save changes'}
          </button>
        </div>
      </div>
    </div>
  )
}
