import React, { useState } from 'react';

export default function ChatDemo() {
  const [message, setMessage] = useState('');
  const [evaluate, setEvaluate] = useState(true);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const send = async () => {
    setLoading(true);
    setError('');
    setResponse(null);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          user_id: 'demo-user',
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

      {response && (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 8 }}>
            <strong>Assistant:</strong>
            <div style={{ whiteSpace: 'pre-wrap' }}>{response.response}</div>
          </div>

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
