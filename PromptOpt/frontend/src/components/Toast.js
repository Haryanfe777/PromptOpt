import React from 'react';

export default function Toast({ kind = 'info', message = '' }) {
  if (!message) return null;
  const bg = kind === 'success' ? '#e6ffed' : kind === 'error' ? '#ffe6e6' : '#eef2ff';
  const color = '#333';
  return (
    <div style={{ background: bg, color, padding: 8, borderRadius: 6, border: '1px solid #ddd' }}>
      {message}
    </div>
  );
}
