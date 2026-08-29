import React from 'react';
import { motion } from 'framer-motion';
import { Target, AlertTriangle, ArrowRight, Activity, Clock, ShieldCheck, CheckCircle2, XCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const OverviewSection = ({ metadata, finalEval }) => {
  const startupScore = finalEval?.startup_score || {};
  const swot = finalEval?.swot || {};
  const risk = finalEval?.risk || {};
  const gtm = finalEval?.gtm || {};

  const score = startupScore.overall_score || 0;
  // Use execution_score or average for innoScore out of 10
  const innoScore = startupScore.execution_score ? Math.round(startupScore.execution_score / 10) : 0;
  const primaryRecommendation = startupScore.verdict || 'Requires further analysis';
  
  const rawSummary = finalEval?.executive_summary;
  const executiveSummary = typeof rawSummary === 'object' && rawSummary !== null
    ? (rawSummary.market_fit || rawSummary.founder_recommendation || metadata.startup_idea)
    : (rawSummary || metadata.startup_idea);
  
  const getOpportunityText = (opp) => {
    if (typeof opp === 'string') return opp;
    return opp?.insight || opp?.description || opp?.opportunity || opp?.title || (opp && Object.values(opp).find(v => typeof v === 'string')) || String(opp);
  };

  const biggestOpportunity = Array.isArray(swot.opportunities) && swot.opportunities.length > 0 
    ? getOpportunityText(swot.opportunities[0])
    : 'N/A';
    
  const getRiskText = (r) => {
    if (typeof r === 'string') return r;
    return r?.insight || r?.description || r?.risk || r?.title || (r && Object.values(r).find(v => typeof v === 'string')) || String(r);
  };

  const getActionText = (a) => {
    if (typeof a === 'string') return a;
    return a?.insight || a?.action || a?.description || a?.step || a?.feature || a?.title || (a && Object.values(a).find(v => typeof v === 'string')) || String(a);
  };

  const topRisks = Array.isArray(risk.top_risks) ? risk.top_risks : (Array.isArray(risk.risks) ? risk.risks : []);
  const biggestRisk = topRisks.length > 0 ? getRiskText(topRisks[0]) : 'N/A';
    
  const nextAction = Array.isArray(gtm.launch_plan) && gtm.launch_plan.length > 0
    ? getActionText(gtm.launch_plan[0])
    : (Array.isArray(risk.recommendations) && risk.recommendations.length > 0 ? getActionText(risk.recommendations[0]) : 'N/A');
    
  const confidence = startupScore.confidence_level || 'N/A';

  const scoringBreakdown = startupScore.overall_score !== undefined ? {
    Market: startupScore.market_score,
    Customer: startupScore.customer_score,
    Competition: startupScore.competition_score,
    Risk: startupScore.risk_score,
    Execution: startupScore.execution_score,
    GTM: startupScore.gtm_score
  } : null;

  // Utility logic for visual styling
  const getScoreColor = (val) => {
    if (val >= 80) return '#22C55E'; // Success
    if (val >= 50) return '#F59E0B'; // Warning
    return '#EF4444'; // Error
  };

  const getInnoColor = (val) => {
    if (val >= 8) return '#4F8CFF'; // Primary/Blue
    if (val >= 5) return '#F59E0B';
    return '#EF4444';
  };

  const isPositive = score >= 70;
  const isWarning = score >= 40 && score < 70;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="space-y-10"
    >
      {/* 1 & 2: Executive Summary & Recommendation Hero */}
      <div className="relative overflow-hidden rounded-3xl p-8 md:p-10 border border-border/50 bg-gradient-to-br from-surface to-background shadow-2xl">
        {/* Premium visual accents */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-success"></div>
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col lg:flex-row gap-10 items-start">
          <div className="flex-1 space-y-8">
            <section>
              <p className="text-xs font-bold text-primary uppercase tracking-widest mb-3">Executive Summary</p>
              <h2 className="text-xl md:text-2xl text-textMain leading-relaxed font-light">
                {executiveSummary}
              </h2>
            </section>
            
            <section className="pt-6 border-t border-border/50">
              <p className="text-xs font-bold text-textMuted uppercase tracking-widest mb-4">Verdict: Should You Build This?</p>
              <div className="flex items-start gap-4">
                <div className={`mt-1 flex-shrink-0 p-3 rounded-2xl ${isPositive ? 'bg-success/10 text-success' : isWarning ? 'bg-warning/10 text-warning' : 'bg-error/10 text-error'}`}>
                  {isPositive ? <CheckCircle2 className="w-8 h-8" /> : isWarning ? <AlertTriangle className="w-8 h-8" /> : <XCircle className="w-8 h-8" />}
                </div>
                <h3 className={`text-3xl md:text-5xl font-extrabold leading-tight tracking-tight ${isPositive ? 'text-success' : isWarning ? 'text-warning' : 'text-error'}`}>
                  {primaryRecommendation}
                </h3>
              </div>
            </section>
          </div>
          
          <aside className="w-full lg:w-auto flex flex-row lg:flex-col gap-4 flex-shrink-0 justify-center">
            {/* 3: Validation Score Hero Widget */}
            <div className="flex-1 lg:flex-none glass-panel p-6 rounded-2xl border-border/50 min-w-[160px] text-center shadow-lg transition-transform hover:scale-105 duration-300">
              <p className="text-xs text-textMuted font-bold uppercase tracking-widest mb-2">Validation Score</p>
              <p className="text-5xl font-black text-textMain" style={{ color: getScoreColor(score) }}>{score}</p>
              <p className="text-[10px] text-textDim uppercase tracking-widest mt-2">Out of 100</p>
            </div>
            
            {/* 4: AI Confidence Hero Widget */}
            <div className="flex-1 lg:flex-none glass-panel p-6 rounded-2xl border-border/50 min-w-[160px] text-center shadow-lg transition-transform hover:scale-105 duration-300">
              <p className="text-xs text-textMuted font-bold uppercase tracking-widest mb-2">AI Confidence</p>
              <div className="flex justify-center items-center gap-2 mt-1">
                <ShieldCheck className="w-6 h-6 text-primary" />
                <p className="text-3xl font-bold text-textMain">{confidence}</p>
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* 5, 6, 7: Core Strategy KPIs */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors flex flex-col h-full">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-primary/10 p-2 rounded-lg text-primary">
              <Target className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-bold text-textMain uppercase tracking-widest">Biggest Opportunity</h3>
          </div>
          <p className="text-textMain leading-relaxed text-sm flex-grow">{biggestOpportunity}</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors flex flex-col h-full">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-error/10 p-2 rounded-lg text-error">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-bold text-textMain uppercase tracking-widest">Biggest Risk</h3>
          </div>
          <p className="text-textMain leading-relaxed text-sm flex-grow">{biggestRisk}</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors flex flex-col h-full">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-success/10 p-2 rounded-lg text-success">
              <ArrowRight className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-bold text-textMain uppercase tracking-widest">Next Action</h3>
          </div>
          <p className="text-textMain leading-relaxed text-sm flex-grow">{nextAction}</p>
        </div>
      </section>

      {/* 8: Supporting Metrics */}
      <section className="pt-10 border-t border-border/30">
        <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest mb-6">Supporting Telemetry</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-panel p-5 rounded-2xl flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-textMuted text-[10px] uppercase font-bold tracking-widest mb-1">Validation</span>
              <span className="text-2xl font-bold" style={{ color: getScoreColor(score) }}>{score}</span>
            </div>
            <div className="h-14 w-14">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[{ value: score }, { value: 100 - score }]}
                    cx="50%" cy="50%" innerRadius={18} outerRadius={26} startAngle={90} endAngle={-270} dataKey="value" stroke="none"
                  >
                    <Cell fill={getScoreColor(score)} />
                    <Cell fill="#1E2A45" />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-textMuted text-[10px] uppercase font-bold tracking-widest mb-1">Innovation</span>
              <span className="text-2xl font-bold" style={{ color: getInnoColor(innoScore) }}>
                {innoScore}<span className="text-sm text-textMuted font-medium">/10</span>
              </span>
            </div>
            <div className="h-14 w-14">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[{ value: innoScore }, { value: 10 - innoScore }]}
                    cx="50%" cy="50%" innerRadius={18} outerRadius={26} startAngle={90} endAngle={-270} dataKey="value" stroke="none"
                  >
                    <Cell fill={getInnoColor(innoScore)} />
                    <Cell fill="#1E2A45" />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="glass-panel p-5 rounded-2xl flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-1 text-textMuted">
              <Clock className="w-3.5 h-3.5" />
              <span className="text-[10px] uppercase font-bold tracking-widest">Execution</span>
            </div>
            <span className="text-xl font-bold text-textMain mt-1">{metadata.execution_time_seconds}s</span>
          </div>

          <div className="glass-panel p-5 rounded-2xl flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-1 text-textMuted">
              <Activity className="w-3.5 h-3.5" />
              <span className="text-[10px] uppercase font-bold tracking-widest">Status</span>
            </div>
            <div className="flex items-center justify-between w-full mt-1">
              <span className="text-xl font-bold text-success capitalize">{metadata.status}</span>
              <span className="text-[10px] text-textDim truncate max-w-[80px]" title={metadata.correlation_id}>
                {metadata.correlation_id?.split('-')[0]}
              </span>
            </div>
          </div>
        </div>
        
        
        {scoringBreakdown && Object.keys(scoringBreakdown).length > 0 && (
          <div className="mt-8">
            <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4" /> Score Driver Panel
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(scoringBreakdown).map(([key, value]) => {
                const displayValue = typeof value === 'object' && value !== null 
                  ? (value.score || value.value || String(Object.values(value)[0] || ''))
                  : String(value);
                  
                const numValue = Number(displayValue);
                const color = getScoreColor(numValue);
                
                // Find matching explanation
                let explanation = `Score for ${key}`;
                if (startupScore.score_explanation && Array.isArray(startupScore.score_explanation)) {
                  const match = startupScore.score_explanation.find(e => e.toLowerCase().includes(key.toLowerCase()));
                  if (match) explanation = match;
                }
                
                return (
                  <div key={key} className="glass-panel p-4 rounded-xl flex flex-col justify-between items-center text-center relative group hover:border-white/20 transition-all cursor-pointer">
                    <span className="text-[10px] uppercase font-bold tracking-widest text-textMuted mb-3">{key}</span>
                    <div className="relative">
                      <svg className="w-16 h-16 transform -rotate-90">
                        <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-surface border-border" />
                        <circle cx="32" cy="32" r="28" stroke={color} strokeWidth="4" fill="transparent" strokeDasharray={175} strokeDashoffset={175 - (175 * numValue) / 100} className="transition-all duration-1000 ease-out" />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-lg font-bold" style={{color}}>{displayValue}</span>
                    </div>
                    
                    {/* Tooltip */}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-48 p-3 bg-surface border border-border/50 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-20 pointer-events-none">
                      <p className="text-xs text-textMain leading-relaxed font-medium">{explanation}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Dynamic Adjustments */}
            {startupScore.score_explanation && Array.isArray(startupScore.score_explanation) && (
              <div className="mt-4 flex flex-col gap-2">
                {startupScore.score_explanation.filter(e => e.includes("Dynamic Adjustment")).map((adj, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs text-primary/80 bg-primary/5 p-2 rounded-lg border border-primary/10">
                    <ShieldCheck className="w-4 h-4 shrink-0" />
                    <span>{adj}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="mt-6 bg-surface/20 p-5 rounded-xl border border-border/30">
          <span className="text-textMuted text-xs font-bold uppercase tracking-widest block mb-2">Original Idea Input</span>
          <span className="text-textMain text-sm italic border-l-2 border-primary/50 pl-3 block">{metadata.startup_idea}</span>
        </div>
      </section>

    </motion.div>
  );
};

export default OverviewSection;
