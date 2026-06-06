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
            {result.indexed_count} article(s) loaded —{' '}
            <strong>{result.new_count} new</strong> indexed,{' '}
            <strong>{result.cached_count} already in database</strong> (no re-embedding).
          </div>

          {result.summary && (
            <div style={{ marginTop: '20px' }}>
              <h3 className="section-title">Literature Summary</h3>
              {result.summary.split(/\n{2,}/).filter(p => p.trim()).map((p, i) => (
                <p key={i} style={{ marginBottom: '0.9em', lineHeight: '1.75', color: '#2d3748', fontSize: '0.95rem' }}>
                  {p.trim()}
                </p>
              ))}
            </div>
          )}

          <div style={{ marginTop: '24px' }}>
            <h3 className="section-title" style={{ marginBottom: '12px' }}>References</h3>
            <ol style={{ paddingLeft: '1.2em', margin: 0 }}>
              {result.articles.map((art, i) => {
                const authors = art.authors || []
                const first = authors.length > 0 ? authors[0].split(',')[0] : 'Unknown'
                const etAl = authors.length > 1 ? ' et al.' : ''
                const year = art.pub_date ? art.pub_date.slice(0, 4) : 'n.d.'
                return (
                  <li key={art.id} style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#4a5568', lineHeight: '1.6' }}>
                    <span style={{ fontWeight: 500, color: '#2b6cb0' }}>{first}{etAl}</span>
                    <span> ({year}). </span>
                    <span style={{ fontStyle: 'italic' }}>{art.title}. </span>
                    {art.journal && <span>{art.journal}. </span>}
                    <span style={{ display: 'inline-flex', gap: '8px', flexWrap: 'wrap', marginTop: '2px' }}>
                      {art.pmid && (
                        <a href={`https://pubmed.ncbi.nlm.nih.gov/${art.pmid}`} target="_blank" rel="noreferrer"
                          style={{ color: '#3182ce', fontSize: '0.8rem' }}>
                          PMID: {art.pmid}
                        </a>
                      )}
                      {art.doi && (
                        <a href={`https://doi.org/${art.doi}`} target="_blank" rel="noreferrer"
                          style={{ color: '#3182ce', fontSize: '0.8rem' }}>
                          DOI: {art.doi}
                        </a>
                      )}
                      {art.pmcid && (
                        <a href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${art.pmcid}`} target="_blank" rel="noreferrer"
                          style={{ color: '#3182ce', fontSize: '0.8rem' }}>
                          {art.pmcid}
                        </a>
                      )}
                      {art.full_text_available && (
                        <span className="badge badge-green">Full Text</span>
                      )}
                    </span>
                  </li>
                )
              })}
            </ol>
          </div>
        </div>
      )}
    </div>
  )
}
