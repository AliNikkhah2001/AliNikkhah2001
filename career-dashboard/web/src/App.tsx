import { useState, useEffect } from 'react'
import { Sidebar, TimelineView, KnowledgeBase, TechStackTab, VariantComposer, TemplatesTab, PublishingStatus, LinkedInExport } from './components'
import { CareerDatabase } from './types'
import { api } from './api'

function App() {
  const [db, setDb] = useState<CareerDatabase | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'timeline' | 'knowledge' | 'stack' | 'variants' | 'templates' | 'publishing' | 'linkedin'>('timeline')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    loadDatabase()
  }, [])

  const loadDatabase = async () => {
    try {
      const data = await api.getDatabase()
      setDb(data)
    } catch (error) {
      console.error('Failed to load database:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDbUpdate = (newDb: CareerDatabase) => {
    setDb(newDb)
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div className="spinner" style={{ width: 40, height: 40, border: '3px solid #dee2e6', borderTopColor: '#0d6efd', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <style>{`
          @keyframes spin { to { transform: rotate(360deg); } }
        `}</style>
      </div>
    )
  }

  return (
    <div className="d-flex min-vh-100">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        db={db}
      />
      <main className="main-content flex-grow-1" style={{ marginLeft: sidebarOpen ? 280 : 0 }}>
        <header style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #dee2e6', background: 'white', position: 'sticky', top: 0, zIndex: 10 }}>
          <div className="d-flex justify-content-between align-items-center">
            <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Career Dashboard</h1>
            <div className="d-flex gap-2">
              <button className="btn btn-outline btn-sm" onClick={loadDatabase}>Reload DB</button>
              <button className="btn btn-primary btn-sm" onClick={() => window.open('/api/export/github-readme', '_blank')}>Export README</button>
            </div>
          </div>
        </header>

        <div className="container" style={{ paddingTop: '1.5rem' }}>
          {activeTab === 'timeline' && <TimelineView db={db} onUpdate={handleDbUpdate} />}
          {activeTab === 'knowledge' && <KnowledgeBase db={db} onUpdate={handleDbUpdate} />}
          {activeTab === 'stack' && <TechStackTab db={db} onUpdate={handleDbUpdate} />}
          {activeTab === 'variants' && <VariantComposer db={db} onUpdate={handleDbUpdate} />}
          {activeTab === 'templates' && <TemplatesTab db={db} />}
          {activeTab === 'publishing' && <PublishingStatus db={db} />}
          {activeTab === 'linkedin' && <LinkedInExport db={db} />}
        </div>
      </main>
    </div>
  )
}

export default App