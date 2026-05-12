import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ConnectScreen from './ConnectScreen'
import ChatScreen from './ChatScreen'
import { authHeaders } from '../../utils/api'

function RagTab() {
  const navigate = useNavigate()
  const [kbs, setKbs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', groq_api_key: '' })
  const [creating, setCreating] = useState(false)
  const [createErr, setCreateErr] = useState('')
  const [deleting, setDeleting] = useState(null)

  const load = () => {
    setLoading(true)
    fetch('/api/rag/kb', { headers: authHeaders() })
      .then(r => r.json())
      .then(data => { setKbs(Array.isArray(data) ? data : []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleCreate = async e => {
    e.preventDefault()
    if (!form.name.trim() || !form.groq_api_key.trim()) return
    setCreating(true)
    setCreateErr('')
    try {
      const res = await fetch('/api/rag/kb', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Failed to create')
      setShowCreate(false)
      setForm({ name: '', description: '', groq_api_key: '' })
      navigate(`/querymind/kb/${data.id}`)
    } catch (err) {
      setCreateErr(err.message)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (kb) => {
    if (!confirm(`Delete "${kb.name}"? This will also remove all its documents.`)) return
    setDeleting(kb.id)
    try {
      await fetch(`/api/rag/kb/${kb.id}`, { method: 'DELETE', headers: authHeaders() })
      load()
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '32px' }}>
      <div style={{ maxWidth: 860, margin: '0 auto' }}>
        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: '#0f172a', margin: 0 }}>AI Knowledge Bases</h2>
            <p style={{ fontSize: 13, color: '#64748b', margin: '4px 0 0' }}>
              Create a knowledge base, upload documents, then embed the chatbot on any website.
            </p>
          </div>
          <button onClick={() => setShowCreate(true)}
            style={{ padding: '10px 20px', border: 'none', borderRadius: 10, background: '#6c63ff', color: '#fff', fontSize: 13, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', flexShrink: 0 }}>
            + New Knowledge Base
          </button>
        </div>

        {/* Create form */}
        {showCreate && (
          <div style={{ background: '#fff', border: '1.5px solid #ddd6fe', borderRadius: 16, padding: '24px', marginBottom: 24, boxShadow: '0 4px 20px rgba(108,99,255,.12)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: '0 0 18px' }}>Create Knowledge Base</h3>
            <form onSubmit={handleCreate}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
                <div>
                  <label style={lbl}>Name *</label>
                  <input style={inp} placeholder="e.g. Customer Support Bot" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} required />
                </div>
                <div>
                  <label style={lbl}>Description</label>
                  <input style={inp} placeholder="What does this chatbot help with?" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
                </div>
              </div>
              <div style={{ marginBottom: 14 }}>
                <label style={lbl}>Groq API Key *</label>
                <input style={inp} type="password" placeholder="gsk_..." value={form.groq_api_key} onChange={e => setForm(f => ({ ...f, groq_api_key: e.target.value }))} required />
                <p style={{ fontSize: 11, color: '#94a3b8', margin: '5px 0 0' }}>Get a free key at console.groq.com — stored securely in your account.</p>
              </div>
              {createErr && <div style={{ padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#dc2626', fontSize: 13, marginBottom: 14 }}>{createErr}</div>}
              <div style={{ display: 'flex', gap: 10 }}>
                <button type="submit" disabled={creating}
                  style={{ padding: '10px 24px', border: 'none', borderRadius: 9, background: creating ? '#a5b4fc' : '#6c63ff', color: '#fff', fontSize: 13, fontWeight: 700, cursor: creating ? 'not-allowed' : 'pointer', fontFamily: 'inherit' }}>
                  {creating ? 'Creating...' : 'Create & Configure →'}
                </button>
                <button type="button" onClick={() => { setShowCreate(false); setCreateErr('') }}
                  style={{ padding: '10px 16px', border: '1.5px solid #e2e8f0', borderRadius: 9, background: '#fff', color: '#64748b', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* KB list */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div style={{ width: 32, height: 32, border: '3px solid #e2e8f0', borderTopColor: '#6c63ff', borderRadius: '50%', animation: 'spin .8s linear infinite', margin: '0 auto 12px' }} />
            <p style={{ color: '#94a3b8', fontSize: 13 }}>Loading...</p>
            <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
          </div>
        ) : kbs.length === 0 ? (
          <div style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, padding: '64px 32px', textAlign: 'center' }}>
            <div style={{ fontSize: 56, marginBottom: 16 }}>🧠</div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', margin: '0 0 8px' }}>No knowledge bases yet</h3>
            <p style={{ fontSize: 13, color: '#64748b', margin: '0 0 24px', maxWidth: 400, marginLeft: 'auto', marginRight: 'auto' }}>
              Create your first knowledge base, upload documents, and get an embeddable AI chatbot for your website — in minutes.
            </p>
            <button onClick={() => setShowCreate(true)}
              style={{ padding: '12px 28px', border: 'none', borderRadius: 10, background: '#6c63ff', color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
              + Create Knowledge Base
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 16 }}>
            {kbs.map(kb => (
              <div key={kb.id} style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, padding: '20px', boxShadow: '0 2px 8px rgba(15,23,42,.06)', display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                  <div style={{ width: 42, height: 42, borderRadius: 12, background: 'linear-gradient(135deg,#ede9fe,#ddd6fe)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, flexShrink: 0 }}>🧠</div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{kb.name}</div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{kb.description || 'No description'}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <span style={{ fontSize: 11, fontWeight: 600, color: '#6c63ff', background: '#ede9fe', padding: '3px 10px', borderRadius: 20 }}>
                    {kb.doc_count} {kb.doc_count === 1 ? 'doc' : 'docs'}
                  </span>
                  <span style={{ fontSize: 11, color: '#94a3b8' }}>
                    {new Date(kb.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button onClick={() => navigate(`/querymind/kb/${kb.id}`)}
                    style={{ flex: 1, padding: '8px', border: 'none', borderRadius: 8, background: '#6c63ff', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
                    Manage →
                  </button>
                  <a href={`/chat/${kb.id}`} target="_blank" rel="noopener noreferrer"
                    style={{ padding: '8px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', color: '#64748b', fontSize: 12, fontWeight: 600, textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
                    ↗
                  </a>
                  <button onClick={() => handleDelete(kb)} disabled={deleting === kb.id}
                    style={{ padding: '8px 12px', border: '1.5px solid #fecaca', borderRadius: 8, background: '#fef2f2', color: '#dc2626', fontSize: 12, cursor: 'pointer', fontFamily: 'inherit' }}>
                    {deleting === kb.id ? '...' : '🗑'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* How it works */}
        <div style={{ marginTop: 32, background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, padding: '24px' }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: '0 0 16px' }}>How it works</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
            {[
              { num: '1', title: 'Create KB', desc: 'Give your chatbot a name and add your Groq API key.' },
              { num: '2', title: 'Upload Docs', desc: 'Upload .txt, .pdf or .md files as the knowledge source.' },
              { num: '3', title: 'Embed & Share', desc: 'Copy the iframe code and paste it into any website.' },
            ].map(s => (
              <div key={s.num} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <div style={{ width: 28, height: 28, borderRadius: '50%', background: '#6c63ff', color: '#fff', fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{s.num}</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{s.title}</div>
                  <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function QueryMindPage() {
  const [tab, setTab] = useState('rag')
  const [session, setSession] = useState(null)

  const sqlContent = session
    ? <ChatScreen session={session} onDisconnect={() => setSession(null)} />
    : <ConnectScreen onConnect={setSession} />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f172a', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 0, background: '#1e293b', borderBottom: '1px solid #334155', flexShrink: 0, padding: '0 24px' }}>
        <div style={{ fontFamily: 'serif', fontSize: 18, fontWeight: 700, color: '#6c63ff', padding: '14px 0', marginRight: 32, whiteSpace: 'nowrap' }}>
          Query<span style={{ color: '#fff' }}>Mind</span>
        </div>
        {[
          { key: 'rag', label: '🤖 AI Chatbot' },
          { key: 'sql', label: '🗄️ SQL Query' },
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            style={{
              padding: '16px 18px', border: 'none', background: 'none', cursor: 'pointer', fontFamily: 'inherit',
              fontSize: 13, fontWeight: tab === t.key ? 700 : 500,
              color: tab === t.key ? '#6c63ff' : '#94a3b8',
              borderBottom: tab === t.key ? '2px solid #6c63ff' : '2px solid transparent',
              transition: 'all .15s',
            }}>
            {t.label}
          </button>
        ))}
        <div style={{ marginLeft: 'auto' }}>
          <a href="/activity" style={{ color: '#64748b', fontSize: 12, textDecoration: 'none' }}>← Back to Dashboard</a>
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', background: tab === 'rag' ? '#f1f5f9' : '#0f172a' }}>
        {tab === 'rag' ? <RagTab /> : sqlContent}
      </div>
    </div>
  )
}

const lbl = { fontSize: 13, fontWeight: 600, color: '#0f172a', display: 'block', marginBottom: 5 }
const inp = { padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 13, fontFamily: 'inherit', color: '#0f172a', background: '#fff', outline: 'none', width: '100%', boxSizing: 'border-box' }
