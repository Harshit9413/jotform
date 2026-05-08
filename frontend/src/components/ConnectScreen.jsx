import { useState } from 'react'
import {
  Database, Lock, Eye, EyeOff, Zap, Shield, Brain,
  AlertCircle, ArrowRight, ShieldCheck,
} from 'lucide-react'

const DB_TYPES = [
  {
    label: 'PostgreSQL',
    example: 'postgresql://user:password@localhost:5432/mydb',
  },
  {
    label: 'MySQL',
    example: 'mysql+pymysql://user:password@localhost:3306/mydb',
  },
  {
    label: 'SQLite',
    example: 'sqlite:///path/to/database.db',
  },
]

const FEATURES = [
  {
    icon: Brain,
    cls: 'feat-purple',
    title: 'Groq AI Powered',
    desc: 'Understands complex questions and generates precise SQL instantly.',
  },
  {
    icon: Shield,
    cls: 'feat-cyan',
    title: 'Read-Only & Safe',
    desc: 'Only SELECT queries allowed. Your data is never modified.',
  },
  {
    icon: Zap,
    cls: 'feat-violet',
    title: 'Schema-Aware AI',
    desc: 'Full schema analysis — tables, columns, PKs, FKs and sample data.',
  },
]

export default function ConnectScreen({ onConnect }) {
  const [dbIndex, setDbIndex] = useState(0)
  const [dbUrl, setDbUrl] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const selectTab = (i) => {
    setDbIndex(i)
    setDbUrl('')
    setError('')
  }

  const handleConnect = async () => {
    setError('')
    if (!dbUrl.trim()) { setError('Please enter a database URL.'); return }
    if (!apiKey.trim()) { setError('Please enter your Groq API key.'); return }

    setLoading(true)
    try {
      const sessionId = crypto.randomUUID()
      const res = await fetch('/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          database_url: dbUrl.trim(),
          groq_api_key: apiKey.trim(),
          session_id: sessionId,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Connection failed.')
      onConnect({
        sessionId,
        schema: data.schema,
        tables: data.tables,
        dbType: data.db_type,
        totalTables: data.total_tables,
        totalColumns: data.total_columns,
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleConnect() }
  }

  return (
    <div className="connect-page">
      {/* animated blobs */}
      <div className="mesh-blob blob-purple" />
      <div className="mesh-blob blob-cyan" />
      <div className="mesh-blob blob-violet" />
      <div className="mesh-grid" />

      {/* ── Brand panel ── */}
      <div className="brand-panel">
        <div className="float-dots">
          <div className="float-dot" /><div className="float-dot" /><div className="float-dot" />
          <div className="float-dot" /><div className="float-dot" />
        </div>

        <div className="brand-logo">
          <div className="brand-logo-icon">
            <Database size={22} color="#fff" />
          </div>
          <div className="brand-logo-text">Query<span>Mind</span></div>
        </div>

        <h1 className="brand-hero">Chat with your<br /><span>Database</span></h1>
        <p className="brand-sub">
          Ask questions in plain English — QueryMind translates them to SQL,
          runs them safely, and explains the results instantly.
        </p>

        <div className="brand-features">
          {FEATURES.map(({ icon: Icon, cls, title, desc }) => (
            <div className="brand-feat" key={title}>
              <div className={`brand-feat-icon ${cls}`}>
                <Icon size={18} />
              </div>
              <div className="brand-feat-text">
                <strong>{title}</strong>
                <span>{desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Form panel ── */}
      <div className="form-panel">
        <div className="connect-card">
          <div className="card-header">
            <h2>Connect your Database</h2>
            <p>Enter your connection details to get started</p>
          </div>

          {/* DB type tabs */}
          <div className="db-tabs">
            {DB_TYPES.map((t, i) => (
              <button
                key={t.label}
                className={`db-tab${dbIndex === i ? ' active' : ''}`}
                onClick={() => selectTab(i)}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Database URL */}
          <div className="field">
            <div className="field-label">
              <Database size={12} />
              Database URL
            </div>
            <textarea
              rows={3}
              placeholder={DB_TYPES[dbIndex].example}
              value={dbUrl}
              onChange={e => setDbUrl(e.target.value)}
              onKeyDown={onKey}
            />
            <div className="field-hint">
              <Lock size={10} />
              Credentials stay in your browser — never logged or stored
            </div>
          </div>

          {/* Groq API Key */}
          <div className="field">
            <div className="field-label">
              <Brain size={12} />
              Groq API Key
            </div>
            <div className="input-wrap">
              <input
                type={showKey ? 'text' : 'password'}
                placeholder="gsk_..."
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
                onKeyDown={onKey}
              />
              <button className="eye-btn" onClick={() => setShowKey(s => !s)} tabIndex={-1}>
                {showKey ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            <div className="field-hint">
              Get yours at console.groq.com → API Keys
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="error-box">
              <AlertCircle size={14} />
              {error}
            </div>
          )}

          {/* Connect button */}
          <button className="connect-btn" onClick={handleConnect} disabled={loading}>
            <span className="btn-inner">
              {loading
                ? <><div className="spinner" /> Connecting...</>
                : <>Connect &amp; Start Chatting <ArrowRight size={15} /></>}
            </span>
          </button>

          <div className="security-note">
            <ShieldCheck size={12} color="var(--text3)" />
            Read-only queries only — your data is always safe
          </div>
        </div>
      </div>
    </div>
  )
}
