const BASE_URL = '/api'

function getAuthHeaders() {
  const token = localStorage.getItem('auth_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

async function handleResponse(res) {
  if (!res.ok) {
    let msg = `HTTP error ${res.status}`
    try {
      const data = await res.json()
      msg = data.detail || JSON.stringify(data)
    } catch (_) {}
    throw new Error(msg)
  }
  return res.json()
}

export async function searchAndIndex(params) {
  const res = await fetch(`${BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(params),
  })
  return handleResponse(res)
}

export async function askQuestion(params) {
  const res = await fetch(`${BASE_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(params),
  })
  return handleResponse(res)
}

export async function listArticles(params = {}) {
  const query = new URLSearchParams()
  if (params.keyword) query.set('keyword', params.keyword)
  if (params.journal) query.set('journal', params.journal)
  if (params.date_from) query.set('date_from', params.date_from)
  if (params.date_to) query.set('date_to', params.date_to)
  if (params.page) query.set('page', params.page)
  if (params.limit) query.set('limit', params.limit)

  const res = await fetch(`${BASE_URL}/articles?${query.toString()}`, {
    headers: { ...getAuthHeaders() },
  })
  return handleResponse(res)
}
