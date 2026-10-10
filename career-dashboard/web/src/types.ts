export interface DatePrecision {
  year: number
  month?: number
  day?: number
}

export interface Organization {
  id: string
  name: string
  aliases: string[]
  url?: string
  type: 'employer' | 'university' | 'research_lab' | 'other'
}

export interface Achievement {
  id: string
  position_id?: string
  project_id?: string
  text: string
  brief_text?: string
  detailed_text?: string
  metrics: Record<string, any>
  skills: string[]
  source_refs: string[]
  verified: boolean
}

export interface Position {
  id: string
  organization_id: string
  title: string
  start: DatePrecision
  end?: DatePrecision
  ongoing: boolean
  employment_type: 'full_time' | 'part_time' | 'contract' | 'internship' | 'fellowship'
  location?: string
  remote: boolean
  work_model?: string
  summary?: string
  description_md?: string
  tech_stack: string[]
  achievements: string[]
  promotion_of?: string
  concurrent_with: string[]
  concurrent_note?: string
}

export interface Project {
  id: string
  title: string
  organization_id?: string
  start: DatePrecision
  end?: DatePrecision
  ongoing: boolean
  summary?: string
  description?: string
  skills: string[]
  achievements: string[]
  position_ids: string[]
  url?: string
}

export interface Education {
  id: string
  organization_id: string
  degree: string
  field?: string
  start: DatePrecision
  end?: DatePrecision
  ongoing: boolean
  gpa?: string
  thesis?: string
  coursework: string[]
}

export interface Publication {
  id: string
  title: string
  authors: string[]
  venue?: string
  year: number
  url?: string
  status: 'published' | 'preprint' | 'in_preparation' | 'under_review'
}

export interface Teaching {
  id: string
  course: string
  role: string
  organization_id?: string
  period: string
  students?: number
}

export interface Skill {
  id: string
  name: string
  category: 'language' | 'ml_vision' | 'agentic' | 'llm_serving' | 'data_mlop' | 'human'
  proficiency?: string
  aliases: string[]
}

export interface Profile {
  id: string
  name: string
  headline: string
  email: string
  phone?: string
  location: string
  website?: string
  linkedin?: string
  github?: string
  summary: string
  summary_brief?: string
  summary_detailed?: string
}

export interface Variant {
  id: string
  label: string
  audience: 'academic' | 'industry' | 'research' | 'general'
  length_target: '1page' | '2page' | '4page' | '10page'
  template: string
  sections: string[]
  position_ids: string[]
  achievement_overrides: Record<string, string>
  wording_level: 'brief' | 'standard' | 'detailed'
  page_limit: number
}

export interface CareerDatabase {
  schema_version: number
  profile: Profile
  organizations: Organization[]
  positions: Position[]
  projects: Project[]
  education: Education[]
  publications: Publication[]
  teaching: Teaching[]
  skills: Skill[]
  achievements: Achievement[]
  variants: Variant[]
}

export interface ValidationIssue {
  severity: 'error' | 'warning' | 'info'
  kind: string
  message: string
  position_ids: string[]
}

export interface ValidationReport {
  issues: ValidationIssue[]
  counts: { error: number; warning: number; info: number }
  total: number
}

export interface TemplateInfo {
  id: string
  name: string
  family: string
  engine: string
  data_source: 'live' | 'sample'
  description: string
  compiled: boolean
  stale: boolean
  pages: number | null
  pdf_url: string | null
  hash: string
}

export interface CompileResult {
  ok: boolean
  cached?: boolean
  pages?: number | null
  duration?: number
  error?: string
  log?: string
}

export interface AtsCheck {
  key: string
  label: string
  weight: number
  score: number
  detail: string
}

export interface AtsResult {
  score: number
  grade: string
  pages: number | null
  checks: AtsCheck[]
  issues: { check: string; lost: number; fix: string }[]
  summary: string
}

export interface PublishingModule {
  id: string
  name: string
  kind: string
  status: 'synced' | 'stale' | 'missing' | 'ready' | 'external' | 'error'
  detail: string
  last_sync?: string
  url?: string
  actions: string[]
}

export interface PublishingAudit {
  generated_at: string
  db_fingerprint: string
  modules: PublishingModule[]
  dry_run: string[]
}