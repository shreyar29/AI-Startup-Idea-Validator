import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, ShieldAlert, Zap } from 'lucide-react';

const SWOTSection = ({ data }) => {
  if (!data) return null;

  const categories = [
    { title: 'Strengths', key: 'strengths', icon: Zap, color: 'text-green-400', bg: 'bg-green-400/10', border: 'border-green-400/20' },
    { title: 'Weaknesses', key: 'weaknesses', icon: ArrowDownRight, color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20' },
    { title: 'Opportunities', key: 'opportunities', icon: ArrowUpRight, color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20' },
    { title: 'Threats', key: 'threats', icon: ShieldAlert, color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/20' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6 border-b border-white/5 pb-4">
        <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
          <Zap className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">SWOT Analysis</h2>
          <p className="text-sm text-textMuted mt-1">Strategic evaluation of internal and external factors</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((cat, i) => {
          const items = Array.isArray(data[cat.key]) ? data[cat.key] : [];

          return (
            <motion.div
              key={cat.key}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className={`glass-panel p-6 rounded-2xl border transition-all ${cat.border} hover:bg-surface/80 flex flex-col h-full`}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-lg ${cat.bg} ${cat.color}`}>
                  <cat.icon className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-textMain">{cat.title}</h3>
              </div>
              <ul className="space-y-3 flex-grow">
                {items.length > 0 ? items.map((item, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm text-textMuted bg-black/20 p-3 rounded-xl shadow-inner border border-white/5">
                    <span className={`mt-0.5 font-bold ${cat.color}`}>•</span>
                    <span className="leading-relaxed w-full">
                      {typeof item === 'string' 
                        ? item 
                        : (
                          <div className="flex flex-col gap-1.5 w-full">
                            <div className="flex justify-between items-start gap-2 w-full">
                              <span className="text-textMain font-medium">{item.insight || item.title || item.factor || item.name || item.description || ''}</span>
                              {item.impact && (
                                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border flex-shrink-0 ${
                                  item.impact === 'Critical' ? 'bg-error/10 border-error/30 text-error' :
                                  item.impact === 'High' ? 'bg-warning/10 border-warning/30 text-warning' :
                                  item.impact === 'Medium' ? 'bg-primary/10 border-primary/30 text-primary' :
                                  'bg-surface/50 border-border/50 text-textMuted'
                                }`}>
                                  {item.impact}
                                </span>
                              )}
                            </div>
                            {item.evidence && item.evidence.length > 0 && (
                              <div className="text-[10px] text-textMuted mt-1 border-l-2 border-border/50 pl-2">
                                {item.evidence.join(', ')}
                              </div>
                            )}
                          </div>
                        )
                      }
                    </span>
                  </li>
                )) : (
                  <li className="flex items-center justify-center h-full text-sm text-textDim italic py-4">
                    No {cat.title.toLowerCase()} identified.
                  </li>
                )}
              </ul>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default SWOTSection;
