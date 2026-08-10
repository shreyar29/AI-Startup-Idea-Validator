import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, AlertCircle, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const History = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        setError("You must be logged in to view your history.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')}/api/history/${userId}`);
        setHistory(response.data.history || []);
      } catch (err) {
        setError("Failed to load history. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="pt-24 pb-12 flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] px-4 sm:px-6 lg:px-8 py-12 max-w-[1200px] mx-auto">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-textMain mb-4">Your Validation History</h1>
        <p className="text-textMuted max-w-2xl mx-auto">Review your previously validated startup ideas and their comprehensive insights.</p>
      </div>

      {error ? (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-6 rounded-2xl text-center max-w-lg mx-auto">
          <AlertCircle className="w-10 h-10 mx-auto mb-3" />
          <p className="font-medium">{error}</p>
        </div>
      ) : history.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-3xl max-w-2xl mx-auto">
          <Clock className="w-16 h-16 text-textMuted/50 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-textMain mb-2">No history yet</h3>
          <p className="text-textMuted">You haven't validated any startup ideas yet. Head over to the dashboard to get started!</p>
        </div>
      ) : (
        <div className="space-y-6">
          {history.map((item, index) => (
            <motion.div 
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-primary/30 transition-all duration-300"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    Idea
                  </span>
                  <div className="flex items-center text-textMuted text-sm">
                    <Calendar className="w-4 h-4 mr-1" />
                    {new Date(item.created_at).toLocaleDateString()}
                  </div>
                </div>
                <h3 className="text-lg font-bold text-textMain line-clamp-2">{item.prompt}</h3>
              </div>
              <div className="flex flex-col sm:flex-row items-center gap-4 mt-4 md:mt-0">
                <div className="flex flex-col items-end w-full sm:w-auto">
                  <span className="text-xs text-textMuted mb-1">Validation Score</span>
                  <span className="text-lg font-bold text-primary">
                    {item.response_data?.final_evaluation?.validation_score || "N/A"}/100
                  </span>
                </div>
                <button 
                  onClick={() => navigate('/dashboard', { state: { idea: item.prompt, result: item.response_data } })}
                  className="w-full sm:w-auto px-4 py-2 bg-surface/50 hover:bg-surface border border-border/50 text-textMain font-medium rounded-lg transition-colors text-sm"
                >
                  View Details
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
