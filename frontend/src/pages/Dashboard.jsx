import React from 'react';
import { useLocation, Navigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle2, AlertTriangle, TrendingUp, Users, Target, ShieldCheck } from 'lucide-react';

const Dashboard = () => {
  const location = useLocation();
  const data = location.state?.resultData;

  if (!data) {
    return <Navigate to="/validate" replace />;
  }

  // Handle error status gracefully
  if (data.metadata?.status === 'error' || data.error) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <div className="glass-panel p-8 rounded-2xl max-w-lg text-center">
          <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Validation Failed</h2>
          <p className="text-textMuted mb-6">{data.error || 'An unexpected error occurred in the mesh network.'}</p>
          <Link to="/validate" className="bg-surface border border-white/10 px-6 py-2 rounded-full hover:bg-white/5 transition-colors">
            Try Again
          </Link>
        </div>
      </div>
    );
  }

  const { market_agent, customer_agent, competitor_agent, comparison_agent, metadata } = data;

  const score = data.final_evaluation?.validation_score || 0;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <Link to="/validate" className="inline-flex items-center text-textMuted hover:text-white transition-colors mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          New Validation
        </Link>
        
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">Validation Results</h1>
            <p className="text-lg text-textMuted">Idea: <span className="text-white">"{metadata?.startup_idea}"</span></p>
          </div>
          <div className="flex items-center space-x-3 glass-panel px-4 py-2 rounded-xl">
            <ShieldCheck className="h-5 w-5 text-secondary" />
            <span className="text-sm font-medium">Executed in {metadata?.execution_time_seconds}s</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Score Card */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-1 glass-panel rounded-3xl p-8 flex flex-col items-center justify-center text-center relative overflow-hidden"
        >
          <div className={`absolute top-0 w-full h-2 ${score >= 70 ? 'bg-secondary' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`} />
          <h3 className="text-xl font-semibold mb-2">Viability Score</h3>
          <div className="relative w-40 h-40 flex items-center justify-center my-6">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="80" cy="80" r="70" className="stroke-white/10" strokeWidth="12" fill="none" />
              <circle 
                cx="80" cy="80" r="70" 
                className={`stroke-current ${score >= 70 ? 'text-secondary' : score >= 40 ? 'text-yellow-500' : 'text-red-500'}`} 
                strokeWidth="12" fill="none" strokeDasharray="440" 
                strokeDashoffset={440 - (440 * score) / 100}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-5xl font-bold">{score}</span>
          </div>
          <p className="text-textMuted text-sm">
            Based on market size, competition, and customer pain points.
          </p>
        </motion.div>

        {/* Market Analysis */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-2 glass-panel rounded-3xl p-8"
        >
          <div className="flex items-center space-x-3 mb-6 border-b border-white/5 pb-4">
            <TrendingUp className="h-6 w-6 text-primary" />
            <h2 className="text-2xl font-bold">Market Analysis</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-surface/50 p-5 rounded-2xl border border-white/5">
              <h4 className="text-sm text-textMuted uppercase tracking-wider mb-2">Market Size</h4>
              <p className="text-lg font-medium">{market_agent?.market_size || 'N/A'}</p>
            </div>
            <div className="bg-surface/50 p-5 rounded-2xl border border-white/5">
              <h4 className="text-sm text-textMuted uppercase tracking-wider mb-2">Growth Rate</h4>
              <p className="text-lg font-medium text-secondary">{market_agent?.growth_rate || 'N/A'}</p>
            </div>
            <div className="md:col-span-2 bg-surface/50 p-5 rounded-2xl border border-white/5">
              <h4 className="text-sm text-textMuted uppercase tracking-wider mb-3">Market Trends</h4>
              <ul className="space-y-2">
                {Array.isArray(market_agent?.market_trends) 
                  ? market_agent.market_trends.map((trend, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-primary mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-300">{trend}</span>
                    </li>
                  ))
                  : <li className="text-gray-300">{market_agent?.market_trends || 'No trends available.'}</li>
                }
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Customer Segments */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-1 glass-panel rounded-3xl p-8"
        >
          <div className="flex items-center space-x-3 mb-6 border-b border-white/5 pb-4">
            <Users className="h-6 w-6 text-accent" />
            <h2 className="text-xl font-bold">Target Customers</h2>
          </div>
          
          <div className="space-y-6">
            <div>
              <h4 className="text-sm text-textMuted uppercase tracking-wider mb-3">Segments</h4>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(customer_agent?.target_customer_segments)
                  ? customer_agent.target_customer_segments.map((seg, i) => (
                    <span key={i} className="bg-accent/10 border border-accent/20 text-accent px-3 py-1 rounded-full text-sm">
                      {seg}
                    </span>
                  ))
                  : <span className="text-gray-300">{customer_agent?.target_customer_segments || 'N/A'}</span>
                }
              </div>
            </div>
            
            <div>
              <h4 className="text-sm text-textMuted uppercase tracking-wider mb-3">Pain Points</h4>
              <ul className="space-y-2">
                {Array.isArray(customer_agent?.pain_points)
                  ? customer_agent.pain_points.map((point, i) => (
                    <li key={i} className="flex items-start text-sm text-gray-300">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-400 mt-2 mr-2 flex-shrink-0"></span>
                      {point}
                    </li>
                  ))
                  : <li className="text-sm text-gray-300">{customer_agent?.pain_points || 'N/A'}</li>
                }
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Competitor Analysis */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-panel rounded-3xl p-8"
        >
          <div className="flex items-center space-x-3 mb-6 border-b border-white/5 pb-4">
            <Target className="h-6 w-6 text-red-400" />
            <h2 className="text-2xl font-bold">Competitor Landscape</h2>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Array.isArray(competitor_agent?.competitors) && competitor_agent.competitors.length > 0 ? (
              competitor_agent.competitors.map((comp, idx) => (
                <div key={idx} className="bg-surface/50 p-5 rounded-2xl border border-white/5 hover:border-white/20 transition-colors">
                  <h3 className="font-semibold text-lg mb-1">{comp.name || 'Unknown Competitor'}</h3>
                  <p className="text-sm text-textMuted mb-3">{comp.source_references?.[0] || 'No URL'}</p>
                  <div className="text-sm">
                    <span className="text-red-400 font-medium">Weakness: </span>
                    <span className="text-gray-300">{comp.weaknesses?.[0] || 'Not identified'}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-2 text-center text-textMuted py-8">
                No direct competitors identified or data unavailable.
              </div>
            )}
          </div>
          
          {/* Feature Comparison */}
          {comparison_agent?.feature_comparison && (
            <div className="mt-8 pt-6 border-t border-white/5">
              <h4 className="text-sm text-textMuted uppercase tracking-wider mb-4">Feature Comparison Matrix</h4>
              <div className="bg-surface/30 p-4 rounded-xl text-sm text-gray-300 overflow-x-auto whitespace-pre-wrap">
                {typeof comparison_agent.feature_comparison === 'string' 
                  ? comparison_agent.feature_comparison 
                  : JSON.stringify(comparison_agent.feature_comparison, null, 2)}
              </div>
            </div>
          )}
        </motion.div>

      </div>
    </div>
  );
};

export default Dashboard;
