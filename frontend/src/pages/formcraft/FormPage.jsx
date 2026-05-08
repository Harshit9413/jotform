import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

function renderField(f, idx, starState, setStarState) {
  if (!f || !f.type) return null
  if (f.type === 'submit' || f.type === 'section') return null
  if (f.type === 'divider') return <hr key={idx} style={{ border: 'none', borderTop: '1.5px dashed #e2e8f0', margin: '8px 0 14px' }} />
  if (f.type === 'cardicons') return (
    <div key={idx} style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
      {['VISA', 'MC', 'UPI', 'PayPal'].map(b => (
        <span key={b} style={{ fontSize: 11, fontWeight: 600, background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 5, padding: '3px 9px', color: '#64748b' }}>{b}</span>
      ))}
    </div>
  )
  if (f.type === 'cardnum') return (
    <div key={idx} style={fg}>
      <label style={lbl}>Card number <span style={{ color: '#dc2626' }}>*</span></label>
      <input style={inp} type="text" name="card_number" placeholder="1234  5678  9012  3456" maxLength={19} />
    </div>
  )
  if (f.type === 'row3card') return (
    <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 88px 78px', gap: 10 }}>
      <div style={fg}><label style={lbl}>Expiry *</label><input style={inp} type="text" name="expiry" placeholder="MM / YY" /></div>
      <div style={fg}><label style={lbl}>CVV *</label><input style={inp} type="text" name="cvv" placeholder="123" maxLength={4} /></div>
      <div style={fg}><label style={lbl}>ZIP</label><input style={inp} type="text" name="zip" placeholder="302001" /></div>
    </div>
  )
  if (f.type === 'row2') return (
    <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
      {(f.fields || []).map((ff, i) => renderField(ff, `${idx}_${i}`, starState, setStarState))}
    </div>
  )
  if (f.type === 'rating') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <div style={{ display: 'flex', gap: 7, fontSize: 26, cursor: 'pointer' }}>
        {[1, 2, 3, 4, 5].map(v => (
          <span key={v} style={{ color: (starState[idx] || 0) >= v ? '#d97706' : '#cbd5e1', transition: 'color .1s' }}
            onClick={() => setStarState(s => ({ ...s, [idx]: v }))}>★</span>
        ))}
      </div>
    </div>
  )
  if (f.type === 'range') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <input type="range" name={f.label || 'range'} min="0" max="10" defaultValue="7" style={{ accentColor: '#d97706', width: '100%' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b', marginTop: 2 }}><span>0</span><span>10</span></div>
    </div>
  )
  if (f.type === 'radio') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
        {(f.options || []).map(o => (
          <label key={o} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, cursor: 'pointer' }}>
            <input type="radio" name={f.label || `radio_${idx}`} value={o} />{o}
          </label>
        ))}
      </div>
    </div>
  )
  if (f.type === 'checkbox') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}</label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
        {(f.options || []).map(o => (
          <label key={o} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, cursor: 'pointer' }}>
            <input type="checkbox" name={`${f.label || 'check'}_${idx}`} value={o} />{o}
          </label>
        ))}
      </div>
    </div>
  )
  if (f.type === 'select') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <select name={f.label || `select_${idx}`} required={f.required} style={inp}>
        <option value="">Select...</option>
        {(f.options || []).map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
  if (f.type === 'textarea') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <textarea name={f.label || `textarea_${idx}`} placeholder={f.placeholder || ''} required={f.required}
        style={{ ...inp, height: 90, resize: 'vertical' }} />
    </div>
  )
  if (f.type === 'file') return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <input type="file" name={f.label || `file_${idx}`} required={f.required} style={{ ...inp, padding: 8 }} />
    </div>
  )
  const itype = f.type === 'email' ? 'email' : f.type === 'phone' ? 'tel' : f.type === 'number' ? 'number' : f.type === 'date' ? 'date' : 'text'
  return (
    <div key={idx} style={fg}>
      <label style={lbl}>{f.label}{f.required && <span style={{ color: '#dc2626' }}> *</span>}</label>
      <input type={itype} name={f.label || `${f.type}_${idx}`} placeholder={f.placeholder || ''} required={f.required} style={inp} />
    </div>
  )
}

const fg  = { display: 'flex', flexDirection: 'column', gap: 5, marginBottom: 14 }
const lbl = { fontSize: 13, fontWeight: 600, color: '#0f172a' }
const inp = { padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, fontFamily: 'inherit', color: '#0f172a', background: '#fff', outline: 'none', width: '100%', boxSizing: 'border-box' }

export default function FormPage() {
  const { formId } = useParams()
  const [form, setForm] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [starState, setStarState] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setNotFound(false)
    setForm(null)

    fetch(`/api/public/${formId}`)
      .then(r => { if (!r.ok) throw new Error(String(r.status)); return r.json() })
      .then(data => {
        if (cancelled) return
        setForm(data)
        setLoading(false)
        document.title = `${data.title} — FormCraft`
      })
      .catch(() => {
        if (cancelled) return
        setNotFound(true)
        setLoading(false)
      })

    return () => {
      cancelled = true
      document.title = 'FormCraft'
    }
  }, [formId])

  const handleSubmit = async e => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = {}
    for (let [k, v] of formData.entries()) {
      if (data[k]) data[k] = Array.isArray(data[k]) ? [...data[k], v] : [data[k], v]
      else data[k] = v
    }
    Object.keys(data).forEach(k => { if (!data[k]) delete data[k] })
    if (!Object.keys(data).length) { alert('Please fill in at least one field!'); return }
    setSubmitting(true)
    try {
      const res = await fetch('/api/submissions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId, form_title: form.title, data }),
      })
      if (!res.ok) throw new Error()
      setSubmitted(true)
    } catch { alert('Submission failed. Please try again.') }
    finally { setSubmitting(false) }
  }

  const copyLink = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const fields = (form?.fields || []).filter(f => f.type !== 'submit')
  const submitField = form?.fields?.find(f => f.type === 'submit')
  const submitLabel = submitField?.label || 'Submit'
  const accentColor = form?.color || '#1a56db'

  if (loading) return (
    <div style={page}>
      <div style={card}>
        <div style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>
          <div style={{ width: 36, height: 36, border: '3px solid #e2e8f0', borderTopColor: '#1a56db', borderRadius: '50%', animation: 'spin .8s linear infinite', margin: '0 auto 12px' }} />
          Loading form...
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )

  if (notFound) return (
    <div style={page}>
      <div style={card}>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>😕</div>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8, color: '#0f172a' }}>Form not found</h2>
          <p style={{ color: '#64748b', marginBottom: 20 }}>This form doesn't exist or has been removed.</p>
          <Link to="/formcraft" style={{ color: '#1a56db', fontWeight: 600, textDecoration: 'none' }}>← Back to FormCraft</Link>
        </div>
      </div>
    </div>
  )

  if (submitted) return (
    <div style={page}>
      <div style={card}>
        <div style={{ textAlign: 'center', padding: 48 }}>
          <div style={{ fontSize: 52, marginBottom: 14 }}>✅</div>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8, color: '#065f46' }}>Submitted!</h2>
          <p style={{ color: '#64748b', marginBottom: 24 }}>Thank you, your response has been recorded.</p>
          <button onClick={() => setSubmitted(false)}
            style={{ padding: '10px 24px', background: accentColor, color: '#fff', border: 'none', borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
            Submit another response
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div style={page}>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } } * { box-sizing: border-box; }`}</style>

      {/* Header bar */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '0 24px', height: 52, display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 10 }}>
        <Link to="/formcraft" style={{ fontFamily: 'serif', fontSize: 18, fontWeight: 700, color: '#1a56db', textDecoration: 'none' }}>
          Form<span style={{ color: '#0f172a' }}>Craft</span>
        </Link>
        <button onClick={copyLink} style={{ padding: '6px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: copied ? '#d1fae5' : '#fff', color: copied ? '#065f46' : '#64748b', fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', transition: 'all .2s' }}>
          {copied ? '✓ Copied!' : '🔗 Copy Link'}
        </button>
      </div>

      {/* Form card */}
      <div style={card}>
        <div style={{ borderBottom: `4px solid ${accentColor}`, borderRadius: '14px 14px 0 0', height: 4, background: accentColor, margin: '-1px -1px 0' }} />
        <div style={{ padding: '28px 32px 32px' }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>{form.title}</h1>
          {form.description && <p style={{ fontSize: 13, color: '#64748b', marginBottom: 24 }}>{form.description}</p>}

          <form onSubmit={handleSubmit}>
            {fields.map((f, i) => renderField(f, i, starState, setStarState))}
            <button type="submit" disabled={submitting}
              style={{ width: '100%', padding: '13px', border: 'none', borderRadius: 10, background: accentColor, color: '#fff', fontSize: 15, fontWeight: 700, cursor: submitting ? 'not-allowed' : 'pointer', opacity: submitting ? 0.6 : 1, fontFamily: 'inherit', marginTop: 8 }}>
              {submitting ? '⏳ Submitting...' : submitLabel}
            </button>
          </form>
        </div>
      </div>

      <p style={{ textAlign: 'center', fontSize: 12, color: '#94a3b8', marginTop: 20 }}>
        Powered by <Link to="/formcraft" style={{ color: '#1a56db', textDecoration: 'none', fontWeight: 600 }}>FormCraft</Link>
      </p>
    </div>
  )
}

const page = { minHeight: '100vh', background: '#f8fafc', fontFamily: "'DM Sans', 'Segoe UI', sans-serif" }
const card = { maxWidth: 560, margin: '32px auto', background: '#fff', borderRadius: 14, border: '1px solid #e2e8f0', boxShadow: '0 4px 24px rgba(15,23,42,.07)' }
