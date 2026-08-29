import React, { useState, useId } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export const AuthInput = ({ label, type = 'text', value, onChange, placeholder, required = true, rightElement }) => {
  const [showPassword, setShowPassword] = useState(false);
  const inputId = useId();
  const isPassword = type === 'password';

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-300">
          {label}
        </label>
        {rightElement}
      </div>
      <div className="relative">
        <input 
          id={inputId}
          type={isPassword ? (showPassword ? 'text' : 'password') : type} 
          value={value}
          onChange={onChange}
          required={required}
          className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-textMain focus:ring-2 focus:ring-primary focus:border-primary transition-all pr-12" 
          placeholder={placeholder}
          aria-required={required}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        )}
      </div>
    </div>
  );
};
