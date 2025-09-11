import React, { useEffect, useMemo, useState } from 'react';
import { API_BASE } from '../config';
import { useAuth } from '../context/AuthContext';

function diffStrings(a, b) {
  // very simple inline diff: marks lines added/removed
  const aLines = String(a || '').split('\n');
  const bLines = String(b || '').split('\n');
  const max = Math.max(aLines.length, bLines.length);
  const out = [];
  for (let i = 0; i < max; i++) {
    const L = aLines[i] ?? '';
    const R = bLines[i] ?? '';
    if (L === R) out.push(`  ${R}`);
    else if (L && !R) out.push(`- ${L}`);
    else if (!L && R) out.push(`+ ${R}`);
    else out.push(`~ ${R}`);
  }
  return out.join('\n');
}

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
  const [editTitle, setEditTitle] = useState('');

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
  useEffect(() => { if (selected) { setEditTitle(selected.title); loadVersions(selected.id); } }, [selected, token]);

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

  const renamePrompt = async () => {
    if (!selected) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/prompts/${selected.id}/title`, { method: 'PATCH', headers, body: JSON.stringify({ title: editTitle }) });
      if (!res.ok) throw new Error('Rename failed');
      await loadPrompts();
      setSelected((prev) => prev ? { ...prev, title: editTitle } : prev);
    } catch (e) { setError(String(e.message || e)); } finally { setLoading(false); }
  };

  const deletePrompt = async () => {
    if (!selected) return;
    if (!confirm('Delete this prompt and all versions?')) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/prompts/${selected.id}`, { method: 'DELETE', headers: token ? { Authorization: `Bearer ${token}` } : {} });
      if (!res.ok) throw new Error('Delete failed');
      setSelected(null);
      setVersions([]);
      await loadPrompts();
    } catch (e) { setError(String(e.message || e)); } finally { setLoading(false); }
  };

  const active = versions.find(v => v.is_active);

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
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
                <input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                <button onClick={renamePrompt} disabled={loading || !editTitle || editTitle === selected.title}>Save title</button>
                <button onClick={deletePrompt} disabled={loading}>Delete prompt</button>
              </div>
              <div style={{ marginBottom: 8 }}>
                <textarea placeholder="New version content" value={content} onChange={(e) => setContent(e.target.value)} rows={6} style={{ width: '100%' }} />
                <button onClick={updatePrompt} disabled={loading || !content}>Save as new version</button>
              </div>
              {active && (
                <div style={{ marginBottom: 8 }}>
                  <strong>Diff vs active (approximate):</strong>
                  <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: 8 }}>{diffStrings(active.content, content)}</pre>
                </div>
              )}
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
