import React from 'react';
import Placeholder from '../components/Placeholder';
import ChatDemo from '../components/ChatDemo';
import Login from '../components/Login';
import { useAuth } from '../context/AuthContext';
import AdminLogs from '../components/AdminLogs';
import PromptManager from '../components/PromptManager';

export default function Home() {
  const { token, user, logout } = useAuth();
  const isAdmin = user?.role === 'admin';
  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <Placeholder text="Welcome to the Prompt Optimization Toolkit!" />
      {!token ? (
        <Login />
      ) : (
        <div>
          <div style={{ marginBottom: 8 }}>
            Signed in as <strong>{user?.username}</strong>
            <button style={{ marginLeft: 8 }} onClick={logout}>Sign out</button>
          </div>
          <ChatDemo />
          {isAdmin && (
            <div style={{ marginTop: 16 }}>
              <PromptManager />
              <div style={{ marginTop: 16 }}>
                <AdminLogs />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
