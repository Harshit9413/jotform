import { useState, useRef, useEffect, useCallback } from 'react'
import {
  Database, ChevronRight, Search, Send, Copy, Check,
  Code2, Table2, LogOut, Sparkles, ChevronDown, ChevronUp,
} from 'lucide-react'

const SUGGESTIONS = [
  'Show me all tables and their row counts',
  'What are the most recent 10 records?',
  'Count records grouped by status',
  'Show me the table structure',
  'Find duplicate records if any',
]

// ── helpers ─────────────────────────────────────────────────
const now = () =>
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

function parseBold(text) {
  return text.split(/\*\*(.*?)\*\*/g).map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
  )
}

// ── TableBlock (schema sidebar) ─────────────────────────────
function TableBlock({ name, info }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="table-item">
      <div className="table-header" onClick={() => setOpen(o => !o)}>
        <Database size={11} className="table-icon" />
        <span className="table-name-label" title={name}>{name}</span>
        <span className="table-count">{info.row_count}</span>
        <ChevronRight size={10} className={`table-chevron${open ? ' open' : ''}`} />
      </div>
      <div className={`col-rows${open ? ' visible' : ''}`}>
        {info.columns.map(col => (
          <div className="col-row" key={col.name}>
            <div className="col-dot" />
            <span className="col-name" title={col.name}>{col.name}</span>
            <div className="col-badges">
              {col.primary_key && <span className="badge badge-pk">PK</span>}
              {col.foreign_key && <span className="badge badge-fk">FK</span>}
            </div>
            <span className="col-type">{col.type.split('(')[0].toLowerCase()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── TypingIndicator ──────────────────────────────────────────
function TypingIndicator() {
  return (
    <div className="typing-row">
      <div className="avatar bot">🤖</div>
      <div className="typing-bubble">
        <div className="dot" /><div className="dot" /><div className="dot" />
      </div>
    </div>
  )
}

// ── DataTable ────────────────────────────────────────────────
function DataTable({ data, columns, rowCount, truncated }) {
  const [showAll, setShowAll] = useState(false)
  const PREVIEW_LIMIT = 100
  const isSliced = !showAll && data.length > PREVIEW_LIMIT
  const displayed = isSliced ? data.slice(0, PREVIEW_LIMIT) : data

  return (
    <div className="data-table-wrap">
      {truncated && (
        <div style={{
          fontSize: 11, color: '#b45309', background: '#fef3c7',
          border: '1px solid #fcd34d', borderRadius: 6,
          padding: '5px 10px', marginBottom: 6,
        }}>
          Results capped at 100,000 rows. Add a LIMIT to your question for a specific count.
        </div>
      )}
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>{columns.map(c => <th key={c}>{c}</th>)}</tr>
          </thead>
          <tbody>
            {displayed.map((row, i) => (
              <tr key={i}>
                {columns.map(c => (
                  <td key={c} title={row[c] !== null ? String(row[c]) : 'null'}>
                    {row[c] === null
                      ? <span className="td-null">null</span>
                      : String(row[c])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-footer">
        <span className="row-chip">
          {isSliced ? `Showing ${PREVIEW_LIMIT} of ${rowCount} rows` : `${rowCount} rows`}
        </span>
        {data.length > PREVIEW_LIMIT && (
          <button className="show-toggle-btn" onClick={() => setShowAll(s => !s)}>
            {showAll
              ? <><ChevronUp size={11} style={{ display:'inline',verticalAlign:'middle' }} /> Show less</>
              : <><ChevronDown size={11} style={{ display:'inline',verticalAlign:'middle' }} /> Show all {data.length} rows</>}
          </button>
        )}
      </div>
    </div>
  )
}

// ── Message ──────────────────────────────────────────────────
function Message({ msg }) {
  const [showSql, setShowSql] = useState(false)
  const [copied, setCopied] = useState(false)
  const isUser = msg.role === 'user'

  const copySql = () => {
    if (!msg.sql) return
    navigator.clipboard.writeText(msg.sql).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className={`msg-row${isUser ? ' user' : ' bot'}${msg.error ? ' err' : ''}`}>
      <div className={`avatar ${isUser ? 'user' : 'bot'}`}>
        {isUser ? '👤' : '🤖'}
      </div>

      <div className="msg-body">
        <div className="msg-meta">
          <span className="msg-sender">{isUser ? 'You' : 'QueryMind'}</span>
          <span className="msg-time">{msg.time}</span>
        </div>

        <div className="bubble">{parseBold(msg.content)}</div>

        {/* SQL controls */}
        {msg.sql && (
          <div className="sql-bar">
            <button className="sql-toggle-btn" onClick={() => setShowSql(s => !s)}>
              <Code2 size={12} />
              {showSql ? 'Hide SQL' : 'View SQL'}
            </button>
            <button
              className={`copy-sql-btn${copied ? ' copied' : ''}`}
              onClick={copySql}
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? 'Copied!' : 'Copy SQL'}
            </button>
          </div>
        )}

        {showSql && msg.sql && (
          <div className="sql-code">
            <span className="sql-code-label">SQL</span>
            {msg.sql}
          </div>
        )}

        {/* Data table */}
        {msg.data?.length > 0 && (
          <DataTable
            data={msg.data}
            columns={msg.columns}
            rowCount={msg.rowCount}
            truncated={msg.truncated}
          />
        )}

        {msg.type === 'sql' && msg.data?.length === 0 && !msg.error && (
          <div style={{ fontSize: 12, color: 'var(--text3)', display: 'flex', alignItems: 'center', gap: 5 }}>
            <Table2 size={12} /> No rows returned
          </div>
        )}
      </div>
    </div>
  )
}

// ── ChatScreen ───────────────────────────────────────────────
export default function ChatScreen({ session, onDisconnect }) {
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const autoGrow = useCallback((el) => {
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 140) + 'px'
  }, [])

  const sendMessage = async (question) => {
    const q = (question ?? input).trim()
    if (!q || loading) return

    const userMsg = { role: 'user', content: q, time: now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setLoading(true)

    const newHistory = [
      ...history,
      { role: 'user', content: q },
    ]

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.sessionId,
          question: q,
          conversation_history: newHistory,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Query failed.')

      const botMsg = {
        role: 'bot',
        content: data.answer || '',
        sql: data.sql,
        data: data.data || [],
        columns: data.columns || [],
        rowCount: data.row_count,
        truncated: data.truncated || false,
        type: data.type,
        time: now(),
      }
      setMessages(prev => [...prev, botMsg])
      setHistory([
        ...newHistory,
        { role: 'assistant', content: data.answer || '' },
      ])
    } catch (e) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: e.message, error: true, time: now() },
      ])
    } finally {
      setLoading(false)
      setTimeout(() => textareaRef.current?.focus(), 50)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleDisconnect = async () => {
    try {
      await fetch('/api/disconnect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.sessionId }),
      })
    } catch { /* ignore */ }
    onDisconnect()
  }

  const filteredTables = Object.entries(session.schema).filter(([name]) =>
    name.toLowerCase().includes(search.toLowerCase())
  )

  const totalRows = Object.values(session.schema)
    .reduce((s, t) => s + (typeof t.row_count === 'number' ? t.row_count : 0), 0)

  const isEmpty = messages.length === 0 && !loading

  return (
    <div className="chat-layout">
      {/* background blobs (subtle in chat) */}
      <div className="mesh-blob blob-purple" style={{ opacity: 0.08 }} />
      <div className="mesh-blob blob-cyan"   style={{ opacity: 0.06 }} />

      {/* ══ SIDEBAR ══ */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Database size={16} color="#fff" />
          </div>
          <div className="sidebar-logo-text">Query<span>Mind</span></div>
        </div>

        {/* connection pill */}
        <div className="conn-pill">
          <div className="conn-pill-dot" />
          <div className="conn-pill-info">
            <div className="conn-pill-db">{session.dbType}</div>
            <div className="conn-pill-rows">
              {session.totalTables} tables · {totalRows.toLocaleString()} rows
            </div>
          </div>
        </div>

        {/* schema tree */}
        <div className="schema-header">
          <span>Schema</span>
          <span style={{ color: 'var(--purple-light)', fontSize: 11 }}>
            {session.totalColumns} cols
          </span>
        </div>

        <div className="schema-search-wrap">
          <input
            className="schema-search"
            placeholder="Search tables..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="schema-list">
          {filteredTables.map(([name, info]) => (
            <TableBlock key={name} name={name} info={info} />
          ))}
          {filteredTables.length === 0 && (
            <div style={{ padding: '20px 16px', textAlign: 'center', color: 'var(--text3)', fontSize: 12 }}>
              No tables match
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          <button className="sidebar-disconnect" onClick={handleDisconnect}>
            <LogOut size={13} /> Disconnect
          </button>
        </div>
      </aside>

      {/* ══ MAIN AREA ══ */}
      <main className="chat-area">
        {/* topbar */}
        <div className="chat-topbar">
          <Sparkles size={16} color="var(--purple-light)" />
          <span className="topbar-title">QueryMind</span>
          <div className="topbar-right">
            <div className="status-badge">
              <div className="status-dot" />
              Connected · {session.dbType}
            </div>
          </div>
        </div>

        {/* messages */}
        <div className="messages">
          {isEmpty ? (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h2>Ask anything about your data</h2>
              <p>
                No SQL knowledge needed. QueryMind understands plain English
                and turns it into accurate database queries.
              </p>
              <div className="suggestions">
                {SUGGESTIONS.map(s => (
                  <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => <Message key={i} msg={msg} />)}
              {loading && <TypingIndicator />}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        {/* suggestion pills row (visible when there are messages) */}
        {!isEmpty && (
          <div className="suggestions-row">
            {SUGGESTIONS.slice(0, 4).map(s => (
              <button key={s} className="suggestion-pill" onClick={() => sendMessage(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {/* input */}
        <div className="input-area">
          <div className="input-box">
            <textarea
              ref={textareaRef}
              rows={1}
              placeholder="Ask a question about your database..."
              value={input}
              onChange={e => { setInput(e.target.value); autoGrow(e.target) }}
              onKeyDown={handleKeyDown}
            />
            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              {loading
                ? <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                : <Send size={16} />}
            </button>
          </div>
          <div className="input-hint">
            Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line
          </div>
        </div>
      </main>
    </div>
  )
}
