import React, { useState } from 'react'
import SearchPanel from './components/SearchPanel'
import QueryPanel from './components/QueryPanel'
import ArticleList from './components/ArticleList'

const TABS = [
  { id: 'search', label: 'Search & Index' },
  { id: 'query', label: 'Ask a Question' },
  { id: 'articles', label: 'Indexed Articles' },
]

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
        {activeTab === 'search' && <SearchPanel />}
        {activeTab === 'query' && <QueryPanel />}
        {activeTab === 'articles' && <ArticleList />}
      </main>
    </div>
  )
}
