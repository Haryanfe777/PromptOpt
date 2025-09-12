import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../config';
import Toast from './Toast';

export default function ChatDemo() {
  const { token } = useAuth();
  const [message, setMessage] = useState('');
  const [evaluate, setEvaluate] = useState(true);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [note, setNote] = useState('');

  const send = async () => {
    setLoading(true);
    setError('');
    setNote('');
    setResponse(null);
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({
          message,
          prompt_id: null,
          conversation_history: [],
          evaluate,
        }),
      });
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }
      const data = await res.json();
      setResponse(data);
      setNote('Message sent successfully.');
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 8 }}>
      <h3>Chat Demo (with Evaluation & Guardrails)</h3>
      <div style={{ marginBottom: 8 }}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask an HR question..."
          rows={4}
          style={{ width: '100%' }}
        />
      </div>
      <label style={{ display: 'block', marginBottom: 8 }}>
        <input type="checkbox" checked={evaluate} onChange={(e) => setEvaluate(e.target.checked)} />
        {' '}Evaluate response
      </label>
      <button onClick={send} disabled={loading || !message.trim()}>
        {loading ? 'Sending...' : 'Send'}
      </button>

      {error && (
        <div style={{ color: 'red', marginTop: 12 }}>Error: {error}</div>
      )}
      {note && (
        <div style={{ marginTop: 12 }}><Toast kind="success" message={note} /></div>
      )}

      {response && (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 8 }}>
            <strong>Assistant:</strong>
            <div style={{ whiteSpace: 'pre-wrap' }}>{response.response}</div>
          </div>

          {response.provenance && (
            <div style={{ marginBottom: 8 }}>
              <strong>Provenance:</strong>
              <ul>
                {response.provenance.map((p, i) => (
                  <li key={i}><em>{p.source || 'doc'}</em>: {p.text}</li>
                ))}
              </ul>
            </div>
          )}

          {response.guardrails && (
            <div style={{ marginBottom: 8 }}>
              <strong>Guardrails:</strong>
              <div>Action: {response.guardrails.action}</div>
              {response.guardrails.message && <div>Note: {response.guardrails.message}</div>}
              {response.guardrails.contains_pii && <div>PII detected</div>}
              {response.guardrails.contains_profanity && <div>Profanity detected</div>}
              {response.guardrails.prompt_injection_suspected && <div>Prompt injection suspected</div>}
              {response.guardrails.contains_sensitive_topics && <div>Sensitive topics detected</div>}
            </div>
          )}

          {response.evaluation && (
            <div>
              <strong>Evaluation:</strong>
              <div>Overall: {response.evaluation.overall_score?.toFixed?.(2)}</div>
              <div>Helpfulness: {response.evaluation.criteria?.helpfulness}</div>
              <div>Accuracy: {response.evaluation.criteria?.accuracy}</div>
              <div>Clarity: {response.evaluation.criteria?.clarity}</div>
              <div>Safety: {response.evaluation.criteria?.safety}</div>
              <div>Relevance: {response.evaluation.criteria?.relevance}</div>
              <div>Tone: {response.evaluation.criteria?.tone}</div>
              <div>Label: {response.evaluation.label}</div>
              {response.evaluation.comments && (
                <div>Comments: {response.evaluation.comments}</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
