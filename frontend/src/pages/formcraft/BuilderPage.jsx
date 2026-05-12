import { useState, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { createPortal } from 'react-dom'
import { authHeaders } from '../../utils/api'
import './formcraft.css'

const LANGUAGES = [
  { code: 'Hindi', label: '🇮🇳 Hindi' },
  { code: 'Spanish', label: '🇪🇸 Spanish' },
  { code: 'French', label: '🇫🇷 French' },
  { code: 'German', label: '🇩🇪 German' },
  { code: 'Arabic', label: '🇸🇦 Arabic' },
  { code: 'Portuguese', label: '🇧🇷 Portuguese' },
  { code: 'Japanese', label: '🇯🇵 Japanese' },
  { code: 'Chinese (Simplified)', label: '🇨🇳 Chinese' },
  { code: 'Italian', label: '🇮🇹 Italian' },
  { code: 'Bengali', label: '🇧🇩 Bengali' },
  { code: 'Gujarati', label: 'ગુ Gujarati' },
  { code: 'Tamil', label: '🇱🇰 Tamil' },
  { code: 'Telugu', label: 'తె Telugu' },
  { code: 'Marathi', label: 'म Marathi' },
]

function TranslateModal({ title, fields, onApply, onClose }) {
  const [lang, setLang] = useState('Hindi')
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('groq_key') || '')
  const [saveKey, setSaveKey] = useState(true)
  const [translating, setTranslating] = useState(false)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState(null)

  const translate = async () => {
    if (!apiKey.trim()) { setError('Groq API key is required'); return }
    if (!fields.length) { setError('Add fields to the form first'); return }
    setTranslating(true)
    setError('')
    setPreview(null)
    try {
      const res = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, fields, target_language: lang, groq_api_key: apiKey.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Translation failed')
      if (saveKey) localStorage.setItem('groq_key', apiKey.trim())
      setPreview(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setTranslating(false)
    }
  }

  return createPortal(
    <div onClick={e => { if (e.target === e.currentTarget) onClose() }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.6)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20, fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      <div onClick={e => e.stopPropagation()}
        style={{ background: '#fff', borderRadius: 20, width: '100%', maxWidth: 520, boxShadow: '0 24px 64px rgba(15,23,42,.22)', overflow: 'hidden' }}>

        {/* Header */}
        <div style={{ background: 'linear-gradient(135deg,#1a56db,#6c63ff)', padding: '20px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h2 style={{ color: '#fff', fontSize: 18, fontWeight: 800, margin: 0 }}>🌐 Translate Form</h2>
              <p style={{ color: 'rgba(255,255,255,.8)', fontSize: 13, margin: '4px 0 0' }}>
                AI-powered translation using Groq — one click, all fields
              </p>
            </div>
            <button onClick={onClose} style={{ background: 'rgba(255,255,255,.2)', border: 'none', color: '#fff', width: 32, height: 32, borderRadius: '50%', fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>×</button>
          </div>
        </div>

        <div style={{ padding: '24px' }}>
          {/* Language picker */}
          <div style={{ marginBottom: 16 }}>
            <label style={lbl2}>Target Language</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 6 }}>
              {LANGUAGES.map(l => (
                <button key={l.code} onClick={() => { setLang(l.code); setPreview(null) }}
                  style={{ padding: '8px 6px', border: `2px solid ${lang === l.code ? '#1a56db' : '#e2e8f0'}`, borderRadius: 9, background: lang === l.code ? '#eff6ff' : '#fff', color: lang === l.code ? '#1a56db' : '#374151', fontSize: 12, fontWeight: lang === l.code ? 700 : 500, cursor: 'pointer', fontFamily: 'inherit', textAlign: 'center' }}>
                  {l.label}
                </button>
              ))}
            </div>
          </div>

          {/* API key */}
          <div style={{ marginBottom: 6 }}>
            <label style={lbl2}>Groq API Key</label>
            <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="gsk_..."
              style={{ width: '100%', padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 13, fontFamily: 'inherit', boxSizing: 'border-box', outline: 'none' }} />
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b', marginBottom: 16, cursor: 'pointer' }}>
            <input type="checkbox" checked={saveKey} onChange={e => setSaveKey(e.target.checked)} />
            Save key for next time
          </label>

          {error && (
            <div style={{ padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#dc2626', fontSize: 13, marginBottom: 16 }}>{error}</div>
          )}

          {/* Preview */}
          {preview && (
            <div style={{ background: '#f8fafc', border: '1.5px solid #e2e8f0', borderRadius: 12, padding: '14px 16px', marginBottom: 16, maxHeight: 180, overflowY: 'auto' }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#1a56db', marginBottom: 8 }}>Preview: "{preview.title}"</div>
              {preview.fields.slice(0, 5).map((f, i) => (
                <div key={i} style={{ fontSize: 12, color: '#374151', padding: '3px 0', borderBottom: '1px solid #f1f5f9' }}>
                  <span style={{ fontWeight: 600 }}>{f.label}</span>
                  {f.placeholder && <span style={{ color: '#94a3b8' }}> — {f.placeholder}</span>}
                  {f.options?.length > 0 && <span style={{ color: '#94a3b8' }}> ({f.options.join(', ')})</span>}
                </div>
              ))}
              {preview.fields.length > 5 && <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>+{preview.fields.length - 5} more fields...</div>}
            </div>
          )}

          <div style={{ display: 'flex', gap: 10 }}>
            {preview ? (
              <>
                <button onClick={() => onApply(preview)}
                  style={{ flex: 1, padding: '11px', border: 'none', borderRadius: 10, background: '#059669', color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
                  ✓ Apply Translation
                </button>
                <button onClick={() => { setPreview(null); translate() }} disabled={translating}
                  style={{ padding: '11px 16px', border: '1.5px solid #e2e8f0', borderRadius: 10, background: '#fff', color: '#64748b', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
                  Retry
                </button>
              </>
            ) : (
              <button onClick={translate} disabled={translating}
                style={{ flex: 1, padding: '11px', border: 'none', borderRadius: 10, background: translating ? '#93c5fd' : '#1a56db', color: '#fff', fontSize: 14, fontWeight: 700, cursor: translating ? 'not-allowed' : 'pointer', fontFamily: 'inherit', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                {translating ? (
                  <><div style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,.4)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin .7s linear infinite' }} />Translating...</>
                ) : '🌐 Translate Now'}
                <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
              </button>
            )}
            <button onClick={onClose}
              style={{ padding: '11px 18px', border: '1.5px solid #e2e8f0', borderRadius: 10, background: '#fff', color: '#64748b', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}

const lbl2 = { display: 'block', fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 8 }

const B_DEFAULTS = {
  text:     { label: 'Short Text',      placeholder: 'Type here...',    required: false },
  email:    { label: 'Email Address',   placeholder: 'you@email.com',   required: true  },
  phone:    { label: 'Phone Number',    placeholder: '+91 98765 43210', required: false },
  textarea: { label: 'Long Text',       placeholder: 'Write here...',   required: false },
  select:   { label: 'Dropdown',        options: ['Option 1','Option 2','Option 3'], required: false },
  radio:    { label: 'Multiple Choice', options: ['Option 1','Option 2','Option 3'], required: false },
  checkbox: { label: 'Checkboxes',      options: ['Option A','Option B','Option C'], required: false },
  number:   { label: 'Number',          placeholder: '0',               required: false },
  date:     { label: 'Date',            placeholder: '',                required: false },
  file:     { label: 'File Upload',                                      required: false },
  rating:   { label: 'Star Rating',                                      required: false },
  divider:  { label: 'Divider' },
}

const FIELD_TYPES = [
  ['text','📝','Text'],['email','📧','Email'],['phone','📱','Phone'],
  ['textarea','📄','Long Text'],['select','📋','Dropdown'],['radio','🔘','Radio'],
  ['checkbox','☑️','Checkbox'],['number','🔢','Number'],['date','📅','Date'],
  ['file','📎','File'],['rating','⭐','Rating'],['divider','➖','Divider'],
]

let _counter = 0

function FieldPreview({ f }) {
  if (f.type === 'radio' || f.type === 'checkbox')
    return <div style={{ fontSize: 11, color: '#64748b' }}>{(f.options || []).map(o => `${f.type === 'radio' ? '◯' : '☐'} ${o}`).join('  ')}</div>
  if (f.type === 'rating')
    return <div style={{ fontSize: 16, color: '#d97706' }}>★★★★★</div>
  if (f.type === 'divider')
    return <hr style={{ border: 'none', borderTop: '2px dashed #e2e8f0' }} />
  if (f.type === 'textarea')
    return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b', height: 36 }}>{f.placeholder || ''}</div>
  if (f.type === 'select')
    return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>{(f.options || [])[0] || 'Select...'} ▾</div>
  if (f.type === 'file')
    return <div style={{ background: '#f8fafc', border: '1.5px dashed #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b', textAlign: 'center' }}>📎 Choose file</div>
  if (f.type === 'date')
    return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#94a3b8', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>📅 <span>dd / mm / yyyy</span></div>
  return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>{f.placeholder || 'Input field'}</div>
}

export default function BuilderPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [title, setTitle] = useState(location.state?.title || 'Untitled Form')
  const [fields, setFields] = useState(location.state?.fields || [])
  const [selectedId, setSelectedId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [showTranslate, setShowTranslate] = useState(false)
  const [originalSnapshot, setOriginalSnapshot] = useState(null)

  const addField = type => {
    const id = `bf_${++_counter}`
    const newField = { id, type, ...JSON.parse(JSON.stringify(B_DEFAULTS[type] || { label: 'Field' })) }
    setFields(f => [...f, newField])
    setSelectedId(id)
  }

  const updateField = (id, key, value) =>
    setFields(f => f.map(fi => fi.id === id ? { ...fi, [key]: value } : fi))

  const moveField = (id, dir) => {
    setFields(f => {
      const idx = f.findIndex(fi => fi.id === id)
      const ni = idx + dir
      if (ni < 0 || ni >= f.length) return f
      const copy = [...f]
      ;[copy[idx], copy[ni]] = [copy[ni], copy[idx]]
      return copy
    })
  }

  const deleteField = id => {
    setFields(f => f.filter(fi => fi.id !== id))
    if (selectedId === id) setSelectedId(null)
  }

  const updateOption = (id, i, v) =>
    setFields(f => f.map(fi => {
      if (fi.id !== id) return fi
      const opts = [...(fi.options || [])]
      opts[i] = v
      return { ...fi, options: opts }
    }))

  const addOption = id =>
    setFields(f => f.map(fi => fi.id === id ? { ...fi, options: [...(fi.options || []), 'New option'] } : fi))

  const removeOption = (id, i) =>
    setFields(f => f.map(fi => {
      if (fi.id !== id) return fi
      const opts = [...(fi.options || [])]
      opts.splice(i, 1)
      return { ...fi, options: opts }
    }))

  const saveToDb = async () => {
    if (!fields.length) { alert('Add some fields first!'); return }
    setSaving(true)
    try {
      const res = await fetch('/api/forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ title, fields }),
      })
      await res.json()
      navigate('/formcraft?myforms=1')
    } catch { alert('❌ Save failed. Make sure the backend is running.') }
    finally { setSaving(false) }
  }

  const selected = fields.find(f => f.id === selectedId)
  const hasOpts = selected && ['radio', 'checkbox', 'select'].includes(selected.type)
  const hasPlaceholder = selected && !['radio', 'checkbox', 'select', 'rating', 'divider', 'file', 'date'].includes(selected.type)

  const aiTips = []
  if (!fields.some(f => f.type === 'email')) aiTips.push({ t: 'Add Email field', fn: () => addField('email') })
  if (!fields.some(f => f.type === 'phone')) aiTips.push({ t: 'Add Phone field', fn: () => addField('phone') })

  return (
    <div className="fc">
      <div style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '9px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 12, color: '#64748b' }}>Form name:</span>
          <input value={title} onChange={e => setTitle(e.target.value)} style={{ border: 'none', outline: 'none', fontSize: 14, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", color: '#0f172a' }} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {originalSnapshot && (
            <button onClick={() => { setTitle(originalSnapshot.title); setFields(originalSnapshot.fields); setOriginalSnapshot(null) }}
              style={{ padding: '7px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', color: '#64748b', fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: "'DM Sans',sans-serif" }}>
              ↩ Restore Original
            </button>
          )}
          <button onClick={() => setShowTranslate(true)} disabled={!fields.length}
            style={{ padding: '7px 16px', border: '1.5px solid #1a56db', borderRadius: 8, background: '#eff6ff', color: '#1a56db', fontSize: 12, fontWeight: 700, cursor: fields.length ? 'pointer' : 'not-allowed', fontFamily: "'DM Sans',sans-serif", opacity: fields.length ? 1 : 0.5 }}>
            🌐 Translate
          </button>
          <button className="fc-btn-primary" onClick={saveToDb} disabled={saving}>{saving ? '⏳ Saving...' : '💾 Save to DB'}</button>
        </div>
      </div>

      {showTranslate && (
        <TranslateModal
          title={title}
          fields={fields}
          onApply={data => {
            if (!originalSnapshot) setOriginalSnapshot({ title, fields: JSON.parse(JSON.stringify(fields)) })
            setTitle(data.title)
            setFields(data.fields)
            setShowTranslate(false)
          }}
          onClose={() => setShowTranslate(false)}
        />
      )}

      <div className="fc-builder-wrap">
        <div className="fc-b-sidebar">
          <h3>Add Fields</h3>
          <div className="fc-field-types">
            {FIELD_TYPES.map(([type, icon, label]) => (
              <div key={type} className="fc-ft-item" onClick={() => addField(type)}>
                <div className="fc-ft-icon">{icon}</div>{label}
              </div>
            ))}
          </div>
          <h3>AI Tips</h3>
          {aiTips.length === 0
            ? <p style={{ fontSize: 11, color: '#64748b' }}>Form looks great! 🎉</p>
            : aiTips.slice(0, 2).map((tip, i) => (
              <div key={i} className="fc-ai-sug">
                <p style={{ margin: '0 0 5px', fontSize: 12, fontWeight: 600 }}>💡 {tip.t}</p>
                <button className="fc-add-btn" onClick={tip.fn}>+ Add</button>
              </div>
            ))}
        </div>

        <div className="fc-b-canvas">
          {fields.length === 0 && <div className="fc-drop-zone">👈 Click a field type to add it here</div>}
          {fields.map(f => (
            <div key={f.id} className={`fc-canvas-card${selectedId === f.id ? ' selected' : ''}`} onClick={() => setSelectedId(f.id)}>
              <div className="fc-canvas-card-hdr">
                <div className="fc-canvas-card-label">
                  <span className="fc-ftbadge">{f.type}</span>
                  {f.label}{f.required && <span style={{ color: '#dc2626' }}>*</span>}
                </div>
                <div className="fc-canvas-card-actions">
                  <button className="fc-ca-btn" onClick={e => { e.stopPropagation(); moveField(f.id, -1) }}>↑</button>
                  <button className="fc-ca-btn" onClick={e => { e.stopPropagation(); moveField(f.id, 1) }}>↓</button>
                  <button className="fc-ca-btn del" onClick={e => { e.stopPropagation(); deleteField(f.id) }}>🗑</button>
                </div>
              </div>
              <div className="fc-canvas-card-body"><FieldPreview f={f} /></div>
            </div>
          ))}
        </div>

        <div className="fc-b-props">
          <h3>Field Settings</h3>
          {!selected
            ? <div className="fc-no-sel"><p style={{ fontSize: 26, marginBottom: 8 }}>⚙️</p><p>Select a field to edit</p></div>
            : (
              <>
                <div className="fc-prop-g">
                  <label className="fc-prop-lbl">Label</label>
                  <input className="fc-prop-input" value={selected.label} onChange={e => updateField(selected.id, 'label', e.target.value)} />
                </div>
                {hasPlaceholder && (
                  <div className="fc-prop-g">
                    <label className="fc-prop-lbl">Placeholder</label>
                    <input className="fc-prop-input" value={selected.placeholder || ''} onChange={e => updateField(selected.id, 'placeholder', e.target.value)} />
                  </div>
                )}
                {hasOpts && (
                  <div className="fc-prop-g">
                    <label className="fc-prop-lbl">Options</label>
                    {(selected.options || []).map((o, i) => (
                      <div key={i} className="fc-opt-row">
                        <input value={o} onChange={e => updateOption(selected.id, i, e.target.value)} />
                        <button className="fc-del-opt" onClick={() => removeOption(selected.id, i)}>×</button>
                      </div>
                    ))}
                    <button className="fc-add-opt-btn" onClick={() => addOption(selected.id)}>+ Add option</button>
                  </div>
                )}
                {selected.type !== 'divider' && (
                  <div className="fc-prop-g">
                    <div className="fc-toggle-row">
                      <span style={{ fontSize: 12, fontWeight: 600 }}>Required</span>
                      <button className={`fc-toggle${selected.required ? ' on' : ''}`} onClick={() => updateField(selected.id, 'required', !selected.required)} />
                    </div>
                  </div>
                )}
                <button onClick={() => deleteField(selected.id)} style={{ width: '100%', padding: 8, border: '1.5px solid #dc2626', borderRadius: 8, background: '#fee2e2', color: '#dc2626', cursor: 'pointer', fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", marginTop: 4 }}>
                  Remove Field
                </button>
              </>
            )}
        </div>
      </div>
    </div>
  )
}
