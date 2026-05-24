import React, { useRef, useEffect, useCallback } from 'react'

const AudioWaveform = React.memo(function AudioWaveform({ isRecording = false, color = 'hsl(250, 85%, 65%)' }) {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  const analyserRef = useRef(null)
  const streamRef = useRef(null)

  const startVisualization = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      const source = audioCtx.createMediaStreamSource(stream)
      const analyser = audioCtx.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)
      analyserRef.current = analyser

      draw()
    } catch (err) {
      // Fallback: draw static wave
      drawStaticWave()
    }
  }, [])

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || !analyserRef.current) return

    const ctx = canvas.getContext('2d')
    const analyser = analyserRef.current
    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const render = () => {
      analyser.getByteTimeDomainData(dataArray)

      ctx.fillStyle = 'rgba(15, 20, 35, 0.3)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.lineWidth = 2
      ctx.strokeStyle = color
      ctx.shadowBlur = 8
      ctx.shadowColor = color
      ctx.beginPath()

      const sliceWidth = canvas.width / bufferLength
      let x = 0

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0
        const y = (v * canvas.height) / 2

        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
        x += sliceWidth
      }

      ctx.lineTo(canvas.width, canvas.height / 2)
      ctx.stroke()
      ctx.shadowBlur = 0

      animationRef.current = requestAnimationFrame(render)
    }

    render()
  }, [color])

  const drawStaticWave = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let phase = 0

    const render = () => {
      ctx.fillStyle = 'rgba(15, 20, 35, 0.15)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.lineWidth = 2
      ctx.strokeStyle = color
      ctx.shadowBlur = 6
      ctx.shadowColor = color
      ctx.beginPath()

      for (let x = 0; x < canvas.width; x++) {
        const y =
          canvas.height / 2 +
          Math.sin((x / canvas.width) * 4 * Math.PI + phase) * 15 +
          Math.sin((x / canvas.width) * 8 * Math.PI + phase * 1.5) * 8
        if (x === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }

      ctx.stroke()
      ctx.shadowBlur = 0
      phase += 0.05

      animationRef.current = requestAnimationFrame(render)
    }

    render()
  }, [color])

  useEffect(() => {
    if (isRecording) {
      startVisualization()
    } else {
      drawStaticWave()
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [isRecording, startVisualization, drawStaticWave])

  return (
    <div
      className="glass-panel-static"
      style={{
        padding: '2px',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
      }}
    >
      <canvas
        ref={canvasRef}
        width={600}
        height={80}
        style={{
          width: '100%',
          height: '60px',
          borderRadius: 'var(--radius-md)',
          display: 'block',
        }}
      />
    </div>
  )
})

export default AudioWaveform
