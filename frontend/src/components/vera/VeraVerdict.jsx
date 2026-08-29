import React from 'react';
import { VeraAvatar } from './VeraAvatar';

export const VeraVerdict = ({ score, verdict, explanation }) => {
  const getState = (s) => {
    if (s >= 90) return 'celebrating';
    if (s >= 75) return 'confident';
    if (s >= 60) return 'cautious';
    return 'critical';
  };

  return (
    <div className="bg-vera-glass border border-white/10 rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-center md:items-start gap-6 sm:gap-8 shadow-2xl relative overflow-hidden mb-8">
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-vera-cyan/10 blur-[80px] rounded-full pointer-events-none" />
      <VeraAvatar state={getState(score)} size="lg" />
      
      <div className="flex-1 text-center md:text-left z-10 w-full">
        <div className="flex flex-col sm:flex-row items-center md:items-end gap-2 sm:gap-4 mb-2">
          <h2 className="text-4xl sm:text-5xl font-extrabold text-white">{score}<span className="text-2xl text-gray-400 font-medium">/100</span></h2>
          <span className={`px-3 py-1 rounded-full text-sm font-bold uppercase tracking-wider mb-1 sm:mb-2 ${
            score >= 75 ? 'bg-vera-green/20 text-vera-green' : 
            score >= 60 ? 'bg-vera-amber/20 text-vera-amber' : 
            'bg-vera-amber/20 text-vera-amber ring-1 ring-vera-amber'
          }`}>
            {verdict}
          </span>
        </div>
        
        <div className="bg-white/5 p-4 sm:p-5 rounded-xl border border-white/5 mt-6 w-full">
          <p className="text-xs text-vera-cyan mb-2 font-mono uppercase tracking-widest flex items-center gap-2 justify-center md:justify-start">
            <span className="w-2 h-2 rounded-full bg-vera-cyan animate-pulse" />
            Vera's Synthesis
          </p>
          <ul className="text-gray-300 text-sm sm:text-base leading-relaxed space-y-2 text-left">
            {explanation && explanation.length > 0 ? (
              explanation.map((item, idx) => (
                <li key={idx} className="flex gap-2">
                  <span className="text-vera-cyan mt-1">•</span>
                  <span>{item}</span>
                </li>
              ))
            ) : (
              <p>No explanation provided by the engine.</p>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};
