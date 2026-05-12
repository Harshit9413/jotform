import { useState, useRef, useCallback } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { createPortal } from 'react-dom'
import { useAuth } from '../context/AuthContext'
import { useMemo } from 'react'

const CATEGORIES = [
  { key: 'contact',      label: '📬 Contact' },
  { key: 'registration', label: '📝 Registration' },
  { key: 'feedback',     label: '⭐ Feedback' },
  { key: 'payment',      label: '💳 Payment' },
  { key: 'hr',           label: '👔 HR / Jobs' },
  { key: 'booking',      label: '📅 Booking' },
  { key: 'survey',       label: '📊 Survey' },
  { key: 'support',      label: '🐛 Support' },
  { key: 'marketing',    label: '📣 Marketing' },
]

const TEMPLATE_TYPES = [
  { key: 'form_type',      icon: '📝', label: 'Form Template',   color: '#1a56db' },
  { key: 'app_type',       icon: '📱', label: 'App Template',    color: '#7c3aed' },
  { key: 'table_type',     icon: '📊', label: 'Table Template',  color: '#059669' },
  { key: 'pdf_type',       icon: '📄', label: 'PDF Template',    color: '#dc2626' },
  { key: 'card_form_type', icon: '💳', label: 'Card Form',       color: '#d97706' },
  { key: 'store_type',     icon: '🛒', label: 'Store Builder',   color: '#0891b2' },
  { key: 'workflow_type',  icon: '⚡', label: 'Workflow',        color: '#f59e0b' },
  { key: 'sign_type',      icon: '✍️', label: 'Sign Template',   color: '#4f46e5' },
  { key: 'board_type',     icon: '📌', label: 'Board Template',  color: '#db2777' },
]

function TemplatesMegaMenu({ anchorRect, templates, onClose }) {
  const navigate = useNavigate()
  const [activeCategory, setActiveCategory] = useState(CATEGORIES[0].key)
  const [activeSection, setActiveSection] = useState('categories') // 'categories' | 'types'

  const activeMeta = activeSection === 'types'
    ? TEMPLATE_TYPES.find(t => t.key === activeCategory)
    : null

  const categoryTemplates = templates.filter(t => t.category === activeCategory)

  const handleSelect = (t) => {
    onClose()
    navigate(`/formcraft?template=${t.id}`)
  }

  const handleTypeClick = (typeKey) => {
    onClose()
    navigate(`/formcraft?type=${typeKey}`)
  }

  return createPortal(
    <div
      onMouseLeave={onClose}
      style={{
        position: 'fixed',
        top: anchorRect.bottom,
        left: 0, right: 0,
        zIndex: 9000,
        background: '#fff',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 16px 48px rgba(15,23,42,.14)',
      }}
    >
      <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex' }}>

        {/* Left sidebar */}
        <div style={{ width: 220, borderRight: '1px solid #f1f5f9', padding: '16px 0', flexShrink: 0 }}>

          {/* Section toggle */}
          <div style={{ display: 'flex', margin: '0 12px 12px', borderRadius: 8, border: '1.5px solid #e2e8f0', overflow: 'hidden' }}>
            {[['categories', '📋 Categories'], ['types', '📂 Browse Types']].map(([sec, lbl]) => (
              <button
                key={sec}
                onClick={() => {
                  setActiveSection(sec)
                  setActiveCategory(sec === 'categories' ? CATEGORIES[0].key : TEMPLATE_TYPES[0].key)
                }}
                style={{
                  flex: 1, padding: '5px 0', border: 'none', fontFamily: 'inherit',
                  fontSize: 10, fontWeight: 700, cursor: 'pointer',
                  background: activeSection === sec ? '#1a56db' : '#fff',
                  color: activeSection === sec ? '#fff' : '#64748b',
                  transition: 'all .12s',
                }}
              >
                {lbl}
              </button>
            ))}
          </div>

          {activeSection === 'categories' ? (
            <>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.08em', padding: '0 18px 8px' }}>
                Categories
              </div>
              {CATEGORIES.map(cat => (
                <div
                  key={cat.key}
                  onMouseEnter={() => setActiveCategory(cat.key)}
                  onClick={() => { navigate('/formcraft'); onClose() }}
                  style={{
                    padding: '9px 18px', fontSize: 13,
                    fontWeight: activeCategory === cat.key ? 700 : 500,
                    color: activeCategory === cat.key ? '#1a56db' : '#374151',
                    background: activeCategory === cat.key ? '#eff6ff' : 'transparent',
                    cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between', transition: 'background .1s',
                  }}
                >
                  <span>{cat.label}</span>
                  {activeCategory === cat.key && <span style={{ fontSize: 10, color: '#1a56db' }}>›</span>}
                </div>
              ))}
            </>
          ) : (
            <>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.08em', padding: '0 18px 8px' }}>
                Template Types
              </div>
              {TEMPLATE_TYPES.map(t => (
                <div
                  key={t.key}
                  onMouseEnter={() => setActiveCategory(t.key)}
                  onClick={() => handleTypeClick(t.key)}
                  style={{
                    padding: '8px 18px', fontSize: 13,
                    fontWeight: activeCategory === t.key ? 700 : 500,
                    color: activeCategory === t.key ? t.color : '#374151',
                    background: activeCategory === t.key ? `${t.color}10` : 'transparent',
                    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, transition: 'background .1s',
                  }}
                >
                  <span style={{ fontSize: 14 }}>{t.icon}</span>
                  <span style={{ flex: 1 }}>{t.label}</span>
                  {activeCategory === t.key && <span style={{ fontSize: 10, color: t.color }}>›</span>}
                </div>
              ))}
            </>
          )}
        </div>

        {/* Right: templates */}
        <div style={{ flex: 1, padding: '20px 24px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, alignContent: 'start' }}>
          {categoryTemplates.length === 0 && (
            <div style={{ gridColumn: '1/-1', textAlign: 'center', color: '#94a3b8', fontSize: 13, padding: 24 }}>
              No templates in this category
            </div>
          )}
          {categoryTemplates.map(t => (
            <div
              key={t.id}
              onClick={() => handleSelect(t)}
              style={{
                display: 'flex', alignItems: 'flex-start', gap: 12, padding: '12px 14px',
                borderRadius: 10, border: '1.5px solid #f1f5f9', cursor: 'pointer',
                transition: 'all .15s', background: '#fff',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = `${t.color}60`
                e.currentTarget.style.background = `${t.color}08`
                e.currentTarget.style.boxShadow = `0 2px 12px ${t.color}20`
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = '#f1f5f9'
                e.currentTarget.style.background = '#fff'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              <div style={{
                width: 36, height: 36, borderRadius: 9,
                background: activeMeta ? `${activeMeta.color}18` : `${t.color}18`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 16,
              }}>
                {activeMeta ? activeMeta.icon : <div style={{ width: 14, height: 14, borderRadius: 3, background: t.color, opacity: .8 }} />}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 3 }}>{t.title}</div>
                <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {t.description}
                </div>
                {t.badge && (
                  <span style={{ display: 'inline-block', marginTop: 5, fontSize: 10, fontWeight: 700, color: t.color, background: `${t.color}15`, padding: '2px 7px', borderRadius: 8 }}>
                    {t.badge}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, borderTop: '1px solid #f1f5f9', padding: '10px 24px', display: 'flex', justifyContent: 'flex-end', background: '#fafbfc' }}>
          <button
            onClick={() => { navigate('/formcraft'); onClose() }}
            style={{ padding: '6px 16px', border: 'none', borderRadius: 7, background: '#1a56db', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}
          >
            View All Templates →
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}

function BrowseTypesDropdown({ anchorRect, templates, onClose }) {
  const navigate = useNavigate()
  const [hoveredKey, setHoveredKey] = useState(null)
  const hoveredMeta = TEMPLATE_TYPES.find(t => t.key === hoveredKey)
  const hoveredItems = hoveredKey ? templates.filter(t => t.category === hoveredKey) : []

  return createPortal(
    <div
      onMouseLeave={onClose}
      style={{
        position: 'fixed', top: anchorRect.bottom, left: 0, right: 0,
        zIndex: 9000, background: '#fff',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 16px 48px rgba(15,23,42,.14)',
      }}
    >
      <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex' }}>

        {/* Left: 9 type tiles */}
        <div style={{ width: 260, borderRight: '1px solid #f1f5f9', padding: '16px 0', flexShrink: 0 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.08em', padding: '0 18px 10px' }}>
            Browse by Type
          </div>
          {TEMPLATE_TYPES.map(t => (
            <div
              key={t.key}
              onMouseEnter={() => setHoveredKey(t.key)}
              onClick={() => { navigate(`/formcraft?type=${t.key}`); onClose() }}
              style={{
                padding: '9px 18px', fontSize: 13, cursor: 'pointer',
                fontWeight: hoveredKey === t.key ? 700 : 500,
                color: hoveredKey === t.key ? t.color : '#374151',
                background: hoveredKey === t.key ? `${t.color}10` : 'transparent',
                display: 'flex', alignItems: 'center', gap: 10, transition: 'background .1s',
              }}
            >
              <span style={{ fontSize: 16 }}>{t.icon}</span>
              <span style={{ flex: 1 }}>{t.label}</span>
              <span style={{ fontSize: 11, color: '#94a3b8' }}>
                {templates.filter(tp => tp.category === t.key).length}
              </span>
              {hoveredKey === t.key && <span style={{ fontSize: 10, color: t.color }}>›</span>}
            </div>
          ))}
        </div>

        {/* Right: templates for hovered type */}
        <div style={{ flex: 1, padding: '20px 24px', alignContent: 'start' }}>
          {!hoveredKey ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94a3b8', gap: 8 }}>
              <span style={{ fontSize: 32 }}>📂</span>
              <span style={{ fontSize: 13 }}>Hover a type to preview templates</span>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                <span style={{ fontSize: 18 }}>{hoveredMeta?.icon}</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: hoveredMeta?.color }}>{hoveredMeta?.label}s</span>
                <span style={{ fontSize: 11, color: '#94a3b8' }}>— {hoveredItems.length} templates</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                {hoveredItems.map(t => (
                  <div
                    key={t.id}
                    onClick={() => { navigate(`/formcraft?template=${t.id}`); onClose() }}
                    style={{
                      display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 12px',
                      borderRadius: 10, border: `1.5px solid ${hoveredMeta.color}20`, cursor: 'pointer',
                      transition: 'all .15s', background: '#fff',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = `${hoveredMeta.color}08`; e.currentTarget.style.borderColor = `${hoveredMeta.color}50` }}
                    onMouseLeave={e => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.borderColor = `${hoveredMeta.color}20` }}
                  >
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: `${hoveredMeta.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 14 }}>
                      {hoveredMeta.icon}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>{t.title}</div>
                      <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.3, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{t.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>,
    document.body
  )
}

const INTEGRATION_CARDS = [
  {
    key: 'excel',
    icon: '📊', title: 'Microsoft Excel',
    color: '#217346', borderColor: '#a5d6a7', bgColor: '#e8f5e9',
    headColor: '#388e3c', shadow: 'rgba(33,115,70,.18)',
    desc: 'Import .xlsx files to auto-generate forms and export submissions as spreadsheets.',
    features: [
      { icon: '📥', label: 'Import from Excel', desc: 'Upload .xlsx and auto-generate form fields' },
      { icon: '📤', label: 'Export submissions', desc: 'Download all responses as spreadsheet' },
      { icon: '🔄', label: 'Auto field mapping', desc: 'Column headers become form fields' },
      { icon: '📊', label: 'CSV support', desc: 'Works with .xlsx, .xls and .csv files' },
    ],
    cta: 'Open Excel Integration →',
    route: '/formcraft/excel',
  },
  {
    key: 'sheets',
    icon: '📋', title: 'Google Sheets',
    color: '#0f9d58', borderColor: '#86efac', bgColor: '#f0fdf4',
    headColor: '#15803d', shadow: 'rgba(15,157,88,.18)',
    desc: 'Automatically push every form submission as a new row into a Google Sheet in real time.',
    features: [
      { icon: '🔄', label: 'Live row sync', desc: 'Each submission adds a new row instantly' },
      { icon: '📌', label: 'Column mapping', desc: 'Form fields map to spreadsheet columns' },
      { icon: '🔑', label: 'Service account auth', desc: 'Secure access via Google service account' },
      { icon: '🗂️', label: 'Sheet selector', desc: 'Choose any tab within the spreadsheet' },
    ],
    cta: 'Configure per Form →',
    route: '/formcraft',
  },
  {
    key: 'email',
    icon: '📧', title: 'Email Notifications',
    color: '#1a56db', borderColor: '#bfdbfe', bgColor: '#eff6ff',
    headColor: '#1d4ed8', shadow: 'rgba(26,86,219,.18)',
    desc: 'Send an admin alert and a user confirmation email automatically on every form submission.',
    features: [
      { icon: '🔔', label: 'Admin alert', desc: 'Get notified on every new submission' },
      { icon: '✉️', label: 'User confirmation', desc: 'Auto-reply to the submitter' },
      { icon: '🔧', label: 'SMTP config', desc: 'Use Gmail, Outlook or any SMTP server' },
      { icon: '🎨', label: 'Custom messages', desc: 'Personalised subject and body per form' },
    ],
    cta: 'Configure per Form →',
    route: '/formcraft',
  },
]

function IntegrationDropdown({ anchorRect, onClose }) {
  const navigate = useNavigate()
  return createPortal(
    <div
      onMouseLeave={onClose}
      style={{
        position: 'fixed', top: anchorRect.bottom, left: 0, right: 0,
        zIndex: 9000, background: '#fff',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 16px 48px rgba(15,23,42,.14)',
      }}
    >
      <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', padding: '24px 32px', gap: 20 }}>
        {INTEGRATION_CARDS.map(card => (
          <div
            key={card.key}
            onClick={() => { navigate(card.route); onClose() }}
            style={{
              flex: 1, border: `1.5px solid ${card.borderColor}`, borderRadius: 14,
              padding: '18px 18px 14px', cursor: 'pointer', transition: 'all .15s', background: '#fff',
            }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = `0 6px 24px ${card.shadow}`; e.currentTarget.style.borderColor = card.color }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.borderColor = card.borderColor }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              <span style={{ fontSize: 20 }}>{card.icon}</span>
              <span style={{ fontSize: 13, fontWeight: 800, color: card.color }}>{card.title}</span>
            </div>
            <div style={{ fontSize: 11, color: '#64748b', marginBottom: 12, lineHeight: 1.4 }}>{card.desc}</div>
            {card.features.map(f => (
              <div key={f.label} style={{ display: 'flex', alignItems: 'flex-start', gap: 9, padding: '5px 0' }}>
                <span style={{ fontSize: 14, flexShrink: 0 }}>{f.icon}</span>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: '#1e293b' }}>{f.label}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8' }}>{f.desc}</div>
                </div>
              </div>
            ))}
            <div style={{ marginTop: 14, padding: '7px 10px', background: card.color, borderRadius: 9, textAlign: 'center', fontSize: 11, fontWeight: 700, color: '#fff' }}>
              {card.cta}
            </div>
          </div>
        ))}
      </div>
    </div>,
    document.body
  )
}

export default function Navbar() {
  const { auth, logout } = useAuth()
  const [showMenu, setShowMenu]             = useState(false)
  const [showBrowse, setShowBrowse]         = useState(false)
  const [showIntegration, setShowIntegration] = useState(false)
  const [anchorRect, setAnchorRect]         = useState(null)
  const [browseRect, setBrowseRect]         = useState(null)
  const [integrationRect, setIntegrationRect] = useState(null)
  const [templates, setTemplates]           = useState([])
  const hideTimer        = useRef(null)
  const browseTimer      = useRef(null)
  const integrationTimer = useRef(null)
  const fetched          = useRef(false)

  const fetchTemplates = useCallback(() => {
    if (!fetched.current) {
      fetched.current = true
      fetch('/api/templates').then(r => r.json()).then(setTemplates).catch(() => {})
    }
  }, [])

  const openMenu = useCallback(e => {
    clearTimeout(hideTimer.current)
    fetchTemplates()
    const navEl = e.currentTarget.closest('nav')
    setAnchorRect(navEl ? navEl.getBoundingClientRect() : e.currentTarget.getBoundingClientRect())
    setShowMenu(true)
  }, [fetchTemplates])

  const closeMenu = useCallback(() => {
    hideTimer.current = setTimeout(() => setShowMenu(false), 150)
  }, [])

  const openBrowse = useCallback(e => {
    clearTimeout(browseTimer.current)
    fetchTemplates()
    const navEl = e.currentTarget.closest('nav')
    setBrowseRect(navEl ? navEl.getBoundingClientRect() : e.currentTarget.getBoundingClientRect())
    setShowBrowse(true)
  }, [fetchTemplates])

  const closeBrowse = useCallback(() => {
    browseTimer.current = setTimeout(() => setShowBrowse(false), 150)
  }, [])

  const openIntegration = useCallback(e => {
    clearTimeout(integrationTimer.current)
    const navEl = e.currentTarget.closest('nav')
    setIntegrationRect(navEl ? navEl.getBoundingClientRect() : e.currentTarget.getBoundingClientRect())
    setShowIntegration(true)
  }, [])

  const closeIntegration = useCallback(() => {
    integrationTimer.current = setTimeout(() => setShowIntegration(false), 150)
  }, [])

  return (
    <nav style={{
      background: '#fff', borderBottom: '1px solid #e2e8f0',
      padding: '0 32px', display: 'flex', alignItems: 'center',
      height: 58, position: 'sticky', top: 0, zIndex: 8500, gap: 24,
    }}>
      <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#1a56db', fontWeight: 700, whiteSpace: 'nowrap' }}>
        Form<span style={{ color: '#0f172a' }}>Craft</span>
        <span style={{ color: '#94a3b8', margin: '0 10px', fontFamily: 'sans-serif', fontWeight: 300 }}>|</span>
        <span style={{ color: '#6c63ff', fontFamily: 'sans-serif', fontSize: 17, fontWeight: 700 }}>Query</span>
        <span style={{ color: '#0f172a', fontFamily: 'sans-serif', fontSize: 17, fontWeight: 700 }}>Mind</span>
      </div>

      <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
        {/* Templates mega menu */}
        <div onMouseEnter={openMenu} onMouseLeave={closeMenu} style={{ position: 'relative' }}>
          <NavLink to="/formcraft" end style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
            📋 Templates ▾
          </NavLink>
          {showMenu && anchorRect && templates.length > 0 && (
            <TemplatesMegaMenu
              anchorRect={anchorRect}
              templates={templates}
              onClose={() => { clearTimeout(hideTimer.current); setShowMenu(false) }}
            />
          )}
        </div>

        {/* Integration button */}
        <div onMouseEnter={openIntegration} onMouseLeave={closeIntegration} style={{ position: 'relative' }}>
          <button
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '6px 14px', borderRadius: 8,
              border: '1.5px solid #a5d6a7', background: '#e8f5e9',
              color: '#217346', fontSize: 13, fontWeight: 700,
              cursor: 'pointer', fontFamily: 'inherit', whiteSpace: 'nowrap',
            }}
          >
            🔗 Integration ▾
          </button>
          {showIntegration && integrationRect && (
            <IntegrationDropdown
              anchorRect={integrationRect}
              onClose={() => { clearTimeout(integrationTimer.current); setShowIntegration(false) }}
            />
          )}
        </div>

        <NavLink to="/formcraft/submissions" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          📊 Submissions
        </NavLink>
        <NavLink to="/activity" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          📈 Activity
        </NavLink>
        <span style={{ width: 1, background: '#e2e8f0', margin: '14px 8px' }} />
        <NavLink to="/querymind" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          🧠 QueryMind
        </NavLink>
      </div>

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
        {auth?.user && (
          <span style={{ fontSize: 13, color: '#64748b', fontWeight: 500 }}>{auth.user.name}</span>
        )}
        <button
          onClick={logout}
          style={{ padding: '6px 14px', borderRadius: 8, border: '1.5px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#64748b', fontFamily: 'inherit', transition: 'all .15s' }}
          onMouseEnter={e => { e.currentTarget.style.background = '#fef2f2'; e.currentTarget.style.borderColor = '#fecaca'; e.currentTarget.style.color = '#dc2626' }}
          onMouseLeave={e => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }}
        >
          Sign Out
        </button>
      </div>
    </nav>
  )
}

const navStyle = {
  padding: '6px 14px', borderRadius: 8, border: 'none', background: 'none',
  cursor: 'pointer', fontSize: 13, fontWeight: 500, color: '#64748b',
  textDecoration: 'none', fontFamily: 'inherit', display: 'inline-block',
}
