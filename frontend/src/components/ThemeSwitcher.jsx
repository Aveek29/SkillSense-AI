import React, { useState, useRef, useEffect } from 'react'

const THEMES = [
  { key: 'slate-dark', label: 'Slate Dark', icon: '\u{1F30C}' },
  { key: 'neon-cyberpunk', label: 'Neon Cyberpunk', icon: '\u{1F525}' },
  { key: 'emerald-horizon', label: 'Emerald Horizon', icon: '\u{1F33F}' },
  { key: 'sunset-fusion', label: 'Sunset Fusion', icon: '\u{1F307}' },
  { key: 'ocean-mist', label: 'Ocean Mist', icon: '\u{1F30A}' },
]

const ThemeSwitcher = React.memo(function ThemeSwitcher({ theme, setTheme }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const active = THEMES.find((t) => t.key === theme) || THEMES[0]

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        className="nav-link"
        onClick={() => setOpen((o) => !o)}
        style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        title="Switch theme"
      >
        <span style={{ fontSize: '1rem' }}>{active.icon}</span>
        <span style={{
          display: 'inline-block',
          width: '20px',
          height: '20px',
          borderRadius: '50%',
          border: '2px solid rgba(255,255,255,0.2)',
          background: {
            'slate-dark': 'linear-gradient(135deg, #1e1b4b, #312e81)',
            'neon-cyberpunk': 'linear-gradient(135deg, #831843, #be185d)',
            'emerald-horizon': 'linear-gradient(135deg, #064e3b, #047857)',
            'sunset-fusion': 'linear-gradient(135deg, #7c2d12, #c2410c)',
            'ocean-mist': 'linear-gradient(135deg, #0c4a6e, #0369a1)',
          }[theme],
        }} />
      </button>

      {open && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          marginTop: '8px',
          background: 'hsl(var(--bg-card))',
          border: '1px solid var(--glass-border)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-lg)',
          padding: '6px',
          minWidth: '190px',
          zIndex: 200,
        }}>
          {THEMES.map((t) => {
            const active = t.key === theme
            return (
              <button
                key={t.key}
                onClick={() => { setTheme(t.key); setOpen(false) }}
                className="theme-option"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  width: '100%',
                  padding: '10px 14px',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  background: active ? 'var(--primary-glow)' : 'transparent',
                  color: active ? 'hsl(var(--primary))' : 'hsl(var(--text-secondary))',
                  cursor: 'pointer',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '0.85rem',
                  fontWeight: active ? 600 : 400,
                  textAlign: 'left',
                }}
              >
                <span style={{ fontSize: '1.15rem' }}>{t.icon}</span>
                <span>{t.label}</span>
                {active && <span style={{ marginLeft: 'auto', fontSize: '0.7rem' }}>&#x2713;</span>}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
})

export default ThemeSwitcher
