import React from 'react';
import { Target, AlertTriangle, Lightbulb, Rocket, Activity } from 'lucide-react';

const ExecutiveSummarySection = ({ summary }) => {
  if (!summary) return null;

  const safeString = (val) => {
    if (typeof val === 'string') return val;
    if (typeof val === 'object' && val !== null) {
      return val.insight || val.description || val.opportunity || val.risk || val.action || val.title || val.name || Object.values(val).find(v => typeof v === 'string') || String(val);
    }
    return String(val || '');
  };

  return (
    <div className="w-full space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-vera-green" />
        <h2 className="text-2xl font-bold text-white tracking-tight">Executive Summary</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Founder Recommendation Full Width */}
        <div className="md:col-span-2 bg-gradient-to-br from-surface to-surface/40 p-6 rounded-2xl border border-white/5 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 blur-[50px] rounded-full pointer-events-none" />
          <h3 className="text-sm text-gray-400 uppercase tracking-wider font-bold mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-primary" /> Founder Recommendation
          </h3>
          <p className="text-lg text-white font-medium leading-relaxed">
            {safeString(summary.founder_recommendation)}
          </p>
        </div>

        {/* Opportunity */}
        <div className="bg-surface/30 p-5 rounded-xl border border-white/5">
          <h3 className="text-sm text-gray-400 uppercase tracking-wider font-bold mb-2 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-vera-green" /> Biggest Opportunity
          </h3>
          <p className="text-gray-200">{safeString(summary.biggest_opportunity)}</p>
        </div>

        {/* Risk */}
        <div className="bg-surface/30 p-5 rounded-xl border border-white/5">
          <h3 className="text-sm text-gray-400 uppercase tracking-wider font-bold mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-vera-amber" /> Biggest Risk
          </h3>
          <p className="text-gray-200">{safeString(summary.biggest_risk)}</p>
        </div>

        {/* Next Steps */}
        <div className="md:col-span-2 bg-primary/10 p-5 rounded-xl border border-primary/20">
          <h3 className="text-sm text-primary uppercase tracking-wider font-bold mb-2 flex items-center gap-2">
            <Rocket className="w-4 h-4" /> Recommended Next Step
          </h3>
          <p className="text-white font-bold text-lg">{safeString(summary.recommended_next_step)}</p>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveSummarySection;
