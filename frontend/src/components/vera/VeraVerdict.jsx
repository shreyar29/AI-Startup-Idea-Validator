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
          <p className="text-xs text-vera-cyan mb-4 font-mono uppercase tracking-widest flex items-center gap-2 justify-center md:justify-start">
            <span className="w-2 h-2 rounded-full bg-vera-cyan animate-pulse" />
            Vera's Synthesis Breakdown
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {explanation && explanation.length > 0 ? (
              explanation.map((item, idx) => {
                // Parse standard format: "Label (Weight X.XX): YY/100 optional extra"
                const match = item.match(/^(.*?)(?:\s*\(Weight\s*([\d.]+)\))?:\s*(\d+)\/100(.*)$/i);
                
                if (match) {
                  const label = match[1].trim();
                  const weight = match[2] ? parseFloat(match[2]) : null;
                  const score = parseInt(match[3], 10);
                  const extra = match[4] ? match[4].trim().replace(/^\s*\(\s*|\s*\)\s*$/g, '') : '';
                  
                  const getScoreColor = (s) => {
                    if (s >= 75) return 'bg-emerald-400';
                    if (s >= 60) return 'bg-amber-400';
                    return 'bg-rose-400';
                  };
                  const getScoreText = (s) => {
                    if (s >= 75) return 'text-emerald-400';
                    if (s >= 60) return 'text-amber-400';
                    return 'text-rose-400';
                  };

                  return (
                    <div key={idx} className="bg-black/20 border border-white/5 rounded-xl p-3 hover:bg-white/5 transition-all">
                      <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2 overflow-hidden pr-2">
                          <span className="text-white font-semibold text-xs truncate" title={label}>{label}</span>
                          {weight && (
                            <span className="text-[9px] uppercase tracking-wider bg-white/10 text-gray-300 px-1.5 py-0.5 rounded shrink-0">
                              {Math.round(weight * 100)}% Wt
                            </span>
                          )}
                        </div>
                        <div className={`font-bold text-sm shrink-0 ${getScoreText(score)}`}>
                          {score}<span className="text-gray-500 text-[10px] font-normal">/100</span>
                        </div>
                      </div>
                      <div className="h-1.5 w-full bg-black/40 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getScoreColor(score)} rounded-full shadow-[0_0_10px_rgba(255,255,255,0.2)]`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                      {extra && (
                        <p className="text-[10px] text-gray-400 mt-2 italic leading-tight line-clamp-1" title={extra}>{extra}</p>
                      )}
                    </div>
                  );
                }

                // Fallback for unparseable strings
                return (
                  <div key={idx} className="flex gap-2 text-gray-300 text-sm bg-black/20 border border-white/5 p-3 rounded-xl">
                    <span className="text-vera-cyan mt-1 shrink-0">•</span>
                    <span>{item}</span>
                  </div>
                );
              })
            ) : (
              <p className="text-gray-400 text-sm italic">No explanation provided by the engine.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
