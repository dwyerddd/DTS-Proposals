// Small fetch wrapper for the FastAPI backend. Every screen imports from
// here rather than calling fetch() directly, so the base URL and error
// handling only live in one place.

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

function qs(params) {
  const clean = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
  )
  const s = new URLSearchParams(clean).toString()
  return s ? `?${s}` : ''
}

export const companiesApi = {
  list: (params = {}) => request(`/companies${qs(params)}`),
  get: (id) => request(`/companies/${id}`),
  create: (data) => request('/companies', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/companies/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  archive: (id) => request(`/companies/${id}/archive`, { method: 'PATCH' }),
  restore: (id) => request(`/companies/${id}/restore`, { method: 'PATCH' }),
}

export const contactsApi = {
  list: (params = {}) => request(`/contacts${qs(params)}`),
  get: (id) => request(`/contacts/${id}`),
  create: (data) => request('/contacts', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/contacts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  archive: (id) => request(`/contacts/${id}/archive`, { method: 'PATCH' }),
  restore: (id) => request(`/contacts/${id}/restore`, { method: 'PATCH' }),
}
