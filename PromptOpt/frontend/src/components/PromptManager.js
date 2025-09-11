import React, { useEffect, useMemo, useState } from 'react';
import { API_BASE } from '../config';
import { useAuth } from '../context/AuthContext';

export default function PromptManager() {
  const { token, user } = useAuth();
  const headers = useMemo(() => ({ 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }), [token]);
  const [prompts, setPrompts] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selected, setSelected] = useState(null);
  const [versions, setVersions] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const loadPrompts = async () => {
    try {
      const res = await fetch(`${API_BASE}/prompts`);
      if (!res.ok) throw new Error('Failed to load prompts');
      setPrompts(await res.json());
    } catch (e) { setError(String(e.message || e)); }
  };

  const loadVersions = async (promptId) => {
    setVersions([]);
    if (!promptId) return;
    try {
      const res = await fetch(`${API_BASE}/prompts/${promptId}/versions`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
      if (!res.ok) throw new Error('Failed to load versions');
      setVersions(await res.json());
    } catch (e) { setError(String(e.message || e)); }
  };

  useEffect(() => { loadPrompts(); }, []);
  useEffect(() => { if (selected) loadVersions(selected.id); }, [selected, token]);

  const createPrompt = async () => {
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/prompts`, { method: 'POST', headers, body: JSON.stringify({ title, content, created_by: user?.username || 'admin' }) });
      if (!res.ok) throw new Error('Create failed');
      setTitle(''); setContent('');
      await loadPrompts();
    } catch (e) { setError(String(e.message || e)); } finally { setLoading(false); }
  };

  const updatePrompt = async () => {
    if (!selected) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/prompts/${selected.id}`, { method: 'PUT', headers, body: JSON.stringify({ id: selected.id, title: selected.title, content, created_by: selected.created_by }) });
      if (!res.ok) throw new Error('Update failed');
      setContent('');
      await loadPrompts();
      await loadVersions(selected.id);
    } catch (e) { setError(String(e.message || e)); } finally { setLoading(false); }
  };

  const activateVersion = async (v) => {
    if (!selected) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/prompts/${selected.id}/activate/${v.version}`, { method: 'POST', headers: token ? { Authorization: `Bearer ${token}` } : {} });
      if (!res.ok) throw new Error('Activate failed');
      await loadVersions(selected.id);
    } catch (e) { setError(String(e.message || e)); } finally { setLoading(false); }
  };

  const isAdmin = user?.role === 'admin';
  if (!isAdmin) return null;

  return (
    <div style={{ border: '1px solid #ccc', padding: 16, borderRadius: 8 }}>
      <h3>Prompt Manager (Admin)</h3>
      {error && <div style={{ color: 'red', marginBottom: 8 }}>{error}</div>}
      <div style={{ display: 'grid', gap: 8, gridTemplateColumns: '1fr 2fr', alignItems: 'start' }}>
        <div>
          <h4>Prompts</h4>
          <ul>
            {prompts.map((p) => (
              <li key={p.id}>
                <button onClick={() => setSelected(p)} style={{ marginRight: 8 }}>{p.title}</button>
              </li>
            ))}
          </ul>
          <div style={{ marginTop: 12 }}>
            <h4>Create new</h4>
            <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} rows={6} style={{ width: '100%', display: 'block', marginTop: 4 }} />
            <button onClick={createPrompt} disabled={loading || !title || !content}>Create</button>
          </div>
        </div>
        <div>
          <h4>Versions {selected ? `for: ${selected.title}` : ''}</h4>
          {!selected && <div>Select a prompt to manage versions.</div>}
          {selected && (
            <div>
              <div style={{ marginBottom: 8 }}>
                <textarea placeholder="New version content" value={content} onChange={(e) => setContent(e.target.value)} rows={6} style={{ width: '100%' }} />
                <button onClick={updatePrompt} disabled={loading || !content}>Save as new version</button>
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left' }}>Version</th>
                    <th style={{ textAlign: 'left' }}>Active</th>
                    <th style={{ textAlign: 'left' }}>Created</th>
                    <th style={{ textAlign: 'left' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {versions.map((v) => (
                    <tr key={v.id}>
                      <td>{v.version}</td>
                      <td>{v.is_active ? 'Yes' : 'No'}</td>
                      <td>{v.created_at || ''}</td>
                      <td>
                        {!v.is_active && <button onClick={() => activateVersion(v)}>Activate</button>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
