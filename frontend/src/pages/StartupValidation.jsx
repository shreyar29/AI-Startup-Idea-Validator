import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, AlertCircle, Search } from 'lucide-react';
import { validateIdea } from '../services/api';

const StartupValidation = () => {
  const [idea, setIdea] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (idea.length < 10) {
      setError('Please provide a more detailed idea (at least 10 characters).');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await validateIdea(idea);
      // Pass data to dashboard
      navigate('/dashboard', { state: { resultData: data } });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || 'An error occurred during validation. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="absolute top-0 inset-x-0 h-64 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-3xl glass-panel p-8 md:p-12 rounded-3xl relative z-10"
      >
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-6">
            <Sparkles className="h-8 w-8 text-primary" />
          </div>
          <h2 className="text-3xl md:text-5xl font-bold mb-4">Validate Your Idea</h2>
          <p className="text-lg text-textMuted">Describe your startup idea. Our AI agents will do the rest.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 pt-4 pointer-events-none">
              <Search className="h-6 w-6 text-textMuted" />
            </div>
            <textarea
              value={idea}
              onChange={(e) => {
                setIdea(e.target.value);
                if (error) setError(null);
              }}
              disabled={isLoading}
              className={`w-full h-40 pl-12 pr-4 py-4 bg-surface/50 border ${error ? 'border-red-500' : 'border-white/10'} focus:border-primary focus:ring-1 focus:ring-primary rounded-2xl text-white placeholder-textMuted resize-none transition-all`}
              placeholder="e.g., An AI-powered smart parking app that helps drivers find available spots in crowded cities using real-time camera feeds..."
            />
          </div>

          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }} 
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-2 text-red-400 bg-red-400/10 p-4 rounded-xl"
            >
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </motion.div>
          )}

          <button
            type="submit"
            disabled={isLoading || !idea.trim()}
            className="w-full relative group flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-200 bg-primary rounded-2xl hover:bg-primaryDark disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
          >
            {isLoading ? (
              <span className="flex items-center space-x-3">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Analyzing Mesh... (Takes 1-3 mins)</span>
              </span>
            ) : (
              <span className="flex items-center">
                Launch Validation
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </span>
            )}
            
            {/* Loading Progress Bar simulation */}
            {isLoading && (
              <div className="absolute bottom-0 left-0 h-1 bg-white/30 w-full overflow-hidden">
                <div className="h-full bg-white animate-[indeterminate_2s_infinite]" />
              </div>
            )}
          </button>
        </form>
      </motion.div>
    </div>
  );
};

export default StartupValidation;
