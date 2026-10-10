import { useState } from 'react'
import { CareerDatabase } from '../types'
import { api } from '../api'

interface KnowledgeBaseProps {
  db: CareerDatabase | null
  onUpdate: (db: CareerDatabase) => void
}

type EntityType = 'positions' | 'achievements' | 'organizations' | 'skills' | 'education' | 'projects' | 'publications' | 'teaching'

export function KnowledgeBase({ db, onUpdate }: KnowledgeBaseProps) {
  const [entityType, setEntityType] = useState<EntityType>('positions')
  const [search, setSearch] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editData, setEditData] = useState<any>(null)

  const entities = db?.[entityType] || []
  const filtered = entities.filter((e: any) => {
    const text = JSON.stringify(e).toLowerCase()
    return text.includes(search.toLowerCase())
  })

  const handleEdit = (entity: any) => {
    setEditingId(entity.id)
    setEditData({ ...entity })
  }

  const handleSave = async (id: string, data: any) => {
    try {
      let endpoint = ''
      switch (entityType) {
        case 'positions': endpoint = `/positions/${id}`; break
        case 'achievements': endpoint = `/achievements/${id}`; break
        case 'organizations': endpoint = `/organizations/${id}`; break
        case 'skills': endpoint = `/skills/${id}`; break
        default: throw new Error('Not implemented')
      }
      await fetch(`/api${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      const newDb = await api.getDatabase()
      onUpdate(newDb)
      setEditingId(null)
      setEditData(null)
    } catch (error) {
      console.error('Save failed:', error)
      alert('Failed to save')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this item?')) return
    try {
      let endpoint = ''
      switch (entityType) {
        case 'positions': endpoint = `/positions/${id}`; break
        case 'achievements': endpoint = `/achievements/${id}`; break
        case 'organizations': endpoint = `/organizations/${id}`; break
        default: throw new Error('Not implemented')
      }
      await fetch(`/api${endpoint}`, { method: 'DELETE' })
      const newDb = await api.getDatabase()
      onUpdate(newDb)
    } catch (error) {
      console.error('Delete failed:', error)
      alert('Failed to delete')
    }
  }

  const renderEntityRow = (entity: any) => {
    if (editingId === entity.id && editData) {
      return (
        <tr>
          <td colSpan={4}>
            <textarea
              value={JSON.stringify(editData, null, 2)}
              onChange={(e) => setEditData(JSON.parse(e.target.value))}
              style={{ width: '100%', height: 200, fontFamily: 'monospace', fontSize: '0.75rem' }}
            />
            <div className="mt-2 d-flex gap-2">
              <button className="btn btn-primary btn-sm" onClick={() => handleSave(entity.id, editData)}>Save</button>
              <button className="btn btn-secondary btn-sm" onClick={() => { setEditingId(null); setEditData(null); }}>Cancel</button>
            </div>
          </td>
        </tr>
      )
    }

    const label = entity.title || entity.name || entity.label || entity.id
    const subtitle = entity.organization_id || entity.category || ''

    return (
      <tr>
        <td style={{ fontWeight: 500 }}>{label}</td>
        <td className="text-muted" style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {subtitle}
        </td>
        <td className="text-muted" style={{ fontSize: '0.875rem' }}>{entity.id}</td>
        <td style={{ whiteSpace: 'nowrap' }}>
          <button className="btn btn-outline btn-sm" onClick={() => handleEdit(entity)}>Edit</button>
          <button className="btn btn-outline btn-sm text-danger" onClick={() => handleDelete(entity.id)}>Delete</button>
        </td>
      </tr>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h2 style={{ margin: 0 }}>Knowledge Base</h2>
        <div className="d-flex gap-2 flex-wrap">
          {(['positions', 'achievements', 'organizations', 'skills', 'education', 'projects', 'publications', 'teaching'] as EntityType[]).map((type) => (
            <button
              key={type}
              className={`btn btn-sm ${entityType === type ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => { setEntityType(type); setEditingId(null); }}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-3">
        <input
          type="text"
          className="form-control"
          placeholder={`Search ${entityType}...`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: 400 }}
        />
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: '30%' }}>Name</th>
              <th style={{ width: '30%' }}>Details</th>
              <th style={{ width: '20%' }}>ID</th>
              <th style={{ width: '20%' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((entity) => renderEntityRow(entity))}
          </tbody>
        </table>
        {filtered.length === 0 && <p className="text-muted text-center py-4">No items found</p>}
      </div>
    </div>
  )
}