import React, { useState, useEffect, useCallback } from 'react'
import { ShieldAlert, Cpu, DollarSign, UserCheck, TrendingUp, Activity, Search } from 'lucide-react'
import CostTrendChart from '../components/CostTrendChart'
import SandboxMetricCard from '../components/SandboxMetricCard'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const MOCK_CANDIDATES = [
  { id: 1, name: 'Alice Johnson', domain: 'AI/ML Engineering', grade: '9.2/10', avgTech: 9.2, sandbox: 'i-098ea1276be30efbc', sandboxStatus: 'running', questions: 5, status: 'Completed' },
  { id: 2, name: 'Bob Smith', domain: 'Cloud DevOps', grade: '8.5/10', avgTech: 8.5, sandbox: 'i-012abef9034edff9d', sandboxStatus: 'terminated', questions: 5, status: 'Completed' },
  { id: 3, name: 'Clara Mendes', domain: 'Full Stack Web', grade: '7.8/10', avgTech: 7.8, sandbox: 'i-0f4e3a91b7c20d385', sandboxStatus: 'running', questions: 3, status: 'In-Progress' },
  { id: 4, name: 'David Kim', domain: 'Systems Architecture', grade: '8.9/10', avgTech: 8.9, sandbox: 'i-0a7b2c4e9d1f63850', sandboxStatus: 'terminated', questions: 5, status: 'Completed' },
]

const MOCK_ANOMALIES = [
  { id: 1, instance: 'i-098ea1276be30efbc', metric: 'CPU Utilization', value: '99.8%', status: 'Critical Anomaly', score: '0.9840' },
  { id: 2, instance: 'i-0f4e3a91b7c20d385', metric: 'Network Egress', value: '4.8 GB', status: 'Warning', score: '0.7215' },
]

const MOCK_METRICS = [
  { instanceId: 'i-098ea1276be30efbc', cpuUtilization: 99.8, ramUtilization: 87.3, isAnomaly: true, anomalyScore: 0.984, status: 'running' },
  { instanceId: 'i-0f4e3a91b7c20d385', cpuUtilization: 34.2, ramUtilization: 41.8, isAnomaly: false, anomalyScore: 0.12, status: 'running' },
  { instanceId: 'i-012abef9034edff9d', cpuUtilization: 0, ramUtilization: 0, isAnomaly: false, anomalyScore: 0, status: 'terminated' },
  { instanceId: 'i-0a7b2c4e9d1f63850', cpuUtilization: 0, ramUtilization: 0, isAnomaly: false, anomalyScore: 0, status: 'terminated' },
]

export default function RecruiterDashboard({ onNavigate }) {
  const [candidates] = useState(MOCK_CANDIDATES)
  const [anomalies, setAnomalies] = useState(MOCK_ANOMALIES)
  const [sandboxMetrics] = useState(MOCK_METRICS)
  const [searchTerm, setSearchTerm] = useState('')
  const [apiStatus, setApiStatus] = useState('loading')

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        const headers = { 'Content-Type': 'application/json' }
        const token = localStorage.getItem('skillsense-token')
        if (token) headers['Authorization'] = `Bearer ${token}`

        const res = await fetch(`${API_BASE}/recruiter/sandbox/anomalies`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            metrics: MOCK_METRICS.map(m => ({
              cpu_utilization: m.cpuUtilization,
              ram_utilization: m.ramUtilization,
              network_egress_bytes: 100000,
              daily_cost: 2.5,
              instance: m.instanceId,
            })),
          }),
        })
        if (res.ok) {
          const data = await res.json()
          if (data.metrics && data.metrics.length > 0) {
            setAnomalies(data.metrics.map((m, i) => ({
              id: i + 1,
              instance: m.instance || `i-mock-${i}`,
              metric: m.metric || 'CPU Utilization',
              value: m.value || `${m.cpu_utilization || 0}%`,
              status: m.is_anomaly ? 'Critical Anomaly' : 'Normal',
              score: String(m.anomaly_score || 0),
              severity: m.severity || 'low',
              hypothesis: m.hypothesis || '',
              recommended_action: m.recommended_action || '',
            })))
          }
          setApiStatus('connected')
        } else {
          setApiStatus('demo')
        }
      } catch {
        setApiStatus('demo')
      }
    }
    fetchAnomalies()
  }, [])

  const filteredCandidates = candidates.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.domain.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const activeSandboxes = sandboxMetrics.filter(m => m.status === 'running').length

  const stats = [
    { icon: Cpu, label: 'Active Sandboxes', value: `${activeSandboxes} VMs Running`, color: '--primary', glow: '' },
    { icon: UserCheck, label: 'Evaluations Completed', value: `${candidates.length} Candidates`, color: '--success', glow: 'glow-success' },
    { icon: DollarSign, label: 'Est. FinOps Savings', value: '28.6% Saved', color: '--warning', glow: '' },
    { icon: ShieldAlert, label: 'Security Events', value: `${anomalies.filter(a => a.status === 'Critical Anomaly').length} Alerts`, color: '--danger', glow: '' },
  ]

  return (
    <div className="container" style={{ padding: '30px 24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div className="flex-between animate-fade-in">
        <div>
          <h2>Recruiter Dashboard</h2>
          <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginTop: '4px' }}>
            Candidate assessments & cloud sandbox FinOps monitoring
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={16} color="hsl(var(--success))" style={{ animation: 'pulseGlow 2s infinite' }} />
          <span style={{ fontSize: '0.8rem', color: apiStatus === 'connected' ? 'hsl(var(--success))' : 'hsl(var(--warning))' }}>
            {apiStatus === 'connected' ? 'Live Data' : 'Demo Mode'}
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {stats.map((stat, i) => (
          <div
            key={stat.label}
            className={`glass-panel animate-fade-in-up stagger-${i + 1} ${stat.glow}`}
            style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '15px' }}
          >
            <div
              style={{
                width: '48px', height: '48px', borderRadius: 'var(--radius-md)',
                background: `hsl(var(${stat.color}) / 0.12)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}
            >
              <stat.icon size={24} color={`hsl(var(${stat.color}))`} />
            </div>
            <div>
              <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.75rem', fontWeight: 500 }}>{stat.label}</p>
              <h3 style={{ fontSize: '1.15rem', marginTop: '2px' }}>{stat.value}</h3>
            </div>
          </div>
        ))}
      </div>

      {/* Main Layout: Chart + Anomalies */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '24px' }}>
        <div className="glass-panel glow-primary animate-fade-in-up" style={{ padding: '24px' }}>
          <CostTrendChart />
        </div>

        <div className="glass-panel animate-fade-in-up" style={{ padding: '24px' }}>
          <h3 style={{
            fontSize: '1rem', marginBottom: '16px', color: 'hsl(var(--danger))',
            display: 'flex', alignItems: 'center', gap: '8px'
          }}>
            <ShieldAlert size={18} /> Isolation Forest Threat Alerts
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {anomalies.map(a => (
              <div
                key={a.id}
                className="glass-panel-static"
                style={{
                  padding: '16px',
                  borderLeft: `4px solid ${a.status === 'Critical Anomaly' ? 'hsl(var(--danger))' : 'hsl(var(--warning))'}`,
                  borderRadius: '0 var(--radius-md) var(--radius-md) 0',
                }}
              >
                <div className="flex-between" style={{ marginBottom: '6px' }}>
                  <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', fontWeight: 600 }}>
                    {a.instance}
                  </span>
                  <span className={`badge ${a.status === 'Critical Anomaly' ? 'badge-danger' : 'badge-warning'}`}>
                    {a.status}
                  </span>
                </div>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.8rem', lineHeight: 1.5 }}>
                  Detected abnormal <strong>{a.metric}</strong> of <strong>{a.value}</strong>.
                  Model score: <code style={{ color: 'hsl(var(--primary))' }}>{a.score}</code>
                </p>
                {a.hypothesis && (
                  <p style={{ color: 'hsl(var(--text-muted))', fontSize: '0.75rem', marginTop: '4px', fontStyle: 'italic' }}>
                    {a.hypothesis}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sandbox Metric Cards */}
      <div>
        <h3 style={{ fontSize: '1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={18} color="hsl(var(--primary))" /> Live Sandbox Telemetry
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
          {sandboxMetrics.map(m => (
            <SandboxMetricCard
              key={m.instanceId}
              instanceId={m.instanceId}
              cpuUtilization={m.cpuUtilization}
              ramUtilization={m.ramUtilization}
              isAnomaly={m.isAnomaly}
              anomalyScore={m.anomalyScore}
              status={m.status}
            />
          ))}
        </div>
      </div>

      {/* Candidate Table */}
      <div className="glass-panel animate-fade-in-up" style={{ padding: '24px' }}>
        <div className="flex-between" style={{ marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1rem' }}>Hiring Assessment & Cloud Sandbox Management</h3>
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--text-muted))' }} />
            <input
              className="input-glass"
              placeholder="Search candidates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: '36px', width: '240px' }}
            />
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                {['Candidate', 'Domain', 'AI Grade', 'Questions', 'Sandbox VM', 'VM Status', 'Session'].map(h => (
                  <th key={h} style={{
                    padding: '12px', color: 'hsl(var(--text-secondary))',
                    fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em',
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredCandidates.map(c => (
                <tr
                  key={c.id}
                  className="table-row-hover"
                  style={{ borderBottom: '1px solid var(--glass-border)', cursor: 'pointer' }}
                  onClick={() => onNavigate('report', {
                    name: c.name,
                    domain: c.domain,
                    history: [],
                    status: c.status,
                  })}
                >
                  <td style={{ padding: '14px 12px', fontWeight: 500 }}>{c.name}</td>
                  <td style={{ padding: '14px 12px', fontSize: '0.9rem' }}>{c.domain}</td>
                  <td style={{ padding: '14px 12px', color: 'hsl(var(--primary))', fontWeight: 700, fontFamily: 'Outfit' }}>
                    {c.grade}
                  </td>
                  <td style={{ padding: '14px 12px', fontSize: '0.9rem' }}>{c.questions}/5</td>
                  <td style={{ padding: '14px 12px', fontFamily: 'monospace', fontSize: '0.8rem', color: 'hsl(var(--text-secondary))' }}>
                    {c.sandbox}
                  </td>
                  <td style={{ padding: '14px 12px' }}>
                    <span className={`badge ${c.sandboxStatus === 'running' ? 'badge-success' : 'badge-neutral'}`}>
                      {c.sandboxStatus}
                    </span>
                  </td>
                  <td style={{ padding: '14px 12px' }}>
                    <span className={`badge ${c.status === 'Completed' ? 'badge-success' : 'badge-warning'}`}>
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
