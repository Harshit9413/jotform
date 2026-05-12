import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'

export default function AuthPage() {
  const { login } = useAuth()
  const [tab, setTab] = useState('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const reset = () => { setName(''); setEmail(''); setPassword(''); setError('') }

  const handleSubmit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const body = tab === 'login'
        ? { email, password }
        : { name: name.trim(), email, password }
      const res = await fetch(tab === 'login' ? '/api/auth/login' : '/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Something went wrong')
      login(data.token, data.user)
      window.location.replace('/activity')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: "'DM Sans', 'Segoe UI', sans-serif", padding: 20 }}>
      <div style={{ marginBottom: 32, textAlign: 'center' }}>
        <div style={{ fontFamily: 'serif', fontSize: 26, fontWeight: 700, color: '#1a56db' }}>
          Form<span style={{ color: '#0f172a' }}>Craft</span>
          <span style={{ color: '#94a3b8', margin: '0 10px', fontFamily: 'sans-serif', fontWeight: 300 }}>|</span>
          <span style={{ color: '#6c63ff', fontFamily: 'sans-serif', fontSize: '22px' }}>Query</span>
          <span style={{ color: '#0f172a', fontFamily: 'sans-serif', fontSize: '22px' }}>Mind</span>
        </div>
        <p style={{ color: '#64748b', fontSize: 13, marginTop: 6 }}>Sign in to manage your forms and queries</p>
      </div>

      <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #e2e8f0', boxShadow: '0 4px 24px rgba(15,23,42,.08)', width: '100%', maxWidth: 420, overflow: 'hidden' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0' }}>
          {[['login', 'Sign In'], ['register', 'Create Account']].map(([key, label]) => (
            <button key={key} onClick={() => { setTab(key); reset() }}
              style={{ flex: 1, padding: '16px', border: 'none', background: 'none', fontSize: 14, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', color: tab === key ? '#1a56db' : '#64748b', borderBottom: tab === key ? '2px solid #1a56db' : '2px solid transparent', transition: 'all .15s' }}>
              {label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '28px 28px 24px' }}>
          {tab === 'register' && (
            <div style={fg}>
              <label style={lbl}>Full Name</label>
              <input style={inp} type="text" placeholder="John Doe" value={name} onChange={e => setName(e.target.value)} required autoFocus />
            </div>
          )}
          <div style={fg}>
            <label style={lbl}>Email Address</label>
            <input style={inp} type="email" placeholder="you@email.com" value={email} onChange={e => setEmail(e.target.value)} required autoFocus={tab === 'login'} />
          </div>
          <div style={{ ...fg, marginBottom: 0 }}>
            <label style={lbl}>Password</label>
            <input style={inp} type="password" placeholder={tab === 'register' ? 'At least 6 characters' : 'Your password'} value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
          </div>

          {error && (
            <div style={{ marginTop: 12, padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#dc2626', fontSize: 13 }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}
            style={{ width: '100%', marginTop: 20, padding: '12px', border: 'none', borderRadius: 10, background: loading ? '#93c5fd' : '#1a56db', color: '#fff', fontSize: 14, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer', fontFamily: 'inherit', transition: 'background .2s' }}>
            {loading ? 'Please wait...' : tab === 'login' ? 'Sign In' : 'Create Account'}
          </button>

          <p style={{ textAlign: 'center', fontSize: 12, color: '#94a3b8', marginTop: 16, marginBottom: 0 }}>
            {tab === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button type="button" onClick={() => { setTab(tab === 'login' ? 'register' : 'login'); reset() }}
              style={{ background: 'none', border: 'none', color: '#1a56db', fontWeight: 600, cursor: 'pointer', fontSize: 12, padding: 0, fontFamily: 'inherit' }}>
              {tab === 'login' ? 'Create one' : 'Sign in'}
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}

const fg = { display: 'flex', flexDirection: 'column', gap: 5, marginBottom: 14 }
const lbl = { fontSize: 13, fontWeight: 600, color: '#0f172a' }
const inp = { padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, fontFamily: 'inherit', color: '#0f172a', background: '#fff', outline: 'none', width: '100%', boxSizing: 'border-box' }
