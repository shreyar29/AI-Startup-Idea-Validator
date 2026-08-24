import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, CheckSquare, Clock, Code2, Zap, Rocket, Activity, Info } from 'lucide-react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, ZAxis
} from 'recharts';

const MVPSection = ({ data }) => {
  const [selectedFeature, setSelectedFeature] = useState(null);

  if (!data) return null;

  const coreFeatures = Array.isArray(data.core_features) ? data.core_features : [];
  const optionalFeatures = Array.isArray(data.optional_features) ? data.optional_features : [];
  const futureFeatures = Array.isArray(data.future_features) ? data.future_features : [];

  const allFeatures = [...coreFeatures, ...optionalFeatures, ...futureFeatures].filter(f => f && typeof f === 'object' && f.feature);

  if (allFeatures.length === 0) return null;

  const getPhaseColor = (phase) => {
    if (phase?.includes('Phase 1')) return '#0ea5e9'; // Primary
    if (phase?.includes('Phase 2')) return '#8b5cf6'; // Purple
    if (phase?.includes('Phase 3')) return '#64748b'; // Slate
    return '#0ea5e9';
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      whileInView={{ opacity: 1, y: 0 }} 
      viewport={{ once: true }} 
      className="space-y-10"
    >
      <div className="flex items-center gap-3 mb-6 border-b border-border/50 pb-4">
        <div className="p-2 bg-primary/10 rounded-xl text-primary">
          <Layers className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">MVP Strategy Builder</h2>
        </div>
        {data.estimated_complexity && (
          <div className="ml-auto px-4 py-1.5 rounded-full bg-surface border border-border/50 text-sm font-semibold flex items-center gap-2 shadow-sm">
            <span className="text-textMuted uppercase text-[10px] tracking-widest">Complexity</span>
            <span className={`
              ${data.estimated_complexity === 'High' ? 'text-error' : ''}
              ${data.estimated_complexity === 'Medium' ? 'text-warning' : ''}
              ${data.estimated_complexity === 'Low' ? 'text-success' : ''}
            `}>
              {data.estimated_complexity}
            </span>
          </div>
        )}
      </div>

      {data.mvp_scope && (
        <div className="glass-panel p-6 rounded-2xl border-border/50 shadow-sm bg-primary/5">
          <h3 className="text-[10px] font-bold text-primary uppercase tracking-widest flex items-center gap-2 mb-3">
            <Rocket className="w-4 h-4" /> Core MVP Scope
          </h3>
          <p className="text-sm text-textMain leading-relaxed font-medium">
            {data.mvp_scope}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Interactive Feature Prioritization Matrix */}
        <div className="glass-panel p-6 rounded-3xl border-border/50 flex flex-col h-[500px] shadow-lg">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6">
            <Activity className="w-4 h-4 text-primary" /> Feature Prioritization (Effort vs Impact)
          </h3>
          <div className="flex-1 w-full relative bg-surface/30 rounded-2xl p-4 border border-border/50">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" dataKey="effort" name="Effort" domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={false} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} label={{ value: 'Implementation Effort', position: 'bottom', fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <YAxis type="number" dataKey="impact" name="Impact" domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={false} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} label={{ value: 'Business Impact', angle: -90, position: 'left', fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <ZAxis type="number" range={[100, 500]} name="Score" />
                <RechartsTooltip cursor={{strokeDasharray: '3 3'}} content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const f = payload[0].payload;
                    return (
                      <div className="bg-surface p-3 rounded-xl border border-border/50 shadow-xl max-w-[200px]">
                        <div className="text-xs font-bold text-textMain mb-1 line-clamp-2">{f.feature}</div>
                        <div className="text-[10px] font-bold" style={{ color: getPhaseColor(f.phase) }}>{f.phase}</div>
                      </div>
                    );
                  }
                  return null;
                }} />
                <Scatter name="Features" data={allFeatures} onClick={(e) => setSelectedFeature(e.payload)}>
                  {allFeatures.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getPhaseColor(entry.phase)} className="cursor-pointer hover:opacity-80 transition-opacity" />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            
            {/* Quadrant Overlays */}
            <div className="absolute top-4 left-4 text-[10px] font-bold text-success/30 uppercase pointer-events-none">Quick Wins</div>
            <div className="absolute top-4 right-4 text-[10px] font-bold text-warning/30 uppercase pointer-events-none">Major Projects</div>
            <div className="absolute bottom-4 left-4 text-[10px] font-bold text-textMuted/30 uppercase pointer-events-none">Fill-ins</div>
            <div className="absolute bottom-4 right-4 text-[10px] font-bold text-error/30 uppercase pointer-events-none">Time Sinks</div>
          </div>
        </div>

        {/* Selected Feature Details */}
        <div className="glass-panel p-6 rounded-3xl border-border/50 flex flex-col h-[500px] shadow-lg relative overflow-hidden bg-gradient-to-br from-surface to-background/80">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6 border-b border-border/30 pb-3">
            <Code2 className="w-4 h-4 text-primary" /> Feature Details
          </h3>
          
          <AnimatePresence mode="wait">
            {selectedFeature ? (
              <motion.div
                key="selected"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex flex-col h-full overflow-y-auto pr-2 custom-scrollbar"
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <h4 className="text-lg font-bold text-textMain leading-snug">{selectedFeature.feature}</h4>
                  <span className="px-2 py-1 bg-surface rounded-md border border-border/50 text-[10px] font-bold uppercase whitespace-nowrap" style={{ color: getPhaseColor(selectedFeature.phase) }}>
                    {selectedFeature.phase || "Unknown"}
                  </span>
                </div>
                
                <div className="flex gap-2 mb-6">
                  <div className="flex-1 bg-surface/50 border border-border/30 rounded-lg p-2 text-center">
                    <div className="text-[9px] text-textMuted uppercase font-bold mb-1">Impact</div>
                    <div className="text-xs font-black text-textMain">{selectedFeature.impact || "N/A"}</div>
                  </div>
                  <div className="flex-1 bg-surface/50 border border-border/30 rounded-lg p-2 text-center">
                    <div className="text-[9px] text-textMuted uppercase font-bold mb-1">Effort</div>
                    <div className="text-xs font-black text-textMain">{selectedFeature.effort || "N/A"}</div>
                  </div>
                </div>

                <div className="bg-primary/5 border-l-4 border-primary/50 p-4 rounded-r-xl mb-6 shadow-inner">
                  <h5 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5" /> Strategic Rationale
                  </h5>
                  <p className="text-sm font-medium text-textMain leading-relaxed">
                    {selectedFeature.reason || "Core functionality requirement."}
                  </p>
                </div>
                
                {selectedFeature.evidence && selectedFeature.evidence.length > 0 && (
                  <div className="mt-auto pt-4 border-t border-border/30">
                     <h5 className="text-[10px] font-bold text-textMuted uppercase tracking-widest mb-3 flex items-center gap-1.5">
                      <Info className="w-3.5 h-3.5" /> Market Validation
                    </h5>
                    <ul className="space-y-2">
                      {selectedFeature.evidence.map((ev, idx) => (
                        <li key={idx} className="text-xs text-textDim leading-relaxed flex items-start gap-2">
                          <span className="w-1 h-1 rounded-full bg-border mt-1.5 flex-shrink-0"></span>
                          {ev}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center h-full text-center opacity-50"
              >
                <Layers className="w-12 h-12 text-textMuted mb-4" />
                <p className="text-sm text-textMuted font-medium max-w-[200px]">
                  Click a feature on the Matrix to view its strategic rationale.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      
      {/* 3: Timeline & Validation Strategy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-border/30">
        {data.estimated_timeline && (
          <div>
            <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-4">
              <Clock className="w-4 h-4 text-primary" /> Estimated Timeline
            </h3>
            <div className="text-2xl font-black text-primary">
              {data.estimated_timeline}
            </div>
          </div>
        )}

        {data.validation_strategy && data.validation_strategy.success_metrics && data.validation_strategy.success_metrics.length > 0 && (
          <div>
            <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-4">
              <CheckSquare className="w-4 h-4 text-success" /> Key Success Metrics (MVP)
            </h3>
            <ul className="space-y-3">
              {data.validation_strategy.success_metrics.map((metric, idx) => (
                <li key={idx} className="flex items-start gap-3 bg-surface/30 p-3 rounded-lg border border-border/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-success mt-1.5 flex-shrink-0"></span>
                  <span className="text-sm font-medium text-textMain">{metric}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MVPSection;
