import React, { useState } from 'react'
import Disclaimer from './Disclaimer'

export default function AnswerCard({ answer, sources }) {
  const [expandedSources, setExpandedSources] = useState(true)

  return (
    <div className="card">
      <h3 className="section-title">Answer</h3>
      <div className="answer-box">{answer}</div>

      {sources && sources.length > 0 && (
        <div className="sources-section">
          <h3
            style={{ cursor: 'pointer', userSelect: 'none' }}
            onClick={() => setExpandedSources(v => !v)}
          >
            Sources ({sources.length}) {expandedSources ? '▾' : '▸'}
          </h3>
          {expandedSources && sources.map((s, i) => (
            <div key={i} className="source-card">
              <div className="source-title">{s.title || 'Untitled'}</div>
              <div className="source-meta">
                {s.pmid && <span>PMID: {s.pmid}</span>}
                {s.pmcid && <span>PMCID: {s.pmcid}</span>}
                {s.doi && <span>DOI: {s.doi}</span>}
                {s.journal && <span>{s.journal}</span>}
                {s.pub_date && <span>{s.pub_date}</span>}
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: '16px' }}>
        <Disclaimer />
      </div>
    </div>
  )
}
