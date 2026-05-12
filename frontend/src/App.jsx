import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import TemplatesPage from './pages/formcraft/TemplatesPage'
import BuilderPage from './pages/formcraft/BuilderPage'
import SubmissionsPage from './pages/formcraft/SubmissionsPage'
import FormPage from './pages/formcraft/FormPage'
import QueryMindPage from './pages/querymind/QueryMindPage'
import KBDetailPage from './pages/querymind/KBDetailPage'
import ChatPage from './pages/chat/ChatPage'
import AuthPage from './pages/auth/AuthPage'
import ActivityPage from './pages/formcraft/ActivityPage'
import ExcelPage from './pages/formcraft/ExcelPage'

function AppRoutes() {
  const { isLoggedIn } = useAuth()
  const { pathname } = useLocation()

  // Public routes — no login required
  if (pathname.startsWith('/form/') || pathname.startsWith('/chat/')) {
    return (
      <Routes>
        <Route path="/form/:formId" element={<FormPage />} />
        <Route path="/chat/:kbId" element={<ChatPage />} />
        <Route path="*" element={<Navigate to="/formcraft" replace />} />
      </Routes>
    )
  }

  if (!isLoggedIn) return <AuthPage />

  const showNav = !pathname.startsWith('/querymind')
  return (
    <>
      {showNav && <Navbar />}
      <Routes>
        <Route path="/" element={<Navigate to="/activity" replace />} />
        <Route path="/formcraft" element={<TemplatesPage />} />
        <Route path="/formcraft/builder" element={<BuilderPage />} />
        <Route path="/formcraft/excel" element={<ExcelPage />} />
        <Route path="/formcraft/submissions" element={<SubmissionsPage />} />
        <Route path="/activity" element={<ActivityPage />} />
        <Route path="/querymind" element={<QueryMindPage />} />
        <Route path="/querymind/kb/:kbId" element={<KBDetailPage />} />
        <Route path="*" element={<Navigate to="/formcraft" replace />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
