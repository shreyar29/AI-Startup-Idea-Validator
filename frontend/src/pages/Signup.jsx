import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from '../features/auth/components/AuthLayout';
import { AuthCard } from '../features/auth/components/AuthCard';
import { AuthInput } from '../features/auth/components/AuthInput';
import { AuthButton } from '../features/auth/components/AuthButton';
import { authService } from '../features/auth/services/authService';

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!name || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address.');
      return;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);
    try {
      await authService.signup(name, email, password);
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
        title="Create Account" 
        subtitle="Join VentureLens to save and track your startup validations."
        error={error}
      >
        <form onSubmit={handleSignup} className="space-y-6" noValidate>
          <AuthInput
            label="Full Name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Jane Doe"
          />
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
          />
          <AuthButton isLoading={isLoading}>
            Create Account
          </AuthButton>
        </form>

        <div className="mt-8 text-center text-sm text-textMuted">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:text-primary/80 font-medium transition-colors">
            Log in here
          </Link>
        </div>
      </AuthCard>
    </AuthLayout>
  );
};

export default Signup;
