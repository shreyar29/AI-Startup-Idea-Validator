import React from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Trophy, 
  AlertTriangle, 
  ShieldCheck, 
  Flag,
  Map,
  Zap,
  PieChart
} from 'lucide-react';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const ComparisonSection = ({ data }) => {
  if (!data || Object.keys(data).length === 0) return null;

  // Safe data extraction mapping directly to executive hierarchy
  const recommendation = Array.isArray(data.recommendations) && data.recommendations.length > 0 
    ? data.recommendations[0] 
    : 'N/A';
    
  const rationale = data.summary || 'N/A';
  const confidence = data.confidence || 'N/A';

  const competitiveAdvantage = Array.isArray(data.competitive_advantages) && data.competitive_advantages.length > 0 
    ? data.competitive_advantages[0] 
    : 'N/A';

  const risks = Array.isArray(data.market_gaps) ? data.market_gaps : [];
  const biggestRisk = risks.length > 0 ? risks[0] : 'N/A';
  const supportingRisks = risks.slice(1);

  const steps = Array.isArray(data.recommendations) && data.recommendations.length > 1 
    ? data.recommendations.slice(1) 
    : [];
    
  const immediateAction = steps.length > 0 ? steps[0] : 'N/A';
  const longTermDirection = steps.length > 1 ? steps[steps.length - 1] : 'N/A';

  // Scoring Utilities
  const score = data.validation_score !== undefined ? data.validation_score : 0;
  const innoScore = data.innovation_score !== undefined ? data.innovation_score : 0;

  const getScoreColor = (val) => {
    if (val >= 80) return '#22C55E';
    if (val >= 50) return '#F59E0B';
    return '#EF4444';
  };

  const getInnoColor = (val) => {
    if (val >= 8) return '#4F8CFF';
    if (val >= 5) return '#F59E0B';
    return '#EF4444';
  };
  
  const isPositive = score >= 70 || recommendation.toLowerCase().includes('pursue') || recommendation.toLowerCase().includes('build');
  const isWarning = (score >= 40 && score < 70) || recommendation.toLowerCase().includes('pivot');

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      whileInView={{ opacity: 1, y: 0 }} 
      viewport={{ once: true }} 
      className="space-y-10"
    >
      
      {/* Section Header */}
      <div className="flex items-center gap-3 border-b border-border/50 pb-4">
        <div className="bg-primary/10 p-2 rounded-xl">
          <Sparkles className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-textMain tracking-tight">Final Strategy</h2>
      </div>

      {/* 1: Executive Strategy Hero */}
      <div className="relative overflow-hidden rounded-3xl p-8 md:p-10 border border-border/50 bg-gradient-to-br from-surface to-background shadow-2xl flex flex-col lg:flex-row gap-10 items-start">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-success"></div>
        <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="flex-1 space-y-8 relative z-10">
          <div>
            <h3 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-3 flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5" /> Final Recommendation
            </h3>
            <h2 className={`text-3xl md:text-5xl font-extrabold leading-tight tracking-tight ${isPositive ? 'text-success' : isWarning ? 'text-warning' : 'text-error'}`}>
              {recommendation}
            </h2>
          </div>
          
          <div className="pt-6 border-t border-border/50">
            <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5">
              <Flag className="w-3.5 h-3.5" /> Strategic Rationale
            </h3>
            <p className="text-lg md:text-xl text-textMain leading-relaxed font-light">
              {rationale}
            </p>
          </div>
        </div>

        <div className="w-full lg:w-auto glass-panel p-6 rounded-2xl border-border/50 text-center flex-shrink-0 relative z-10 shadow-lg flex flex-row lg:flex-col items-center justify-between lg:justify-center gap-4">
          <p className="text-[10px] font-bold text-textMuted uppercase tracking-widest">AI Confidence</p>
          <div className="flex items-center lg:flex-col gap-2">
            <ShieldCheck className={`w-8 h-8 ${confidence.toLowerCase() === 'high' ? 'text-success' : confidence.toLowerCase() === 'medium' ? 'text-warning' : 'text-error'}`} />
            <span className="text-3xl font-black text-textMain">{confidence}</span>
          </div>
        </div>
      </div>

      {/* 2: Strategy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-8 rounded-3xl border-primary/30 bg-primary/5 shadow-lg relative overflow-hidden flex flex-col hover:bg-primary/10 transition-colors">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none"></div>
          <h3 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-4 flex items-center gap-2 relative z-10">
            <Trophy className="w-3.5 h-3.5" /> Biggest Competitive Advantage
          </h3>
          <p className="text-base md:text-lg font-bold text-textMain leading-relaxed relative z-10 flex-grow">
            {competitiveAdvantage}
          </p>
        </div>

        <div className="glass-panel p-8 rounded-3xl border-error/30 bg-error/5 shadow-lg relative overflow-hidden flex flex-col hover:bg-error/10 transition-colors">
          <div className="absolute inset-0 bg-gradient-to-br from-error/5 to-transparent pointer-events-none"></div>
          <h3 className="text-[10px] font-bold text-error uppercase tracking-widest mb-4 flex items-center gap-2 relative z-10">
            <AlertTriangle className="w-3.5 h-3.5" /> Biggest Risk
          </h3>
          <p className="text-base md:text-lg font-bold text-textMain leading-relaxed relative z-10 flex-grow">
            {biggestRisk}
          </p>
        </div>

        <div className="glass-panel p-8 rounded-3xl border-success/30 bg-success/5 shadow-lg relative overflow-hidden flex flex-col hover:bg-success/10 transition-colors">
          <div className="absolute inset-0 bg-gradient-to-br from-success/5 to-transparent pointer-events-none"></div>
          <h3 className="text-[10px] font-bold text-success uppercase tracking-widest mb-4 flex items-center gap-2 relative z-10">
            <Zap className="w-3.5 h-3.5" /> Immediate Next Action
          </h3>
          <p className="text-base md:text-lg font-bold text-textMain leading-relaxed relative z-10 flex-grow">
            {immediateAction}
          </p>
        </div>

        <div className="glass-panel p-8 rounded-3xl border-border/50 shadow-lg relative overflow-hidden flex flex-col hover:bg-surface transition-colors">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest mb-4 flex items-center gap-2 relative z-10">
            <Map className="w-3.5 h-3.5 text-primary" /> Long-Term Strategic Direction
          </h3>
          <p className="text-base md:text-lg font-bold text-textMain leading-relaxed relative z-10 flex-grow">
            {longTermDirection}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 pt-6">
        
        {/* 5: 90-Day Action Plan (Roadmap) */}
        <div className="space-y-6">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-3">
            <Map className="w-3.5 h-3.5 text-success" /> 90-Day Action Plan
          </h3>
          <div className="space-y-0 pt-2">
            {steps.map((step, i) => (
              <div key={i} className="flex gap-5 relative">
                {/* Timeline vertical line */}
                {i !== steps.length - 1 && (
                  <div className="absolute left-2.5 top-6 bottom-[-16px] w-0.5 bg-gradient-to-b from-primary/50 to-primary/10 z-0"></div>
                )}
                {/* Timeline node */}
                <div className="relative mt-1 w-5 h-5 rounded-full bg-surface border-2 border-primary flex items-center justify-center flex-shrink-0 z-10 shadow-lg">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                </div>
                {/* Content */}
                <div className="glass-panel p-5 rounded-2xl shadow-sm border border-border/50 hover:border-primary/30 transition-colors flex-grow mb-4 bg-gradient-to-br from-surface to-background">
                  <div className="text-[10px] text-primary font-black uppercase tracking-widest mb-2">Phase 0{i + 1}</div>
                  <p className="text-sm text-textMain leading-relaxed font-medium">{step}</p>
                </div>
              </div>
            ))}
            {steps.length === 0 && (
              <div className="text-sm text-textDim italic pl-2">No strategic roadmap generated.</div>
            )}
          </div>
        </div>

        <div className="space-y-8">
          {/* 3: Supporting Metrics */}
          { (data.validation_score !== undefined || data.innovation_score !== undefined) && (
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2">
                <PieChart className="w-3.5 h-3.5 text-primary" /> Quantitative Metrics
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {data.validation_score !== undefined && (
                  <div className="glass-panel p-5 rounded-2xl flex items-center justify-between shadow-sm">
                    <div className="flex flex-col">
                      <span className="text-textMuted text-[10px] uppercase font-bold tracking-widest mb-1">Validation</span>
                      <span className="text-2xl font-black" style={{ color: getScoreColor(score) }}>{score}</span>
                    </div>
                    <div className="h-12 w-12">
                      <ResponsiveContainer width="100%" height="100%">
                        <RechartsPieChart>
                          <Pie data={[{ value: score }, { value: 100 - score }]} cx="50%" cy="50%" innerRadius={15} outerRadius={22} startAngle={90} endAngle={-270} dataKey="value" stroke="none">
                            <Cell fill={getScoreColor(score)} />
                            <Cell fill="#1E2A45" />
                          </Pie>
                        </RechartsPieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
                
                {data.innovation_score !== undefined && (
                  <div className="glass-panel p-5 rounded-2xl flex items-center justify-between shadow-sm">
                    <div className="flex flex-col">
                      <span className="text-textMuted text-[10px] uppercase font-bold tracking-widest mb-1">Innovation</span>
                      <span className="text-2xl font-black" style={{ color: getInnoColor(innoScore) }}>{innoScore}<span className="text-sm text-textMuted font-medium">/10</span></span>
                    </div>
                    <div className="h-12 w-12">
                      <ResponsiveContainer width="100%" height="100%">
                        <RechartsPieChart>
                          <Pie data={[{ value: innoScore }, { value: 10 - innoScore }]} cx="50%" cy="50%" innerRadius={15} outerRadius={22} startAngle={90} endAngle={-270} dataKey="value" stroke="none">
                            <Cell fill={getInnoColor(innoScore)} />
                            <Cell fill="#1E2A45" />
                          </Pie>
                        </RechartsPieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 4: Supporting Risks */}
          {supportingRisks.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-error" /> Secondary Risks
              </h3>
              <div className="flex flex-col gap-3">
                {supportingRisks.map((risk, i) => (
                  <div key={i} className="flex items-start gap-3 bg-surface/30 p-4 rounded-xl border border-border/50 transition-colors hover:bg-surface">
                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-error/70 flex-shrink-0" />
                    <span className="text-sm font-medium text-textMain leading-relaxed">{risk}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
      </div>
    </motion.div>
  );
};

export default ComparisonSection;
