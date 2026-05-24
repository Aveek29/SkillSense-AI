import React, { useRef, useEffect, useState } from 'react'
import { Video, VideoOff } from 'lucide-react'

const WebcamStream = React.memo(function WebcamStream({ isActive = true }) {
  const videoRef = useRef(null)
  const [stream, setStream] = useState(null)
  const [error, setError] = useState(null)
  const [cameraOn, setCameraOn] = useState(isActive)

  useEffect(() => {
    if (cameraOn) {
      startCamera()
    } else {
      stopCamera()
    }
    return () => stopCamera()
  }, [cameraOn])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false,
      })
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setStream(mediaStream)
      setError(null)
    } catch (err) {
      setError('Camera access denied or unavailable')
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  return (
    <div
      className="glass-panel-static"
      style={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 'var(--radius-lg)',
        aspectRatio: '4/3',
        background: 'rgba(10, 14, 25, 0.9)',
      }}
    >
      {error ? (
        <div className="flex-center" style={{ height: '100%', flexDirection: 'column', gap: '12px' }}>
          <VideoOff size={48} color="hsl(var(--text-muted))" />
          <p style={{ color: 'hsl(var(--text-muted))', fontSize: '0.85rem' }}>{error}</p>
        </div>
      ) : !cameraOn ? (
        <div className="flex-center" style={{ height: '100%', flexDirection: 'column', gap: '12px' }}>
          <VideoOff size={48} color="hsl(var(--text-muted))" />
          <p style={{ color: 'hsl(var(--text-muted))', fontSize: '0.85rem' }}>Camera Off</p>
        </div>
      ) : (
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: 'scaleX(-1)',
          }}
        />
      )}

      {/* Camera toggle overlay */}
      <button
        onClick={() => setCameraOn(!cameraOn)}
        style={{
          position: 'absolute',
          bottom: '12px',
          right: '12px',
          background: cameraOn ? 'rgba(230, 60, 60, 0.8)' : 'rgba(30, 200, 100, 0.8)',
          border: 'none',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        {cameraOn ? <VideoOff size={18} color="white" /> : <Video size={18} color="white" />}
      </button>

      {/* Live indicator */}
      {cameraOn && !error && (
        <div
          style={{
            position: 'absolute',
            top: '12px',
            left: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(230, 60, 60, 0.85)',
            padding: '4px 10px',
            borderRadius: '12px',
            fontSize: '0.7rem',
            fontWeight: 700,
            letterSpacing: '0.05em',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              background: 'white',
              borderRadius: '50%',
              animation: 'pulseGlow 1.5s infinite',
            }}
          />
          LIVE
        </div>
      )}
    </div>
  )
})

export default WebcamStream
