import { CareerDatabase } from '../types'

interface SidebarProps {
  open: boolean
  onToggle: () => void
  activeTab: 'timeline' | 'knowledge' | 'stack' | 'variants' | 'templates' | 'publishing' | 'linkedin'
  onTabChange: (tab: 'timeline' | 'knowledge' | 'stack' | 'variants' | 'templates' | 'publishing' | 'linkedin') => void
  db: CareerDatabase | null
}

const tabs = [
  { id: 'timeline', label: 'Timeline', icon: '📅' },
  { id: 'knowledge', label: 'Knowledge Base', icon: '🧠' },
  { id: 'stack', label: 'Tech Stack', icon: '🧰' },
  { id: 'variants', label: 'CV Variants', icon: '📄' },
  { id: 'templates', label: 'Templates', icon: '🧩' },
  { id: 'publishing', label: 'Publishing', icon: '🚀' },
  { id: 'linkedin', label: 'LinkedIn Export', icon: '💼' },
] as const

export function Sidebar({ open, onToggle, activeTab, onTabChange, db }: SidebarProps) {
  const orgCount = db?.organizations.length ?? 0
  const posCount = db?.positions.length ?? 0
  const achCount = db?.achievements.length ?? 0
  const variantCount = db?.variants.length ?? 0

  return (
    <>
      <button
        className="btn btn-secondary btn-sm"
        onClick={onToggle}
        style={{
          position: 'fixed',
          top: 12,
          left: 12,
          zIndex: 101,
          display: open ? 'none' : 'block',
        }}
      >
        ☰ Menu
      </button>

      <aside className={`sidebar ${open ? 'open' : ''}`} style={{ width: open ? 280 : 0, overflow: 'hidden', transition: 'width 0.3s ease' }}>
        <div style={{ padding: '1rem', borderBottom: '1px solid #dee2e6' }}>
          <h2 style={{ margin: 0, fontSize: '1.1rem' }}>Career Dashboard</h2>
          <p className="text-muted" style={{ margin: '0.25rem 0 0', fontSize: '0.75rem' }}>
            {orgCount} orgs · {posCount} positions · {achCount} achievements · {variantCount} variants
          </p>
        </div>

        <nav className="nav-section">
          <div className="nav-section-title">Views</div>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => onTabChange(tab.id as typeof activeTab)}
            >
              <span className="nav-item-icon">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        <nav className="nav-section">
          <div className="nav-section-title">Data Counts</div>
          <div className="nav-item" style={{ justifyContent: 'space-between', cursor: 'default' }}>
            <span>Organizations</span>
            <span className="badge badge-bg">{orgCount}</span>
          </div>
          <div className="nav-item" style={{ justifyContent: 'space-between', cursor: 'default' }}>
            <span>Positions</span>
            <span className="badge badge-success">{posCount}</span>
          </div>
          <div className="nav-item" style={{ justifyContent: 'space-between', cursor: 'default' }}>
            <span>Achievements</span>
            <span className="badge badge-warning">{achCount}</span>
          </div>
          <div className="nav-item" style={{ justifyContent: 'space-between', cursor: 'default' }}>
            <span>Variants</span>
            <span className="badge badge-secondary">{variantCount}</span>
          </div>
        </nav>

        <div style={{ padding: '1rem', borderTop: '1px solid #dee2e6', fontSize: '0.75rem', color: '#6c757d' }}>
          Single source of truth for your career. Edit once, publish everywhere.
        </div>
      </aside>
    </>
  )
}