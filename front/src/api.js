const API_BASE = ''

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function chat(prompt, role = 'admin', sessionId = null, model = null) {
  const body = { prompt, role }
  if (sessionId) body.session_id = sessionId
  if (model) body.model = model
  return request('/api/v1/chat', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function getVault(sessionId) {
  return request(`/api/v1/vault/${sessionId}`)
}

export async function deleteVault(sessionId) {
  return request(`/api/v1/vault/${sessionId}`, { method: 'DELETE' })
}

export async function getStats() {
  return request('/api/v1/stats')
}

export async function getAudit(limit = 20) {
  return request(`/api/v1/audit?limit=${limit}`)
}

export async function getSessionAudit(sessionId, limit = 50) {
  return request(`/api/v1/audit/${sessionId}?limit=${limit}`)
}

export async function getHealth() {
  return request('/health')
}
