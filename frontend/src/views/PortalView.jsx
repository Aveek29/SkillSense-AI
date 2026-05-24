import React, { useState, useEffect } from 'react'
import { Upload, UserCircle, Building2, ArrowRight, FileText, Mic, Cloud, Shield, Brain, Cpu, AlertCircle, Info } from 'lucide-react'
import Button from '../components/Button'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const MODES = [
  { key: 'Technical', desc: 'Core CS concepts, system design & problem-solving', wpm: '120-160', icon: '\u{2699}\u{FE0F}' },
  { key: 'HR', desc: 'Soft skills, leadership, conflict resolution', wpm: '140-180', icon: '\u{1F91D}' },
  { key: 'System Design', desc: 'Architectural thinking & scalability planning', wpm: '110-150', icon: '\u{1F3D7}\u{FE0F}' },
  { key: 'Behavioral', desc: 'Past experiences, situational responses & culture fit', wpm: '130-170', icon: '\u{1F9D1}\u{200D}\u{1F393}' },
  { key: 'Coding', desc: 'Algorithmic thinking, code quality & optimization', wpm: '100-140', icon: '\u{2328}\u{FE0F}' },
  { key: 'DevOps', desc: 'CI/CD knowledge, infrastructure as code & monitoring', wpm: '120-160', icon: '\u{1F310}' },
]

export default function PortalView({ onNavigate }) {
  const [role, setRole] = useState(null)
  const [formData, setFormData] = useState({ name: '', email: '', domain: 'AI/ML Engineering', mode: 'Technical' })
  const [selectedModeInfo, setSelectedModeInfo] = useState(MODES[0])
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const m = MODES.find((x) => x.key === formData.mode)
    if (m) setSelectedModeInfo(m)
  }, [formData.mode])

  const domains = ['AI/ML Engineering', 'Cloud DevOps', 'Full Stack Web', 'Systems Architecture']

  const handleFileChange = (e) => {
    const f = e.target.files[0]
    if (f && f.type === 'application/pdf') { setFile(f); setError(null) }
  }

  const handleStartInterview = async () => {
    if (!file) { setError('Please upload your resume (PDF) to continue.'); return }
    setLoading(true); setError(null)
    try {
      const body = new FormData()
      body.append('name', formData.name); body.append('email', formData.email)
      body.append('domain', formData.domain); body.append('mode', formData.mode)
      body.append('file', file)
      const res = await fetch(`${API_BASE}/candidate/upload-resume`, { method: 'POST', body })
      if (!res.ok) throw new Error(`Server responded ${res.status}`)
      const json = await res.json()
      onNavigate('interview', {
        ...formData,
        skills: json.candidate_skills || ['Python', 'React', 'AWS', 'Docker', 'PostgreSQL'],
        interviewId: json.interview_id || crypto.randomUUID(),
        sandboxId: json.sandbox_id || ('i-' + Math.random().toString(16).slice(2, 18)),
        currentQuestion: json.first_question || {
          question_text: 'Explain standard database scaling constraints when migrating from local monolithic models to cloud instances.',
          difficulty: 'medium',
          target_keywords: ['horizontal scale', 'sharding', 'replicas', 'pooling'],
        },
      })
    } catch (err) {
      setError('Backend unreachable. Please ensure the server is running on http://localhost:8000')
      setLoading(false)
      return
    }
    setLoading(false)
  }

  const features = [
    { icon: Brain, title: 'AI-Powered Grading', desc: 'Adaptive question generation with 3-axis technical scoring' },
    { icon: FileText, title: 'Resume Intelligence', desc: 'Automated skill extraction using NLP entity recognition' },
    { icon: Mic, title: 'Speech Analytics', desc: 'Real-time fluency, pacing, and filler-word detection' },
    { icon: Cpu, title: 'Resource Monitoring', desc: 'Anomaly detection with AI-driven root cause analysis' },
    { icon: Cloud, title: 'Cloud Cost Control', desc: 'Sandbox lifecycle management with usage forecasting' },
    { icon: Shield, title: 'Smart Alerting', desc: 'Automated severity classification and remediation steps' },
  ]

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)' }}>
      {/* Hero Section */}
      <section style={{ padding: '80px 24px 0', textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
        <div className="animate-fade-in-up">
          <h1 style={{
            fontSize: '3.2rem', fontWeight: 800, lineHeight: 1.1, marginBottom: '16px',
            background: 'linear-gradient(135deg, hsl(var(--text-primary)) 0%, hsl(var(--primary)) 50%, #a855f7 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>
            SkillSense AI
          </h1>
          <p style={{
            fontSize: '1.1rem', color: 'hsl(var(--text-secondary))', maxWidth: '640px',
            margin: '0 auto 36px', lineHeight: 1.7,
          }}>
            An enterprise platform that combines speech analytics, NLP parsing, and AI-driven evaluation
            to streamline technical recruiting and cloud infrastructure management.
          </p>
        </div>

        {/* Role Selector */}
        {!role ? (
          <div className="animate-fade-in-up stagger-2" style={{
            display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '60px',
          }}>
            <div className="glass-panel" onClick={() => setRole('candidate')} style={{
              padding: '28px 40px', cursor: 'pointer', textAlign: 'center', minWidth: '230px',
              transition: 'all 0.3s ease',
            }}>
              <UserCircle size={44} color="hsl(var(--primary))" style={{ marginBottom: '10px' }} />
              <h3 style={{ marginBottom: '6px' }}>I'm a Candidate</h3>
              <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>
                Upload your resume and begin a live AI-graded interview
              </p>
            </div>
            <div className="glass-panel" onClick={() => onNavigate('recruiter')} style={{
              padding: '28px 40px', cursor: 'pointer', textAlign: 'center', minWidth: '230px',
              transition: 'all 0.3s ease',
            }}>
              <Building2 size={44} color="hsl(var(--success))" style={{ marginBottom: '10px' }} />
              <h3 style={{ marginBottom: '6px' }}>I'm a Recruiter</h3>
              <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>
                Review candidate reports and cloud FinOps analytics
              </p>
            </div>
          </div>
        ) : (
          /* Candidate Form */
          <div className="glass-panel animate-fade-in-up" style={{
            maxWidth: '500px', margin: '0 auto 60px', padding: '32px', textAlign: 'left',
          }}>
            <h3 style={{ marginBottom: '24px', textAlign: 'center' }}>Start Your Assessment</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', display: 'block', marginBottom: '6px' }}>Full Name</label>
                <input className="input-glass" placeholder="Alice Johnson" value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', display: 'block', marginBottom: '6px' }}>Email</label>
                <input className="input-glass" type="email" placeholder="alice@techcorp.com" value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', display: 'block', marginBottom: '6px' }}>Domain</label>
                  <select className="input-glass" value={formData.domain}
                    onChange={(e) => setFormData({ ...formData, domain: e.target.value })}>
                    {domains.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
                <div style={{ flex: 1, position: 'relative' }}>
                  <label style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', display: 'block', marginBottom: '6px' }}>
                    Mode <Info size={12} style={{ verticalAlign: 'middle', marginLeft: '4px', color: 'hsl(var(--text-muted))' }} />
                  </label>
                  <select className="input-glass" value={formData.mode}
                    onChange={(e) => setFormData({ ...formData, mode: e.target.value })}>
                    {MODES.map(m => <option key={m.key} value={m.key}>{m.key}</option>)}
                  </select>
                  {/* Mode Info Card */}
                  <div style={{
                    marginTop: '8px',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--primary-glow)',
                    border: '1px solid var(--glass-border)',
                    fontSize: '0.78rem',
                    color: 'hsl(var(--text-secondary))',
                    lineHeight: 1.5,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '1rem' }}>{selectedModeInfo?.icon}</span>
                      <strong style={{ color: 'hsl(var(--text-primary))' }}>{selectedModeInfo?.key}</strong>
                    </div>
                    <p>{selectedModeInfo?.desc}</p>
                    <p style={{ marginTop: '4px', fontSize: '0.72rem', color: 'hsl(var(--text-muted))' }}>
                      Ideal WPM: {selectedModeInfo?.wpm}
                    </p>
                  </div>
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', display: 'block', marginBottom: '6px' }}>Resume (PDF)</label>
                <label className="glass-panel-static" style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                  padding: '24px', cursor: 'pointer', borderStyle: 'dashed',
                  borderColor: file ? 'hsl(var(--success))' : 'var(--glass-border)',
                }}>
                  <Upload size={20} color={file ? 'hsl(var(--success))' : 'hsl(var(--text-muted))'} />
                  <span style={{ fontSize: '0.85rem', color: file ? 'hsl(var(--success))' : 'hsl(var(--text-muted))' }}>
                    {file ? file.name : 'Click to upload PDF'}
                  </span>
                  <input type="file" accept=".pdf" onChange={handleFileChange} style={{ display: 'none' }} />
                </label>
              </div>
              {error && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px',
                  background: 'rgba(230,60,60,0.1)', border: '1px solid rgba(230,60,60,0.2)',
                  borderRadius: 'var(--radius-sm)', color: 'hsl(var(--danger))', fontSize: '0.85rem',
                }}>
                  <AlertCircle size={16} /> {error}
                </div>
              )}
              <Button icon={ArrowRight} onClick={handleStartInterview}
                disabled={!formData.name || !formData.email || !file || loading}
                style={{ width: '100%', justifyContent: 'center', marginTop: '4px' }}>
                {loading ? 'Initializing...' : 'Launch Interview'}
              </Button>
              <button onClick={() => { setRole(null); setError(null) }} style={{
                background: 'none', border: 'none', color: 'hsl(var(--text-muted))',
                cursor: 'pointer', fontSize: '0.8rem', marginTop: '4px',
              }}>
                {'\u2190'} Back
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Features Section */}
      {!role && (
        <section style={{ padding: '40px 24px 80px' }}>
          <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px',
              maxWidth: '900px', margin: '0 auto',
            }}>
              {features.map((feat, i) => (
                <div key={feat.title} className={`glass-panel animate-fade-in-up stagger-${i + 1}`}
                  style={{ padding: '24px', textAlign: 'center' }}>
                  <div style={{
                    width: '44px', height: '44px', borderRadius: '12px',
                    background: 'var(--primary-glow)', display: 'flex',
                    alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px',
                  }}>
                    <feat.icon size={22} color="hsl(var(--primary))" />
                  </div>
                  <h4 style={{ marginBottom: '6px', fontSize: '0.9rem' }}>{feat.title}</h4>
                  <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.78rem', lineHeight: 1.5 }}>{feat.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
