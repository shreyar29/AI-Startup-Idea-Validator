import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from '../features/auth/components/AuthLayout';
import { AuthCard } from '../features/auth/components/AuthCard';
import { AuthInput } from '../features/auth/components/AuthInput';
import { AuthButton } from '../features/auth/components/AuthButton';
import { authService } from '../features/auth/services/authService';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    
    setIsLoading(true);
    try {
      await authService.login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <AuthCard 
        title="Welcome Back" 
        subtitle="Sign in to access your validated ideas."
        error={error}
      >
        <form onSubmit={handleLogin} className="space-y-6" noValidate>
          <AuthInput
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
          <AuthInput
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            rightElement={
              <a href="#" className="text-xs text-primary hover:text-primary/80 transition-colors">
                Forgot password?
              </a>
            }
          />
          <AuthButton isLoading={isLoading}>
            Sign In
          </AuthButton>
        </form>

        <div className="mt-8 text-center text-sm text-textMuted">
          Don't have an account?{' '}
          <Link to="/signup" className="text-primary hover:text-primary/80 font-medium transition-colors">
            Sign up now
          </Link>
        </div>
      </AuthCard>
    </AuthLayout>
  );
};

export default Login;
