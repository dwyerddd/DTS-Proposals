import { useEffect, useState } from 'react'
import CompaniesScreen from './CompaniesScreen'
import ContactsScreen from './ContactsScreen'

// Bare-bones tab switcher — no router needed yet for just three screens.
// The connectivity check stays as its own tab so it's still easy to
// confirm the backend/Supabase link is alive at a glance.

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function ConnectivityCheck() {
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
    <div>
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

const TABS = [
  { key: 'check', label: 'Connectivity check', render: () => <ConnectivityCheck /> },
  { key: 'companies', label: 'Companies', render: () => <CompaniesScreen /> },
  { key: 'contacts', label: 'Contacts', render: () => <ContactsScreen /> },
]

function App() {
  const [tab, setTab] = useState('companies')
  const active = TABS.find((t) => t.key === tab)

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem', maxWidth: 900 }}>
      <h1>DTS Proposals</h1>

      <nav style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid #ccc' }}>
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            style={{
              padding: '0.5rem 0',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              fontWeight: tab === t.key ? 'bold' : 'normal',
              borderBottom: tab === t.key ? '2px solid #333' : '2px solid transparent',
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {active.render()}
    </div>
  )
}

export default App
