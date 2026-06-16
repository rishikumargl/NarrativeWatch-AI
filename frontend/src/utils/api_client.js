/**
 * API client that automatically includes JWT token in requests
 */

export function getAuthHeaders() {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json'
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

export async function apiCall(url, options = {}) {
  const headers = {
    ...getAuthHeaders(),
    ...options.headers
  }

  const response = await fetch(url, {
    ...options,
    headers
  })

  return response
}

export async function apiCallJson(url, options = {}) {
  const response = await apiCall(url, options)
  return response.json()
}

export async function apiPost(url, body, options = {}) {
  return apiCall(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body)
  })
}

export async function apiPostJson(url, body, options = {}) {
  const response = await apiPost(url, body, options)
  return response.json()
}

export async function apiGet(url, options = {}) {
  return apiCall(url, {
    ...options,
    method: 'GET'
  })
}

export async function apiGetJson(url, options = {}) {
  const response = await apiGet(url, options)
  return response.json()
}

export async function apiDelete(url, options = {}) {
  return apiCall(url, {
    ...options,
    method: 'DELETE'
  })
}

export async function apiDeleteJson(url, options = {}) {
  const response = await apiDelete(url, options)
  return response.json()
}

export async function apiPut(url, body, options = {}) {
  return apiCall(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(body)
  })
}

export async function apiPutJson(url, body, options = {}) {
  const response = await apiPut(url, body, options)
  return response.json()
}
