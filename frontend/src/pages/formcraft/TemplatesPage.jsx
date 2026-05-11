import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { authHeaders } from '../../utils/api'
import './formcraft.css'

// ─── Integration Tab ──────────────────────────────────────────────────────────
const ITG_META = {
  google_sheets: {
    icon: '📊', name: 'Google Sheets',
    desc: 'Automatically add every submission as a new row in a Google Sheet.',
    color: '#059669', bg: '#ecfdf5', border: '#a7f3d0',
    fields: [
      { key: 'spreadsheet_id', label: 'Spreadsheet ID', placeholder: 'From the Google Sheet URL (between /d/ and /edit)', required: true },
      { key: 'sheet_name',     label: 'Sheet / Tab Name', placeholder: 'Sheet1', required: false },
      { key: 'service_account_json', label: 'Service Account JSON', placeholder: 'Paste the entire JSON content here...', type: 'textarea', required: true },
    ],
  },
  email: {
    icon: '📧', name: 'Email Notifications',
    desc: 'Send an admin alert + user confirmation email on every submission.',
    color: '#1a56db', bg: '#eff6ff', border: '#bfdbfe',
    fields: [
      { key: 'smtp_host',    label: 'SMTP Host',    placeholder: 'smtp.gmail.com',  required: true },
      { key: 'smtp_port',    label: 'SMTP Port',    placeholder: '587',             required: true },
      { key: 'from_email',   label: 'From Email',   placeholder: 'you@gmail.com',   required: true },
      { key: 'password',     label: 'App Password', placeholder: 'Gmail app password (16 chars)', type: 'password', required: true },
      { key: 'admin_email',  label: 'Admin Email',  placeholder: 'Notify this address on every submission', required: true },
    ],
  },
}

function IntegrationConnectForm({ type, existing, onSave, onCancel, saving }) {
  const meta = ITG_META[type]
  const [vals, setVals] = useState(() => {
    const init = {}
    meta.fields.forEach(f => { init[f.key] = (existing?.config?.[f.key] || '') })
    if (type === 'google_sheets' && existing?.config?.service_account_json?._masked) init.service_account_json = ''
    if (type === 'email' && existing?.config?.password?.startsWith('***')) init.password = ''
    return init
  })
  return (
    <div style={{ background: '#f8fafc', border: `1.5px solid ${meta.border}`, borderRadius: 12, padding: '18px 20px', marginTop: 12 }}>
      <h4 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: '0 0 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
        {meta.icon} Configure {meta.name}
      </h4>
      {meta.fields.map(f => (
        <div key={f.key} style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', fontSize: 12, fontWeight: 700, color: '#374151', marginBottom: 4 }}>{f.label}{f.required && ' *'}</label>
          {f.type === 'textarea' ? (
            <textarea
              value={vals[f.key]}
              onChange={e => setVals(v => ({ ...v, [f.key]: e.target.value }))}
              placeholder={f.placeholder}
              rows={5}
              style={{ width: '100%', padding: '8px 10px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 12, fontFamily: 'monospace', resize: 'vertical', boxSizing: 'border-box', outline: 'none' }}
            />
          ) : (
            <input
              type={f.type || 'text'}
              value={vals[f.key]}
              onChange={e => setVals(v => ({ ...v, [f.key]: e.target.value }))}
              placeholder={f.placeholder}
              style={{ width: '100%', padding: '8px 10px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 13, fontFamily: 'inherit', boxSizing: 'border-box', outline: 'none' }}
            />
          )}
        </div>
      ))}
      <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
        <button onClick={() => onSave(vals)} disabled={saving}
          style={{ padding: '8px 20px', border: 'none', borderRadius: 8, background: saving ? '#93c5fd' : meta.color, color: '#fff', fontSize: 13, fontWeight: 700, cursor: saving ? 'not-allowed' : 'pointer', fontFamily: 'inherit' }}>
          {saving ? 'Saving…' : existing ? 'Update' : 'Connect'}
        </button>
        <button onClick={onCancel}
          style={{ padding: '8px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', color: '#64748b', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
          Cancel
        </button>
      </div>
    </div>
  )
}

function IntegrationCard({ type, integration, onSave, onToggle, onDelete }) {
  const meta = ITG_META[type]
  const [open, setOpen] = useState(false)
  const [saving, setSaving] = useState(false)

  const handleSave = async vals => {
    setSaving(true)
    const ok = await onSave(type, vals, integration?.id)
    setSaving(false)
    if (ok) setOpen(false)
  }

  const isConnected = !!integration
  const isActive    = integration?.is_active

  return (
    <div style={{ border: `1.5px solid ${isConnected ? meta.border : '#e2e8f0'}`, borderRadius: 14, padding: '16px 18px', background: isConnected ? meta.bg : '#fff', marginBottom: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 42, height: 42, borderRadius: 12, background: isConnected ? meta.color + '18' : '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, flexShrink: 0 }}>
          {meta.icon}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{meta.name}</div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{meta.desc}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          {isConnected ? (
            <>
              <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 9px', borderRadius: 20, background: isActive ? '#dcfce7' : '#f1f5f9', color: isActive ? '#059669' : '#94a3b8' }}>
                {isActive ? '● Active' : '○ Paused'}
              </span>
              <button onClick={() => onToggle(integration.id)}
                title={isActive ? 'Pause' : 'Resume'}
                style={{ padding: '5px 10px', border: '1.5px solid #e2e8f0', borderRadius: 7, background: '#fff', cursor: 'pointer', fontSize: 12, fontWeight: 600, color: '#64748b', fontFamily: 'inherit' }}>
                {isActive ? '⏸' : '▶'}
              </button>
              <button onClick={() => setOpen(o => !o)}
                style={{ padding: '5px 10px', border: `1.5px solid ${meta.border}`, borderRadius: 7, background: meta.bg, cursor: 'pointer', fontSize: 12, fontWeight: 600, color: meta.color, fontFamily: 'inherit' }}>
                Edit
              </button>
              <button onClick={() => onDelete(integration.id)}
                style={{ padding: '5px 8px', border: '1.5px solid #fecaca', borderRadius: 7, background: '#fef2f2', cursor: 'pointer', fontSize: 12, color: '#dc2626', fontFamily: 'inherit' }}>
                ✕
              </button>
            </>
          ) : (
            <button onClick={() => setOpen(o => !o)}
              style={{ padding: '7px 18px', border: 'none', borderRadius: 8, background: meta.color, color: '#fff', fontSize: 13, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
              Connect
            </button>
          )}
        </div>
      </div>
      {open && (
        <IntegrationConnectForm type={type} existing={integration} onSave={handleSave} onCancel={() => setOpen(false)} saving={saving} />
      )}
    </div>
  )
}

function IntegrationsTab({ formId }) {
  const [integrations, setIntegrations] = useState([])
  const [logs, setLogs]                 = useState([])
  const [loading, setLoading]           = useState(true)
  const [err, setErr]                   = useState('')

  const reload = useCallback(() => {
    fetch(`/api/integrations/${formId}`, { headers: authHeaders() })
      .then(r => r.json())
      .then(data => { setIntegrations(Array.isArray(data) ? data : []); setLoading(false) })
      .catch(() => setLoading(false))
    fetch(`/api/integrations/${formId}/logs`, { headers: authHeaders() })
      .then(r => r.json())
      .then(data => setLogs(Array.isArray(data) ? data : []))
      .catch(() => {})
  }, [formId])

  useEffect(() => { reload() }, [reload])

  const handleSave = async (type, config, existingId) => {
    setErr('')
    const processedConfig = { ...config }

    if (type === 'google_sheets') {
      const sa = processedConfig.service_account_json
      const saIsEmpty = !sa || (typeof sa === 'string' && !sa.trim())

      if (saIsEmpty) {
        if (existingId) {
          // Editing: JSON not changed — use PATCH to update only other fields
          const patchConfig = { ...processedConfig }
          delete patchConfig.service_account_json
          const res = await fetch(`/api/integrations/${existingId}/config`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify({ config: patchConfig }),
          })
          const data = await res.json()
          if (!res.ok) { setErr(data.detail || 'Failed to save'); return false }
          reload()
          return true
        }
        setErr('Service Account JSON is required. Paste the full contents of your service-account.json file.')
        return false
      }

      if (typeof sa === 'string') {
        const raw = sa.trim()
        let parsed = null
        try { parsed = JSON.parse(raw) } catch {}
        if (!parsed) {
          try {
            const fixed = raw.replace(/("private_key"\s*:\s*")([\s\S]*?)(")/g,
              (_, pre, key, post) => pre + key.replace(/\r/g, '').replace(/\n/g, '\\n') + post)
            parsed = JSON.parse(fixed)
          } catch {}
        }
        if (!parsed || typeof parsed !== 'object') {
          setErr('Service Account JSON is not valid. Paste the entire contents of your service-account.json file.')
          return false
        }
        processedConfig.service_account_json = parsed
      }
    }

    if (existingId) {
      await fetch(`/api/integrations/${existingId}`, { method: 'DELETE', headers: authHeaders() })
    }
    const res = await fetch('/api/integrations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ form_id: formId, type, config: processedConfig }),
    })
    const data = await res.json()
    if (!res.ok) { setErr(data.detail || 'Failed to save'); return false }
    reload()
    return true
  }

  const handleToggle = async id => {
    await fetch(`/api/integrations/${id}/toggle`, { method: 'PATCH', headers: authHeaders() })
    reload()
  }

  const handleDelete = async id => {
    if (!confirm('Remove this integration?')) return
    await fetch(`/api/integrations/${id}`, { method: 'DELETE', headers: authHeaders() })
    reload()
  }

  const getItg = type => integrations.find(i => i.type === type) || null

  if (loading) return (
    <div style={{ padding: '40px 0', textAlign: 'center' }}>
      <div style={{ width: 28, height: 28, border: '3px solid #e2e8f0', borderTopColor: '#1a56db', borderRadius: '50%', animation: 'spin .8s linear infinite', margin: '0 auto 10px' }} />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  )

  return (
    <div style={{ padding: '20px 24px' }}>
      <div style={{ marginBottom: 18 }}>
        <h3 style={{ fontSize: 15, fontWeight: 800, color: '#0f172a', margin: '0 0 4px' }}>Integrations</h3>
        <p style={{ fontSize: 12, color: '#64748b', margin: 0 }}>
          Connect this form to external services. Runs automatically after every submission.
        </p>
      </div>

      {err && (
        <div style={{ padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#dc2626', fontSize: 13, marginBottom: 14 }}>{err}</div>
      )}

      {Object.keys(ITG_META).map(type => (
        <IntegrationCard key={type} type={type} integration={getItg(type)} onSave={handleSave} onToggle={handleToggle} onDelete={handleDelete} />
      ))}

      {/* Recent logs */}
      {logs.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>Recent Trigger History</div>
          <div style={{ border: '1.5px solid #e2e8f0', borderRadius: 10, overflow: 'hidden' }}>
            {logs.slice(0, 8).map((lg, i) => {
              const itgType = integrations.find(it => it.id === lg.integration_id)?.type || 'unknown'
              const meta = ITG_META[itgType]
              return (
                <div key={lg.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 14px', borderBottom: i < Math.min(logs.length, 8) - 1 ? '1px solid #f1f5f9' : 'none', background: '#fff' }}>
                  <span style={{ fontSize: 14 }}>{meta?.icon || '🔗'}</span>
                  <span style={{ fontSize: 12, color: '#0f172a', fontWeight: 600, flex: 1 }}>{meta?.name || itgType}</span>
                  <span style={{ fontSize: 11, color: '#64748b' }}>Sub #{lg.submission_id}</span>
                  <span style={{
                    fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 20,
                    background: lg.status === 'success' ? '#dcfce7' : '#fef2f2',
                    color: lg.status === 'success' ? '#059669' : '#dc2626',
                  }}>
                    {lg.status === 'success' ? '✓' : '✗'} {lg.status}
                  </span>
                  <span style={{ fontSize: 10, color: '#94a3b8' }}>
                    {new Date(lg.triggered_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              )
            })}
          </div>
          {logs[0]?.error_message && (
            <div style={{ marginTop: 8, padding: '8px 12px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, fontSize: 11, color: '#dc2626', fontFamily: 'monospace' }}>
              Last error: {logs[0].error_message}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const AI_RESPONSES = [
  "Great idea! Adding a WhatsApp opt-in will boost follow-up reach significantly.",
  "You can add a 'Preferred contact time' dropdown with Morning / Afternoon / Evening options.",
  "Consider adding a CAPTCHA or honeypot field to prevent spam submissions.",
  "A progress bar at the top increases form completion rate by up to 28%.",
  "Making phone field show +91 prefix by default reduces input errors.",
  "Adding 'How did you hear about us?' dropdown helps track marketing channels.",
]

function renderField(f, idx, starState, setStarState) {
  if (!f || !f.type) return null
  if (f.type === 'section') return <div key={idx} className="fc-fsec">{f.label}</div>
  if (f.type === 'cardicons') return (
    <div key={idx} style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
      {['VISA', 'MC', 'UPI', 'PayPal'].map(b => (
        <span key={b} style={{ fontSize: 11, fontWeight: 600, background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 5, padding: '3px 9px', color: '#64748b' }}>{b}</span>
      ))}
    </div>
  )
  if (f.type === 'cardnum') return (
    <div key={idx} className="fc-fg">
      <label>Card number <span className="fc-req">*</span></label>
      <input type="text" name="card_number" placeholder="1234  5678  9012  3456" maxLength={19} />
    </div>
  )
  if (f.type === 'row3card') return (
    <div key={idx} className="fc-frow3">
      <div className="fc-fg"><label>Expiry <span className="fc-req">*</span></label><input type="text" name="expiry" placeholder="MM / YY" /></div>
      <div className="fc-fg"><label>CVV <span className="fc-req">*</span></label><input type="text" name="cvv" placeholder="123" maxLength={4} /></div>
      <div className="fc-fg"><label>ZIP</label><input type="text" name="zip" placeholder="302001" /></div>
    </div>
  )
  if (f.type === 'submit') return null
  if (f.type === 'row2') return (
    <div key={idx} className="fc-frow">
      {(f.fields || []).map((ff, i) => renderField(ff, `${idx}_${i}`, starState, setStarState))}
    </div>
  )
  if (f.type === 'rating') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <div className="fc-star-row">
        {[1, 2, 3, 4, 5].map(v => (
          <span
            key={v}
            className={`fc-star${(starState[idx] || 0) >= v ? ' on' : ''}`}
            onClick={() => setStarState(s => ({ ...s, [idx]: v }))}
          >★</span>
        ))}
      </div>
    </div>
  )
  if (f.type === 'range') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <input type="range" name={f.label || 'range'} min="0" max="10" defaultValue="7" style={{ accentColor: '#d97706', width: '100%' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b', marginTop: 2 }}>
        <span>0</span><span>10</span>
      </div>
    </div>
  )
  if (f.type === 'radio') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <div className="fc-radio-g">
        {(f.options || []).map(o => (
          <label key={o} className="fc-radio-opt">
            <input type="radio" name={f.label || `radio_${idx}`} value={o} />{o}
          </label>
        ))}
      </div>
    </div>
  )
  if (f.type === 'checkbox') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}</label>
      <div className="fc-check-g">
        {(f.options || []).map(o => (
          <label key={o} className="fc-check-opt">
            <input type="checkbox" name={`${f.label || 'check'}_${idx}`} value={o} />{o}
          </label>
        ))}
      </div>
    </div>
  )
  if (f.type === 'select') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <select name={f.label || `select_${idx}`} required={f.required}>
        <option value="">Select...</option>
        {(f.options || []).map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
  if (f.type === 'textarea') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <textarea name={f.label || `textarea_${idx}`} placeholder={f.placeholder || ''} required={f.required} />
    </div>
  )
  if (f.type === 'file') return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <input type="file" name={f.label || `file_${idx}`} style={{ padding: 6 }} required={f.required} />
    </div>
  )
  if (f.type === 'divider') return <hr key={idx} style={{ border: 'none', borderTop: '1.5px dashed #e2e8f0', margin: '8px 0 14px' }} />
  const itype = f.type === 'email' ? 'email' : f.type === 'phone' ? 'tel' : f.type === 'number' ? 'number' : f.type === 'date' ? 'date' : 'text'
  return (
    <div key={idx} className="fc-fg">
      <label>{f.label}{f.required && <span className="fc-req"> *</span>}</label>
      <input type={itype} name={f.label || `${f.type}_${idx}`} placeholder={f.placeholder || ''} required={f.required} />
    </div>
  )
}

const adaptCustomForm = cf => ({
  id: `custom_${cf.id}`,
  title: cf.title,
  category: 'custom',
  description: `${cf.fields.length} field${cf.fields.length !== 1 ? 's' : ''} • Built with Builder`,
  color: '#6c63ff',
  badge: '🔨 Custom',
  tags: ['custom'],
  score: null,
  score_tip: null,
  fields: cf.fields,
  suggestions: [],
})

function ShareModal({ formId, title, onClose }) {
  const link = `${window.location.origin}/form/${formId}`
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(link)
      } else {
        const el = document.createElement('textarea')
        el.value = link; el.style.position = 'fixed'; el.style.opacity = '0'
        document.body.appendChild(el); el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
      }
      setCopied(true); setTimeout(() => setCopied(false), 2500)
    } catch (e) {
      console.error('Copy failed:', e)
    }
  }
  return createPortal(
    <div onClick={e => { if (e.target === e.currentTarget) { e.stopPropagation(); onClose() } }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.55)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ background: '#fff', borderRadius: 16, width: '100%', maxWidth: 460, padding: '28px 28px 24px', boxShadow: '0 16px 48px rgba(15,23,42,.18)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', margin: 0 }}>🔗 Share Form</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer', color: '#64748b', lineHeight: 1 }}>✕</button>
        </div>

        <p style={{ fontSize: 13, color: '#64748b', marginBottom: 14 }}>
          Share this link with anyone — they can open it in any browser, fill your <strong style={{ color: '#0f172a' }}>{title}</strong> form and submit it. No login required.
        </p>

        <a href={link} target="_blank" rel="noopener noreferrer"
          style={{ display: 'flex', alignItems: 'center', background: '#f8fafc', border: '1.5px solid #e2e8f0', borderRadius: 10, padding: '10px 14px', marginBottom: 14, gap: 10, textDecoration: 'none', cursor: 'pointer' }}>
          <span style={{ flex: 1, fontSize: 13, color: '#1a56db', wordBreak: 'break-all', fontFamily: 'monospace' }}>{link}</span>
          <span style={{ fontSize: 11, color: '#94a3b8', whiteSpace: 'nowrap', flexShrink: 0 }}>↗ Open</span>
        </a>

        <button onClick={copy}
          style={{ width: '100%', padding: '11px', border: 'none', borderRadius: 10, background: copied ? '#059669' : '#1a56db', color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', transition: 'background .2s' }}>
          {copied ? '✅ Link Copied!' : '📋 Copy Link'}
        </button>

        <p style={{ fontSize: 11, color: '#94a3b8', textAlign: 'center', marginTop: 12, marginBottom: 0 }}>
          The person opening this link will see just the form — clean, no distractions.
        </p>
      </div>
    </div>,
    document.body
  )
}

function ShareBtn({ formId, title }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button onClick={e => { e.stopPropagation(); setOpen(true) }}
        style={{ padding: '3px 9px', fontSize: 11, fontWeight: 600, border: '1.5px solid #e2e8f0', borderRadius: 6, background: '#fff', color: '#94a3b8', cursor: 'pointer', fontFamily: 'inherit', whiteSpace: 'nowrap' }}>
        🔗 Share
      </button>
      {open && <ShareModal formId={formId} title={title} onClose={() => setOpen(false)} />}
    </>
  )
}

function FilterDropdown({ filter, label, templates, pos, onSelect, onMouseEnter, onMouseLeave }) {
  const items = templates.filter(t => t.category === filter)
  if (!items.length) return null

  const viewportW = window.innerWidth
  const dropW = 340
  const left = Math.min(pos.left, viewportW - dropW - 12)

  return createPortal(
    <div
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      style={{
        position: 'fixed', top: pos.bottom + 6, left, zIndex: 8000, width: dropW,
        background: '#fff', borderRadius: 14, border: '1.5px solid #e2e8f0',
        boxShadow: '0 12px 40px rgba(15,23,42,.16)', padding: '10px 8px', pointerEvents: 'auto',
      }}
    >
      <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.08em', padding: '2px 10px 8px' }}>
        {label} — {items.length} template{items.length !== 1 ? 's' : ''}
      </div>
      {items.map(t => (
        <div key={t.id}
          onClick={() => onSelect(t)}
          style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '9px 10px', borderRadius: 9, cursor: 'pointer', transition: 'background .12s' }}
          onMouseEnter={e => e.currentTarget.style.background = '#f8fafc'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          <div style={{ width: 38, height: 38, borderRadius: 9, background: `${t.color}18`, border: `1.5px solid ${t.color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <div style={{ width: 16, height: 16, borderRadius: 3, background: t.color, opacity: .7 }} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.title}</div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.description}</div>
          </div>
          {t.badge && (
            <span style={{ fontSize: 10, fontWeight: 700, color: t.color, background: `${t.color}15`, padding: '2px 7px', borderRadius: 10, whiteSpace: 'nowrap', flexShrink: 0 }}>{t.badge}</span>
          )}
        </div>
      ))}
    </div>,
    document.body
  )
}

function FormModal({ currentTemplate, onClose }) {
  const [activeTab, setActiveTab] = useState('form')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [starState, setStarState] = useState({})
  const [addedSugs, setAddedSugs] = useState({})
  const [formFields, setFormFields] = useState(currentTemplate.fields || [])
  const [aiInput, setAiInput] = useState('')
  const [aiResp, setAiResp] = useState('')

  const submitLabel = formFields.find(f => f.type === 'submit')?.label || 'Submit'
  const submitColor = formFields.find(f => f.type === 'submit')?.color || '#1a56db'

  const addSuggestedField = (sug, i) => {
    if (addedSugs[i] || !sug.field) return
    setFormFields(prev => {
      const submitIdx = prev.findIndex(f => f.type === 'submit')
      if (submitIdx === -1) return [...prev, sug.field]
      return [...prev.slice(0, submitIdx), sug.field, ...prev.slice(submitIdx)]
    })
    setAddedSugs(p => ({ ...p, [i]: true }))
  }

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
      await fetch('/api/submissions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: String(currentTemplate.id), form_title: currentTemplate.title, data }),
      })
      setSubmitted(true)
      setTimeout(onClose, 2500)
    } catch { alert('Failed to save. Make sure the backend is running.') }
    finally { setSubmitting(false) }
  }

  const askAI = () => {
    if (!aiInput.trim()) return
    setAiResp('🤔 Thinking...')
    setTimeout(() => {
      setAiResp('🤖 ' + AI_RESPONSES[Math.floor(Math.random() * AI_RESPONSES.length)])
    }, 700)
    setAiInput('')
  }

  const TABS = [
    { key: 'form', label: '📝 Form' },
    { key: 'integrations', label: '🔗 Integrations' },
  ]

  return (
    <div className="fc-overlay open" onClick={e => e.target.classList.contains('fc-overlay') && onClose()}>
      <div className="fc-modal">
        <div className="fc-mhdr">
          <div className="fc-mhdr-l">
            <h2>{currentTemplate.title}</h2>
            <p>{currentTemplate.description}</p>
          </div>
          {/* Tab switcher */}
          <div style={{ display: 'flex', borderRadius: 10, border: '1.5px solid #e2e8f0', overflow: 'hidden', marginLeft: 'auto', marginRight: 12 }}>
            {TABS.map(t => (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                style={{ padding: '6px 14px', border: 'none', background: activeTab === t.key ? '#1a56db' : '#fff', color: activeTab === t.key ? '#fff' : '#64748b', fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', borderRight: t.key === 'form' ? '1px solid #e2e8f0' : 'none' }}>
                {t.label}
              </button>
            ))}
          </div>
          <button className="fc-mclose" onClick={onClose}>✕</button>
        </div>

        {activeTab === 'form' ? (
          <div className="fc-mbody">
            <div className="fc-mform">
              {submitted ? (
                <div className="fc-form-success show"><span style={{ display: 'block', fontSize: 28, marginBottom: 6 }}>✅</span>Submitted successfully!</div>
              ) : (
                <form onSubmit={handleSubmit}>
                  {formFields.filter(f => f.type !== 'submit').map((f, i) => renderField(f, i, starState, setStarState))}
                  <button type="submit" className="fc-submit-btn" style={{ background: submitColor }} disabled={submitting}>
                    {submitting ? '⏳ Saving...' : submitLabel}
                  </button>
                </form>
              )}
            </div>
            <div className="fc-mai">
              <div className="fc-ai-hdr"><span className="fc-ai-dot" />AI Suggestions</div>
              {currentTemplate.score && (
                <div className="fc-ai-score-box">
                  <div className="fc-score-n">{currentTemplate.score}</div>
                  <div className="fc-score-info"><strong>Form Score</strong><p>{currentTemplate.score_tip || 'Keep improving!'}</p></div>
                </div>
              )}
              {(currentTemplate.suggestions || []).length > 0 && (
                <>
                  <div className="fc-ai-section-lbl">Recommended fields</div>
                  {currentTemplate.suggestions.map((s, i) => (
                    <div key={i} className="fc-ai-sug">
                      <h4>{s.icon} {s.title}</h4>
                      <p>{s.text}</p>
                      <button className={`fc-add-btn${addedSugs[i] ? ' done' : ''}`} onClick={() => addSuggestedField(s, i)} disabled={addedSugs[i]}>
                        {addedSugs[i] ? '✓ Added' : '+ Add this field'}
                      </button>
                    </div>
                  ))}
                </>
              )}
              {(currentTemplate.suggestions || []).length === 0 && (
                <div style={{ fontSize: 12, color: '#64748b', textAlign: 'center', padding: '16px 0' }}>
                  <p style={{ fontSize: 20, marginBottom: 6 }}>🔨</p>
                  <p>Custom form — fill it out and submit!</p>
                </div>
              )}
              <div className="fc-ai-section-lbl">Ask AI anything</div>
              <div className="fc-ai-ask-wrap">
                <input placeholder="e.g. add a rating field..." value={aiInput} onChange={e => setAiInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && askAI()} />
                <button className="fc-ask-btn" onClick={askAI}>Ask</button>
              </div>
              {aiResp && <div className="fc-ai-resp show">{aiResp}</div>}
            </div>
          </div>
        ) : (
          <IntegrationsTab formId={String(currentTemplate.id)} />
        )}
      </div>
    </div>
  )
}

const EXCEL_FEATURES = [
  { icon: '📥', label: 'Import from Excel', desc: 'Upload .xlsx and auto-generate form fields' },
  { icon: '📤', label: 'Export submissions', desc: 'Download all responses as spreadsheet' },
  { icon: '🔄', label: 'Auto field mapping', desc: 'Column headers become form fields' },
  { icon: '📊', label: 'CSV support', desc: 'Works with .xlsx, .xls and .csv files' },
]

const TEMPLATE_TYPES = [
  { key: 'form_type',      icon: '📝', label: 'Form Template',    color: '#1a56db', desc: 'Standard web forms' },
  { key: 'app_type',       icon: '📱', label: 'App Template',     color: '#7c3aed', desc: 'App-like interfaces' },
  { key: 'table_type',     icon: '📊', label: 'Table Template',   color: '#059669', desc: 'Data entry & tables' },
  { key: 'pdf_type',       icon: '📄', label: 'PDF Template',     color: '#dc2626', desc: 'Documents & reports' },
  { key: 'card_form_type', icon: '💳', label: 'Card Form',        color: '#d97706', desc: 'Card-based checkout' },
  { key: 'store_type',     icon: '🛒', label: 'Store Builder',    color: '#0891b2', desc: 'E-commerce & orders' },
  { key: 'workflow_type',  icon: '⚡', label: 'Workflow',         color: '#f59e0b', desc: 'Multi-step processes' },
  { key: 'sign_type',      icon: '✍️', label: 'Sign Template',    color: '#4f46e5', desc: 'e-Signatures & contracts' },
  { key: 'board_type',     icon: '📌', label: 'Board Template',   color: '#db2777', desc: 'Kanban & project boards' },
]

function TemplateTypeDropdown({ pos, typeKey, templates, onSelect, onMouseEnter, onMouseLeave }) {
  const viewportW = window.innerWidth

  // ── All-types grid (shown from the folder button) ──────────────────────────
  if (typeKey === '__all__') {
    const dropW = 430
    const left = Math.min(Math.max(pos.left + pos.width / 2 - dropW / 2, 8), viewportW - dropW - 8)
    return createPortal(
      <div
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        style={{
          position: 'fixed', top: pos.bottom + 8, left, zIndex: 8000, width: dropW,
          background: '#fff', borderRadius: 16, border: '1.5px solid #e0e7ff',
          boxShadow: '0 16px 48px rgba(79,70,229,.14)', padding: '14px 10px', pointerEvents: 'auto',
        }}
      >
        <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.08em', padding: '2px 10px 10px' }}>
          Browse by Template Type
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 4 }}>
          {TEMPLATE_TYPES.map(t => {
            const count = templates.filter(tp => tp.category === t.key).length
            return (
              <div
                key={t.key}
                onClick={() => onSelect(t.key)}
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'flex-start',
                  gap: 4, padding: '10px 12px', borderRadius: 10, cursor: 'pointer',
                  border: '1.5px solid transparent', transition: 'all .12s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = `${t.color}12`
                  e.currentTarget.style.borderColor = `${t.color}35`
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.borderColor = 'transparent'
                }}
              >
                <span style={{ fontSize: 22 }}>{t.icon}</span>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', lineHeight: 1.3 }}>{t.label}</div>
                <div style={{ fontSize: 10, color: '#94a3b8' }}>{count} templates</div>
              </div>
            )
          })}
        </div>
      </div>,
      document.body
    )
  }

  // ── Per-type template list ─────────────────────────────────────────────────
  const meta = TEMPLATE_TYPES.find(t => t.key === typeKey)
  if (!meta) return null
  const items = templates.filter(t => t.category === typeKey)
  const dropW = 320
  const left = Math.min(Math.max(pos.left - 20, 8), viewportW - dropW - 8)
  return createPortal(
    <div
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      style={{
        position: 'fixed', top: pos.bottom + 8, left, zIndex: 8000, width: dropW,
        background: '#fff', borderRadius: 14, border: `1.5px solid ${meta.color}30`,
        boxShadow: `0 16px 48px ${meta.color}22`, padding: '12px 8px', pointerEvents: 'auto',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '2px 10px 10px' }}>
        <span style={{ fontSize: 16 }}>{meta.icon}</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: meta.color, textTransform: 'uppercase', letterSpacing: '.07em' }}>{meta.label}s</span>
        <span style={{ fontSize: 10, color: '#94a3b8', marginLeft: 'auto' }}>{items.length} templates</span>
      </div>
      {items.map(t => (
        <div
          key={t.id}
          onClick={() => onSelect(t.id)}
          style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 9, cursor: 'pointer', transition: 'background .12s' }}
          onMouseEnter={e => e.currentTarget.style.background = `${meta.color}0e`}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          <div style={{ width: 34, height: 34, borderRadius: 8, background: `${meta.color}15`, border: `1.5px solid ${meta.color}25`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 14 }}>
            {meta.icon}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.title}</div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.description}</div>
          </div>
        </div>
      ))}
      <div
        onClick={() => onSelect(typeKey)}
        style={{ margin: '8px 10px 2px', padding: '8px 12px', background: `${meta.color}12`, border: `1.5px solid ${meta.color}30`, borderRadius: 9, textAlign: 'center', fontSize: 12, fontWeight: 700, color: meta.color, cursor: 'pointer' }}
        onMouseEnter={e => e.currentTarget.style.background = `${meta.color}22`}
        onMouseLeave={e => e.currentTarget.style.background = `${meta.color}12`}
      >
        View all {meta.label}s →
      </div>
    </div>,
    document.body
  )
}

function ExcelHoverCard({ pos, onMouseEnter, onMouseLeave, onClick }) {
  const viewportW = window.innerWidth
  const cardW = 280
  const left = Math.min(pos.left, viewportW - cardW - 12)
  return createPortal(
    <div
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
      style={{
        position: 'fixed', top: pos.bottom + 6, left, zIndex: 8000, width: cardW,
        background: '#fff', borderRadius: 14, border: '1.5px solid #a5d6a7',
        boxShadow: '0 12px 40px rgba(33,115,70,.18)', padding: '14px 12px', pointerEvents: 'auto', cursor: 'pointer',
      }}
    >
      <div style={{ fontSize: 10, fontWeight: 700, color: '#388e3c', textTransform: 'uppercase', letterSpacing: '.08em', padding: '0 6px 10px' }}>
        Microsoft Excel Integration
      </div>
      {EXCEL_FEATURES.map(f => (
        <div key={f.label} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '7px 6px', borderRadius: 8 }}
          onMouseEnter={e => e.currentTarget.style.background = '#f1f8e9'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
          <span style={{ fontSize: 16, flexShrink: 0 }}>{f.icon}</span>
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, color: '#1b5e20' }}>{f.label}</div>
            <div style={{ fontSize: 11, color: '#66bb6a' }}>{f.desc}</div>
          </div>
        </div>
      ))}
      <div style={{ marginTop: 10, padding: '8px 10px', background: '#217346', borderRadius: 9, textAlign: 'center', fontSize: 12, fontWeight: 700, color: '#fff' }}>
        Click to Open Excel Integration →
      </div>
    </div>,
    document.body
  )
}

export default function TemplatesPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [templates, setTemplates] = useState([])
  const [customForms, setCustomForms] = useState([])
  const [activeFilter, setActiveFilter] = useState(
    searchParams.get('myforms') ? 'custom' :
    searchParams.get('type') ? searchParams.get('type') : 'all'
  )
  const [search, setSearch] = useState('')
  const [currentTemplate, setCurrentTemplate] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const [hoveredFilter, setHoveredFilter] = useState(null)
  const [hoveredLabel, setHoveredLabel] = useState('')
  const [dropPos, setDropPos] = useState(null)
  const [showTypesDropdown, setShowTypesDropdown] = useState(false)
  const [typesBtnPos, setTypesBtnPos] = useState(null)
  const [hoveredTypeKey, setHoveredTypeKey] = useState(null)
  const hideTimer = useRef(null)
  const typesHideTimer = useRef(null)

  // Load data once on mount
  useEffect(() => {
    fetch('/api/', { headers: authHeaders() }).then(r => r.ok ? setApiStatus('ok') : setApiStatus('err')).catch(() => setApiStatus('err'))
    fetch('/api/templates').then(r => r.json()).then(setTemplates).catch(() => {})
    fetch('/api/forms', { headers: authHeaders() }).then(r => r.json()).then(setCustomForms).catch(() => setCustomForms([]))
  }, [])

  // React to ?template= param
  useEffect(() => {
    const tid = searchParams.get('template')
    if (!tid || !templates.length) return
    const found = templates.find(t => t.id === tid)
    if (found) {
      setCurrentTemplate(found)
      setIsModalOpen(true)
      setSearchParams(p => { p.delete('template'); return p }, { replace: true })
    }
  }, [searchParams, templates])

  // React to ?type= param (from Navbar Browse Types)
  useEffect(() => {
    const type = searchParams.get('type')
    if (!type) return
    setActiveFilter(type)
    setSearchParams(p => { p.delete('type'); return p }, { replace: true })
  }, [searchParams])

  const filtered = useMemo(() => templates.filter(t => {
    if (activeFilter === 'custom') return false
    const mc = activeFilter === 'all' ? true : t.category === activeFilter
    const mq = !search || t.title.toLowerCase().includes(search.toLowerCase()) ||
      (t.tags || []).some(tg => tg.toLowerCase().includes(search.toLowerCase()))
    return mc && mq
  }), [templates, activeFilter, search])

  const activeTypeMeta = TEMPLATE_TYPES.find(t => t.key === activeFilter) || null

  const isTypeFilter = TEMPLATE_TYPES.some(t => t.key === activeFilter)

  const filteredCustom = useMemo(() => customForms.filter(cf => {
    if (isTypeFilter) return false
    if (activeFilter !== 'all' && activeFilter !== 'custom') return false
    if (!search) return true
    return cf.title.toLowerCase().includes(search.toLowerCase())
  }), [customForms, activeFilter, search, isTypeFilter])

  const openModal = useCallback(t => {
    setCurrentTemplate(t)
    setIsModalOpen(true)
  }, [])

  const closeModal = useCallback(() => {
    setIsModalOpen(false)
    setCurrentTemplate(null)
  }, [])

  return (
    <div className="fc">
      <div className="fc-hero">
        <div className="fc-hero-tag">✦ Real PostgreSQL Backend</div>
        <h1>Forms that <em>convert</em><br />& impress</h1>
        <p>Click any template to preview it instantly. All submissions saved to PostgreSQL.</p>
        <div className="fc-search-wrap">
          <input placeholder="Search templates..." value={search} onChange={e => setSearch(e.target.value)} />
          <button onClick={() => {}}>Search</button>
        </div>
        <div style={{ marginTop: 12, fontSize: 12, color: apiStatus === 'ok' ? '#065f46' : '#991b1b' }}>
          {apiStatus === 'checking' ? '⚡ Checking API...' : apiStatus === 'ok' ? '🟢 API Connected' : '🔴 API Offline'}
        </div>
      </div>

      <div className="fc-filter-row">
        {[
          ['all','All'],
          ['contact','📬 Contact'],
          ['registration','📝 Registration'],
          ['feedback','⭐ Feedback'],
          ['payment','💳 Payment'],
          ['hr','👔 HR / Jobs'],
          ['booking','📅 Booking'],
          ['survey','📊 Survey'],
          ['support','🐛 Support'],
          ['marketing','📣 Marketing'],
          ['custom','🔨 My Forms'],
        ].map(([f, label]) => (
          <button
            key={f}
            className={`fc-filter-pill${activeFilter === f ? ' active' : ''}`}
            onClick={() => { setActiveFilter(f); setHoveredFilter(null) }}
            onMouseEnter={e => {
              clearTimeout(hideTimer.current)
              if (f === 'all' || f === 'custom') { setHoveredFilter(null); return }
              const rect = e.currentTarget.getBoundingClientRect()
              setDropPos(rect)
              setHoveredFilter(f)
              setHoveredLabel(label)
            }}
            onMouseLeave={() => {
              hideTimer.current = setTimeout(() => setHoveredFilter(null), 180)
            }}
          >
            {label}
          </button>
        ))}

      </div>

      {showTypesDropdown && typesBtnPos && hoveredTypeKey && (
        <TemplateTypeDropdown
          pos={typesBtnPos}
          typeKey={hoveredTypeKey}
          templates={templates}
          onSelect={idOrKey => {
            setShowTypesDropdown(false)
            setHoveredTypeKey(null)
            const byId = templates.find(t => t.id === idOrKey)
            if (byId) { openModal(byId) }
            else { setActiveFilter(idOrKey) }
          }}
          onMouseEnter={() => clearTimeout(typesHideTimer.current)}
          onMouseLeave={() => { typesHideTimer.current = setTimeout(() => { setShowTypesDropdown(false); setHoveredTypeKey(null) }, 180) }}
        />
      )}

      {hoveredFilter && dropPos && (
        <FilterDropdown
          filter={hoveredFilter}
          label={hoveredLabel}
          templates={templates}
          pos={dropPos}
          onSelect={t => { openModal(t); setHoveredFilter(null) }}
          onMouseEnter={() => clearTimeout(hideTimer.current)}
          onMouseLeave={() => { hideTimer.current = setTimeout(() => setHoveredFilter(null), 180) }}
        />
      )}

      {/* Type category header banner */}
      {activeTypeMeta && (
        <div style={{ padding: '12px 36px 0', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10, padding: '8px 16px',
            background: `${activeTypeMeta.color}10`, border: `1.5px solid ${activeTypeMeta.color}30`,
            borderRadius: 10,
          }}>
            <span style={{ fontSize: 18 }}>{activeTypeMeta.icon}</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: activeTypeMeta.color }}>{activeTypeMeta.label}s</span>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>— {filtered.length} template{filtered.length !== 1 ? 's' : ''}</span>
          </div>
          <button
            onClick={() => setActiveFilter('all')}
            style={{ fontSize: 12, color: '#94a3b8', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: '4px 8px', borderRadius: 6 }}
          >
            ✕ Clear
          </button>
        </div>
      )}

      {/* Templates grid */}
      {activeFilter !== 'custom' && (
        <div className="fc-grid">
          {filtered.length === 0 && activeFilter !== 'custom' && (
            <div className="fc-loading"><div className="fc-spinner" /><p>No templates found</p></div>
          )}
          {filtered.map(t => (
            <div key={t.id} className="fc-tcard" onClick={() => openModal(t)}>
              <div className="fc-tcard-preview" style={{ background: `${t.color}18` }}>
                {t.badge && <div className="fc-badge-pill" style={{ color: t.color }}>{t.badge}</div>}
                <div className="fc-mf title" /><div className="fc-mf lbl" /><div className="fc-mf" />
                <div className="fc-mf lbl" style={{ width: '50%' }} /><div className="fc-mf" />
                <div className="fc-mf btn" style={{ background: `${t.color}cc` }} />
              </div>
              <div className="fc-tcard-body">
                <div className="fc-tcard-cat">{t.category}</div>
                <div className="fc-tcard-title">{t.title}</div>
                <div className="fc-tcard-desc">{t.description}</div>
                <div className="fc-tcard-foot">
                  <div className="fc-tags">{(t.tags || []).map(tg => <span key={tg} className="fc-tag">{tg}</span>)}</div>
                  <div style={{ display: 'flex', gap: 5 }}>
                    <ShareBtn formId={t.id} title={t.title} />
                    <button className="fc-use-btn" onClick={e => { e.stopPropagation(); openModal(t) }}>Use →</button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* My Forms section */}
      {(activeFilter === 'all' || activeFilter === 'custom') && filteredCustom.length > 0 && (
        <>
          <div style={{ padding: '8px 36px 0', display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1, height: 1, background: '#e2e8f0' }} />
            <span style={{ fontSize: 11, fontWeight: 700, color: '#6c63ff', textTransform: 'uppercase', letterSpacing: '.07em', whiteSpace: 'nowrap' }}>
              🔨 My Forms ({filteredCustom.length})
            </span>
            <div style={{ flex: 1, height: 1, background: '#e2e8f0' }} />
          </div>
          <div className="fc-grid">
            {filteredCustom.map(cf => {
              const adapted = adaptCustomForm(cf)
              return (
                <div key={cf.id} className="fc-tcard" onClick={() => openModal(adapted)}>
                  <div className="fc-tcard-preview" style={{ background: '#6c63ff18' }}>
                    <div className="fc-badge-pill" style={{ color: '#6c63ff' }}>🔨 Custom</div>
                    <div className="fc-mf title" /><div className="fc-mf lbl" /><div className="fc-mf" />
                    <div className="fc-mf lbl" style={{ width: '50%' }} /><div className="fc-mf" />
                    <div className="fc-mf btn" style={{ background: '#6c63ffcc' }} />
                  </div>
                  <div className="fc-tcard-body">
                    <div className="fc-tcard-cat" style={{ color: '#6c63ff' }}>custom</div>
                    <div className="fc-tcard-title">{cf.title}</div>
                    <div className="fc-tcard-desc">{adapted.description}</div>
                    <div className="fc-tcard-foot">
                      <span style={{ fontSize: 11, color: '#94a3b8' }}>
                        {new Date(cf.created_at).toLocaleDateString('en-IN')}
                      </span>
                      <div style={{ display: 'flex', gap: 5 }}>
                        <ShareBtn formId={adapted.id} title={cf.title} />
                        <button className="fc-use-btn" style={{ borderColor: '#6c63ff', color: '#6c63ff' }} onClick={e => { e.stopPropagation(); openModal(adapted) }}>Use →</button>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </>
      )}

      {activeFilter === 'custom' && filteredCustom.length === 0 && (
        <div className="fc-loading">
          <div style={{ fontSize: 36, marginBottom: 10 }}>🔨</div>
          <p>No custom forms yet. <a href="/formcraft/builder" style={{ color: '#6c63ff', fontWeight: 600 }}>Build one →</a></p>
        </div>
      )}

      {isModalOpen && currentTemplate && (
        <FormModal currentTemplate={currentTemplate} onClose={closeModal} />
      )}
    </div>
  )
}
