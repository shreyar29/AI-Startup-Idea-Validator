import React from 'react';
import { motion } from 'framer-motion';
import { 
  Crosshair, 
  Shield, 
  CheckCircle2, 
  DollarSign, 
  Target, 
  AlertTriangle, 
  Zap, 
  Search, 
  Activity, 
  Flag 
} from 'lucide-react';

const CompetitorSection = ({ data }) => {
  const competitors = data?.competitors || [];
  
  if (competitors.length === 0) return null;

  const gapAnalysis = data?.gap_analysis || [];
  
  // Synthesize Executive Summary without inventing new backend fields
  const topCompetitorName = competitors[0]?.name || 'established players';
  const execSummary = `The market currently features ${competitors.length} primary competitors, led by ${topCompetitorName}. Our analysis identifies critical gaps in their current offerings, providing a clear entry vector for disruptive solutions.`;



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
          <Crosshair className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-textMain tracking-tight">Competitive Intelligence</h2>
      </div>

      {/* 1: Competitive Landscape Hero */}
      <div className="relative overflow-hidden rounded-3xl p-8 md:p-10 border border-border/50 bg-gradient-to-br from-surface to-background shadow-2xl">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-success"></div>
        <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10">
          <h3 className="text-xs font-bold text-primary uppercase tracking-widest mb-4 flex items-center gap-2">
            <Search className="w-4 h-4" /> Executive Landscape
          </h3>
          <p className="text-lg md:text-xl text-textMain leading-relaxed font-light">
            {execSummary}
          </p>
        </div>
      </div>

      {/* 2: Differentiation Opportunity */}
      <div>
        <div className="glass-panel p-8 rounded-3xl border-primary/30 flex flex-col justify-center relative overflow-hidden shadow-lg bg-primary/5 hover:bg-primary/10 transition-colors">
          <div className="absolute top-0 right-0 p-32 bg-primary/10 blur-3xl rounded-full pointer-events-none"></div>
          <div className="relative z-10 space-y-5">
            <h3 className="text-[10px] font-bold text-primary uppercase tracking-widest flex items-center gap-2">
              <Zap className="w-3.5 h-3.5" /> Differentiation Opportunity
            </h3>
            <div className="flex flex-col gap-4">
              {gapAnalysis.length > 0 ? gapAnalysis.map((gap, i) => (
                <div key={i} className="text-sm md:text-base font-medium text-textMain leading-relaxed border-l-4 border-primary/50 pl-4 py-1">
                  {gap}
                </div>
              )) : (
                <div className="text-sm font-medium text-textMain leading-relaxed border-l-4 border-primary/50 pl-4 py-1">
                  Unique value proposition required to disrupt the market.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 3: Top Competitors */}
      <div className="space-y-6 pt-8">
        <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-3">
          <Target className="w-3.5 h-3.5 text-success" /> In-Depth Competitor Profiles
        </h3>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {competitors.map((comp, i) => (
            <div key={i} className="glass-panel p-8 rounded-3xl flex flex-col shadow-lg border-border/50 bg-gradient-to-br from-surface to-background/50 hover:border-border transition-colors">
              
              {/* Competitor Header */}
              <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-8 border-b border-border/30 pb-6">
                <div className="flex items-center gap-4 max-w-full">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-surface to-background border border-border flex items-center justify-center text-2xl font-black text-white shadow-inner flex-shrink-0">
                    {comp.name ? comp.name.charAt(0).toUpperCase() : '?'}
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-xl md:text-2xl font-extrabold text-textMain tracking-tight truncate">{comp.name || 'Unknown Competitor'}</h3>
                    {comp.target_customers && comp.target_customers !== "Unavailable" && comp.target_customers !== "Unknown" && (
                      <p className="text-[10px] uppercase font-bold text-textMuted tracking-wider mt-1 line-clamp-1">{comp.target_customers}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-wrap items-center gap-2 flex-shrink-0">
                  {comp.business_model && comp.business_model !== "Unknown" && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 rounded-xl border border-primary/20 shadow-sm max-w-[150px]">
                      <Activity className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                      <span className="text-xs font-bold text-primary uppercase tracking-wider truncate">{comp.business_model}</span>
                    </div>
                  )}
                  {comp.pricing && comp.pricing !== "Unknown" && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-success/10 rounded-xl border border-success/20 shadow-sm max-w-[150px]">
                      <DollarSign className="w-3.5 h-3.5 text-success flex-shrink-0" />
                      <span className="text-xs font-bold text-success uppercase tracking-wider truncate">{comp.pricing}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-8 flex-grow">
                {/* 4: Strengths & Weaknesses (Premium Cards) */}
                {(comp.strengths?.length > 0 || comp.weaknesses?.length > 0) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {comp.strengths?.length > 0 && (
                      <div className="bg-success/5 border border-success/10 rounded-2xl p-5 shadow-inner">
                        <h4 className="text-[10px] font-bold text-success uppercase tracking-widest mb-3 flex items-center gap-1.5">
                          <Shield className="w-3.5 h-3.5" /> Core Strengths
                        </h4>
                        <ul className="space-y-3">
                          {comp.strengths.map((str, j) => (
                            <li key={j} className="text-xs font-medium text-textMain leading-relaxed flex items-start gap-2.5">
                              <span className="w-1.5 h-1.5 rounded-full bg-success mt-1 flex-shrink-0"></span>
                              {str}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {comp.weaknesses?.length > 0 && (
                      <div className="bg-error/5 border border-error/10 rounded-2xl p-5 shadow-inner">
                        <h4 className="text-[10px] font-bold text-error uppercase tracking-widest mb-3 flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5" /> Critical Weaknesses
                        </h4>
                        <ul className="space-y-3">
                          {comp.weaknesses.map((wk, j) => (
                            <li key={j} className="text-xs font-medium text-textMain leading-relaxed flex items-start gap-2.5">
                              <span className="w-1.5 h-1.5 rounded-full bg-error mt-1 flex-shrink-0"></span>
                              {wk}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Key Features (Tag Cloud) */}
                {Array.isArray(comp.features) && comp.features.length > 0 && (
                  <div>
                    <h4 className="text-[10px] font-bold text-textMuted uppercase tracking-widest mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-primary"/> Key Capabilities
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {comp.features.map((feat, j) => (
                        <div key={j} className="text-[10px] font-bold uppercase tracking-wider text-textMain bg-surface border border-border/80 px-3 py-1.5 rounded-lg shadow-sm line-clamp-2 max-w-full whitespace-normal">
                          {feat}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Differentiation field fallback if present */}
                {comp.differentiation && (
                  <div className="bg-primary/5 border-l-4 border-primary/50 p-4 rounded-r-xl mt-4">
                    <h4 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1.5">Unique Approach</h4>
                    <p className="text-xs font-medium text-textMain leading-relaxed">{comp.differentiation}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default CompetitorSection;
