import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { authHeaders } from '../../utils/api'

function ChatPreview({ kbId }) {
  const [messages, setMessages] = useState([{ role: 'assistant', content: 'Hi! Ask me anything about this knowledge base.' }])
  const [input, setInput] = useState('')
  const [thinking, setThinking] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, thinking])

  const send = async () => {
    const q = input.trim()
    if (!q || thinking) return
    setInput('')
    const updated = [...messages, { role: 'user', content: q }]
    setMessages(updated)
    setThinking(true)
    try {
      const res = await fetch(`/api/rag/chat/${kbId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, history: updated.slice(-6) }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error')
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
    } finally {
      setThinking(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 380, border: '1.5px solid #e2e8f0', borderRadius: 12, overflow: 'hidden', background: '#f8fafc' }}>
      <div style={{ background: 'linear-gradient(135deg,#1a56db,#6c63ff)', padding: '10px 16px', fontSize: 13, fontWeight: 700, color: '#fff' }}>
        🤖 Chat Preview
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              maxWidth: '80%', padding: '8px 12px', borderRadius: m.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
              background: m.role === 'user' ? '#1a56db' : '#fff',
              color: m.role === 'user' ? '#fff' : '#0f172a',
              fontSize: 13, lineHeight: 1.5,
              border: m.role === 'assistant' ? '1px solid #e2e8f0' : 'none',
              whiteSpace: 'pre-wrap',
            }}>
              {m.content}
            </div>
          </div>
        ))}
        {thinking && (
          <div style={{ display: 'flex', gap: 4, padding: '8px 12px', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '14px 14px 14px 4px', width: 'fit-content' }}>
            {[0, 1, 2].map(i => (
              <div key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: '#1a56db', animation: `bounce .8s ${i * .15}s infinite` }} />
            ))}
            <style>{`@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}`}</style>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div style={{ display: 'flex', gap: 8, padding: '10px 12px', background: '#fff', borderTop: '1px solid #e2e8f0' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          placeholder="Ask a question..."
          disabled={thinking}
          style={{ flex: 1, padding: '8px 12px', border: '1.5px solid #e2e8f0', borderRadius: 20, fontSize: 13, fontFamily: 'inherit', outline: 'none', background: '#f8fafc', color: '#0f172a' }}
        />
        <button
          onClick={send}
          disabled={!input.trim() || thinking}
          style={{ padding: '8px 16px', border: 'none', borderRadius: 20, background: (!input.trim() || thinking) ? '#e2e8f0' : '#1a56db', color: '#fff', fontSize: 13, fontWeight: 600, cursor: (!input.trim() || thinking) ? 'not-allowed' : 'pointer', fontFamily: 'inherit' }}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default function KBDetailPage() {
  const { kbId } = useParams()
  const navigate = useNavigate()
  const [kb, setKb] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')
  const [deleting, setDeleting] = useState(null)
  const [copied, setCopied] = useState(false)
  const fileRef = useRef(null)

  const embedUrl = `${window.location.origin}/chat/${kbId}`
  const embedCode = `<iframe src="${embedUrl}" width="400" height="600" frameborder="0" allow="microphone"></iframe>`

  const load = () => {
    fetch(`/api/rag/kb/${kbId}`, { headers: authHeaders() })
      .then(r => r.json())
      .then(data => { setKb(data); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [kbId])

  const handleUpload = async e => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadMsg('')
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch(`/api/rag/kb/${kbId}/docs`, {
        method: 'POST',
        headers: authHeaders(),
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Upload failed')
      setUploadMsg(`✓ "${data.filename}" uploaded (${data.chars.toLocaleString()} chars)`)
      load()
    } catch (err) {
      setUploadMsg(`✗ ${err.message}`)
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const handleDeleteDoc = async (docId) => {
    if (!confirm('Delete this document?')) return
    setDeleting(docId)
    try {
      await fetch(`/api/rag/kb/${kbId}/docs/${docId}`, { method: 'DELETE', headers: authHeaders() })
      load()
    } finally {
      setDeleting(null)
    }
  }

  const copyEmbed = async () => {
    try {
      await navigator.clipboard.writeText(embedCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
    } catch { }
  }

  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ width: 32, height: 32, border: '3px solid #e2e8f0', borderTopColor: '#1a56db', borderRadius: '50%', animation: 'spin .8s linear infinite', margin: '0 auto 12px' }} />
        <p style={{ color: '#64748b', fontSize: 13 }}>Loading...</p>
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    </div>
  )

  if (!kb) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 40, marginBottom: 12 }}>❌</div>
        <p style={{ color: '#64748b' }}>Knowledge base not found.</p>
        <button onClick={() => navigate('/querymind')} style={btn}>← Back</button>
      </div>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', background: '#f1f5f9', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg,#1a56db 0%,#1e40af 60%,#6c63ff 100%)', padding: '20px 0 32px' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 32px' }}>
          <button onClick={() => navigate('/querymind')} style={{ background: 'rgba(255,255,255,.15)', border: 'none', color: 'rgba(255,255,255,.9)', padding: '6px 14px', borderRadius: 8, fontSize: 13, cursor: 'pointer', fontFamily: 'inherit', marginBottom: 16 }}>
            ← Back to QueryMind
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 48, height: 48, borderRadius: 14, background: 'rgba(255,255,255,.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22 }}>🧠</div>
            <div>
              <h1 style={{ color: '#fff', fontSize: 22, fontWeight: 800, margin: 0 }}>{kb.name}</h1>
              {kb.description && <p style={{ color: 'rgba(255,255,255,.75)', fontSize: 13, margin: '4px 0 0' }}>{kb.description}</p>}
            </div>
            <div style={{ marginLeft: 'auto' }}>
              <a href={embedUrl} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-block', padding: '9px 18px', border: '1.5px solid rgba(255,255,255,.35)', borderRadius: 9, background: 'rgba(255,255,255,.1)', color: '#fff', fontSize: 13, fontWeight: 600, textDecoration: 'none' }}>
                ↗ Open Chat
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1100, margin: '-20px auto 0', padding: '0 32px 48px', display: 'grid', gridTemplateColumns: '340px 1fr', gap: 24 }}>

        {/* Left: Documents */}
        <div>
          <div style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, overflow: 'hidden', boxShadow: '0 2px 8px rgba(15,23,42,.06)' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h2 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: 0 }}>Documents</h2>
                <p style={{ fontSize: 11, color: '#94a3b8', margin: '2px 0 0' }}>{kb.documents?.length || 0} uploaded</p>
              </div>
              <button onClick={() => fileRef.current?.click()} disabled={uploading}
                style={{ padding: '6px 14px', border: 'none', borderRadius: 8, background: uploading ? '#93c5fd' : '#1a56db', color: '#fff', fontSize: 12, fontWeight: 700, cursor: uploading ? 'not-allowed' : 'pointer', fontFamily: 'inherit' }}>
                {uploading ? 'Uploading...' : '+ Upload'}
              </button>
              <input ref={fileRef} type="file" accept=".txt,.pdf,.md,.csv" style={{ display: 'none' }} onChange={handleUpload} />
            </div>

            {uploadMsg && (
              <div style={{ padding: '10px 16px', background: uploadMsg.startsWith('✓') ? '#ecfdf5' : '#fef2f2', borderBottom: '1px solid #e2e8f0', fontSize: 12, color: uploadMsg.startsWith('✓') ? '#059669' : '#dc2626' }}>
                {uploadMsg}
              </div>
            )}

            <div style={{ padding: '8px 0' }}>
              {!kb.documents?.length ? (
                <div style={{ padding: '32px 20px', textAlign: 'center', color: '#94a3b8', fontSize: 13 }}>
                  <div style={{ fontSize: 32, marginBottom: 8 }}>📄</div>
                  No documents yet.<br />Upload a .txt or .pdf file to get started.
                </div>
              ) : (
                kb.documents.map(doc => (
                  <div key={doc.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 16px', borderBottom: '1px solid #f1f5f9' }}
                    onMouseEnter={e => e.currentTarget.style.background = '#f8fafc'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, flexShrink: 0 }}>
                      {doc.filename.endsWith('.pdf') ? '📕' : '📄'}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.filename}</div>
                      <div style={{ fontSize: 11, color: '#94a3b8' }}>{doc.chars?.toLocaleString()} chars</div>
                    </div>
                    <button onClick={() => handleDeleteDoc(doc.id)} disabled={deleting === doc.id}
                      style={{ padding: '3px 8px', border: '1px solid #fecaca', borderRadius: 5, background: '#fef2f2', color: '#dc2626', fontSize: 11, cursor: 'pointer', fontFamily: 'inherit' }}>
                      {deleting === doc.id ? '...' : '✕'}
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Accepted formats */}
          <div style={{ marginTop: 12, padding: '12px 16px', background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 12, fontSize: 12, color: '#64748b' }}>
            <strong style={{ color: '#0f172a' }}>Accepted formats:</strong> .txt, .pdf, .md, .csv
            <br /><span style={{ color: '#94a3b8' }}>Max recommended: 5MB per file</span>
          </div>
        </div>

        {/* Right: Chat + Embed */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Chat preview */}
          <div style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, overflow: 'hidden', boxShadow: '0 2px 8px rgba(15,23,42,.06)' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0' }}>
              <h2 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: 0 }}>Test Your Chatbot</h2>
              <p style={{ fontSize: 12, color: '#94a3b8', margin: '2px 0 0' }}>Try asking questions to see how the AI responds</p>
            </div>
            <div style={{ padding: 16 }}>
              {!kb.documents?.length ? (
                <div style={{ padding: '40px 20px', textAlign: 'center', color: '#94a3b8', fontSize: 13 }}>
                  Upload at least one document to test the chatbot.
                </div>
              ) : (
                <ChatPreview kbId={kbId} />
              )}
            </div>
          </div>

          {/* Embed code */}
          <div style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, overflow: 'hidden', boxShadow: '0 2px 8px rgba(15,23,42,.06)' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0' }}>
              <h2 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: 0 }}>Embed on Your Website</h2>
              <p style={{ fontSize: 12, color: '#94a3b8', margin: '2px 0 0' }}>Copy this code and paste it anywhere on your website</p>
            </div>
            <div style={{ padding: '16px 20px' }}>
              <div style={{ background: '#0f172a', borderRadius: 10, padding: '14px 16px', fontFamily: 'monospace', fontSize: 12, color: '#e2e8f0', lineHeight: 1.7, wordBreak: 'break-all', marginBottom: 12 }}>
                {embedCode}
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                <button onClick={copyEmbed}
                  style={{ flex: 1, padding: '10px', border: 'none', borderRadius: 9, background: copied ? '#059669' : '#1a56db', color: '#fff', fontSize: 13, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', transition: 'background .2s' }}>
                  {copied ? '✓ Copied!' : '📋 Copy Embed Code'}
                </button>
                <a href={embedUrl} target="_blank" rel="noopener noreferrer"
                  style={{ padding: '10px 16px', border: '1.5px solid #e2e8f0', borderRadius: 9, background: '#fff', color: '#1a56db', fontSize: 13, fontWeight: 600, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}>
                  ↗ Preview
                </a>
              </div>
              <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 10, marginBottom: 0 }}>
                Anyone with the link can chat — no login required. Customize width/height in the iframe tag.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const btn = { padding: '8px 18px', border: 'none', borderRadius: 8, background: '#1a56db', color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', marginTop: 12 }
