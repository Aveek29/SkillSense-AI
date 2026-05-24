import React, { useMemo } from 'react'
import Chart from 'react-apexcharts'
import {
  BarChart3, MessageSquare, Mic, Target,
  CheckCircle, Clock, ArrowLeft, TrendingUp, Zap
} from 'lucide-react'
import Button from '../components/Button'

export default function ReportDashboard({ data, onNavigate }) {
  const history = data?.history || [
    {
      question: 'Explain database scaling constraints for cloud migration.',
      transcript: 'Horizontal scaling with sharding and read replicas...',
      score_tech: 8.5, score_comm: 8.0, score_rel: 7.5,
      fluency_score: 8.2, speaking_rate_wpm: 132.5,
      feedback: 'Excellent coverage of sharding strategies. Consider connection pooling impacts.'
    },
    {
      question: 'Design a microservices event bus for real-time data.',
      transcript: 'Using Kafka with event-driven architecture and pub/sub patterns...',
      score_tech: 9.0, score_comm: 8.5, score_rel: 9.0,
      fluency_score: 7.8, speaking_rate_wpm: 141.2,
      feedback: 'Strong event-driven design knowledge. Elaborate on fault tolerance.'
    },
    {
      question: 'Container orchestration with Kubernetes.',
      transcript: 'Deploying pods with services, ingress controllers, and HPA...',
      score_tech: 7.8, score_comm: 7.5, score_rel: 8.0,
      fluency_score: 8.5, speaking_rate_wpm: 128.7,
      feedback: 'Good fundamentals. Explore StatefulSets for database workloads.'
    },
    {
      question: 'CI/CD pipeline with automated testing.',
      transcript: 'GitHub Actions workflow with Docker build and blue-green deployments...',
      score_tech: 8.2, score_comm: 8.8, score_rel: 8.5,
      fluency_score: 9.0, speaking_rate_wpm: 135.4,
      feedback: 'Well-structured pipeline design. Include security scanning stages.'
    },
    {
      question: 'Isolation Forest anomaly detection in telemetry.',
      transcript: 'Using path length scoring with contamination parameters...',
      score_tech: 9.2, score_comm: 8.0, score_rel: 9.5,
      fluency_score: 8.7, speaking_rate_wpm: 138.9,
      feedback: 'Exceptional ML understanding. Consider ensemble approaches.'
    },
  ]

  const candidateName = data?.name || 'Alice Johnson'
  const domain = data?.domain || 'AI/ML Engineering'

  // Compute averages — memoized
  const { avgTech, avgComm, avgRel, avgFluency, avgWpm, overallGrade } = useMemo(() => {
    const t = (history.reduce((a, h) => a + h.score_tech, 0) / history.length).toFixed(1)
    const c = (history.reduce((a, h) => a + h.score_comm, 0) / history.length).toFixed(1)
    const r = (history.reduce((a, h) => a + h.score_rel, 0) / history.length).toFixed(1)
    const f = (history.reduce((a, h) => a + h.fluency_score, 0) / history.length).toFixed(1)
    const w = (history.reduce((a, h) => a + h.speaking_rate_wpm, 0) / history.length).toFixed(0)
    const o = ((parseFloat(t) + parseFloat(c) + parseFloat(r)) / 3).toFixed(1)
    return { avgTech: t, avgComm: c, avgRel: r, avgFluency: f, avgWpm: w, overallGrade: o }
  }, [history])

  // Radar chart for skill axes
  const radarOptions = useMemo(() => ({
    chart: { type: 'radar', toolbar: { show: false }, background: 'transparent', fontFamily: 'Inter' },
    colors: ['#785aff'],
    fill: { opacity: 0.25 },
    stroke: { width: 2 },
    markers: { size: 4, colors: ['#785aff'], strokeWidth: 0 },
    xaxis: {
      categories: ['Technical', 'Communication', 'Relevance', 'Fluency', 'Pace'],
      labels: { style: { colors: Array(5).fill('#94a3b8'), fontSize: '12px', fontFamily: 'Inter' } }
    },
    yaxis: { show: false, max: 10 },
    plotOptions: { radar: { polygons: { strokeColors: 'rgba(255,255,255,0.08)', connectorColors: 'rgba(255,255,255,0.08)' } } },
  }), [])

  const radarSeries = useMemo(() => [{
    name: 'Score',
    data: [parseFloat(avgTech), parseFloat(avgComm), parseFloat(avgRel), parseFloat(avgFluency), Math.min(10, parseFloat(avgWpm) / 15)]
  }], [avgTech, avgComm, avgRel, avgFluency, avgWpm])

  // Per-question score trend
  const trendOptions = useMemo(() => ({
    chart: { type: 'bar', toolbar: { show: false }, background: 'transparent', fontFamily: 'Inter' },
    colors: ['#785aff', '#a855f7', '#1ec864'],
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
    dataLabels: { enabled: false },
    xaxis: {
      categories: history.map((_, i) => `Q${i + 1}`),
      labels: { style: { colors: '#94a3b8', fontFamily: 'Inter' } },
      axisBorder: { show: false },
    },
    yaxis: {
      max: 10,
      labels: { style: { colors: '#94a3b8', fontFamily: 'Inter' }, formatter: (v) => v.toFixed(0) },
    },
    legend: { labels: { colors: '#f1f5f9' }, position: 'top' },
    grid: { borderColor: 'rgba(255,255,255,0.06)', strokeDashArray: 4 },
    tooltip: { theme: 'dark' },
  }), [])

  const trendSeries = useMemo(() => [
    { name: 'Technical', data: history.map(h => h.score_tech) },
    { name: 'Communication', data: history.map(h => h.score_comm) },
    { name: 'Relevance', data: history.map(h => h.score_rel) },
  ], [history])

  const getGradeColor = (score) => {
    if (score >= 8.5) return 'hsl(var(--success))'
    if (score >= 7) return 'hsl(var(--primary))'
    if (score >= 5) return 'hsl(var(--warning))'
    return 'hsl(var(--danger))'
  }

  return (
    <div className="container" style={{ padding: '30px 24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div className="flex-between animate-fade-in">
        <div>
          <Button variant="outline" size="sm" icon={ArrowLeft} onClick={() => onNavigate('portal')} style={{ marginBottom: '12px' }}>
            Back
          </Button>
          <h2>Assessment Report</h2>
          <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginTop: '4px' }}>
            {candidateName} — {domain}
          </p>
        </div>
        <div
          className="glass-panel-static glow-primary"
          style={{
            padding: '16px 28px',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '0.7rem', color: 'hsl(var(--text-secondary))', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Overall Grade
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, fontFamily: 'Outfit', color: getGradeColor(overallGrade) }}>
            {overallGrade}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>out of 10.0</div>
        </div>
      </div>

      {/* Summary KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
        {[
          { icon: Target, label: 'Technical', value: avgTech, color: '--primary' },
          { icon: MessageSquare, label: 'Communication', value: avgComm, color: '--success' },
          { icon: Zap, label: 'Relevance', value: avgRel, color: '--warning' },
          { icon: Mic, label: 'Fluency', value: avgFluency, color: '--primary' },
          { icon: TrendingUp, label: 'Avg WPM', value: avgWpm, color: '--success' },
        ].map((kpi, i) => (
          <div key={kpi.label} className={`glass-panel animate-fade-in-up stagger-${i + 1}`} style={{ padding: '16px', textAlign: 'center' }}>
            <kpi.icon size={20} color={`hsl(var(${kpi.color}))`} style={{ marginBottom: '8px' }} />
            <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'Outfit', color: `hsl(var(${kpi.color}))` }}>
              {kpi.value}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'hsl(var(--text-secondary))', marginTop: '4px' }}>{kpi.label}</div>
          </div>
        ))}
      </div>

      {/* Charts Row: Radar + Score Trend */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '24px' }}>
        <div className="glass-panel animate-fade-in-up" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '8px' }}>Competency Radar</h3>
          <Chart options={radarOptions} series={radarSeries} type="radar" height={280} />
        </div>

        <div className="glass-panel animate-fade-in-up" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '8px' }}>Per-Question Score Breakdown</h3>
          <Chart options={trendOptions} series={trendSeries} type="bar" height={280} />
        </div>
      </div>

      {/* Question-by-Question Breakdown */}
      <div className="glass-panel animate-fade-in-up" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart3 size={18} color="hsl(var(--primary))" />
          Detailed Question Analysis
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {history.map((entry, i) => (
            <div
              key={i}
              className="glass-panel-static"
              style={{
                padding: '20px',
                borderLeft: `4px solid ${getGradeColor(entry.score_tech)}`,
                borderRadius: '0 var(--radius-md) var(--radius-md) 0',
              }}
            >
              <div className="flex-between" style={{ marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={16} color="hsl(var(--success))" />
                  <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Question {i + 1}</span>
                </div>
                <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem' }}>
                  <span>Tech: <strong style={{ color: getGradeColor(entry.score_tech) }}>{entry.score_tech}</strong></span>
                  <span>Comm: <strong style={{ color: getGradeColor(entry.score_comm) }}>{entry.score_comm}</strong></span>
                  <span>Rel: <strong style={{ color: getGradeColor(entry.score_rel) }}>{entry.score_rel}</strong></span>
                </div>
              </div>

              <p style={{ fontSize: '0.9rem', marginBottom: '8px', lineHeight: 1.5 }}>
                <strong style={{ color: 'hsl(var(--text-secondary))' }}>Q:</strong> {entry.question}
              </p>

              <div style={{ display: 'flex', gap: '16px', marginBottom: '8px', fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Mic size={12} /> {entry.speaking_rate_wpm} WPM
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Clock size={12} /> Fluency: {entry.fluency_score}/10
                </span>
              </div>

              <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-secondary))', lineHeight: 1.6, fontStyle: 'italic' }}>
                "{entry.feedback}"
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
