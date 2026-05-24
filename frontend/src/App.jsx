import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Brain, Github } from 'lucide-react'
import PortalView from './views/PortalView'
import InterviewConsole from './views/InterviewConsole'
import RecruiterDashboard from './views/RecruiterDashboard'
import ReportDashboard from './views/ReportDashboard'
import ChatBot from './components/ChatBot'
import ThemeSwitcher from './components/ThemeSwitcher'

const VIEWS = {
  PORTAL: 'portal',
  INTERVIEW: 'interview',
  RECRUITER: 'recruiter',
  REPORT: 'report',
}

const NAV_ITEMS = [
  { key: VIEWS.PORTAL, label: 'Portal' },
  { key: VIEWS.INTERVIEW, label: 'Interview' },
  { key: VIEWS.RECRUITER, label: 'Recruiter' },
  { key: VIEWS.REPORT, label: 'Reports' },
]

const DEFAULT_THEME = 'slate-dark'

const Footer = React.memo(() => (
  <footer
    style={{
      borderTop: '1px solid var(--glass-border)',
      padding: '20px 24px',
      background: 'rgba(10, 14, 25, 0.6)',
    }}
  >
    <div
      className="container"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Brain size={16} color="hsl(var(--primary))" />
        <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))' }}>
          SkillSense AI v1.0.0
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>
          &copy; {new Date().getFullYear()} &mdash; Unified Assessment Platform
        </span>
        <a
          href="#"
          style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', textDecoration: 'none' }}
          onClick={(e) => { e.preventDefault() }}
        >
          <Github size={14} />
        </a>
      </div>
    </div>
  </footer>
))

export default function App() {
  const [currentView, setCurrentView] = useState(VIEWS.PORTAL)
  const [interviewData, setInterviewData] = useState(null)
  const [theme, setThemeState] = useState(
    () => localStorage.getItem('skillsense-theme') || DEFAULT_THEME
  )

  useEffect(() => {
    document.body.setAttribute('data-theme', theme)
    localStorage.setItem('skillsense-theme', theme)
  }, [theme])

  const setTheme = useCallback((t) => setThemeState(t), [])

  const navigate = useCallback((view, data = null) => {
    if (data) setInterviewData(data)
    setCurrentView(view)
  }, [])

  const renderView = useMemo(() => {
    switch (currentView) {
      case VIEWS.INTERVIEW:
        return <InterviewConsole data={interviewData} onNavigate={navigate} />
      case VIEWS.RECRUITER:
        return <RecruiterDashboard onNavigate={navigate} />
      case VIEWS.REPORT:
        return <ReportDashboard data={interviewData} onNavigate={navigate} />
      default:
        return <PortalView onNavigate={navigate} />
    }
  }, [currentView, interviewData, navigate])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => navigate(VIEWS.PORTAL)}>
            <div className="navbar-brand-icon">
              <Brain size={18} color="white" />
            </div>
            SkillSense AI
          </div>
          <div className="navbar-nav">
            {NAV_ITEMS.map(item => (
              <button
                key={item.key}
                className={`nav-link ${currentView === item.key ? 'active' : ''}`}
                onClick={() => navigate(item.key)}
              >
                {item.label}
              </button>
            ))}
            <ThemeSwitcher theme={theme} setTheme={setTheme} />
          </div>
        </div>
      </nav>

      <main style={{ flex: 1 }}>
        <div key={currentView} className="animate-fade-in" style={{ animationDuration: '0.35s' }}>
          {renderView}
        </div>
      </main>

      <Footer />

      <ChatBot />
    </div>
  )
}
