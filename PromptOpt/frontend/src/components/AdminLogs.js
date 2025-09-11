import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../config';

export default function AdminLogs() {
  const { token, user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const run = async () => {
      setError('');
      try {
        const res = await fetch(`${API_BASE}/chat/logs`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) throw new Error(`Failed: ${res.status}`);
        const data = await res.json();
        setLogs(data.logs || []);
      } catch (e) {
        setError(String(e.message || e));
      }
    };
    if (token && user?.role === 'admin') run();
  }, [token, user]);

  if (!token || user?.role !== 'admin') return null;

  return (
    <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 8 }}>
      <h3>Recent Conversations (Admin)</h3>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>ID</th>
            <th style={{ textAlign: 'left' }}>User</th>
            <th style={{ textAlign: 'left' }}>Prompt Version</th>
            <th style={{ textAlign: 'left' }}>Started</th>
            <th style={{ textAlign: 'left' }}>Messages</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.id}>
              <td>{l.id}</td>
              <td>{l.user_id}</td>
              <td>{l.prompt_version_id || '-'}</td>
              <td>{l.started_at}</td>
              <td>{l.message_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
