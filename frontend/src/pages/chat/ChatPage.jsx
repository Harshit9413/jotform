import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'

export default function ChatPage() {
  const { kbId } = useParams()
  const [kb, setKb] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [thinking, setThinking] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    fetch(`/api/rag/public/${kbId}`)
      .then(r => r.json())
      .then(data => {
        if (data.detail) { setError(data.detail); setLoading(false); return }
        setKb(data)
        setMessages([{ role: 'assistant', content: `Hi! I'm the AI assistant for **${data.name}**. ${data.description ? data.description + ' ' : ''}How can I help you?` }])
        setLoading(false)
      })
      .catch(() => { setError('Failed to load chatbot'); setLoading(false) })
  }, [kbId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  const send = async () => {
    const q = input.trim()
    if (!q || thinking) return
    setInput('')
    const newMessages = [...messages, { role: 'user', content: q }]
    setMessages(newMessages)
    setThinking(true)
    try {
      const res = await fetch(`/api/rag/chat/${kbId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, history: newMessages.slice(-6) }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error')
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Sorry, something went wrong: ${err.message}` }])
    } finally {
      setThinking(false)
    }
  }

  const handleKey = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }

  if (loading) return (
    <div style={fullPage}>
      <div style={{ textAlign: 'center' }}>
        <div style={spinner} />
        <p style={{ color: '#64748b', fontSize: 13, marginTop: 12 }}>Loading chatbot...</p>
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    </div>
  )

  if (error) return (
    <div style={fullPage}>
      <div style={{ textAlign: 'center', color: '#dc2626', fontSize: 14 }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>⚠️</div>
        {error}
      </div>
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#f8fafc', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg,#1a56db,#6c63ff)', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
        <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>🤖</div>
        <div>
          <div style={{ color: '#fff', fontWeight: 700, fontSize: 15 }}>{kb.name}</div>
          {kb.description && <div style={{ color: 'rgba(255,255,255,.75)', fontSize: 12 }}>{kb.description}</div>}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#4ade80', display: 'inline-block' }} />
          <span style={{ color: 'rgba(255,255,255,.85)', fontSize: 12 }}>Online</span>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {m.role === 'assistant' && (
              <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'linear-gradient(135deg,#1a56db,#6c63ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0, marginRight: 8, marginTop: 2 }}>🤖</div>
            )}
            <div style={{
              maxWidth: '72%', padding: '10px 14px', borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
              background: m.role === 'user' ? 'linear-gradient(135deg,#1a56db,#6c63ff)' : '#fff',
              color: m.role === 'user' ? '#fff' : '#0f172a',
              fontSize: 14, lineHeight: 1.6,
              boxShadow: '0 1px 4px rgba(15,23,42,.1)',
              border: m.role === 'assistant' ? '1px solid #e2e8f0' : 'none',
              whiteSpace: 'pre-wrap',
            }}>
              {m.content.replace(/\*\*(.*?)\*\*/g, '$1')}
            </div>
          </div>
        ))}
        {thinking && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'linear-gradient(135deg,#1a56db,#6c63ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>🤖</div>
            <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '18px 18px 18px 4px', padding: '12px 16px', boxShadow: '0 1px 4px rgba(15,23,42,.1)' }}>
              <div style={{ display: 'flex', gap: 4 }}>
                {[0, 1, 2].map(i => (
                  <div key={i} style={{ width: 7, height: 7, borderRadius: '50%', background: '#1a56db', animation: `bounce .8s ${i * .15}s infinite` }} />
                ))}
              </div>
              <style>{`@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}`}</style>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ background: '#fff', borderTop: '1px solid #e2e8f0', padding: '12px 16px', display: 'flex', gap: 10, flexShrink: 0 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question..."
          disabled={thinking}
          style={{ flex: 1, padding: '10px 14px', border: '1.5px solid #e2e8f0', borderRadius: 24, fontSize: 14, fontFamily: 'inherit', outline: 'none', background: '#f8fafc', color: '#0f172a' }}
        />
        <button
          onClick={send}
          disabled={!input.trim() || thinking}
          style={{ width: 42, height: 42, borderRadius: '50%', border: 'none', background: (!input.trim() || thinking) ? '#e2e8f0' : 'linear-gradient(135deg,#1a56db,#6c63ff)', color: '#fff', fontSize: 18, cursor: (!input.trim() || thinking) ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}
        >
          ↑
        </button>
      </div>
    </div>
  )
}

const fullPage = { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'DM Sans','Segoe UI',sans-serif" }
const spinner = { width: 32, height: 32, border: '3px solid #e2e8f0', borderTopColor: '#1a56db', borderRadius: '50%', animation: 'spin .8s linear infinite', margin: '0 auto' }
