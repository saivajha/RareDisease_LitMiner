import React, { useState } from 'react'
import Disclaimer from './Disclaimer'

function formatAuthors(authors) {
  if (!authors || authors.length === 0) return ''
  if (authors.length === 1) return authors[0]
  if (authors.length === 2) return authors.join(' & ')
  return `${authors[0]} et al.`
}

function formatYear(pub_date) {
  return pub_date ? pub_date.slice(0, 4) : 'n.d.'
}

export default function AnswerCard({ answer, sources }) {
  const [expandedRefs, setExpandedRefs] = useState(true)

  const paragraphs = answer
    ? answer.split(/\n{2,}/).filter(p => p.trim())
    : []

  return (
    <div className="card">
      <h3 className="section-title">Answer</h3>

      <div className="answer-prose">
        {paragraphs.length > 0
          ? paragraphs.map((p, i) => (
              <p key={i} style={{ marginBottom: '0.9em', lineHeight: '1.75', color: '#2d3748' }}>
                {p.trim()}
              </p>
            ))
          : <p style={{ color: '#718096' }}>{answer}</p>
        }
      </div>

      {sources && sources.length > 0 && (
        <div className="sources-section" style={{ marginTop: '24px' }}>
          <h4
            style={{ cursor: 'pointer', userSelect: 'none', color: '#4a5568', marginBottom: '12px', fontSize: '0.95rem', fontWeight: 600 }}
            onClick={() => setExpandedRefs(v => !v)}
          >
            References ({sources.length}) {expandedRefs ? '▾' : '▸'}
          </h4>
          {expandedRefs && (
            <ol style={{ paddingLeft: '1.2em', margin: 0 }}>
              {sources.map((s, i) => (
                <li key={i} style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#4a5568', lineHeight: '1.6' }}>
                  <span style={{ fontWeight: 500, color: '#2b6cb0' }}>
                    {formatAuthors(s.authors)}
                  </span>
                  {s.pub_date && <span> ({formatYear(s.pub_date)}). </span>}
                  <span style={{ fontStyle: 'italic' }}>{s.title}. </span>
                  {s.journal && <span>{s.journal}. </span>}
                  <span style={{ display: 'inline-flex', gap: '8px', flexWrap: 'wrap', marginTop: '2px' }}>
                    {s.pmid && (
                      <a href={`https://pubmed.ncbi.nlm.nih.gov/${s.pmid}`} target="_blank" rel="noreferrer"
                        style={{ color: '#3182ce', fontSize: '0.8rem' }}>
                        PMID: {s.pmid}
                      </a>
                    )}
                    {s.doi && (
                      <a href={`https://doi.org/${s.doi}`} target="_blank" rel="noreferrer"
                        style={{ color: '#3182ce', fontSize: '0.8rem' }}>
                        DOI: {s.doi}
                      </a>
                    )}
                    {s.pmcid && (
                      <a href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${s.pmcid}`} target="_blank" rel="noreferrer"
                        style={{ color: '#3182ce', fontSize: '0.8rem' }}>
                        {s.pmcid}
                      </a>
                    )}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <Disclaimer />
      </div>
    </div>
  )
}
