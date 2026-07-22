import { useEffect, useState } from 'react'
import { companiesApi } from './api'

const emptyForm = { name: '', abn: '', address: '', notes: '' }

function CompaniesScreen() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [showArchived, setShowArchived] = useState(false)

  // null = form closed; otherwise the company being edited, or emptyForm for "new"
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  function load() {
    setLoading(true)
    setError(null)
    companiesApi
      .list({ search, include_archived: showArchived })
      .then(setCompanies)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [search, showArchived])

  function startNew() {
    setEditing({ id: null })
    setForm(emptyForm)
  }

  function startEdit(company) {
    setEditing(company)
    setForm({
      name: company.name || '',
      abn: company.abn || '',
      address: company.address || '',
      notes: company.notes || '',
    })
  }

  function cancelEdit() {
    setEditing(null)
    setForm(emptyForm)
  }

  async function save(e) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      if (editing.id) {
        await companiesApi.update(editing.id, form)
      } else {
        await companiesApi.create(form)
      }
      cancelEdit()
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function toggleArchive(company) {
    setError(null)
    try {
      if (company.active) {
        await companiesApi.archive(company.id)
      } else {
        await companiesApi.restore(company.id)
      }
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2>Companies</h2>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
        <input
          placeholder="Search by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: '0.4rem', flex: 1 }}
        />
        <label style={{ whiteSpace: 'nowrap' }}>
          <input
            type="checkbox"
            checked={showArchived}
            onChange={(e) => setShowArchived(e.target.checked)}
          />{' '}
          Show archived
        </label>
        <button onClick={startNew}>+ New company</button>
      </div>

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {editing && (
        <form
          onSubmit={save}
          style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}
        >
          <h3>{editing.id ? 'Edit company' : 'New company'}</h3>
          <div style={{ display: 'grid', gap: '0.5rem', maxWidth: 400 }}>
            <label>
              Name *
              <input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              ABN
              <input
                value={form.abn}
                onChange={(e) => setForm({ ...form, abn: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              Address
              <input
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              Notes
              <textarea
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
          </div>
          <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
            <button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button type="button" onClick={cancelEdit}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : companies.length === 0 ? (
        <p>No companies found.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid #ccc' }}>
              <th>Name</th>
              <th>ABN</th>
              <th>Address</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {companies.map((c) => (
              <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
                <td>{c.name}</td>
                <td>{c.abn}</td>
                <td>{c.address}</td>
                <td>{c.active ? 'Active' : 'Archived'}</td>
                <td style={{ whiteSpace: 'nowrap' }}>
                  <button onClick={() => startEdit(c)}>Edit</button>{' '}
                  <button onClick={() => toggleArchive(c)}>
                    {c.active ? 'Archive' : 'Restore'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default CompaniesScreen
