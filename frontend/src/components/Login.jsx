import React from 'react'

export default function Login({ error }) {
  const handleLogin = () => {
    window.location.href = '/auth/login'
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div style={{
        background: 'white', borderRadius: '16px', padding: '48px 40px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.15)', maxWidth: '420px', width: '100%', textAlign: 'center'
      }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#1a202c', marginBottom: '8px' }}>
          RareDisease LitMiner
        </h1>
        <p style={{ color: '#718096', marginBottom: '32px', fontSize: '0.95rem' }}>
          AI-powered scientific literature mining
        </p>

        {error && (
          <div style={{
            background: '#fff5f5', border: '1px solid #fed7d7', borderRadius: '8px',
            padding: '12px', marginBottom: '20px', color: '#c53030', fontSize: '0.875rem'
          }}>
            {error === 'unauthorized_domain'
              ? '⛔ Access restricted to @neurocrine.com and @soleno.life accounts.'
              : '❌ Login failed. Please try again.'}
          </div>
        )}

        <button
          onClick={handleLogin}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px',
            width: '100%', padding: '14px 24px', background: 'white',
            border: '2px solid #e2e8f0', borderRadius: '10px', cursor: 'pointer',
            fontSize: '1rem', fontWeight: 600, color: '#2d3748',
            transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
          }}
          onMouseOver={e => e.currentTarget.style.borderColor = '#4299e1'}
          onMouseOut={e => e.currentTarget.style.borderColor = '#e2e8f0'}
        >
          <img src="https://www.google.com/favicon.ico" width="20" height="20" alt="Google" />
          Sign in with Google
        </button>

        <p style={{ marginTop: '24px', fontSize: '0.8rem', color: '#a0aec0' }}>
          Access restricted to Neurocrine Biosciences and Soleno Therapeutics employees.
        </p>
      </div>
    </div>
  )
}
