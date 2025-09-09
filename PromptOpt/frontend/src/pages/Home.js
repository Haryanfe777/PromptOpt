import React from 'react';
import Placeholder from '../components/Placeholder';
import ChatDemo from '../components/ChatDemo';

export default function Home() {
  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <Placeholder text="Welcome to the Prompt Optimization Toolkit!" />
      <ChatDemo />
    </div>
  );
}
