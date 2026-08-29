import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, AlertCircle, Calendar, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const History = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setError("You must be logged in to view your history.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/reports`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setHistory(response.data || []);
      } catch (err) {
        if (err.response && err.response.status === 401) {
          setError("Your session has expired. Please log in again.");
          localStorage.removeItem('token');
          window.dispatchEvent(new Event('auth-change'));
        } else {
          setError("Failed to load history. Please try again later.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="pt-24 pb-12 flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] px-4 sm:px-6 lg:px-8 py-12 max-w-[1200px] mx-auto">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Your Validation History</h1>
        <p className="text-slate-400 max-w-2xl mx-auto">Review your previously validated startup ideas and their comprehensive insights.</p>
      </div>

      {error ? (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl text-center max-w-lg mx-auto backdrop-blur-sm">
          <AlertCircle className="w-10 h-10 mx-auto mb-3" />
          <p className="font-medium">{error}</p>
          <button 
            onClick={() => navigate('/login')}
            className="mt-4 px-6 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors"
          >
            Go to Login
          </button>
        </div>
      ) : history.length === 0 ? (
        <div className="bg-[#070b14]/50 border border-white/10 p-12 text-center rounded-3xl max-w-2xl mx-auto backdrop-blur-sm">
          <Clock className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No history yet</h3>
          <p className="text-slate-400 mb-6">You haven't validated any startup ideas yet.</p>
          <button 
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)]"
          >
            Validate an Idea
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {history.map((item, index) => (
            <motion.div 
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => navigate(`/report/${item.id}`)}
              className="group bg-[#0a0f1e]/80 border border-white/5 hover:border-blue-500/30 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 cursor-pointer transition-all duration-300 shadow-lg hover:shadow-[0_0_30px_rgba(37,99,235,0.15)] backdrop-blur-sm"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border border-blue-500/20">
                    Startup Idea
                  </span>
                  <div className="flex items-center text-slate-500 text-sm">
                    <Calendar className="w-4 h-4 mr-1.5" />
                    {new Date(item.created_at).toLocaleDateString(undefined, {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </div>
                </div>
                <h3 className="text-lg md:text-xl font-semibold text-white line-clamp-2 leading-relaxed group-hover:text-blue-100 transition-colors">
                  {item.startup_idea}
                </h3>
              </div>
              
              <div className="flex items-center gap-6 mt-2 md:mt-0 pt-4 md:pt-0 border-t border-white/5 md:border-0">
                <div className="flex flex-col items-end">
                  <span className="text-xs text-slate-500 font-medium mb-1 uppercase tracking-wider">Score</span>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-3xl font-black ${
                      item.validation_score >= 80 ? 'text-emerald-400' : 
                      item.validation_score >= 50 ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {item.validation_score}
                    </span>
                    <span className="text-sm text-slate-500">/100</span>
                  </div>
                </div>
                
                <div className="w-12 h-12 rounded-full bg-white/5 group-hover:bg-blue-500/20 flex items-center justify-center transition-colors">
                  <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-blue-400 transition-colors group-hover:translate-x-1 duration-300" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
