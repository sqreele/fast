'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';

interface LoginFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function LoginForm({ onSuccess, onError }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const result = await signIn('credentials', {
        username: formData.username,
        password: formData.password,
        redirect: false
      });

      if (result?.error) {
        setError('Invalid credentials. Please try again.');
        onError?.(result.error);
      } else {
        onSuccess?.();
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      onError?.(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="auth-container">
      <div className="auth-header">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Sign in to your PM System account</p>
      </div>

      {error && (
        <div className="auth-error">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-group">
          <label htmlFor="username" className="form-label">
            Username
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            className="form-input"
            placeholder="Enter your username"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            className="form-input"
            placeholder="Enter your password"
            required
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          className={`btn-auth btn-primary ${isLoading ? 'btn-loading' : ''}`}
          disabled={isLoading}
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}