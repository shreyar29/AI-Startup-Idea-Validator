import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { Layers } from 'lucide-react';
import axios from 'axios';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
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
    
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')}/api/auth/login`, {
        username: email,
        password: password
      });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('username', response.data.username);
      localStorage.setItem('user_id', response.data.user_id);
      window.dispatchEvent(new Event('auth-change'));
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel p-8 md:p-12 rounded-3xl w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center bg-primary/10 p-3 rounded-2xl mb-4">
            <Layers className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-3xl font-bold text-textMain tracking-tight mb-2">Welcome Back</h2>
          <p className="text-textMuted text-sm">Sign in to access your validated ideas.</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 text-red-500 rounded-lg text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-textMain focus:ring-2 focus:ring-primary focus:border-primary transition-all" 
              placeholder="you@example.com"
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-300">Password</label>
              <a href="#" className="text-xs text-primary hover:text-primary/80 transition-colors">Forgot password?</a>
            </div>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-textMain focus:ring-2 focus:ring-primary focus:border-primary transition-all" 
              placeholder="••••••••"
            />
          </div>
          <button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-background font-bold py-3.5 rounded-xl transition-all shadow-md hover:shadow-primary/20"
          >
            Sign In
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-textMuted">
          Don't have an account?{' '}
          <Link to="/signup" className="text-primary hover:text-primary/80 font-medium transition-colors">
            Sign up now
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
