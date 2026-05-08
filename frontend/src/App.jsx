import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import TemplatesPage from './pages/formcraft/TemplatesPage'
import BuilderPage from './pages/formcraft/BuilderPage'
import SubmissionsPage from './pages/formcraft/SubmissionsPage'
import FormPage from './pages/formcraft/FormPage'
import QueryMindPage from './pages/querymind/QueryMindPage'

function AppRoutes() {
  const { pathname } = useLocation()
  const showNav = !pathname.startsWith('/querymind') && !pathname.startsWith('/form/')

  return (
    <>
      {showNav && <Navbar />}
      <Routes>
        <Route path="/" element={<Navigate to="/formcraft" replace />} />
        <Route path="/formcraft" element={<TemplatesPage />} />
        <Route path="/formcraft/builder" element={<BuilderPage />} />
        <Route path="/formcraft/submissions" element={<SubmissionsPage />} />
        <Route path="/form/:formId" element={<FormPage />} />
        <Route path="/querymind" element={<QueryMindPage />} />
        <Route path="*" element={<Navigate to="/formcraft" replace />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}
