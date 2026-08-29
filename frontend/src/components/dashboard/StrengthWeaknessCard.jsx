import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export const StrengthWeaknessCard = ({ type, data }) => {
  if (!data) return null;

  const isStrength = type === 'strength';
  const Icon = isStrength ? ArrowUpRight : ArrowDownRight;
  const colorClass = isStrength ? 'text-emerald-400' : 'text-orange-400';
  const bgClass = isStrength ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-orange-500/10 border-orange-500/20';
  const title = isStrength ? 'Strongest Pillar' : 'Key Vulnerability';

  return (
    <div 
      className={`p-4 rounded-xl border ${bgClass} flex items-center justify-between`}
      role="region"
      aria-label={`${title} Card`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-background/50 ${colorClass}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-xs font-semibold text-textMuted uppercase tracking-wider">{title}</h4>
          <p className="text-sm font-bold text-textMain mt-0.5">{data.label}</p>
        </div>
      </div>
      <div className={`text-xl font-extrabold ${colorClass}`}>
        {data.score}
      </div>
    </div>
  );
};
