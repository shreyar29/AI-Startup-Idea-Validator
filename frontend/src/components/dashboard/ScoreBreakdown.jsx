import React from 'react';
import { motion } from 'framer-motion';

const ProgressBar = ({ label, score, delay }) => {
  const normalizedScore = Math.min(100, Math.max(0, score || 0));
  
  const getScoreColor = (s) => {
    if (s >= 80) return 'bg-vera-green';
    if (s >= 60) return 'bg-vera-cyan';
    if (s >= 40) return 'bg-vera-amber';
    return 'bg-red-500';
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium text-gray-300">{label}</span>
        <span className="text-sm font-bold text-white">{normalizedScore}/100</span>
      </div>
      <div className="w-full h-2.5 bg-black/40 rounded-full overflow-hidden border border-white/5">
        <motion.div
          className={`h-full rounded-full ${getScoreColor(normalizedScore)}`}
          initial={{ width: 0 }}
          animate={{ width: `${normalizedScore}%` }}
          transition={{ duration: 1, delay, ease: "easeOut" }}
        />
      </div>
    </div>
  );
};

export const ScoreBreakdown = ({ scores }) => {
  const breakdown = [
    { label: 'Market Potential', score: scores?.market_score },
    { label: 'Customer Demand', score: scores?.customer_score },
    { label: 'Competitive Position', score: scores?.competition_score },
    { label: 'Execution Feasibility', score: scores?.execution_score },
    { label: 'Go-To-Market Fit', score: scores?.gtm_score },
    { label: 'Risk Profile', score: scores?.risk_score }
  ].filter(item => item.score !== undefined && item.score !== null);

  if (breakdown.length === 0) {
    return (
      <div className="p-6 bg-surface/30 rounded-2xl border border-white/5 flex items-center justify-center h-full w-full">
        <p className="text-gray-400">Detailed breakdown not available.</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-surface/30 rounded-2xl border border-white/5 flex flex-col justify-center h-full space-y-5 w-full">
      <h3 className="text-lg font-semibold text-white mb-2">Detailed Analysis</h3>
      <div className="space-y-4">
        {breakdown.map((item, idx) => (
          <ProgressBar key={item.label} label={item.label} score={item.score} delay={0.2 + idx * 0.1} />
        ))}
      </div>
    </div>
  );
};
