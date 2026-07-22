import { useEffect, useState } from 'react'

// Bare-bones starting shell. This screen's only job is to prove the full
// chain works — React talks to FastAPI, FastAPI talks to Supabase — before
// any real proposal UI gets built. It calls the backend's /db-check
// endpoint and shows what comes back.

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/db-check`)
      .then((res) => {
        if (!res.ok) throw new Error(`Backend responded with ${res.status}`)
        return res.json()
      })
      .then(setResult)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem', maxWidth: 600 }}>
      <h1>DTS Proposals</h1>
      <p>Connectivity check — frontend → backend → Supabase.</p>

      {error && (
        <p style={{ color: 'crimson' }}>
          Could not reach the backend at {API_URL}: {error}
          <br />
          Make sure the FastAPI server is running (see backend/README.md).
        </p>
      )}

      {result && (
        <div>
          <p style={{ color: 'green' }}>
            Connected — {result.table_count} tables found in Supabase.
          </p>
          <ul>
            {result.tables.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
      )}

      {!result && !error && <p>Checking connection…</p>}
    </div>
  )
}

export default App
