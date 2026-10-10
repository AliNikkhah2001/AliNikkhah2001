import { useEffect, useRef, useState } from 'react'
import { CareerDatabase, Position } from '../types'
import { categorizePosition, CATEGORY_META, formatDatePrecision, PROJECT_CATEGORY } from '../categories'
import { PositionEditModal } from './PositionEditModal'
import { AlertsPanel } from './AlertsPanel'
import 'vis-timeline/dist/vis-timeline-graph2d.min.css'

interface TimelineViewProps {
  db: CareerDatabase | null
  onUpdate: (db: CareerDatabase) => void
}

interface TimelineItem {
  id: string
  content: string
  start: string
  end?: string
  type: 'range' | 'box' | 'point'
  className: string
  title: string
  group: string
}

const LANE_DEFS = [
  { id: 'full-time', label: 'Full-time Work' },
  { id: 'part-time', label: 'Part-time / Contract' },
  { id: 'research', label: 'R&D / Research' },
  { id: 'education', label: 'Education & Teaching' },
  { id: 'project', label: 'Projects' },
]

declare global {
  interface Window {
    vis: {
      Timeline: new (container: HTMLElement, items: any, options: any) => any
      DataSet: new (data: any[], options?: any) => any
    }
  }
}

function loadVisTimeline(): Promise<void> {
  if (window.vis?.Timeline && window.vis?.DataSet) {
    console.log('[Timeline] vis already loaded')
    return Promise.resolve()
  }

  return new Promise((resolve, reject) => {
    // Check if script already loading
    const existingScript = document.querySelector('script[data-vis-timeline]') as HTMLScriptElement | null
    if (existingScript) {
      console.log('[Timeline] Script already loading, waiting...')
      existingScript.addEventListener('load', () => {
        console.log('[Timeline] Existing script loaded')
        resolve()
      })
      existingScript.addEventListener('error', () => reject(new Error('Failed to load vis-timeline script')))
      return
    }

    console.log('[Timeline] Loading vis-timeline script...')
    const script = document.createElement('script')
    script.src = '/vis-timeline-graph2d.min.js'
    script.async = true
    script.setAttribute('data-vis-timeline', 'true')
    script.onload = () => {
      console.log('[Timeline] Script loaded, checking window.vis...')
      console.log('[Timeline] window.vis =', window.vis)
      console.log('[Timeline] Object.keys(window.vis) =', window.vis ? Object.keys(window.vis) : 'null')
      if (window.vis) {
        console.log('[Timeline] window.vis.Timeline =', window.vis.Timeline)
        console.log('[Timeline] window.vis.DataSet =', window.vis.DataSet)
        console.log('[Timeline] window.vis.default =', (window.vis as any).default)
        console.log('[Timeline] window.vis.Timeline type =', typeof window.vis.Timeline)
        console.log('[Timeline] window.vis.DataSet type =', typeof window.vis.DataSet)
      }
      const visAny = window.vis as any
      if (visAny?.Timeline && visAny?.DataSet) {
        console.log('[Timeline] Timeline and DataSet available')
        resolve()
      } else if (visAny?.default?.Timeline && visAny?.default?.DataSet) {
        console.log('[Timeline] Found on window.vis.default')
        window.vis.Timeline = visAny.default.Timeline
        window.vis.DataSet = visAny.default.DataSet
        resolve()
      } else {
        console.error('[Timeline] Timeline/DataSet not found on window.vis')
        reject(new Error('vis-timeline loaded but Timeline/DataSet not found'))
      }
    }
    script.onerror = () => {
      console.error('[Timeline] Script failed to load')
      reject(new Error('Failed to load vis-timeline script'))
    }
    document.head.appendChild(script)
  })
}

export function TimelineView({ db, onUpdate }: TimelineViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const timelineRef = useRef<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedItem, setSelectedItem] = useState<{ id: string; type: 'education' | 'project' } | null>(null)
  const [editingPosition, setEditingPosition] = useState<Position | null>(null)

  useEffect(() => {
    if (!containerRef.current || !db) return

    let mounted = true

    const initTimeline = async () => {
      setLoading(true)
      setError(null)

      try {
        await loadVisTimeline()

        if (!mounted || !containerRef.current) return

        console.log('[Timeline] vis loaded, creating timeline...')
        console.log('[Timeline] containerRef.current =', containerRef.current)
        console.log('[Timeline] window.vis =', window.vis)
        console.log('[Timeline] window.vis.Timeline =', window.vis?.Timeline)
        console.log('[Timeline] window.vis.DataSet =', window.vis?.DataSet)

        const items: TimelineItem[] = []
        const orgMap = new Map(db.organizations.map(o => [o.id, o.name]))

        const fmtDate = (d?: { year: number; month?: number }) =>
          d ? `${d.year}-${String(d.month ?? 1).padStart(2, '0')}-01` : undefined

        const addMonth = (dateStr: string) => {
          const [y, m] = dateStr.split('-').map(Number)
          const ny = m === 12 ? y + 1 : y
          const nm = m === 12 ? 1 : m + 1
          return `${ny}-${String(nm).padStart(2, '0')}-01`
        }

        // vis-timeline requires `end` on range items; ongoing items end "today"
        const now = new Date()
        const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
        const resolveEnd = (start: string, end: string | undefined, ongoing?: boolean) => {
          const candidate = ongoing ? todayStr : end
          if (candidate && candidate > start) return candidate
          return addMonth(start)
        }

        // Add positions (color-coded by category: full-time / part-time / research / education)
        db.positions.forEach((pos: Position) => {
          const org = orgMap.get(pos.organization_id) || 'Unknown'
          const start = fmtDate(pos.start) ?? `${pos.start.year}-01-01`
          const end = resolveEnd(start, fmtDate(pos.end), pos.ongoing)
          const cat = categorizePosition(pos)
          const meta = CATEGORY_META[cat]

          items.push({
            id: pos.id,
            content: `<div style="white-space:normal"><strong>${pos.title}</strong><br><small>${org}</small><br><span class="tl-tag" style="background:${meta.bg};color:${meta.color}">${meta.label}</span></div>`,
            start,
            end,
            type: 'range',
            className: `tl-cat-${cat}`,
            title: `${pos.title} at ${org} (${meta.label}) — click to edit`,
            group: cat,
          })
        })

        // Add education
        db.education.forEach((edu) => {
          const org = orgMap.get(edu.organization_id) || 'Unknown'
          const start = fmtDate(edu.start) ?? `${edu.start.year}-01-01`
          const end = resolveEnd(start, fmtDate(edu.end), edu.ongoing)

          items.push({
            id: `edu_${edu.id}`,
            content: `<div style="white-space:normal"><strong>${edu.degree}</strong><br><small>${org}</small><br><span class="tl-tag" style="background:${CATEGORY_META.education.bg};color:${CATEGORY_META.education.color}">Education</span></div>`,
            start,
            end,
            type: 'range',
            className: 'tl-cat-education',
            title: `${edu.degree} at ${org}`,
            group: 'education',
          })
        })

        // Add projects
        db.projects.forEach((prj) => {
          const start = fmtDate(prj.start) ?? `${prj.start.year}-01-01`
          const end = resolveEnd(start, fmtDate(prj.end), prj.ongoing)

          items.push({
            id: `prj_${prj.id}`,
            content: `<div style="white-space:normal"><strong>${prj.title}</strong><br><span class="tl-tag" style="background:${PROJECT_CATEGORY.bg};color:${PROJECT_CATEGORY.color}">${PROJECT_CATEGORY.label}</span></div>`,
            start,
            end,
            type: 'range',
            className: 'tl-cat-project',
            title: prj.title,
            group: 'project',
          })
        })

        if (!mounted || !containerRef.current) return

        // Resolve UMD constructors before building options (groups need DataSet)
        const visAny = window.vis as any
        const TimelineCtor = visAny.Timeline || visAny.default?.Timeline
        const DataSetCtor = visAny.DataSet || visAny.default?.DataSet
        if (!TimelineCtor || !DataSetCtor) {
          throw new Error('Timeline or DataSet constructor not found on window.vis')
        }

        const usedGroups = new Set(items.map((i) => i.group))
        const laneDefs = LANE_DEFS.filter((g) => usedGroups.has(g.id))
        const groupItems = laneDefs.map((g) => ({
          id: g.id,
          content: g.label,
          className: `tl-lane tl-lane-${g.id}`,
        }))

        const options = {
          stack: true,
          height: '100%',
          minHeight: '700px',
          editable: false,
          showCurrentTime: true,
          zoomKey: 'ctrlKey',
          max: new Date(new Date().getFullYear() + 2, 0),
          min: new Date(2018, 0),
          orientation: 'top' as const,
          margin: { item: 10, axis: 20 },
          template: (item: any) => item.content,
          horizontalScroll: true,
          verticalScroll: true,
          groupOrder: (a: any, b: any) =>
            laneDefs.findIndex((g) => g.id === a.id) - laneDefs.findIndex((g) => g.id === b.id),
          groupOrderSortable: false,
          groupToggleVisible: true,
          groupHeightMode: 'auto' as const,
        }

        // Use the global vis object from UMD.
        // NOTE: this UMD build ignores options.groups — groups must be the
        // 3rd constructor arg: Timeline(container, items, groups, options).
        console.log('[Timeline] Creating Timeline instance...')
        const itemsDs = new DataSetCtor(items)
        const groupsDs = new DataSetCtor(groupItems)
        const tl = new TimelineCtor(containerRef.current, itemsDs, groupsDs, options)
        console.log('[Timeline] Timeline created successfully:', tl)
        timelineRef.current = tl

        tl.on('select', (props: any) => {
          if (props.items.length > 0) {
            const id = props.items[0]
            if (id.startsWith('edu_')) {
              setSelectedItem({ id, type: 'education' })
              setEditingPosition(null)
            } else if (id.startsWith('prj_')) {
              setSelectedItem({ id, type: 'project' })
              setEditingPosition(null)
            } else {
              const pos = db.positions.find((p) => p.id === id)
              if (pos) {
                setSelectedItem(null)
                setEditingPosition(pos)
              }
            }
          } else {
            setSelectedItem(null)
          }
        })

        // Fit all items initially
        tl.fit()

        // vis-timeline lazily skips rendering items in groups outside its
        // vertical scroll viewport (education/projects lanes sit below the
        // fold) and only computes group sizes during redraws. Iterate:
        // measure → grow → fit → re-measure until the layout is stable.
        let lastNeeded = -1
        let stableCount = 0
        let totalTicks = 0
        const fitAllLanes = () => {
          if (!mounted || !containerRef.current) return
          try {
            totalTicks++
            tl.redraw()
            const groups: Record<string, { top?: number; height?: number }> =
              (tl as any).itemSet?.groups || {}
            let needed = 0
            for (const key of Object.keys(groups)) {
              if (key === '__background__') continue
              const grp = groups[key]
              if (typeof grp.top === 'number' && typeof grp.height === 'number') {
                needed = Math.max(needed, grp.top + grp.height)
              }
            }
            const current = containerRef.current.clientHeight
            if (totalTicks >= 30) {
              tl.fit()
              return
            }
            if (needed > 0 && needed + 88 > current + 4) {
              stableCount = 0
              containerRef.current.style.height = `${Math.min(needed + 88, 2400)}px`
              tl.redraw()
              window.requestAnimationFrame(fitAllLanes)
            } else {
              if (needed === lastNeeded) stableCount++
              else stableCount = 0
              lastNeeded = needed
              tl.fit()
              if (stableCount < 3) window.requestAnimationFrame(fitAllLanes)
            }
          } catch (e) {
            // non-fatal: internal vertical scroll still works
            console.log('[Timeline] fitAllLanes error:', e)
          }
        }
        window.requestAnimationFrame(fitAllLanes)

      } catch (err) {
        console.error('Timeline initialization failed:', err)
        if (mounted) {
          setError(`Failed to load timeline: ${err instanceof Error ? err.message : String(err)}`)
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }

    initTimeline()

    return () => {
      mounted = false
      if (timelineRef.current) {
        timelineRef.current.destroy()
        timelineRef.current = null
      }
    }
  }, [db])

  const legendItems = db
    ? ([
        ...(['full-time', 'part-time', 'research'] as const).map((cat) => ({
          key: cat as string,
          label: CATEGORY_META[cat].label,
          color: CATEGORY_META[cat].color,
          bg: CATEGORY_META[cat].bg,
          count: db.positions.filter((p) => categorizePosition(p) === cat).length,
        })),
        {
          key: 'education',
          label: 'Education',
          color: CATEGORY_META.education.color,
          bg: CATEGORY_META.education.bg,
          count: db.education.length + db.positions.filter((p) => categorizePosition(p) === 'education').length,
        },
        {
          key: 'project',
          label: 'Project',
          color: PROJECT_CATEGORY.color,
          bg: PROJECT_CATEGORY.bg,
          count: db.projects.length,
        },
      ])
    : []

  const selectedEdu = selectedItem?.type === 'education' && db
    ? db.education.find((e) => `edu_${e.id}` === selectedItem.id)
    : undefined
  const selectedPrj = selectedItem?.type === 'project' && db
    ? db.projects.find((p) => `prj_${p.id}` === selectedItem.id)
    : undefined

  const orgName = (id?: string) => db?.organizations.find((o) => o.id === id)?.name ?? ''

  const closeDetails = () => {
    setSelectedItem(null)
    timelineRef.current?.setSelection?.([])
  }

  return (
    <div className="card">
      <AlertsPanel db={db} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h2 style={{ margin: 0 }}>Career Timeline</h2>
        <div className="d-flex gap-2 flex-wrap align-items-center">
          {legendItems.map((item) => (
            <span key={item.key} className="legend-chip">
              <span className="legend-swatch" style={{ background: item.bg, borderColor: item.color }} />
              {item.label}
              <span className="legend-count">{item.count}</span>
            </span>
          ))}
          <span className="text-muted" style={{ fontSize: '0.75rem', marginLeft: '0.5rem' }}>
            Click a bar to edit
          </span>
        </div>
      </div>

      <div
        ref={containerRef}
        className="timeline-container"
        style={{ height: 'calc(100vh - 320px)', minHeight: '700px', position: 'relative' }}
      >
        {loading && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6c757d', background: 'rgba(255,255,255,0.75)', zIndex: 2 }}>
            Loading timeline...
          </div>
        )}
        {error && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', background: 'rgba(255,255,255,0.9)', zIndex: 2 }}>
            <div style={{ background: '#f8d7da', border: '1px solid #f5c6cb', color: '#721c24', padding: '1rem', borderRadius: 6 }}>
              <strong>Timeline failed to load:</strong> {error}
              <br />
              <small>Check console for details.</small>
            </div>
          </div>
        )}
      </div>

      {selectedEdu && (
        <div className="card mt-3">
          <div className="d-flex justify-content-between align-items-center">
            <h4 style={{ margin: 0 }}>
              {selectedEdu.degree}
              <span className="tl-tag" style={{ background: CATEGORY_META.education.bg, color: CATEGORY_META.education.color, marginLeft: 8 }}>Education</span>
            </h4>
            <button className="btn btn-outline btn-sm" onClick={closeDetails}>Close</button>
          </div>
          <p className="text-muted" style={{ marginBottom: '0.25rem' }}>
            {orgName(selectedEdu.organization_id)} · {formatDatePrecision(selectedEdu.start)} – {selectedEdu.ongoing ? 'present' : formatDatePrecision(selectedEdu.end)}
          </p>
          {selectedEdu.thesis && <p style={{ marginBottom: 0 }}>Thesis: {selectedEdu.thesis}</p>}
          <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '0.5rem', marginBottom: 0 }}>
            Edit in the Knowledge Base tab.
          </p>
        </div>
      )}

      {selectedPrj && (
        <div className="card mt-3">
          <div className="d-flex justify-content-between align-items-center">
            <h4 style={{ margin: 0 }}>
              {selectedPrj.title}
              <span className="tl-tag" style={{ background: PROJECT_CATEGORY.bg, color: PROJECT_CATEGORY.color, marginLeft: 8 }}>{PROJECT_CATEGORY.label}</span>
            </h4>
            <button className="btn btn-outline btn-sm" onClick={closeDetails}>Close</button>
          </div>
          <p className="text-muted" style={{ marginBottom: '0.25rem' }}>
            {selectedPrj.organization_id ? `${orgName(selectedPrj.organization_id)} · ` : ''}
            {formatDatePrecision(selectedPrj.start)} – {selectedPrj.ongoing ? 'present' : formatDatePrecision(selectedPrj.end)}
          </p>
          {selectedPrj.summary && <p style={{ marginBottom: 0 }}>{selectedPrj.summary}</p>}
          <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '0.5rem', marginBottom: 0 }}>
            Edit in the Knowledge Base tab.
          </p>
        </div>
      )}

      {editingPosition && db && (
        <PositionEditModal
          position={editingPosition}
          db={db}
          onClose={() => {
            setEditingPosition(null)
            timelineRef.current?.setSelection?.([])
          }}
          onUpdate={onUpdate}
        />
      )}
    </div>
  )
}