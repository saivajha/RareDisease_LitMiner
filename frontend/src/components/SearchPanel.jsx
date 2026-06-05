import React, { useState } from 'react'
import { searchAndIndex } from '../services/api'

export default function SearchPanel() {
  const [form, setForm] = useState({
    keyword: '',
    max_results: 20,
    date_from: '',
    date_to: '',
    journal_filter: '',
    fetch_fulltext: false,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.keyword.trim()) {
      setError('Please enter a keyword.')
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const payload = {
        keyword: form.keyword.trim(),
        max_results: parseInt(form.max_results, 10) || 20,
        date_from: form.date_from || null,
        date_to: form.date_to || null,
        journal_filter: form.journal_filter || null,
        fetch_fulltext: form.fetch_fulltext,
      }
      const data = await searchAndIndex(payload)
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
        <h2 className="section-title">Search & Index PubMed Articles</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Search Keyword *</label>
            <input
              type="text"
              name="keyword"
              value={form.keyword}
              onChange={handleChange}
              placeholder="e.g., Prader-Willi Syndrome DCCR hyperphagia"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Max Results</label>
              <input
                type="number"
                name="max_results"
                value={form.max_results}
                onChange={handleChange}
                min={1}
                max={200}
              />
            </div>
            <div className="form-group">
              <label>Journal Filter</label>
              <input
                type="text"
                name="journal_filter"
                value={form.journal_filter}
                onChange={handleChange}
                placeholder="e.g., Nature, NEJM"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Date From</label>
              <input
                type="date"
                name="date_from"
                value={form.date_from}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Date To</label>
              <input
                type="date"
                name="date_to"
                value={form.date_to}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group">
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="fetch_fulltext"
                name="fetch_fulltext"
                checked={form.fetch_fulltext}
                onChange={handleChange}
              />
              <label htmlFor="fetch_fulltext">
                Fetch PMC Open Access full text (slower, more comprehensive)
              </label>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading && <span className="spinner" />}
            {loading ? 'Searching & Indexing...' : 'Search & Index'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card">
          <div className="success-box">
            Successfully indexed {result.indexed_count} article(s).
          </div>
          <h3 className="section-title">Indexed Articles</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {result.articles.map((art) => (
              <li key={art.id} style={{
                padding: '10px 0',
                borderBottom: '1px solid #e2e8f0',
                fontSize: '0.9rem'
              }}>
                <div style={{ fontWeight: 600, color: '#2b6cb0' }}>{art.title}</div>
                <div style={{ color: '#718096', marginTop: 3, fontSize: '0.8rem' }}>
                  PMID: {art.pmid}
                  {art.journal && ` | ${art.journal}`}
                  {art.pub_date && ` | ${art.pub_date}`}
                  {art.full_text_available && (
                    <span className="badge badge-green" style={{ marginLeft: 8 }}>Full Text</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
