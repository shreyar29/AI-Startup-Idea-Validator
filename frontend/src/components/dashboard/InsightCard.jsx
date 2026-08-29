import React from 'react';

export const InsightCard = ({ title, insight, icon: Icon }) => {
  return (
    <div 
      className="bg-vera-glass border border-vera-cyan/20 p-5 rounded-xl flex items-start gap-4 shadow-[0_0_15px_rgba(0,240,255,0.05)]"
      role="complementary"
      aria-label={`${title} Insight`}
    >
      <div className="w-10 h-10 rounded-full bg-vera-cyan/20 flex items-center justify-center shrink-0 mt-0.5 relative">
        {Icon ? <Icon className="w-5 h-5 text-vera-cyan relative z-10" /> : <div className="w-4 h-4 rounded-full bg-vera-cyan animate-pulse relative z-10" />}
        <div className="absolute inset-0 rounded-full bg-vera-cyan/10 animate-ping" />
      </div>
      <div>
        <h4 className="text-sm font-bold text-vera-cyan mb-1">{title}</h4>
        <p className="text-gray-300 text-sm font-medium leading-relaxed">{insight}</p>
      </div>
    </div>
  );
};
