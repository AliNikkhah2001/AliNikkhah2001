const API_BASE = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const err = new Error(body?.detail || body?.error || `HTTP ${response.status}`) as Error & { payload?: unknown }
    err.payload = body
    throw err
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

async function requestText(path: string, options: RequestInit = {}): Promise<string> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
  })

  if (!response.ok) {
    const body = await response.text().catch(() => '')
    throw new Error(body.slice(0, 200) || `HTTP ${response.status}`)
  }

  return response.text()
}

export const api = {
  getDatabase: () => request<import('./types').CareerDatabase>('/db'),
  reloadDatabase: () => request('/db/reload', { method: 'POST' }),

  getProfile: () => request<import('./types').Profile>('/profile'),
  updateProfile: (data: any) => request<import('./types').Profile>('/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  listOrganizations: () => request<import('./types').Organization[]>('/organizations'),
  createOrganization: (org: import('./types').Organization) => request<import('./types').Organization>('/organizations', {
    method: 'POST',
    body: JSON.stringify(org),
  }),
  updateOrganization: (id: string, org: import('./types').Organization) => request<import('./types').Organization>(`/organizations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(org),
  }),
  deleteOrganization: (id: string) => request(`/organizations/${id}`, { method: 'DELETE' }),

  listPositions: () => request<import('./types').Position[]>('/positions'),
  createPosition: (pos: import('./types').Position) => request<import('./types').Position>('/positions', {
    method: 'POST',
    body: JSON.stringify(pos),
  }),
  updatePosition: (id: string, pos: import('./types').Position) => request<import('./types').Position>(`/positions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(pos),
  }),
  deletePosition: (id: string) => request(`/positions/${id}`, { method: 'DELETE' }),

  listAchievements: () => request<import('./types').Achievement[]>('/achievements'),
  createAchievement: (ach: import('./types').Achievement) => request<import('./types').Achievement>('/achievements', {
    method: 'POST',
    body: JSON.stringify(ach),
  }),
  updateAchievement: (id: string, ach: import('./types').Achievement) => request<import('./types').Achievement>(`/achievements/${id}`, {
    method: 'PUT',
    body: JSON.stringify(ach),
  }),
  deleteAchievement: (id: string) => request(`/achievements/${id}`, { method: 'DELETE' }),

  listProjects: () => request<import('./types').Project[]>('/projects'),
  createProject: (proj: import('./types').Project) => request<import('./types').Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(proj),
  }),
  updateProject: (id: string, proj: import('./types').Project) => request<import('./types').Project>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(proj),
  }),

  deriveTechStacks: () => request<{ updated_positions: number; skills_added: number }>('/positions/tech-stack/derive', {
    method: 'POST',
  }),

  listEducation: () => request<import('./types').Education[]>('/education'),
  listPublications: () => request<import('./types').Publication[]>('/publications'),
  listTeaching: () => request<import('./types').Teaching[]>('/teaching'),
  listSkills: () => request<import('./types').Skill[]>('/skills'),

  listVariants: () => request<import('./types').Variant[]>('/variants'),
  createVariant: (variant: import('./types').Variant) => request<import('./types').Variant>('/variants', {
    method: 'POST',
    body: JSON.stringify(variant),
  }),

  exportJsonResume: () => request<any>('/export/json-resume'),
  exportRenderCV: (variantId: string) => requestText(`/export/rendercv/${variantId}`),
  exportLinkedIn: () => request<any>('/export/linkedin'),
  exportGitHubReadme: () => request<{ content: string; format: string }>('/export/github-readme'),
  exportReactiveResume: () => request<any>('/export/reactive-resume'),
  exportJobOps: () => requestText('/export/jobops'),

  getValidation: () => request<import('./types').ValidationReport>('/validation'),

  listTemplates: () => request<import('./types').TemplateInfo[]>('/templates'),
  compileTemplate: (id: string, force = false) =>
    request<import('./types').CompileResult>(`/templates/${encodeURIComponent(id)}/compile`, {
      method: 'POST',
      body: JSON.stringify({ force }),
    }),
  getAts: (id: string) => request<import('./types').AtsResult>(`/ats/${encodeURIComponent(id)}`),

  getPublishingAudit: () => request<import('./types').PublishingAudit>('/publishing/audit'),

  search: (q: string) => request<any>(`/search?q=${encodeURIComponent(q)}`),
}