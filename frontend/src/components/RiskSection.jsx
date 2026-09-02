import React, { useState } from 'react';
import AgentScoreBadge from './dashboard/AgentScoreBadge';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, TrendingDown, Target, Zap, Server, Shield, CheckCircle2, Activity, Info } from 'lucide-react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, ZAxis
} from 'recharts';

const ICONS = {
  Market: Target,
  Technical: Server,
  Financial: TrendingDown,
  Operational: Zap,
  Regulatory: Shield,
  Default: AlertTriangle
};

const RiskSection = ({ data }) => {
  const [selectedRisk, setSelectedRisk] = useState(null);

  if (!data) return null;

  const risks = Array.isArray(data.risks) && data.risks.length > 0 ? data.risks : Array.isArray(data.top_risks) ? data.top_risks : [];

  if (risks.length === 0) return null;

  const getRiskColor = (risk) => {
    const s = risk.risk_score || 0;
    if (s >= 45) return '#ef4444'; // Red
    if (s >= 24) return '#f59e0b'; // Amber
    if (s >= 12) return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      whileInView={{ opacity: 1, y: 0 }} 
      viewport={{ once: true }} 
      className="space-y-10"
    >
      <div className="flex items-center gap-3 mb-6 border-b border-border/50 pb-4">
        <div className="p-2 bg-error/10 rounded-xl text-error">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">Risk Center</h2>
          <AgentScoreBadge score={data.overall_risk_score} confidence={data.confidence_level} inverted={true} />
        </div>
        {data.overall_risk_level && (
          <div className="ml-auto px-4 py-1.5 rounded-full bg-surface border border-border/50 text-sm font-semibold flex items-center gap-2 shadow-sm">
            <span className="text-textMuted uppercase text-[10px] tracking-widest">Overall Risk</span>
            <span className={`
              ${data.overall_risk_level === 'Critical' ? 'text-error' : ''}
              ${data.overall_risk_level === 'High' ? 'text-warning' : ''}
              ${data.overall_risk_level === 'Medium' ? 'text-yellow-400' : ''}
              ${data.overall_risk_level === 'Low' ? 'text-success' : ''}
            `}>
              {data.overall_risk_level}
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Interactive Heatmap */}
        <div className="glass-panel p-6 rounded-3xl border-border/50 flex flex-col h-[500px] shadow-lg">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6">
            <Activity className="w-4 h-4 text-error" /> Risk Heatmap (Probability vs Impact)
          </h3>
          <div className="flex-1 w-full relative bg-surface/30 rounded-2xl p-4 border border-border/50">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" dataKey="probability_score" name="Probability" domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={false} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} label={{ value: 'Probability (Likelihood)', position: 'bottom', fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <YAxis type="number" dataKey="impact_score" name="Impact" domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={false} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} label={{ value: 'Business Impact', angle: -90, position: 'left', fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <ZAxis type="number" dataKey="risk_score" range={[100, 500]} name="Score" />
                <RechartsTooltip cursor={{strokeDasharray: '3 3'}} content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const r = payload[0].payload;
                    return (
                      <div className="bg-surface p-3 rounded-xl border border-border/50 shadow-xl max-w-[200px]">
                        <div className="text-xs font-bold text-textMain mb-1 line-clamp-2">{r.risk || r.description}</div>
                        <div className="text-[10px] text-textMuted uppercase">{r.category}</div>
                      </div>
                    );
                  }
                  return null;
                }} />
                <Scatter name="Risks" data={risks} onClick={(e) => setSelectedRisk(e.payload)}>
                  {risks.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getRiskColor(entry)} className="cursor-pointer hover:opacity-80 transition-opacity" />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            
            {/* Quadrant Overlays */}
            <div className="absolute top-4 right-4 text-[10px] font-bold text-error/30 uppercase pointer-events-none">Critical</div>
            <div className="absolute top-4 left-4 text-[10px] font-bold text-warning/30 uppercase pointer-events-none">High</div>
            <div className="absolute bottom-4 right-4 text-[10px] font-bold text-yellow-500/30 uppercase pointer-events-none">Medium</div>
            <div className="absolute bottom-4 left-4 text-[10px] font-bold text-success/30 uppercase pointer-events-none">Low</div>
          </div>
        </div>

        {/* Selected Risk Mitigation Drawer */}
        <div className="glass-panel p-6 rounded-3xl border-border/50 flex flex-col h-[500px] shadow-lg relative overflow-hidden bg-gradient-to-br from-surface to-background/80">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6 border-b border-border/30 pb-3">
            <Shield className="w-4 h-4 text-primary" /> Mitigation Strategy
          </h3>
          
          <AnimatePresence mode="wait">
            {selectedRisk ? (
              <motion.div
                key="selected"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex flex-col h-full overflow-y-auto pr-2 custom-scrollbar"
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <h4 className="text-lg font-bold text-textMain leading-snug">{selectedRisk.risk || selectedRisk.description}</h4>
                  <span className="px-2 py-1 bg-surface rounded-md border border-border/50 text-[10px] font-bold text-textMuted uppercase whitespace-nowrap">
                    {selectedRisk.category || "General"}
                  </span>
                </div>
                
                <div className="flex gap-2 mb-6">
                  <div className="flex-1 bg-surface/50 border border-border/30 rounded-lg p-2 text-center">
                    <div className="text-[9px] text-textMuted uppercase font-bold mb-1">Severity</div>
                    <div className="text-xs font-black text-textMain">{selectedRisk.severity || selectedRisk.impact || "Medium"}</div>
                  </div>
                  <div className="flex-1 bg-surface/50 border border-border/30 rounded-lg p-2 text-center">
                    <div className="text-[9px] text-textMuted uppercase font-bold mb-1">Likelihood</div>
                    <div className="text-xs font-black text-textMain">{selectedRisk.likelihood || "Medium"}</div>
                  </div>
                  <div className="flex-1 bg-primary/10 border border-primary/20 rounded-lg p-2 text-center">
                    <div className="text-[9px] text-primary uppercase font-bold mb-1">Score</div>
                    <div className="text-xs font-black text-primary">{selectedRisk.risk_score || "N/A"}</div>
                  </div>
                </div>

                <div className="bg-primary/5 border-l-4 border-primary/50 p-4 rounded-r-xl mb-6 shadow-inner">
                  <h5 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Recommended Mitigation
                  </h5>
                  <p className="text-sm font-medium text-textMain leading-relaxed">
                    {selectedRisk.mitigation || "Validate this assumption with users."}
                  </p>
                </div>
                
                {selectedRisk.evidence_metadata && selectedRisk.evidence_metadata.length > 0 && (
                  <div className="mt-auto pt-4 border-t border-border/30">
                     <h5 className="text-[10px] font-bold text-textMuted uppercase tracking-widest mb-3 flex items-center gap-1.5">
                      <Info className="w-3.5 h-3.5" /> Evidence Trail
                    </h5>
                    <ul className="space-y-2">
                      {selectedRisk.evidence_metadata.map((ev, idx) => (
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
                <Target className="w-12 h-12 text-textMuted mb-4" />
                <p className="text-sm text-textMuted font-medium max-w-[200px]">
                  Click a node on the Heatmap to view its mitigation strategy.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      
      {/* 3: Top Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="pt-6 border-t border-border/30">
           <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6">
            <CheckCircle2 className="w-4 h-4 text-success" /> Key Strategic Recommendations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.recommendations.map((rec, i) => (
              <div key={i} className="bg-surface/30 border border-border/50 p-4 rounded-xl flex items-start gap-3">
                <span className="text-success font-black mt-0.5">{i+1}.</span>
                <p className="text-sm text-textMain leading-relaxed">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default RiskSection;
