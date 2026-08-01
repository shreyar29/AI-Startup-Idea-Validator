import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2, AlertTriangle, ShieldCheck, Activity, Users, Globe } from 'lucide-react';
import axios from 'axios';

export const ValidateStartup = () => {
  const [idea, setIdea] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleValidate = async (e) => {
    e.preventDefault();
    if (!idea.trim()) return;
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await axios.get(`http://localhost:8000/search?idea=${encodeURIComponent(idea)}`);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const hasRateLimitError = (data) => {
    if (!data) return false;
    const checkString = JSON.stringify(data).toLowerCase();
    return checkString.includes('status 429') || checkString.includes('rate limit') || checkString.includes('429');
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header Section */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
            AI Startup Validator (V2)
          </h1>
          <p className="text-slate-400 max-w-xl mx-auto">
            We are building this from scratch! Enter your startup idea below to trigger the multi-agent mesh network.
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleValidate} className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl backdrop-blur-sm">
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="E.g., An AI-powered platform that detects skin diseases using smartphone images..."
            className="w-full h-32 bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none"
            disabled={loading}
          />
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              disabled={loading || !idea.trim()}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white font-medium py-3 px-8 rounded-xl transition-colors flex items-center shadow-lg"
            >
              {loading ? (
                <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Validating...</>
              ) : (
                <><Search className="w-5 h-5 mr-2" /> Validate Idea</>
              )}
            </button>
          </div>
        </form>

        {/* Global Error State */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/50 p-4 rounded-xl flex items-start space-x-3 text-red-400">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold">System Error</h3>
              <p className="text-sm opacity-90">{error}</p>
            </div>
          </div>
        )}

        {/* Results Container */}
        {results && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            
            {/* Rate Limit Detection */}
            {hasRateLimitError(results) && (
              <div className="bg-yellow-900/20 border border-yellow-500/50 p-6 rounded-xl flex items-start space-x-4 text-yellow-500 shadow-lg">
                <AlertTriangle className="w-8 h-8 flex-shrink-0" />
                <div>
                  <h3 className="font-bold text-lg mb-1">OpenRouter API Rate Limit Hit (HTTP 429)</h3>
                  <p className="text-sm opacity-90 text-yellow-200">
                    Your backend agents successfully ran, but they were blocked by OpenRouter's free-tier rate limits. 
                    The agents gracefully returned fallback data (empty grids and 0 validation scores) rather than crashing. 
                    This is why the data below looks empty or inaccurate!
                  </p>
                </div>
              </div>
            )}

            {/* Metadata Panel */}
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 flex justify-between items-center">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">Analyzed Idea</p>
                <p className="font-medium text-blue-300">{results.metadata?.startup_idea}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">Execution Time</p>
                <p className="font-mono text-xl">{results.metadata?.execution_time_seconds}s</p>
              </div>
            </div>

            {/* Agent Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Web Search Agent */}
              <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
                <h3 className="text-lg font-bold flex items-center mb-4 text-emerald-400">
                  <Globe className="w-5 h-5 mr-2" /> Web Search Agent
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-slate-300">
                    <span className="font-bold text-slate-500">Competitors Found:</span> {results.web_search_agent?.search_results?.competitors?.length || 0}
                  </p>
                  <p className="text-sm text-slate-300">
                    <span className="font-bold text-slate-500">Market Data Pulled:</span> {results.web_search_agent?.search_results?.market_size?.length || 0}
                  </p>
                </div>
              </div>

              {/* Market Agent */}
              <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
                <h3 className="text-lg font-bold flex items-center mb-4 text-indigo-400">
                  <Activity className="w-5 h-5 mr-2" /> Market Agent
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Size:</span> {results.market_agent?.market_size}</p>
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Growth:</span> {results.market_agent?.growth_rate}</p>
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Summary:</span> {results.market_agent?.market_summary}</p>
                </div>
              </div>

              {/* Customer Agent */}
              <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
                <h3 className="text-lg font-bold flex items-center mb-4 text-orange-400">
                  <Users className="w-5 h-5 mr-2" /> Customer Agent
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Confidence:</span> {results.customer_agent?.customer_validation_metrics?.confidence}</p>
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Personas:</span> {results.customer_agent?.customer_personas?.length || 0}</p>
                </div>
              </div>

              {/* Final Synthesis Agent */}
              <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
                <h3 className="text-lg font-bold flex items-center mb-4 text-fuchsia-400">
                  <ShieldCheck className="w-5 h-5 mr-2" /> Final Evaluation
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Score:</span> {results.comparison_agent?.validation_score}/100</p>
                  <p className="text-sm text-slate-300"><span className="font-bold text-slate-500">Verdict:</span> {results.comparison_agent?.summary}</p>
                </div>
              </div>

            </div>

          </motion.div>
        )}
      </div>
    </div>
  );
};
