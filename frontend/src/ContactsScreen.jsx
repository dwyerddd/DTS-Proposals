import { useEffect, useState } from 'react'
import { companiesApi, contactsApi } from './api'

const emptyForm = {
  company_id: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  position: '',
  notes: '',
}

function ContactsScreen() {
  const [contacts, setContacts] = useState([])
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [companyFilter, setCompanyFilter] = useState('')
  const [showArchived, setShowArchived] = useState(false)

  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  // Load the companies dropdown once — used both as a filter and in the form.
  useEffect(() => {
    companiesApi.list({}).then(setCompanies).catch((err) => setError(err.message))
  }, [])

  function load() {
    setLoading(true)
    setError(null)
    contactsApi
      .list({ search, company_id: companyFilter || undefined, include_archived: showArchived })
      .then(setContacts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [search, companyFilter, showArchived])

  function startNew() {
    setEditing({ id: null })
    setForm(emptyForm)
  }

  function startEdit(contact) {
    setEditing(contact)
    setForm({
      company_id: contact.company_id || '',
      first_name: contact.first_name || '',
      last_name: contact.last_name || '',
      email: contact.email || '',
      phone: contact.phone || '',
      position: contact.position || '',
      notes: contact.notes || '',
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
    const payload = {
      ...form,
      company_id: form.company_id ? Number(form.company_id) : null,
    }
    try {
      if (editing.id) {
        await contactsApi.update(editing.id, payload)
      } else {
        await contactsApi.create(payload)
      }
      cancelEdit()
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function toggleArchive(contact) {
    setError(null)
    try {
      if (contact.active) {
        await contactsApi.archive(contact.id)
      } else {
        await contactsApi.restore(contact.id)
      }
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2>Contacts</h2>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <input
          placeholder="Search by surname or first name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: '0.4rem', flex: 1, minWidth: 200 }}
        />
        <select value={companyFilter} onChange={(e) => setCompanyFilter(e.target.value)}>
          <option value="">All companies</option>
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <label style={{ whiteSpace: 'nowrap' }}>
          <input
            type="checkbox"
            checked={showArchived}
            onChange={(e) => setShowArchived(e.target.checked)}
          />{' '}
          Show archived
        </label>
        <button onClick={startNew}>+ New contact</button>
      </div>

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {editing && (
        <form
          onSubmit={save}
          style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}
        >
          <h3>{editing.id ? 'Edit contact' : 'New contact'}</h3>
          <div style={{ display: 'grid', gap: '0.5rem', maxWidth: 400 }}>
            <label>
              Company (optional — leave blank for an individual client)
              <select
                value={form.company_id}
                onChange={(e) => setForm({ ...form, company_id: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              >
                <option value="">— none —</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              First name *
              <input
                required
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              Last name *
              <input
                required
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              Phone
              <input
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                style={{ width: '100%', padding: '0.3rem' }}
              />
            </label>
            <label>
              Position / title
              <input
                value={form.position}
                onChange={(e) => setForm({ ...form, position: e.target.value })}
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
      ) : contacts.length === 0 ? (
        <p>No contacts found.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid #ccc' }}>
              <th>Name</th>
              <th>Company</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {contacts.map((c) => (
              <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
                <td>
                  {c.first_name} {c.last_name}
                </td>
                <td>{c.company_name || '—'}</td>
                <td>{c.email}</td>
                <td>{c.phone}</td>
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

export default ContactsScreen
