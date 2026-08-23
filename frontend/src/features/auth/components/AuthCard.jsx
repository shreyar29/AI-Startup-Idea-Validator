import React from 'react';
import { motion } from 'framer-motion';
import { Layers } from 'lucide-react';

export const AuthCard = ({ title, subtitle, error, children }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-8 md:p-12 rounded-3xl w-full max-w-md"
      role="region"
      aria-label={title}
    >
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center bg-primary/10 p-3 rounded-2xl mb-4" aria-hidden="true">
          <Layers className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-3xl font-bold text-textMain tracking-tight mb-2">{title}</h2>
        <p className="text-textMuted text-sm">{subtitle}</p>
      </div>

      {error && (
        <div 
          className="mb-6 p-3 bg-red-500/10 border border-red-500/20 text-red-500 rounded-lg text-sm text-center"
          role="alert"
          aria-live="assertive"
        >
          {error}
        </div>
      )}

      {children}
    </motion.div>
  );
};
