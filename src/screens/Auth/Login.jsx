import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { login } from '../../api/auth';
import '../../styles/Auth.css';

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
      navigate('/home');
    } catch (err) {
      setError(
        err?.details?.detail ||
        err?.message ||
        'Invalid email or password.',
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="screen auth-screen">
      <div className="auth-blob" aria-hidden="true" />

      <div className="auth-content">
        <h1 className="auth-logo">
          Myntra <span className="auth-logo-accent">Identity</span>
        </h1>

        <p className="auth-subtitle">Welcome back — log in to continue</p>

        <div className="auth-card">
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label className="auth-label" htmlFor="login-email">
                Email
              </label>
              <input
                id="login-email"
                className="auth-input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="login-password">
                Password
              </label>
              <input
                id="login-password"
                className="auth-input"
                type="password"
                placeholder="Your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            {error && <div className="auth-error">{error}</div>}

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              <span>{loading ? 'Logging in…' : 'Log In'}</span>
              {!loading && <ArrowRight size={18} aria-hidden="true" />}
            </button>
          </form>
        </div>

        <p className="auth-footer">
          Don&apos;t have an account?{' '}
          <button
            type="button"
            className="auth-link"
            onClick={() => navigate('/signup')}
          >
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
}
