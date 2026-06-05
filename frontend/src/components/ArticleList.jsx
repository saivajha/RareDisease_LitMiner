import React, { useState, useEffect } from 'react'
import { listArticles } from '../services/api'

export default function ArticleList() {
  const [articles, setArticles] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ keyword: '', journal: '' })

  const limit = 20

  const fetchArticles = async (pg = 1) => {
    setLoading(true)
    setError(null)
    try {
      const data = await listArticles({
        keyword: filters.keyword || undefined,
        journal: filters.journal || undefined,
        page: pg,
        limit,
      })
      setArticles(data.articles)
      setTotal(data.total)
      setPage(pg)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchArticles(1)
  }, [])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(f => ({ ...f, [name]: value }))
  }

  const handleSearch = (e) => {
    e.preventDefault()
    fetchArticles(1)
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="card">
      <h2 className="section-title">Indexed Articles ({total})</h2>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <input
          type="text"
          name="keyword"
          value={filters.keyword}
          onChange={handleFilterChange}
          placeholder="Filter by keyword..."
          style={{ flex: '1', padding: '8px 12px', border: '1px solid #cbd5e0', borderRadius: 6, minWidth: 180 }}
        />
        <input
          type="text"
          name="journal"
          value={filters.journal}
          onChange={handleFilterChange}
          placeholder="Filter by journal..."
          style={{ flex: '1', padding: '8px 12px', border: '1px solid #cbd5e0', borderRadius: 6, minWidth: 140 }}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '8px 20px' }}>
          Filter
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 24, color: '#718096' }}>Loading...</div>
      ) : articles.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 24, color: '#718096' }}>
          No articles indexed yet. Use the Search & Index tab to add articles.
        </div>
      ) : (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table className="article-table">
              <thead>
                <tr>
                  <th>PMID</th>
                  <th>Title</th>
                  <th>Journal</th>
                  <th>Date</th>
                  <th>Full Text</th>
                </tr>
              </thead>
              <tbody>
                {articles.map((art) => (
                  <tr key={art.id}>
                    <td>
                      <a
                        href={`https://pubmed.ncbi.nlm.nih.gov/${art.pmid}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: '#2b6cb0', textDecoration: 'none' }}
                      >
                        {art.pmid}
                      </a>
                    </td>
                    <td style={{ maxWidth: 350 }}>
                      <span title={art.title}>
                        {art.title.length > 80 ? art.title.slice(0, 77) + '...' : art.title}
                      </span>
                    </td>
                    <td>{art.journal || '—'}</td>
                    <td>{art.pub_date || '—'}</td>
                    <td>
                      <span className={`badge ${art.full_text_available ? 'badge-green' : 'badge-gray'}`}>
                        {art.full_text_available ? 'Yes' : 'No'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={() => fetchArticles(page - 1)} disabled={page <= 1}>
                Previous
              </button>
              <span style={{ color: '#4a5568', fontSize: '0.9rem' }}>
                Page {page} of {totalPages}
              </span>
              <button onClick={() => fetchArticles(page + 1)} disabled={page >= totalPages}>
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
