import React, { useState } from 'react'
import { askQuestion } from '../services/api'
import AnswerCard from './AnswerCard'

export default function QueryPanel() {
  const [question, setQuestion] = useState('')
  const [filters, setFilters] = useState({
    keyword: '',
    date_from: '',
    date_to: '',
    journal: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(f => ({ ...f, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const payload = {
        question: question.trim(),
        filters: {
          keyword: filters.keyword || null,
          date_from: filters.date_from || null,
          date_to: filters.date_to || null,
          journal: filters.journal || null,
        },
      }
      const data = await askQuestion(payload)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2 className="section-title">Ask a Scientific Question</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Your Question *</label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={4}
              placeholder="e.g., What is the mechanism by which DCCR reduces hyperphagia in Prader-Willi Syndrome?"
              required
            />
          </div>

          <details style={{ marginBottom: 16 }}>
            <summary style={{ cursor: 'pointer', color: '#4a5568', fontSize: '0.9rem', fontWeight: 600 }}>
              Filter Options (optional)
            </summary>
            <div style={{ marginTop: 12 }}>
              <div className="form-row">
                <div className="form-group">
                  <label>Keyword Filter</label>
                  <input
                    type="text"
                    name="keyword"
                    value={filters.keyword}
                    onChange={handleFilterChange}
                    placeholder="Narrow by topic"
                  />
                </div>
                <div className="form-group">
                  <label>Journal</label>
                  <input
                    type="text"
                    name="journal"
                    value={filters.journal}
                    onChange={handleFilterChange}
                    placeholder="e.g., Nature"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Date From</label>
                  <input
                    type="date"
                    name="date_from"
                    value={filters.date_from}
                    onChange={handleFilterChange}
                  />
                </div>
                <div className="form-group">
                  <label>Date To</label>
                  <input
                    type="date"
                    name="date_to"
                    value={filters.date_to}
                    onChange={handleFilterChange}
                  />
                </div>
              </div>
            </div>
          </details>

          {error && <div className="error-box">{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading && <span className="spinner" />}
            {loading ? 'Generating Answer...' : 'Ask'}
          </button>
        </form>
      </div>

      {result && (
        <AnswerCard answer={result.answer} sources={result.sources} />
      )}
    </div>
  )
}
