import { useState } from 'react'
import { CareerDatabase, Variant } from '../types'
import { api } from '../api'

interface VariantComposerProps {
  db: CareerDatabase | null
  onUpdate: (db: CareerDatabase) => void
}

export function VariantComposer({ db, onUpdate }: VariantComposerProps) {
  const [variants, setVariants] = useState<Variant[]>(db?.variants || [])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editVariant, setEditVariant] = useState<Variant | null>(null)
  const [newVariant, setNewVariant] = useState<Partial<Variant>>({
    id: '',
    label: '',
    audience: 'industry',
    length_target: '2page',
    template: 'industrial',
    sections: ['summary', 'experience', 'education', 'skills'],
    position_ids: [],
    achievement_overrides: {},
    wording_level: 'standard',
    page_limit: 2,
  })

  const availablePositions = db?.positions || []

  const handleEdit = (variant: Variant) => {
    setEditingId(variant.id)
    setEditVariant({ ...variant })
  }

  const handleSave = async (variant: Variant) => {
    try {
      const endpoint = editingId ? `/variants/${editingId}` : '/variants'
      const method = editingId ? 'PUT' : 'POST'
      await fetch(`/api${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(variant),
      })
      const newDb = await api.getDatabase()
      onUpdate(newDb)
      setEditingId(null)
      setEditVariant(null)
      setNewVariant({ id: '', label: '', audience: 'industry', length_target: '2page', template: 'industrial', sections: [], position_ids: [], achievement_overrides: {}, wording_level: 'standard', page_limit: 2 })
    } catch (error) {
      console.error('Save failed:', error)
      alert('Failed to save')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this variant?')) return
    try {
      await fetch(`/api/variants/${id}`, { method: 'DELETE' })
      const newDb = await api.getDatabase()
      onUpdate(newDb)
    } catch (error) {
      console.error('Delete failed:', error)
      alert('Failed to delete')
    }
  }

  const handlePositionToggle = (variant: Variant, posId: string) => {
    const ids = variant.position_ids.includes(posId)
      ? variant.position_ids.filter((id) => id !== posId)
      : [...variant.position_ids, posId]
    const updated = { ...variant, position_ids: ids }
    if (editingId === variant.id) setEditVariant(updated)
    else setVariants(variants.map((v) => (v.id === variant.id ? updated : v)))
  }

  const renderVariantCard = (variant: Variant) => {
    if (editingId === variant.id && editVariant) {
      return (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h3>Editing: {editVariant.label}</h3>
            <div className="d-flex gap-2">
              <button className="btn btn-primary btn-sm" onClick={() => handleSave(editVariant)}>Save</button>
              <button className="btn btn-secondary btn-sm" onClick={() => { setEditingId(null); setEditVariant(null); }}>Cancel</button>
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label">ID</label>
            <input className="form-control" value={editVariant.id} onChange={(e) => setEditVariant({ ...editVariant, id: e.target.value })} />
          </div>
          <div className="mb-3">
            <label className="form-label">Label</label>
            <input className="form-control" value={editVariant.label} onChange={(e) => setEditVariant({ ...editVariant, label: e.target.value })} />
          </div>
          <div className="row g-3 mb-3">
            <div className="col-md-4">
              <label className="form-label">Audience</label>
              <select className="form-control" value={editVariant.audience} onChange={(e) => setEditVariant({ ...editVariant, audience: e.target.value as any })}>
                <option value="industry">Industry</option>
                <option value="academic">Academic</option>
                <option value="research">Research</option>
                <option value="general">General</option>
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Length Target</label>
              <select className="form-control" value={editVariant.length_target} onChange={(e) => setEditVariant({ ...editVariant, length_target: e.target.value as any })}>
                <option value="1page">1 Page</option>
                <option value="2page">2 Pages</option>
                <option value="4page">4 Pages</option>
                <option value="10page">10 Pages</option>
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Wording Level</label>
              <select className="form-control" value={editVariant.wording_level} onChange={(e) => setEditVariant({ ...editVariant, wording_level: e.target.value as any })}>
                <option value="brief">Brief</option>
                <option value="standard">Standard</option>
                <option value="detailed">Detailed</option>
              </select>
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label">Page Limit</label>
            <input type="number" className="form-control" value={editVariant.page_limit} onChange={(e) => setEditVariant({ ...editVariant, page_limit: parseInt(e.target.value) })} min={1} max={20} />
          </div>
          <div className="mb-3">
            <label className="form-label">Positions ({editVariant.position_ids.length} selected)</label>
            <div style={{ maxHeight: 300, overflow: 'auto', border: '1px solid #dee2e6', borderRadius: 6, padding: '0.5rem' }}>
              {availablePositions.map((pos) => (
                <label key={pos.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.25rem' }}>
                  <input
                    type="checkbox"
                    checked={editVariant.position_ids.includes(pos.id)}
                    onChange={() => handlePositionToggle(editVariant, pos.id)}
                  />
                  <span>{pos.title} at {pos.organization_id}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )
    }

    return (
      <div className="card mb-3">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h4 style={{ margin: 0 }}>{variant.label}</h4>
            <div className="d-flex gap-2 mt-1 flex-wrap">
              <span className="badge badge-bg">{variant.audience}</span>
              <span className="badge badge-secondary">{variant.length_target}</span>
              <span className="badge badge-warning">{variant.wording_level}</span>
              <span className="badge badge-success">{variant.page_limit} pages</span>
            </div>
          </div>
          <div className="d-flex gap-2">
            <button className="btn btn-outline btn-sm" onClick={() => handleEdit(variant)}>Edit</button>
            <button className="btn btn-outline btn-sm text-danger" onClick={() => handleDelete(variant.id)}>Delete</button>
          </div>
        </div>
        <div className="mt-2 text-muted small">
          Positions: {variant.position_ids.length} · Template: {variant.template} · Sections: {variant.sections.join(', ') || 'default'}
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ margin: 0 }}>CV Variants</h2>
        <button className="btn btn-primary" onClick={() => { setEditingId('new'); setEditVariant(newVariant as Variant); }}>New Variant</button>
      </div>

      {editingId === 'new' && editVariant && (
        <div className="card mb-3">
          <h3>New Variant</h3>
          <div className="row g-3 mb-3">
            <div className="col-md-4">
              <label className="form-label">ID</label>
              <input className="form-control" value={newVariant.id} onChange={(e) => setNewVariant({ ...newVariant, id: e.target.value })} />
            </div>
            <div className="col-md-4">
              <label className="form-label">Label</label>
              <input className="form-control" value={newVariant.label} onChange={(e) => setNewVariant({ ...newVariant, label: e.target.value })} />
            </div>
            <div className="col-md-4">
              <label className="form-label">Audience</label>
              <select className="form-control" value={newVariant.audience} onChange={(e) => setNewVariant({ ...newVariant, audience: e.target.value as any })}>
                <option value="industry">Industry</option>
                <option value="academic">Academic</option>
                <option value="research">Research</option>
                <option value="general">General</option>
              </select>
            </div>
          </div>
          <div className="row g-3 mb-3">
            <div className="col-md-4">
              <label className="form-label">Length Target</label>
              <select className="form-control" value={newVariant.length_target} onChange={(e) => setNewVariant({ ...newVariant, length_target: e.target.value as any })}>
                <option value="1page">1 Page</option>
                <option value="2page">2 Pages</option>
                <option value="4page">4 Pages</option>
                <option value="10page">10 Pages</option>
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Wording Level</label>
              <select className="form-control" value={newVariant.wording_level} onChange={(e) => setNewVariant({ ...newVariant, wording_level: e.target.value as any })}>
                <option value="brief">Brief</option>
                <option value="standard">Standard</option>
                <option value="detailed">Detailed</option>
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Page Limit</label>
              <input type="number" className="form-control" value={newVariant.page_limit} onChange={(e) => setNewVariant({ ...newVariant, page_limit: parseInt(e.target.value) })} min={1} max={20} />
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label">Positions ({newVariant.position_ids?.length ?? 0} selected)</label>
            <div style={{ maxHeight: 200, overflow: 'auto', border: '1px solid #dee2e6', borderRadius: 6, padding: '0.5rem' }}>
              {availablePositions.map((pos) => (
                <label key={pos.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.25rem' }}>
                  <input
                    type="checkbox"
                    checked={newVariant.position_ids?.includes(pos.id) ?? false}
                    onChange={() => setNewVariant({ ...newVariant, position_ids: newVariant.position_ids?.includes(pos.id) ? newVariant.position_ids.filter((id) => id !== pos.id) : [...(newVariant.position_ids || []), pos.id] })} />
                  <span>{pos.title} at {pos.organization_id}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="d-flex gap-2">
            <button className="btn btn-primary" onClick={async () => {
              try {
                await fetch('/api/variants', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(newVariant) })
                const newDb = await api.getDatabase()
                onUpdate(newDb)
                setNewVariant({ id: '', label: '', audience: 'industry', length_target: '2page', template: 'industrial', sections: [], position_ids: [], achievement_overrides: {}, wording_level: 'standard', page_limit: 2 })
              } catch (error) { alert('Failed to create') }
            }}>Create</button>
            <button className="btn btn-secondary" onClick={() => setNewVariant({ id: '', label: '', audience: 'industry', length_target: '2page', template: 'industrial', sections: [], position_ids: [], achievement_overrides: {}, wording_level: 'standard', page_limit: 2 })}>Cancel</button>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1rem' }}>
        {variants.map(renderVariantCard)}
      </div>

      {variants.length === 0 && editingId !== 'new' && (
        <p className="text-muted text-center py-4">No variants defined. Click "New Variant" to create one.</p>
      )}
    </div>
  )
}