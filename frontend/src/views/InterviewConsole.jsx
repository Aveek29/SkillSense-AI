import React, { useState, useRef } from 'react'
import {
  Send, Clock, Award, MessageSquare,
  Mic, MicOff, CheckCircle2, AlertCircle
} from 'lucide-react'
import Button from '../components/Button'
import WebcamStream from '../components/WebcamStream'
import AudioWaveform from '../components/AudioWaveform'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

export default function InterviewConsole({ data, onNavigate }) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [questionIndex, setQuestionIndex] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const mediaRecorderRef = useRef(null)

  const [history, setHistory] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(
    data?.currentQuestion || {
      question_text: 'Explain standard database scaling constraints when migrating from local monolithic models to cloud instances.',
      difficulty: 'medium',
      target_keywords: ['horizontal scale', 'sharding', 'replicas', 'pooling'],
    }
  )
  const [latestGrade, setLatestGrade] = useState(null)

  const skills = data?.skills || ['Python', 'React', 'AWS', 'Docker', 'PostgreSQL']
  const interviewId = data?.interviewId
  const sandboxId = data?.sandboxId

  const handleSubmit = async () => {
    if (!transcript.trim()) return
    setSubmitting(true)
    setSubmitError(null)

    const questionText = currentQuestion.question_text

    try {
      if (!interviewId) {
        setSubmitError('No interview session. Please start a new interview from the portal.')
        setSubmitting(false)
        return
      }
      const body = new FormData()
      body.append('interview_id', interviewId)
      body.append('question_text', questionText)
      body.append('transcript', transcript)
      body.append('file', new Blob(['placeholder'], { type: 'audio/webm' }), 'answer.webm')

      const res = await fetch(`${API_BASE}/candidate/submit-answer`, {
        method: 'POST',
        body,
      })

      if (!res.ok) {
        throw new Error(`Server responded ${res.status}`)
      }

      const json = await res.json()
      const g = json.grades || {}
      const m = json.metrics || {}

      const grade = {
        score_tech: g.score_tech ?? 0,
        score_comm: g.score_comm ?? 0,
        score_rel: g.score_rel ?? 0,
        feedback: g.feedback || '',
        fluency_score: m.fluency_score ?? 0,
        speaking_rate_wpm: m.speaking_rate_wpm ?? 0,
      }

      appendGrade(grade, json)
    } catch (err) {
      setSubmitError(err.message || 'Network error. Please try again.')
      setSubmitting(false)
      return
    }
  }

  const appendGrade = (grade, json) => {
    const nextQ = json?.next_question
    const newEntry = {
      question: currentQuestion.question_text,
      transcript,
      ...grade,
    }

    const updatedHistory = [...history, newEntry]
    setHistory(updatedHistory)
    setLatestGrade(grade)
    setTranscript('')
    setIsRecording(false)

    if (json?.session_status === 'Completed' || updatedHistory.length >= 5) {
      setTimeout(() => {
        onNavigate('report', {
          ...data,
          history: updatedHistory,
          status: 'Completed',
        })
      }, 2000)
      setSubmitting(false)
      return
    }

    if (nextQ) {
      setCurrentQuestion({
        question_text: nextQ.question_text,
        difficulty: nextQ.difficulty || 'medium',
        target_keywords: nextQ.target_keywords || [],
      })
    } else {
      const nextQuestions = [
        { question_text: 'How would you design a microservices event bus for real-time data streaming?', difficulty: 'hard', target_keywords: ['Kafka', 'event-driven', 'pub/sub'] },
        { question_text: 'Describe container orchestration strategies with Kubernetes for a FastAPI application.', difficulty: 'medium', target_keywords: ['pods', 'services', 'ingress', 'HPA'] },
        { question_text: 'Walk through implementing a CI/CD pipeline with automated testing and blue-green deployments.', difficulty: 'hard', target_keywords: ['GitHub Actions', 'Docker', 'canary'] },
        { question_text: 'How does an Isolation Forest detect anomalies in time-series resource telemetry data?', difficulty: 'medium', target_keywords: ['path length', 'contamination', 'unsupervised'] },
      ]
      setCurrentQuestion(nextQuestions[questionIndex % nextQuestions.length])
      setQuestionIndex(questionIndex + 1)
    }

    setSubmitting(false)
  }

  const getDifficultyColor = (diff) => {
    if (diff === 'hard') return 'hsl(var(--danger))'
    if (diff === 'easy') return 'hsl(var(--success))'
    return 'hsl(var(--warning))'
  }

  return (
    <div className="container" style={{ padding: '30px 24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="flex-between animate-fade-in">
        <div>
          <h2>Live Interview Console</h2>
          <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginTop: '4px' }}>
            {data?.domain || 'AI/ML Engineering'} — {data?.mode || 'Technical'} Assessment
            {sandboxId && <span style={{ marginLeft: '12px', fontFamily: 'monospace', fontSize: '0.75rem' }}>VM: {sandboxId}</span>}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>
            <Clock size={16} />
            Q{history.length + 1} of 5
          </div>
          <div style={{ display: 'flex', gap: '4px' }}>
            {[0, 1, 2, 3, 4].map(i => (
              <div
                key={`q-progress-${i}`}
                style={{
                  width: '32px',
                  height: '4px',
                  borderRadius: '2px',
                  background: i < history.length
                    ? 'hsl(var(--success))'
                    : i === history.length
                      ? 'hsl(var(--primary))'
                      : 'rgba(255,255,255,0.1)',
                  transition: 'background 0.3s',
                }}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="animate-fade-in-up" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {skills.map((skill) => (
          <span
            key={skill}
            style={{
              padding: '4px 12px',
              borderRadius: '16px',
              fontSize: '0.75rem',
              fontWeight: 600,
              background: 'var(--primary-glow)',
              color: 'hsl(var(--primary))',
              border: '1px solid rgba(120, 90, 255, 0.2)',
            }}
          >
            {skill}
          </span>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.3fr', gap: '24px', alignItems: 'start' }}>
        <div className="animate-slide-left" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <WebcamStream isActive={true} />
          <AudioWaveform isRecording={isRecording} />

          <Button
            variant={isRecording ? 'danger' : 'primary'}
            icon={isRecording ? MicOff : Mic}
            onClick={() => setIsRecording(!isRecording)}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {isRecording ? 'Stop Recording' : 'Start Recording'}
          </Button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="glass-panel glow-primary" style={{ padding: '24px' }}>
            <div className="flex-between" style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MessageSquare size={18} color="hsl(var(--primary))" />
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'hsl(var(--text-secondary))' }}>
                  QUESTION {history.length + 1}
                </span>
              </div>
              <span
                className="badge"
                style={{
                  background: `${getDifficultyColor(currentQuestion.difficulty)}20`,
                  color: getDifficultyColor(currentQuestion.difficulty),
                }}
              >
                {currentQuestion.difficulty}
              </span>
            </div>
            <p style={{ fontSize: '1.05rem', lineHeight: 1.6 }}>
              {currentQuestion.question_text}
            </p>
            {currentQuestion.target_keywords && (
              <div style={{ marginTop: '12px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {currentQuestion.target_keywords.map((kw) => (
                  <span
                    key={kw}
                    style={{
                      padding: '2px 8px',
                      borderRadius: '6px',
                      fontSize: '0.7rem',
                      background: 'rgba(255,255,255,0.05)',
                      color: 'hsl(var(--text-muted))',
                    }}
                  >
                    {kw}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="glass-panel-static" style={{ padding: '20px' }}>
            <label
              style={{
                fontSize: '0.8rem',
                color: 'hsl(var(--text-secondary))',
                display: 'block',
                marginBottom: '8px',
              }}
            >
              Your Response Transcript
            </label>
            <textarea
              className="input-glass"
              placeholder="Type or dictate your response here..."
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              style={{
                minHeight: '120px',
                resize: 'vertical',
                marginBottom: '12px',
              }}
            />
            <Button
              icon={submitting ? CheckCircle2 : Send}
              onClick={handleSubmit}
              disabled={!transcript.trim() || submitting}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {submitting ? 'Analyzing Response...' : 'Submit Answer'}
            </Button>

            {submitError && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  marginTop: '8px',
                  fontSize: '0.8rem',
                  color: 'hsl(var(--danger))',
                }}
              >
                <AlertCircle size={14} />
                {submitError}
              </div>
            )}
          </div>

          {latestGrade && (
            <div className="glass-panel glow-success animate-fade-in-up" style={{ padding: '20px' }}>
              <div className="flex-between" style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Award size={18} color="hsl(var(--success))" />
                  <span style={{ fontWeight: 600 }}>AI Grading Result</span>
                </div>
                <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'hsl(var(--text-secondary))' }}>
                  {latestGrade.speaking_rate_wpm} WPM
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '12px' }}>
                {[
                  { label: 'Technical', score: latestGrade.score_tech },
                  { label: 'Communication', score: latestGrade.score_comm },
                  { label: 'Relevance', score: latestGrade.score_rel },
                ].map((axis, i) => (
                  <div
                    key={i}
                    style={{
                      textAlign: 'center',
                      padding: '12px',
                      background: 'rgba(255,255,255,0.03)',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '1.4rem',
                        fontWeight: 700,
                        fontFamily: 'Outfit',
                        color: axis.score >= 8 ? 'hsl(var(--success))' : axis.score >= 6 ? 'hsl(var(--warning))' : 'hsl(var(--danger))',
                      }}
                    >
                      {axis.score}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'hsl(var(--text-secondary))', marginTop: '4px' }}>
                      {axis.label}
                    </div>
                  </div>
                ))}
              </div>

              <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-secondary))', lineHeight: 1.6 }}>
                {latestGrade.feedback}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
