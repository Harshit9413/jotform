export function authHeaders() {
  try {
    const s = localStorage.getItem('fc_auth')
    if (!s) return {}
    const { token } = JSON.parse(s)
    return token ? { Authorization: `Bearer ${token}` } : {}
  } catch { return {} }
}

export async function authFetch(url, options = {}) {
  return fetch(url, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  })
}
