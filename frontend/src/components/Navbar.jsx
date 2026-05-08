import { NavLink, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { pathname } = useLocation()
  const isFormCraft = pathname.startsWith('/formcraft')

  return (
    <nav style={{
      background: '#fff',
      borderBottom: '1px solid #e2e8f0',
      padding: '0 32px',
      display: 'flex',
      alignItems: 'center',
      height: '58px',
      position: 'sticky',
      top: 0,
      zIndex: 200,
      gap: '24px',
    }}>
      <div style={{
        fontFamily: "'Playfair Display', serif",
        fontSize: '20px',
        color: '#1a56db',
        fontWeight: 700,
        whiteSpace: 'nowrap',
      }}>
        Form<span style={{ color: '#0f172a' }}>Craft</span>
        <span style={{ color: '#94a3b8', margin: '0 10px', fontFamily: 'sans-serif', fontWeight: 300 }}>|</span>
        <span style={{ color: '#6c63ff', fontFamily: 'sans-serif', fontSize: '17px', fontWeight: 700 }}>Query</span>
        <span style={{ color: '#0f172a', fontFamily: 'sans-serif', fontSize: '17px', fontWeight: 700 }}>Mind</span>
      </div>

      <div style={{ display: 'flex', gap: '4px' }}>
        <NavLink to="/formcraft" end style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          📋 Templates
        </NavLink>
        <NavLink to="/formcraft/builder" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          🔨 Builder
        </NavLink>
        <NavLink to="/formcraft/submissions" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          📊 Submissions
        </NavLink>
        <span style={{ width: 1, background: '#e2e8f0', margin: '14px 8px' }} />
        <NavLink to="/querymind" style={navStyle} className={({ isActive }) => isActive ? 'nav-active' : ''}>
          🧠 QueryMind
        </NavLink>
      </div>
    </nav>
  )
}

const navStyle = {
  padding: '6px 14px',
  borderRadius: '8px',
  border: 'none',
  background: 'none',
  cursor: 'pointer',
  fontSize: '13px',
  fontWeight: 500,
  color: '#64748b',
  textDecoration: 'none',
  fontFamily: 'inherit',
}
