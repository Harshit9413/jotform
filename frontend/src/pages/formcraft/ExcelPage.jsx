import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import * as XLSX from 'xlsx'

const GREEN = '#217346'
const GREEN_LIGHT = '#e8f5e9'
const GREEN_BORDER = '#a5d6a7'

const TYPE_MAP = {
  email: 'email', mail: 'email',
  phone: 'phone', mobile: 'phone', contact: 'phone',
  date: 'date', dob: 'date', birthday: 'date',
  note: 'textarea', comment: 'textarea', message: 'textarea', description: 'textarea',
  number: 'number', age: 'number', count: 'number', qty: 'number', quantity: 'number',
}

let _xc = 0
function headersToFields(headers) {
  return headers.filter(Boolean).map(h => {
    const key = String(h).toLowerCase().trim()
    let type = 'text'
    for (const [kw, t] of Object.entries(TYPE_MAP)) {
      if (key.includes(kw)) { type = t; break }
    }
    return { id: `xf_${++_xc}`, type, label: String(h), placeholder: '', required: false }
  })
}

function parseExcelFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = e => {
      try {
        const wb = XLSX.read(e.target.result, { type: 'array' })
        const sheet = wb.Sheets[wb.SheetNames[0]]
        const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 })
        const headers = (rows[0] || []).filter(Boolean)
        if (!headers.length) { reject(new Error('No column headers found in first row')); return }
        resolve({ headers, sheetName: wb.SheetNames[0], rowCount: rows.length - 1 })
      } catch (err) {
        reject(new Error('Could not read file. Make sure it is a valid .xlsx or .csv file.'))
      }
    }
    reader.onerror = () => reject(new Error('File read failed'))
    reader.readAsArrayBuffer(file)
  })
}

// ── Drop Zone ─────────────────────────────────────────────────────────────────
function DropZone({ onFile, err }) {
  const inputRef = useRef()
  const [dragging, setDragging] = useState(false)

  const handleDrop = e => {
    e.preventDefault(); setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current.click()}
      style={{
        border: `2.5px dashed ${dragging ? GREEN : '#c8e6c9'}`,
        borderRadius: 14, padding: '36px 24px', textAlign: 'center',
        background: dragging ? '#f1f8e9' : '#fafff8', cursor: 'pointer',
        transition: 'all .18s',
      }}
    >
      <input ref={inputRef} type="file" accept=".xlsx,.xls,.csv" style={{ display: 'none' }}
        onChange={e => { const f = e.target.files[0]; if (f) { onFile(f); e.target.value = '' } }} />
      <div style={{ fontSize: 40, marginBottom: 10 }}>📂</div>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#1b5e20', marginBottom: 4 }}>
        Drop your Excel file here
      </div>
      <div style={{ fontSize: 13, color: '#66bb6a' }}>or click to browse — .xlsx, .xls, .csv</div>
      {err && (
        <div style={{ marginTop: 12, fontSize: 13, color: '#c62828', background: '#ffebee', border: '1px solid #ef9a9a', borderRadius: 8, padding: '8px 14px' }}>
          {err}
        </div>
      )}
    </div>
  )
}

// ── Field Preview Card ─────────────────────────────────────────────────────────
function FieldChip({ label, type }) {
  const icons = { email: '📧', phone: '📱', date: '📅', textarea: '📝', number: '🔢', text: '✏️' }
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 6,
      padding: '6px 12px', border: `1.5px solid ${GREEN_BORDER}`,
      borderRadius: 8, background: GREEN_LIGHT, fontSize: 12, fontWeight: 600, color: '#1b5e20',
    }}>
      <span>{icons[type] || '✏️'}</span>
      <span style={{ color: '#0f172a' }}>{label}</span>
      <span style={{ color: '#66bb6a', fontWeight: 400 }}>{type}</span>
    </div>
  )
}

// ── Template Card (Existing Template flow) ────────────────────────────────────
function TemplateCard({ t, onClick }) {
  return (
    <div onClick={onClick}
      style={{
        border: '1.5px solid #e2e8f0', borderRadius: 12, padding: '16px', cursor: 'pointer',
        background: '#fff', transition: 'all .15s',
      }}
      onMouseEnter={e => { e.currentTarget.style.border = `1.5px solid ${GREEN}`; e.currentTarget.style.boxShadow = '0 4px 16px rgba(33,115,70,.12)' }}
      onMouseLeave={e => { e.currentTarget.style.border = '1.5px solid #e2e8f0'; e.currentTarget.style.boxShadow = 'none' }}
    >
      <div style={{ width: 36, height: 36, borderRadius: 9, background: `${t.color}22`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10, fontSize: 16 }}>
        📋
      </div>
      <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>{t.title}</div>
      <div style={{ fontSize: 11, color: '#64748b' }}>{t.description}</div>
      <div style={{ marginTop: 10, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        {(t.tags || []).slice(0, 3).map(tg => (
          <span key={tg} style={{ fontSize: 10, padding: '2px 7px', borderRadius: 10, background: `${t.color}15`, color: t.color, fontWeight: 600 }}>{tg}</span>
        ))}
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function ExcelPage() {
  const navigate = useNavigate()
  const [mode, setMode] = useState(null)         // null | 'build' | 'existing'
  const [templates, setTemplates] = useState([])
  const [loadingTpl, setLoadingTpl] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [parseErr, setParseErr] = useState('')
  const [parsed, setParsed] = useState(null)     // { headers, fields, sheetName, rowCount, fileName }

  useEffect(() => {
    if (mode === 'existing') {
      setLoadingTpl(true)
      fetch('/api/templates').then(r => r.json()).then(d => { setTemplates(Array.isArray(d) ? d : []); setLoadingTpl(false) }).catch(() => setLoadingTpl(false))
    }
  }, [mode])

  const handleFile = async file => {
    setParsing(true); setParseErr(''); setParsed(null)
    try {
      const result = await parseExcelFile(file)
      const fields = headersToFields(result.headers)
      setParsed({ ...result, fields, fileName: file.name })
    } catch (err) {
      setParseErr(err.message)
    } finally {
      setParsing(false)
    }
  }

  const openInBuilder = () => {
    navigate('/formcraft/builder', {
      state: { title: parsed.fileName.replace(/\.(xlsx|xls|csv)$/i, ''), fields: parsed.fields },
    })
  }

  // ── Landing ────────────────────────────────────────────────────────────────
  if (!mode) return (
    <div style={{ minHeight: '100vh', background: '#f8fffe', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      {/* Header */}
      <div style={{ background: `linear-gradient(135deg, ${GREEN} 0%, #1a8a52 100%)`, padding: '40px 0 32px', textAlign: 'center', color: '#fff' }}>
        <button onClick={() => navigate('/formcraft')}
          style={{ position: 'absolute', left: 28, top: 20, background: 'rgba(255,255,255,.18)', border: 'none', color: '#fff', borderRadius: 8, padding: '6px 14px', cursor: 'pointer', fontSize: 13, fontWeight: 600, fontFamily: 'inherit' }}>
          ← Back
        </button>
        <div style={{ fontSize: 44, marginBottom: 12 }}>
          <img src="https://upload.wikimedia.org/wikipedia/commons/3/34/Microsoft_Office_Excel_%282019–present%29.svg"
            alt="Excel" width={52} height={52}
            style={{ verticalAlign: 'middle', marginRight: 10, filter: 'drop-shadow(0 2px 6px rgba(0,0,0,.25))' }}
            onError={e => { e.target.style.display = 'none' }} />
          📊
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, margin: '0 0 8px' }}>Microsoft Excel Integration</h1>
        <p style={{ fontSize: 14, color: 'rgba(255,255,255,.85)', margin: 0 }}>
          Import Excel data as form fields · Export submissions to spreadsheet
        </p>
      </div>

      {/* Feature chips */}
      <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap', padding: '20px 24px 0' }}>
        {['📥 Import from Excel', '📤 Export submissions', '🔄 Auto field mapping', '📋 Column → Field', '📊 CSV support'].map(f => (
          <span key={f} style={{ fontSize: 12, fontWeight: 600, padding: '5px 14px', borderRadius: 20, background: GREEN_LIGHT, color: GREEN, border: `1px solid ${GREEN_BORDER}` }}>{f}</span>
        ))}
      </div>

      {/* Two option cards */}
      <div style={{ display: 'flex', gap: 24, justifyContent: 'center', flexWrap: 'wrap', padding: '36px 24px 48px', maxWidth: 800, margin: '0 auto' }}>
        {/* Build Template */}
        <div onClick={() => setMode('build')}
          style={{ flex: 1, minWidth: 280, maxWidth: 360, border: `2px solid ${GREEN_BORDER}`, borderRadius: 20, padding: '32px 28px', cursor: 'pointer', background: '#fff', textAlign: 'center', transition: 'all .18s', boxShadow: '0 2px 12px rgba(33,115,70,.07)' }}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(33,115,70,.18)'; e.currentTarget.style.borderColor = GREEN }}
          onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '0 2px 12px rgba(33,115,70,.07)'; e.currentTarget.style.borderColor = GREEN_BORDER }}
        >
          <div style={{ width: 64, height: 64, borderRadius: 18, background: GREEN_LIGHT, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, margin: '0 auto 18px' }}>🔨</div>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 10px' }}>Build Template</h2>
          <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.6, margin: '0 0 20px' }}>
            Upload your Excel file and we'll auto-generate form fields from the column headers.
          </p>
          <div style={{ padding: '8px 20px', background: GREEN, color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 700, display: 'inline-block' }}>
            Upload Excel →
          </div>
        </div>

        {/* Existing Template */}
        <div onClick={() => setMode('existing')}
          style={{ flex: 1, minWidth: 280, maxWidth: 360, border: `2px solid ${GREEN_BORDER}`, borderRadius: 20, padding: '32px 28px', cursor: 'pointer', background: '#fff', textAlign: 'center', transition: 'all .18s', boxShadow: '0 2px 12px rgba(33,115,70,.07)' }}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(33,115,70,.18)'; e.currentTarget.style.borderColor = GREEN }}
          onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '0 2px 12px rgba(33,115,70,.07)'; e.currentTarget.style.borderColor = GREEN_BORDER }}
        >
          <div style={{ width: 64, height: 64, borderRadius: 18, background: GREEN_LIGHT, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, margin: '0 auto 18px' }}>📋</div>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 10px' }}>Existing Template</h2>
          <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.6, margin: '0 0 20px' }}>
            Choose from our ready-made templates and open it directly to fill or configure.
          </p>
          <div style={{ padding: '8px 20px', background: GREEN, color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 700, display: 'inline-block' }}>
            Browse Templates →
          </div>
        </div>
      </div>
    </div>
  )

  // ── Build Template Flow ────────────────────────────────────────────────────
  if (mode === 'build') return (
    <div style={{ minHeight: '100vh', background: '#f8fffe', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      <div style={{ background: `linear-gradient(135deg, ${GREEN} 0%, #1a8a52 100%)`, padding: '24px 32px', display: 'flex', alignItems: 'center', gap: 16 }}>
        <button onClick={() => { setMode(null); setParsed(null); setParseErr('') }}
          style={{ background: 'rgba(255,255,255,.2)', border: 'none', color: '#fff', borderRadius: 8, padding: '6px 14px', cursor: 'pointer', fontSize: 13, fontWeight: 600, fontFamily: 'inherit' }}>← Back</button>
        <div>
          <h1 style={{ color: '#fff', fontSize: 20, fontWeight: 800, margin: 0 }}>🔨 Build Template from Excel</h1>
          <p style={{ color: 'rgba(255,255,255,.8)', fontSize: 13, margin: '3px 0 0' }}>Upload your Excel file — column headers become form fields automatically</p>
        </div>
      </div>

      <div style={{ maxWidth: 720, margin: '36px auto', padding: '0 24px' }}>
        {!parsed ? (
          <>
            <DropZone onFile={handleFile} err={parseErr} />
            {parsing && (
              <div style={{ textAlign: 'center', marginTop: 20, color: GREEN, fontWeight: 600 }}>
                <div style={{ width: 24, height: 24, border: `3px solid ${GREEN_BORDER}`, borderTopColor: GREEN, borderRadius: '50%', animation: 'spin .7s linear infinite', margin: '0 auto 8px' }} />
                Parsing Excel file...
                <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
              </div>
            )}
          </>
        ) : (
          <div style={{ background: '#fff', borderRadius: 16, border: `1.5px solid ${GREEN_BORDER}`, overflow: 'hidden' }}>
            {/* File info */}
            <div style={{ background: GREEN_LIGHT, padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 28 }}>📊</span>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#1b5e20' }}>{parsed.fileName}</div>
                <div style={{ fontSize: 12, color: '#388e3c' }}>Sheet: {parsed.sheetName} · {parsed.rowCount} data row{parsed.rowCount !== 1 ? 's' : ''} · {parsed.headers.length} column{parsed.headers.length !== 1 ? 's' : ''} detected</div>
              </div>
            </div>

            {/* Generated fields preview */}
            <div style={{ padding: '20px' }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 12 }}>
                Generated Form Fields ({parsed.fields.length})
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
                {parsed.fields.map(f => <FieldChip key={f.id} label={f.label} type={f.type} />)}
              </div>

              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: '12px 16px', marginBottom: 20, fontSize: 12, color: '#64748b', lineHeight: 1.6 }}>
                💡 Field types are auto-detected from column names. You can edit labels, types, and options in the Builder after opening.
              </div>

              <div style={{ display: 'flex', gap: 10 }}>
                <button onClick={openInBuilder}
                  style={{ flex: 1, padding: '12px', border: 'none', borderRadius: 10, background: GREEN, color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
                  🔨 Open in Builder
                </button>
                <button onClick={() => { setParsed(null); setParseErr('') }}
                  style={{ padding: '12px 18px', border: `1.5px solid ${GREEN_BORDER}`, borderRadius: 10, background: '#fff', color: GREEN, fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
                  Upload Different File
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  // ── Existing Template Flow ─────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', background: '#f8fffe', fontFamily: "'DM Sans','Segoe UI',sans-serif" }}>
      <div style={{ background: `linear-gradient(135deg, ${GREEN} 0%, #1a8a52 100%)`, padding: '24px 32px', display: 'flex', alignItems: 'center', gap: 16 }}>
        <button onClick={() => setMode(null)}
          style={{ background: 'rgba(255,255,255,.2)', border: 'none', color: '#fff', borderRadius: 8, padding: '6px 14px', cursor: 'pointer', fontSize: 13, fontWeight: 600, fontFamily: 'inherit' }}>← Back</button>
        <div>
          <h1 style={{ color: '#fff', fontSize: 20, fontWeight: 800, margin: 0 }}>📋 Choose Existing Template</h1>
          <p style={{ color: 'rgba(255,255,255,.8)', fontSize: 13, margin: '3px 0 0' }}>Select a template to open and use directly</p>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: '32px auto', padding: '0 24px 48px' }}>
        {loadingTpl ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: GREEN }}>
            <div style={{ width: 28, height: 28, border: `3px solid ${GREEN_BORDER}`, borderTopColor: GREEN, borderRadius: '50%', animation: 'spin .7s linear infinite', margin: '0 auto 12px' }} />
            <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
            Loading templates...
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
            {templates.map(t => (
              <TemplateCard key={t.id} t={t} onClick={() => navigate(`/formcraft?template=${t.id}`)} />
            ))}
            {templates.length === 0 && (
              <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '48px 0', color: '#64748b' }}>
                No templates found. Make sure the backend is running.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
