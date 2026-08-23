import React from 'react';
import { motion } from 'framer-motion';
import { Layers, CheckSquare, Clock, XCircle, Code2, PlaySquare } from 'lucide-react';

const MVPSection = ({ data }) => {
  if (!data) return null;

  const coreFeatures = Array.isArray(data.core_features) ? data.core_features : [];
  const excludedFeatures = Array.isArray(data.future_features) ? data.future_features : Array.isArray(data.excluded_features) ? data.excluded_features : [];

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3 mb-6 border-b border-white/5 pb-4">
        <div className="p-2.5 bg-blue-500/10 rounded-xl text-blue-500">
          <Layers className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">MVP Definition</h2>
          <p className="text-sm text-textMuted mt-1">Minimum Viable Product roadmap and feature prioritization</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-white/5">
            <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
              <CheckSquare className="w-5 h-5 text-primary" />
              Core Features (Build First)
            </h3>
            <ul className="space-y-3">
              {coreFeatures.map((feature, i) => (
                <motion.li 
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-start gap-3 p-3 bg-primary/5 rounded-xl border border-primary/10"
                >
                  <Code2 className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span className="text-sm text-textMuted font-medium leading-relaxed">
                    {typeof feature === 'string' ? feature : feature.feature || feature.description || JSON.stringify(feature)}
                  </span>
                </motion.li>
              ))}
            </ul>
          </div>
        </div>

        <div className="space-y-6">
          {(data.development_timeline || (data.development_priority && data.development_priority.length > 0)) && (
            <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-surface/40">
              <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
                <Clock className="w-5 h-5 text-blue-400" />
                Estimated Timeline / Priority
              </h3>
              {data.development_timeline ? (
                <p className="text-lg text-blue-300 font-semibold">{data.development_timeline}</p>
              ) : (
                <ul className="space-y-2">
                  {data.development_priority.map((step, i) => (
                    <li key={i} className="text-sm text-blue-300/80 font-medium">{step}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
          
          {data.tech_stack_recommendations && (
            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
                <PlaySquare className="w-5 h-5 text-purple-400" />
                Recommended Tech Stack
              </h3>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(data.tech_stack_recommendations) 
                  ? data.tech_stack_recommendations.map((tech, i) => (
                      <span key={i} className="px-3 py-1 bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-bold rounded-full">
                        {typeof tech === 'string' ? tech : tech.name || JSON.stringify(tech)}
                      </span>
                    ))
                  : <p className="text-sm text-textMuted">{data.tech_stack_recommendations}</p>
                }
              </div>
            </div>
          )}

          {excludedFeatures.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
                <XCircle className="w-5 h-5 text-red-400" />
                What to Ignore for V1
              </h3>
              <ul className="space-y-2">
                {excludedFeatures.map((feat, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-textMuted line-through opacity-70">
                    <span className="text-red-400 mt-0.5">•</span>
                    {typeof feat === 'string' ? feat : feat.feature || feat.description || JSON.stringify(feat)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MVPSection;
