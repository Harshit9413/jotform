import { useState, useEffect } from 'react'
import './formcraft.css'

export default function SubmissionsPage() {
  const [submissions, setSubmissions] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedSub, setSelectedSub] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [subs, st] = await Promise.all([
        fetch('/api/submissions').then(r => r.json()),
        fetch('/api/stats').then(r => r.json()),
      ])
      setSubmissions(subs)
      setStats(st)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const viewSub = async id => {
    const s = await fetch(`/api/submissions/${id}`).then(r => r.json())
    setSelectedSub(s)
    await fetch(`/api/submissions/${id}/read`, { method: 'PATCH' })
    load()
  }

  const clearAll = async () => {
    if (!confirm('Delete ALL submissions? This cannot be undone.')) return
    await fetch('/api/submissions', { method: 'DELETE' })
    load()
  }

  const exportCSV = () => {
    if (!submissions.length) { alert('No submissions to export.'); return }
    const rows = [['ID', 'Form', 'Date', 'Status', 'Data']]
    submissions.forEach(s => rows.push([s.id, s.form_title, s.submitted_at, s.status, JSON.stringify(s.data)]))
    const csv = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n')
    const a = document.createElement('a')
    a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
    a.download = 'formcraft_submissions.csv'
    a.click()
  }

  return (
    <div className="fc">
      <div className="fc-sub-page">
        <div className="fc-sub-hdr">
          <h2>📊 Submissions</h2>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="fc-btn-ghost" onClick={exportCSV}>⬇️ Export CSV</button>
            <button className="fc-btn-ghost" style={{ borderColor: '#dc2626', color: '#dc2626' }} onClick={clearAll}>🗑 Clear All</button>
          </div>
        </div>

        {stats && (
          <div className="fc-stats-grid">
            {[
              { l: 'Total Submissions', v: stats.total, s: 'All time' },
              { l: 'New (Unread)', v: stats.new, s: 'Needs review' },
              { l: 'Today', v: stats.today, s: 'Submitted today' },
              { l: 'Completion Rate', v: stats.completion_rate, s: 'This week' },
            ].map(s => (
              <div key={s.l} className="fc-stat-card">
                <div className="fc-stat-lbl">{s.l}</div>
                <div className="fc-stat-val">{s.v}</div>
                <div className="fc-stat-sub">{s.s}</div>
              </div>
            ))}
          </div>
        )}

        <div className="fc-sub-table">
          <div className="fc-sub-table-hdr">
            <div>Submission</div><div>Form</div><div>Date</div><div>Status</div><div>Action</div>
          </div>
          {loading
            ? <div className="fc-loading"><div className="fc-spinner" /></div>
            : submissions.length === 0
            ? <div className="fc-empty-state"><div style={{ fontSize: 36, marginBottom: 10 }}>📭</div><p>No submissions yet.</p></div>
            : submissions.map(s => (
              <div key={s.id} className="fc-sub-row">
                <div style={{ fontWeight: 500 }}>#{s.id} — {Object.values(s.data || {})[0] || 'Anonymous'}</div>
                <div style={{ color: '#64748b', fontSize: 12 }}>{s.form_title}</div>
                <div style={{ color: '#64748b', fontSize: 12 }}>{new Date(s.submitted_at).toLocaleDateString('en-IN')}</div>
                <div><span className={`fc-status-${s.status}`}>{s.status === 'new' ? '🔵 New' : '✅ Read'}</span></div>
                <div><button className="fc-view-btn" onClick={() => viewSub(s.id)}>View</button></div>
              </div>
            ))
          }
        </div>
      </div>

      {selectedSub && (
        <div className="fc-overlay open" onClick={e => e.target.classList.contains('fc-overlay') && setSelectedSub(null)}>
          <div className="fc-detail-modal">
            <div className="fc-mhdr">
              <div className="fc-mhdr-l"><h2>Submission Detail</h2></div>
              <button className="fc-mclose" onClick={() => setSelectedSub(null)}>✕</button>
            </div>
            <div className="fc-detail-body">
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 11, color: '#64748b', marginBottom: 3 }}>Form</div>
                <div style={{ fontWeight: 600 }}>{selectedSub.form_title}</div>
              </div>
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 11, color: '#64748b', marginBottom: 3 }}>Submitted</div>
                <div>{new Date(selectedSub.submitted_at).toLocaleString('en-IN')}</div>
              </div>
              {Object.entries(selectedSub.data || {}).map(([k, v]) => (
                <div key={k} className="fc-detail-field">
                  <div className="fc-detail-key">{k}</div>
                  <div className="fc-detail-val">{Array.isArray(v) ? v.join(', ') : String(v)}</div>
                </div>
              ))}
              <button className="fc-btn-primary" style={{ width: '100%', marginTop: 18, padding: 11 }} onClick={() => setSelectedSub(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
