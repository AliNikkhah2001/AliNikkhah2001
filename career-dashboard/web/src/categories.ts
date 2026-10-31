import { Position } from './types'

export type Category = 'full-time' | 'part-time' | 'research' | 'education' | 'teaching'

export const CATEGORY_META: Record<Category, { label: string; color: string; bg: string }> = {
  'full-time': { label: 'Full-time', color: '#2563eb', bg: '#dbeafe' },
  'part-time': { label: 'Part-time', color: '#198754', bg: '#d1e7dd' },
  research: { label: 'Research', color: '#fd7e14', bg: '#fff3e0' },
  education: { label: 'Education', color: '#6f42c1', bg: '#f3e8ff' },
  teaching: { label: 'Teaching', color: '#db2777', bg: '#fce7f3' },
}

export const PROJECT_CATEGORY = { label: 'Project', color: '#0d9488', bg: '#e6f4f1' }

export function categorizePosition(pos: Position): Category {
  const t = pos.title.toLowerCase()
  if (t.includes('teaching assistant') || t.includes('instructor')) return 'teaching'
  // Full-time industry roles (incl. R&D Lead) belong to Full-time Work, not Research.
  if (pos.employment_type === 'full_time') return 'full-time'
  if (/research|\br&d\b|scholar|fellow|collaborator/.test(t)) return 'research'
  return 'part-time'
}

export function formatDatePrecision(d?: { year: number; month?: number }): string {
  if (!d) return '—'
  if (d.month) return `${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.month - 1]} ${d.year}`
  return String(d.year)
}
