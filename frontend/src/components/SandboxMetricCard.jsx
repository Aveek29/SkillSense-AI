import React from 'react'
import { Cpu, HardDrive, AlertTriangle } from 'lucide-react'

const SandboxMetricCard = React.memo(function SandboxMetricCard({
  instanceId = 'i-unknown',
  cpuUtilization = 0,
  ramUtilization = 0,
  isAnomaly = false,
  anomalyScore = 0,
  status = 'running',
}) {
  const getCpuColor = (val) => {
    if (val >= 85) return 'hsl(var(--danger))'
    if (val >= 60) return 'hsl(var(--warning))'
    return 'hsl(var(--success))'
  }

  const getRamColor = (val) => {
    if (val >= 80) return 'hsl(var(--danger))'
    if (val >= 55) return 'hsl(var(--warning))'
    return 'hsl(var(--success))'
  }

  return (
    <div
      className={`glass-panel ${isAnomaly ? 'glow-danger' : ''}`}
      style={{
        padding: '20px',
        position: 'relative',
      }}
    >
      {/* Anomaly Alert Banner */}
      {isAnomaly && (
        <div
          style={{
            position: 'absolute',
            top: '-1px',
            left: '-1px',
            right: '-1px',
            padding: '6px 12px',
            background: 'linear-gradient(90deg, rgba(230, 60, 60, 0.3), rgba(230, 60, 60, 0.1))',
            borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.7rem',
            fontWeight: 700,
            color: 'hsl(var(--danger))',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}
        >
          <AlertTriangle size={12} />
          Anomaly Detected — Score: {anomalyScore.toFixed(4)}
        </div>
      )}

      <div style={{ marginTop: isAnomaly ? '24px' : 0 }}>
        {/* Instance header */}
        <div className="flex-between" style={{ marginBottom: '16px' }}>
          <span
            style={{
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              color: 'hsl(var(--text-secondary))',
            }}
          >
            {instanceId}
          </span>
          <span
            className={`badge ${status === 'running' ? 'badge-success' : 'badge-neutral'}`}
          >
            {status}
          </span>
        </div>

        {/* Metrics */}
        <div style={{ display: 'flex', gap: '20px' }}>
          {/* CPU */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <Cpu size={14} color={getCpuColor(cpuUtilization)} />
              <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-secondary))' }}>CPU</span>
            </div>
            <div
              style={{
                fontSize: '1.4rem',
                fontWeight: 700,
                fontFamily: 'Outfit',
                color: getCpuColor(cpuUtilization),
              }}
            >
              {cpuUtilization}%
            </div>
            <div
              style={{
                height: '4px',
                background: 'rgba(255,255,255,0.08)',
                borderRadius: '2px',
                marginTop: '8px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${Math.min(cpuUtilization, 100)}%`,
                  background: getCpuColor(cpuUtilization),
                  borderRadius: '2px',
                  transition: 'width 0.5s ease',
                }}
              />
            </div>
          </div>

          {/* RAM */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <HardDrive size={14} color={getRamColor(ramUtilization)} />
              <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-secondary))' }}>RAM</span>
            </div>
            <div
              style={{
                fontSize: '1.4rem',
                fontWeight: 700,
                fontFamily: 'Outfit',
                color: getRamColor(ramUtilization),
              }}
            >
              {ramUtilization}%
            </div>
            <div
              style={{
                height: '4px',
                background: 'rgba(255,255,255,0.08)',
                borderRadius: '2px',
                marginTop: '8px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${Math.min(ramUtilization, 100)}%`,
                  background: getRamColor(ramUtilization),
                  borderRadius: '2px',
                  transition: 'width 0.5s ease',
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
})

export default SandboxMetricCard
