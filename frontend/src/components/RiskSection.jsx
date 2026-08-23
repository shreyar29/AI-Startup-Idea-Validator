import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, TrendingDown, Target, Zap, Server, Shield, CheckCircle2 } from 'lucide-react';

const ICONS = {
  Market: Target,
  Technical: Server,
  Financial: TrendingDown,
  Operational: Zap,
  Regulatory: Shield,
  Default: AlertTriangle
};

const RiskSection = ({ data }) => {
  if (!data) return null;

  // Use data.risks (objects) first, fallback to top_risks if risks is empty
  const risks = Array.isArray(data.risks) && data.risks.length > 0 ? data.risks : Array.isArray(data.top_risks) ? data.top_risks : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6 border-b border-white/5 pb-4">
        <div className="p-2.5 bg-red-500/10 rounded-xl text-red-500">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">Risk Matrix</h2>
          <p className="text-sm text-textMuted mt-1">Identified vulnerabilities and mitigation strategies</p>
        </div>
        {data.risk_level && (
          <div className="ml-auto px-4 py-1.5 rounded-full bg-surface border border-white/10 text-sm font-semibold flex items-center gap-2 shadow-sm">
            <span>Overall Risk:</span>
            <span className={`
              ${data.risk_level === 'High' ? 'text-red-400' : ''}
              ${data.risk_level === 'Medium' ? 'text-yellow-400' : ''}
              ${data.risk_level === 'Low' ? 'text-green-400' : ''}
            `}>
              {data.risk_level}
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {risks.map((risk, i) => {
          // Normalizing schema differences if any
          const category = risk.category || "General";
          const description = risk.description || risk.risk || JSON.stringify(risk);
          const impact = risk.severity || risk.impact || "Medium";
          const mitigation = risk.mitigation || "No mitigation provided.";
          
          const Icon = ICONS[category] || ICONS.Default;
          
          let impactColor = "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
          if (impact === "High") impactColor = "text-red-400 bg-red-400/10 border-red-400/20";
          if (impact === "Low") impactColor = "text-green-400 bg-green-400/10 border-green-400/20";

          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-panel p-6 rounded-2xl flex flex-col gap-4 border border-white/5 hover:border-red-500/30 hover:bg-surface/60 transition-colors"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-surface/80 rounded-lg text-textMuted shadow-inner">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-textMain">{category}</h3>
                  </div>
                </div>
                <div className={`px-2.5 py-1 text-xs font-bold rounded-md border ${impactColor}`}>
                  {impact} Impact
                </div>
              </div>
              
              <p className="text-sm text-textMuted leading-relaxed bg-black/20 p-3 rounded-lg border border-white/5 shadow-inner">
                {description}
              </p>
              
              <div className="mt-auto pt-4 border-t border-white/5 flex gap-2">
                <CheckCircle2 className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                <p className="text-sm text-textMain font-medium">{mitigation}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default RiskSection;
