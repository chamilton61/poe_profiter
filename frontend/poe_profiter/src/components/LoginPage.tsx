import { useState } from 'react';
import './LoginPage.css';

interface LoginPageProps {
  onLogin: () => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  function handleLogin() {
    if (username && password) {
      setError(false);
      onLogin();
    } else {
      setError(true);
    }
  }

  return (
    <div className="login-page">
      <div className="login-orb">⚗</div>
      <div className="login-title">PoE Profiter</div>
      <div className="login-subtitle">Trade Intelligence System</div>
      <div className="login-card">
        <div className="form-group">
          <label className="form-label">Username</label>
          <input
            className="form-input"
            type="text"
            placeholder="Exile"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Password</label>
          <input
            className="form-input"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
          />
        </div>
        <button className="login-btn" onClick={handleLogin}>
          Enter the League
        </button>
        {error && (
          <div className="login-error">Invalid credentials. Try again.</div>
        )}
      </div>
    </div>
  );
}
