import React from 'react';
import Home from './pages/Home';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <div>
        <h1>Prompt Optimization Toolkit</h1>
        <Home />
      </div>
    </AuthProvider>
  );
}

export default App;
