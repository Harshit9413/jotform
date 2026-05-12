import { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)
const STORAGE_KEY = 'fc_auth'

function loadAuth() {
  try {
    const s = localStorage.getItem(STORAGE_KEY)
    return s ? JSON.parse(s) : null
  } catch { return null }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadAuth)

  const login = useCallback((token, user) => {
    const data = { token, user }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    setAuth(data)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    setAuth(null)
  }, [])

  return (
    <AuthContext.Provider value={{ auth, login, logout, isLoggedIn: !!auth }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
