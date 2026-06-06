import React, { useState, useEffect } from 'react'
import SearchPanel from './components/SearchPanel'
import QueryPanel from './components/QueryPanel'
import ArticleList from './components/ArticleList'
import Login from './components/Login'

const TABS = [
  { id: 'search', label: 'Search & Index' },
  { id: 'query', label: 'Ask a Question' },
  { id: 'articles', label: 'Indexed Articles' },
]

function decodeToken(token) {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

function DbStatsBanner() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetch('/api/stats').then(r => r.json()).then(setStats).catch(() => {})
  }, [])

  if (!stats) return null

  return (
    <div style={{
      background: 'linear-gradient(90deg, #ebf8ff, #e9d8fd)',
      border: '1px solid #bee3f8',
      borderRadius: '8px',
      padding: '10px 18px',
      marginBottom: '16px',
      display: 'flex',
      flexWrap: 'wrap',
      gap: '18px',
      fontSize: '0.85rem',
      color: '#2d3748',
      alignItems: 'center',
    }}>
      <span>🗄️ <strong>Shared Knowledge Base:</strong></span>
      <span>📄 <strong>{stats.total_articles.toLocaleString()}</strong> articles</span>
      <span>🧩 <strong>{stats.total_chunks_embedded.toLocaleString()}</strong> embedded chunks</span>
      <span>🔍 <strong>{stats.cached_searches}</strong> cached searches</span>
      <span>📚 <strong>{stats.unique_journals}</strong> journals</span>
      {stats.recent_searches?.length > 0 && (
        <span style={{ color: '#718096' }}>
          Recent: {stats.recent_searches.slice(0, 3).map(s => `"${s.keyword}"`).join(', ')}
        </span>
      )}
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState('search')

  // Parse URL params on mount
  const params = new URLSearchParams(window.location.search)
  const tokenFromUrl = params.get('token')
  const authErrorFromUrl = params.get('auth_error')

  if (tokenFromUrl) {
    localStorage.setItem('auth_token', tokenFromUrl)
    window.history.replaceState({}, '', '/')
  }

  const [token, setToken] = useState(tokenFromUrl || localStorage.getItem('auth_token'))
  const [authError, setAuthError] = useState(authErrorFromUrl || null)

  useEffect(() => {
    if (authErrorFromUrl) {
      setAuthError(authErrorFromUrl)
      window.history.replaceState({}, '', '/')
    }
  }, [])

  function logout() {
    localStorage.removeItem('auth_token')
    setToken(null)
    setAuthError(null)
  }

  if (!token) {
    return <Login error={authError} />
  }

  const user = decodeToken(token)

  return (
    <div className="app-container">
      <header className="app-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1>RareDisease LitMiner</h1>
          <p>AI-powered scientific literature mining for rare disease research</p>
        </div>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(255,255,255,0.15)', borderRadius: '10px', padding: '8px 14px' }}>
            {user.picture && (
              <img
                src={user.picture}
                alt={user.name}
                width={32}
                height={32}
                style={{ borderRadius: '50%', border: '2px solid rgba(255,255,255,0.5)' }}
              />
            )}
            <div style={{ fontSize: '0.85rem', lineHeight: 1.3 }}>
              <div style={{ fontWeight: 600 }}>{user.name}</div>
              <div style={{ opacity: 0.8, fontSize: '0.78rem' }}>{user.sub}</div>
            </div>
            <button
              onClick={logout}
              style={{
                marginLeft: '8px', padding: '5px 12px', borderRadius: '6px',
                border: '1px solid rgba(255,255,255,0.4)', background: 'rgba(255,255,255,0.15)',
                color: 'white', cursor: 'pointer', fontSize: '0.82rem', fontWeight: 500
              }}
            >
              Logout
            </button>
          </div>
        )}
      </header>

      <div className="tab-bar">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <main>
        <DbStatsBanner />
        {activeTab === 'search' && <SearchPanel />}
        {activeTab === 'query' && <QueryPanel />}
        {activeTab === 'articles' && <ArticleList />}
      </main>
    </div>
  )
}
