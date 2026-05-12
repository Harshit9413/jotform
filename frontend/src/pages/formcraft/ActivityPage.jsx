import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { authHeaders } from '../../utils/api'
import { useNavigate } from 'react-router-dom'
import { createPortal } from 'react-dom'

function ShareModal({ formId, title, onClose }) {
  const link = `${window.location.origin}/form/custom_${formId}`
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
    } catch { }
  }
  return createPortal(
    <div onClick={e => { if (e.target === e.currentTarget) onClose() }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.6)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div onClick={e => e.stopPropagation()}
        style={{ background: '#fff', borderRadius: 16, width: '100%', maxWidth: 460, padding: '28px 28px 24px', boxShadow: '0 20px 60px rgba(15,23,42,.2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', margin: 0 }}>Share Form</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', color: '#94a3b8', lineHeight: 1 }}>×</button>
        </div>
        <p style={{ fontSize: 13, color: '#64748b', marginBottom: 14 }}>
          Anyone with this link can fill the <strong style={{ color: '#0f172a' }}>{title}</strong> form — no login required.
        </p>
        <a href={link} target="_blank" rel="noopener noreferrer"
          style={{ display: 'flex', alignItems: 'center', background: '#f8fafc', border: '1.5px solid #e2e8f0', borderRadius: 10, padding: '10px 14px', marginBottom: 14, gap: 10, textDecoration: 'none' }}>
          <span style={{ flex: 1, fontSize: 12, color: '#1a56db', wordBreak: 'break-all', fontFamily: 'monospace' }}>{link}</span>
          <span style={{ fontSize: 11, color: '#94a3b8', whiteSpace: 'nowrap' }}>↗ Open</span>
        </a>
        <button onClick={copy}
          style={{ width: '100%', padding: '11px', border: 'none', borderRadius: 10, background: copied ? '#059669' : '#1a56db', color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', transition: 'background .2s' }}>
          {copied ? '✓ Copied!' : 'Copy Link'}
        </button>
      </div>
    </div>,
    document.body
  )
}

export default function ActivityPage() {
  const { auth } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [shareForm, setShareForm] = useState(null)
  const [emailEnabled, setEmailEnabled] = useState(null)

  useEffect(() => {
    fetch('/api/stats/user', { headers: authHeaders() })
      .then(r => r.json())
      .then(data => { setStats(data); setLoading(false) })
      .catch(() => setLoading(false))
    fetch('/api/settings/notifications')
      .then(r => r.json())
      .then(d => setEmailEnabled(d.email_enabled))
      .catch(() => {})
  }, [])

  const userName = auth?.user?.name || 'there'
  const initial = userName.charAt(0).toUpperCase()

  return (
    <div style={{ minHeight: '100vh', background: '#f1f5f9', fontFamily: "'DM Sans', 'Segoe UI', sans-serif" }}>

      {/* Hero header */}
      <div style={{ background: 'linear-gradient(135deg, #1a56db 0%, #1e40af 60%, #6c63ff 100%)', padding: '40px 0 56px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 32px', display: 'flex', alignItems: 'center', gap: 20 }}>
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'rgba(255,255,255,.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 700, color: '#fff', flexShrink: 0, border: '2px solid rgba(255,255,255,.35)' }}>
            {initial}
          </div>
          <div>
            <p style={{ color: 'rgba(255,255,255,.75)', fontSize: 13, margin: '0 0 4px', fontWeight: 500 }}>Welcome back</p>
            <h1 style={{ color: '#fff', fontSize: 26, fontWeight: 800, margin: 0 }}>{userName}</h1>
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 10 }}>
            <button onClick={() => navigate('/formcraft')}
              style={{ padding: '9px 18px', border: '1.5px solid rgba(255,255,255,.35)', borderRadius: 9, background: 'rgba(255,255,255,.1)', color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', backdropFilter: 'blur(4px)' }}>
              Browse Templates
            </button>
            <button onClick={() => navigate('/formcraft/builder')}
              style={{ padding: '9px 18px', border: 'none', borderRadius: 9, background: '#fff', color: '#1a56db', fontSize: 13, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
              + New Form
            </button>
          </div>
        </div>
      </div>

      {/* Cards pulled up */}
      <div style={{ maxWidth: 960, margin: '-28px auto 0', padding: '0 32px' }}>

        {/* Stat cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 }}>
          {[
            { label: 'Forms Created', value: loading ? '—' : (stats?.total_forms ?? 0), icon: '📋', color: '#1a56db', bg: '#eff6ff', border: '#bfdbfe' },
            { label: 'Total Submissions', value: loading ? '—' : (stats?.total_submissions ?? 0), icon: '📥', color: '#059669', bg: '#ecfdf5', border: '#a7f3d0' },
            { label: 'Account Status', value: 'Active', icon: '✅', color: '#7c3aed', bg: '#f5f3ff', border: '#ddd6fe' },
            {
              label: 'Email Alerts',
              value: emailEnabled === null ? '—' : (emailEnabled ? 'On' : 'Off'),
              icon: emailEnabled ? '🔔' : '🔕',
              color: emailEnabled ? '#059669' : '#94a3b8',
              bg: emailEnabled ? '#ecfdf5' : '#f8fafc',
              border: emailEnabled ? '#a7f3d0' : '#e2e8f0',
              tip: !emailEnabled,
            },
          ].map((c, i) => (
            <div key={i} style={{ background: '#fff', border: `1.5px solid ${c.border}`, borderRadius: 14, padding: '22px 20px', display: 'flex', alignItems: 'center', gap: 14, boxShadow: '0 2px 8px rgba(15,23,42,.06)', position: 'relative' }}>
              <div style={{ width: 46, height: 46, borderRadius: 12, background: c.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, flexShrink: 0 }}>
                {c.icon}
              </div>
              <div>
                <div style={{ fontSize: 26, fontWeight: 800, color: c.color, lineHeight: 1 }}>{c.value}</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 4, fontWeight: 500 }}>{c.label}</div>
                {c.tip && (
                  <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>Set RESEND_API_KEY in .env</div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* My Forms table */}
        <div style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 16, boxShadow: '0 2px 8px rgba(15,23,42,.06)', overflow: 'hidden', marginBottom: 24 }}>
          <div style={{ padding: '20px 24px', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', margin: '0 0 2px' }}>My Custom Forms</h2>
              <p style={{ fontSize: 12, color: '#94a3b8', margin: 0 }}>Forms you've built with the Form Builder</p>
            </div>
            <button onClick={() => navigate('/formcraft/builder')}
              style={{ padding: '8px 16px', border: 'none', borderRadius: 8, background: '#1a56db', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
              + Build New
            </button>
          </div>

          {loading ? (
            <div style={{ padding: '60px 24px', textAlign: 'center' }}>
              <div style={{ width: 32, height: 32, border: '3px solid #e2e8f0', borderTopColor: '#1a56db', borderRadius: '50%', animation: 'spin .8s linear infinite', margin: '0 auto 12px' }} />
              <p style={{ color: '#94a3b8', fontSize: 13 }}>Loading your forms...</p>
              <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
            </div>
          ) : !stats?.recent_forms?.length ? (
            <div style={{ padding: '60px 24px', textAlign: 'center' }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🛠️</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', margin: '0 0 8px' }}>No forms yet</h3>
              <p style={{ fontSize: 13, color: '#64748b', margin: '0 0 20px' }}>Build your first custom form with the drag-and-drop builder.</p>
              <button onClick={() => navigate('/formcraft/builder')}
                style={{ padding: '10px 24px', border: 'none', borderRadius: 9, background: '#1a56db', color: '#fff', fontSize: 13, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
                Open Builder →
              </button>
            </div>
          ) : (
            <>
              {/* Table head */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 150px 200px', gap: 12, padding: '10px 24px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                {['Form Name', 'Fields', 'Created On', 'Actions'].map(h => (
                  <span key={h} style={{ fontSize: 11, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.06em' }}>{h}</span>
                ))}
              </div>

              {stats.recent_forms.map((form, idx) => (
                <div key={form.id}
                  style={{ display: 'grid', gridTemplateColumns: '1fr 90px 150px 200px', gap: 12, padding: '14px 24px', alignItems: 'center', borderBottom: idx < stats.recent_forms.length - 1 ? '1px solid #f1f5f9' : 'none' }}
                  onMouseEnter={e => e.currentTarget.style.background = '#fafbfc'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>{form.title}</div>
                    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2, fontFamily: 'monospace' }}>ID: custom_{form.id}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#64748b', background: '#f1f5f9', padding: '3px 10px', borderRadius: 20 }}>
                      {form.field_count} {form.field_count === 1 ? 'field' : 'fields'}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: '#64748b' }}>
                    {new Date(form.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </div>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button onClick={() => setShareForm(form)}
                      style={{ padding: '5px 12px', fontSize: 11, fontWeight: 600, border: '1.5px solid #bfdbfe', borderRadius: 6, background: '#eff6ff', color: '#1a56db', cursor: 'pointer', fontFamily: 'inherit' }}>
                      Share
                    </button>
                    <button onClick={() => navigate(`/formcraft/submissions?form_id=custom_${form.id}`)}
                      style={{ padding: '5px 12px', fontSize: 11, fontWeight: 600, border: '1.5px solid #e2e8f0', borderRadius: 6, background: '#fff', color: '#64748b', cursor: 'pointer', fontFamily: 'inherit' }}>
                      Submissions
                    </button>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>

        {/* Quick links */}
        <div style={{ display: 'flex', gap: 12, paddingBottom: 40 }}>
          {[
            { label: '📋 All Templates', path: '/formcraft' },
            { label: '📊 All Submissions', path: '/formcraft/submissions' },
            { label: '🧠 QueryMind', path: '/querymind' },
          ].map(item => (
            <button key={item.path} onClick={() => navigate(item.path)}
              style={{ padding: '9px 18px', border: '1.5px solid #e2e8f0', borderRadius: 9, background: '#fff', color: '#64748b', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', boxShadow: '0 1px 3px rgba(15,23,42,.05)' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#1a56db'; e.currentTarget.style.color = '#1a56db' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }}>
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {shareForm && (
        <ShareModal formId={shareForm.id} title={shareForm.title} onClose={() => setShareForm(null)} />
      )}
    </div>
  )
}
