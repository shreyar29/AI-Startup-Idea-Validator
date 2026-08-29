import React from 'react';
import { motion } from 'framer-motion';

const ScoreGaugeComponent = ({ score, title, subtitle, verdict, confidence, size = "lg" }) => {
  // Normalize score to 0-100
  const normalizedScore = Math.min(100, Math.max(0, score || 0));
  
  const getScoreColor = (s) => {
    if (s >= 90) return 'text-vera-green stroke-vera-green';
    if (s >= 75) return 'text-emerald-400 stroke-emerald-400';
    if (s >= 60) return 'text-vera-cyan stroke-vera-cyan';
    if (s >= 40) return 'text-vera-amber stroke-vera-amber';
    return 'text-red-500 stroke-red-500';
  };

  const getScoreGlow = (s) => {
    if (s >= 90) return 'drop-shadow-[0_0_15px_rgba(57,255,20,0.6)]';
    if (s >= 75) return 'drop-shadow-[0_0_15px_rgba(52,211,153,0.6)]';
    if (s >= 60) return 'drop-shadow-[0_0_15px_rgba(0,240,255,0.6)]';
    if (s >= 40) return 'drop-shadow-[0_0_15px_rgba(255,176,0,0.6)]';
    return 'drop-shadow-[0_0_15px_rgba(239,68,68,0.6)]';
  };

  const colorClass = getScoreColor(normalizedScore);
  const glowClass = getScoreGlow(normalizedScore);

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-surface/30 rounded-2xl border border-white/5 w-full h-full">
      <div className={`relative flex items-center justify-center mb-2 ${size === 'sm' ? 'w-32 h-32' : 'w-48 h-48'}`}>
        {/* Background Circle */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 140 140">
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="8"
            className="text-white/10"
          />
          {/* Progress Circle */}
          <motion.circle
            cx="70"
            cy="70"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            className={`${colorClass.split(' ')[1]} ${glowClass}`}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>
        
        {/* Score Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`${size === 'sm' ? 'text-3xl' : 'text-5xl'} font-extrabold ${colorClass.split(' ')[0]}`}>
            {normalizedScore}
          </span>
          <span className={`${size === 'sm' ? 'text-xs' : 'text-sm'} text-gray-400 font-medium`}>/ 100</span>
        </div>
      </div>
      
      <div className="text-center space-y-1">
        {title ? (
          <h3 className={`${size === 'sm' ? 'text-base' : 'text-xl'} font-bold text-white tracking-wide`}>{title}</h3>
        ) : (
          <h3 className="text-xl font-bold text-white tracking-wide">{verdict || "Evaluating"}</h3>
        )}
        
        {subtitle ? (
          <p className="text-xs text-gray-400 font-medium">{subtitle}</p>
        ) : (
          confidence && <p className="text-sm text-gray-400 font-medium">Confidence: <span className="text-gray-200">{confidence}</span></p>
        )}
      </div>
    </div>
  );
};
export const ScoreGauge = React.memo(ScoreGaugeComponent);
