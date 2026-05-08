import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import './formcraft.css'

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
  const base = import.meta.env.VITE_APP_URL || window.location.origin
  const link = `${base}/form/${formId}`
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
  return (
    <div onClick={e => { if (e.target === e.currentTarget) { e.stopPropagation(); onClose() } }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.55)', zIndex: 500, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
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
    </div>
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

export default function TemplatesPage() {
  const [searchParams] = useSearchParams()
  const [templates, setTemplates] = useState([])
  const [customForms, setCustomForms] = useState([])
  const [activeFilter, setActiveFilter] = useState(searchParams.get('myforms') ? 'custom' : 'all')
  const [search, setSearch] = useState('')
  const [currentTemplate, setCurrentTemplate] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [starState, setStarState] = useState({})
  const [addedSugs, setAddedSugs] = useState({})
  const [formFields, setFormFields] = useState([])
  const [aiInput, setAiInput] = useState('')
  const [aiResp, setAiResp] = useState('')
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    fetch('/api/').then(r => r.ok ? setApiStatus('ok') : setApiStatus('err')).catch(() => setApiStatus('err'))
    fetch('/api/templates').then(r => r.json()).then(setTemplates).catch(() => {})
    fetch('/api/forms').then(r => r.json()).then(setCustomForms).catch(() => {})
  }, [])

  const filtered = templates.filter(t => {
    const mc = activeFilter === 'all' || activeFilter === 'custom' ? true : t.category === activeFilter
    const mq = !search || t.title.toLowerCase().includes(search.toLowerCase()) ||
      (t.tags || []).some(tg => tg.toLowerCase().includes(search.toLowerCase()))
    return mc && mq && activeFilter !== 'custom'
  })

  const filteredCustom = customForms.filter(cf => {
    if (activeFilter !== 'all' && activeFilter !== 'custom') return false
    if (!search) return true
    return cf.title.toLowerCase().includes(search.toLowerCase())
  })

  const openModal = t => {
    setCurrentTemplate(t)
    setFormFields(t.fields || [])
    setIsModalOpen(true)
    setSubmitted(false)
    setStarState({})
    setAddedSugs({})
    setAiResp('')
  }
  const closeModal = () => { setIsModalOpen(false); setCurrentTemplate(null); setFormFields([]) }

  const addSuggestedField = (sug, i) => {
    if (addedSugs[i] || !sug.field) return
    setFormFields(prev => {
      const submitIdx = prev.findIndex(f => f.type === 'submit')
      const newField = sug.field
      if (submitIdx === -1) return [...prev, newField]
      return [...prev.slice(0, submitIdx), newField, ...prev.slice(submitIdx)]
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
      setTimeout(closeModal, 2500)
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

  const submitLabel = formFields.find(f => f.type === 'submit')?.label || 'Submit'
  const submitColor = formFields.find(f => f.type === 'submit')?.color || '#1a56db'

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
          <button key={f} className={`fc-filter-pill${activeFilter === f ? ' active' : ''}`} onClick={() => setActiveFilter(f)}>{label}</button>
        ))}
      </div>

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
        <div className="fc-overlay open" onClick={e => e.target.classList.contains('fc-overlay') && closeModal()}>
          <div className="fc-modal">
            <div className="fc-mhdr">
              <div className="fc-mhdr-l">
                <h2>{currentTemplate.title}</h2>
                <p>{currentTemplate.description}</p>
              </div>
              <button className="fc-mclose" onClick={closeModal}>✕</button>
            </div>
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
          </div>
        </div>
      )}
    </div>
  )
}
