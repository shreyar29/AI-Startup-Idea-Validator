import React from 'react';

export const KPICard = ({ title, value, subtitle, valueColor = 'text-white' }) => {
  return (
    <div 
      className="bg-surface/40 border border-white/5 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow"
      role="region"
      aria-label={`${title} KPI Card`}
    >
      <h3 className="text-xs font-semibold uppercase tracking-wider text-textMuted mb-2">{title}</h3>
      <div className={`text-2xl font-bold ${valueColor}`}>{value}</div>
      {subtitle && (
        <div className="text-sm font-medium text-textDim mt-1">{subtitle}</div>
      )}
    </div>
  );
};
