import React, { useState, useRef, useEffect, useCallback } from 'react'
import { MessageCircle, X, Send, Mic, MicOff } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

export default function ChatBot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Namaste! I am your AI assistant. Ask me anything in Hindi or English.\n\nनमस्ते! मैं आपका AI सहायक हूँ। हिंदी या अंग्रेज़ी में कुछ भी पूछें।' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const positionRef = useRef({ x: window.innerWidth - 380, y: 80 })
  const [position, setPosition] = useState(positionRef.current)
  const draggingRef = useRef(false)
  const dragOffsetRef = useRef({ x: 0, y: 0 })
  const chatRef = useRef(null)
  const endRef = useRef(null)
  const recognitionRef = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Draggable logic — uses refs to avoid re-renders during drag
  useEffect(() => {
    const handleMove = (e) => {
      if (!draggingRef.current) return
      const newX = Math.max(0, Math.min(window.innerWidth - 360, e.clientX - dragOffsetRef.current.x))
      const newY = Math.max(0, Math.min(window.innerHeight - 500, e.clientY - dragOffsetRef.current.y))
      positionRef.current = { x: newX, y: newY }
      setPosition(positionRef.current)
    }
    const handleUp = () => {
      draggingRef.current = false
    }
    window.addEventListener('mousemove', handleMove)
    window.addEventListener('mouseup', handleUp)
    return () => { window.removeEventListener('mousemove', handleMove); window.removeEventListener('mouseup', handleUp) }
  }, [])

  const handleMouseDown = useCallback((e) => {
    draggingRef.current = true
    dragOffsetRef.current = { x: e.clientX - positionRef.current.x, y: e.clientY - positionRef.current.y }
  }, [])

  const sendMessage = async (text) => {
    if (!text.trim()) return
    const userMsg = { role: 'user', content: text }
    const updated = [...messages, userMsg]
    setMessages(updated)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: updated.slice(-10).map(m => ({ role: m.role, content: m.content })),
        }),
      })
      if (!res.ok) throw new Error('API error')
      const json = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: json.reply }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I could not reach the AI service. Please ensure the backend is running with GROQ_API_KEY configured.'
      }])
    }
    setLoading(false)
  }

  const toggleListening = () => {
    if (!SpeechRecognition) {
      setInput('Speech recognition not supported in this browser.')
      return
    }
    if (listening) {
      recognitionRef.current?.stop()
      setListening(false)
      return
    }
    const recognition = new SpeechRecognition()
    recognition.lang = 'hi-IN'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInput(transcript)
      setListening(false)
      sendMessage(transcript)
    }
    recognition.onerror = () => setListening(false)
    recognitionRef.current = recognition
    recognition.start()
    setListening(true)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input) }
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setOpen(!open)}
        className="chat-toggle-btn"
        style={{
          position: 'fixed', bottom: '24px', right: '24px', zIndex: 9999,
          width: '52px', height: '52px', borderRadius: '50%',
          background: 'linear-gradient(135deg, hsl(var(--primary)) 0%, #a855f7 100%)',
          border: 'none', color: 'white', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(120,90,255,0.4)',
        }}
      >
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>

      {/* Chat panel */}
      {open && (
        <div
          ref={chatRef}
          className="glass-panel"
          style={{
            position: 'fixed',
            left: `${position.x}px`, top: `${position.y}px`,
            width: '360px', height: '480px', zIndex: 9998,
            display: 'flex', flexDirection: 'column',
            cursor: draggingRef.current ? 'grabbing' : 'default',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            onMouseDown={handleMouseDown}
            style={{
              padding: '14px 16px', cursor: 'grab', display: 'flex',
              alignItems: 'center', justifyContent: 'space-between',
              borderBottom: '1px solid var(--glass-border)',
              background: 'rgba(10,14,25,0.5)',
              userSelect: 'none',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <MessageCircle size={16} color="hsl(var(--primary))" />
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>AI Assistant</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              style={{ background: 'none', border: 'none', color: 'hsl(var(--text-muted))', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {messages.map((msg, i) => (
              <div
                key={`msg-${i}`}
                style={{
                  maxWidth: '85%',
                  padding: '10px 14px',
                  borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  background: msg.role === 'user'
                    ? 'linear-gradient(135deg, hsl(var(--primary)) 0%, #a855f7 100%)'
                    : 'rgba(255,255,255,0.06)',
                  color: msg.role === 'user' ? 'white' : 'hsl(var(--text-primary))',
                  fontSize: '0.85rem',
                  lineHeight: 1.6,
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {msg.content}
              </div>
            ))}
            {loading && (
              <div style={{
                alignSelf: 'flex-start', padding: '10px 14px',
                borderRadius: '16px 16px 16px 4px',
                background: 'rgba(255,255,255,0.06)',
                fontSize: '0.85rem', color: 'hsl(var(--text-muted))',
              }}>
                <span style={{ animation: 'pulseGlow 1.5s infinite' }}>Thinking...</span>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Input */}
          <div style={{
            padding: '10px 12px', borderTop: '1px solid var(--glass-border)',
            display: 'flex', gap: '8px', alignItems: 'flex-end',
          }}>
            <button
              onClick={toggleListening}
              style={{
                background: listening ? 'rgba(230,60,60,0.2)' : 'rgba(255,255,255,0.05)',
                border: '1px solid', borderColor: listening ? 'hsl(var(--danger))' : 'var(--glass-border)',
                borderRadius: '50%', width: '36px', height: '36px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', color: listening ? 'hsl(var(--danger))' : 'hsl(var(--text-muted))',
                flexShrink: 0,
              }}
              title={listening ? 'Listening... (Hindi)' : 'Voice input (Hindi)'}
            >
              {listening ? <MicOff size={16} /> : <Mic size={16} />}
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message in Hindi or English..."
              rows={1}
              className="input-glass"
              style={{
                flex: 1, resize: 'none', padding: '10px 12px', minHeight: '36px', maxHeight: '80px',
                fontSize: '0.85rem',
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              style={{
                background: input.trim() && !loading
                  ? 'linear-gradient(135deg, hsl(var(--primary)) 0%, #a855f7 100%)'
                  : 'rgba(255,255,255,0.05)',
                border: 'none', borderRadius: '50%', width: '36px', height: '36px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: input.trim() && !loading ? 'pointer' : 'default',
                color: input.trim() && !loading ? 'white' : 'hsl(var(--text-muted))',
                flexShrink: 0,
              }}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
