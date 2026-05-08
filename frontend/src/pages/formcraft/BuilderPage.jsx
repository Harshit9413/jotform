import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './formcraft.css'

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
  return <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>{f.placeholder || 'Input field'}</div>
}

export default function BuilderPage() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('Untitled Form')
  const [fields, setFields] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [saving, setSaving] = useState(false)

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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, fields }),
      })
      await res.json()
      navigate('/formcraft?myforms=1')
    } catch { alert('❌ Save failed. Make sure the backend is running.') }
    finally { setSaving(false) }
  }

  const selected = fields.find(f => f.id === selectedId)
  const hasOpts = selected && ['radio', 'checkbox', 'select'].includes(selected.type)
  const hasPlaceholder = selected && !['radio', 'checkbox', 'select', 'rating', 'divider', 'file'].includes(selected.type)

  const aiTips = []
  if (!fields.some(f => f.type === 'email')) aiTips.push({ t: 'Add Email field', fn: () => addField('email') })
  if (!fields.some(f => f.type === 'phone')) aiTips.push({ t: 'Add Phone field', fn: () => addField('phone') })

  return (
    <div className="fc">
      <div style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '9px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 12, color: '#64748b' }}>Form name:</span>
          <input value={title} onChange={e => setTitle(e.target.value)} style={{ border: 'none', outline: 'none', fontSize: 14, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", color: '#0f172a' }} />
        </div>
        <button className="fc-btn-primary" onClick={saveToDb} disabled={saving}>{saving ? '⏳ Saving...' : '💾 Save to DB'}</button>
      </div>

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
