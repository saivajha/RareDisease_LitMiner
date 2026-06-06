import React, { useState, useEffect } from 'react'
import SearchPanel from './components/SearchPanel'
import QueryPanel from './components/QueryPanel'
import ArticleList from './components/ArticleList'

const TABS = [
  { id: 'search', label: 'Search & Index' },
  { id: 'query', label: 'Ask a Question' },
  { id: 'articles', label: 'Indexed Articles' },
]

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

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>RareDisease LitMiner</h1>
        <p>AI-powered scientific literature mining for rare disease research</p>
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
