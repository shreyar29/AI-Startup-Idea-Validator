import React from 'react';
import AgentScoreBadge from './dashboard/AgentScoreBadge';
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
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Cell
} from 'recharts';

const CompetitorSection = ({ data }) => {
  const validCompetitors = (data?.competitors || []).filter(c => {
    if (!c || typeof c !== 'object') return false;
    const name = c.name?.trim().toLowerCase();
    if (!name || name === 'unknown' || name === 'unknown competitor') return false;
    
    // Require some minimum data to be considered valid
    const hasData = (c.pricing && c.pricing !== "Unknown") || 
                    (c.business_model && c.business_model !== "Unknown") || 
                    (c.strengths && c.strengths.length > 0) || 
                    (c.weaknesses && c.weaknesses.length > 0) || 
                    (c.features && c.features.length > 0);
    return hasData;
  });

  if (validCompetitors.length === 0) return null;

  const competitors = validCompetitors;
  const gapAnalysis = data?.competitor_gaps || data?.gap_analysis || [];
  
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
        <AgentScoreBadge score={data.competition_score} confidence={data.confidence_level} />
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

      {/* 2.5: Interactive Positioning Map & Moat Score */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-4">
        {/* Positioning Map */}
        <div className="glass-panel p-6 rounded-2xl border-border/50 flex flex-col h-[400px]">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-4">
            <Activity className="w-3.5 h-3.5 text-vera-cyan" /> Competitive Positioning (Price vs. Value)
          </h3>
          <div className="flex-1 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis type="number" dataKey="position_x" name="Price" domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={false} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} label={{ value: 'Price / Complexity', position: 'bottom', fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <YAxis type="number" dataKey="position_y" name="Value" domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={false} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} label={{ value: 'Market Value / Depth', angle: -90, position: 'left', fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <RechartsTooltip cursor={{strokeDasharray: '3 3'}} content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-surface p-3 rounded-xl border border-border/50 shadow-xl">
                        <div className="text-sm font-bold text-primary mb-1">{data.name}</div>
                        <div className="text-xs text-textMuted mb-2">{data.pricing}</div>
                        <div className="text-[10px] text-textMain max-w-[150px] leading-tight">{data.product_summary}</div>
                      </div>
                    );
                  }
                  return null;
                }} />
                <Scatter name="Competitors" data={competitors} fill="#0ea5e9">
                  {competitors.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? '#8b5cf6' : '#0ea5e9'} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Competitive Moat Analysis */}
        {competitors[0]?.moat_score && (
          <div className="glass-panel p-6 rounded-2xl border-border/50 flex flex-col h-[400px]">
            <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-4">
              <Shield className="w-3.5 h-3.5 text-primary" /> Top Competitor Moat Analysis ({competitors[0].name})
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart outerRadius={100} width={730} height={250} data={[
                  { subject: 'Technology', A: competitors[0].moat_score.technology || 50, fullMark: 100 },
                  { subject: 'Brand', A: competitors[0].moat_score.brand || 50, fullMark: 100 },
                  { subject: 'Distribution', A: competitors[0].moat_score.distribution || 50, fullMark: 100 },
                  { subject: 'Execution', A: competitors[0].moat_score.execution || 50, fullMark: 100 },
                ]}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar name={competitors[0].name} dataKey="A" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
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
                  <div className="min-w-0 flex-1">
                    <h3 className="text-xl md:text-2xl font-extrabold text-textMain tracking-tight line-clamp-2 break-words" title={comp.name || 'Unknown Competitor'}>{comp.name || 'Unknown Competitor'}</h3>
                    {comp.target_customers && comp.target_customers !== "Unavailable" && comp.target_customers !== "Unknown" && (
                      <p className="text-[10px] uppercase font-bold text-textMuted tracking-wider mt-1 line-clamp-2 break-words" title={comp.target_customers}>{comp.target_customers}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-wrap items-center gap-2 flex-shrink-0 w-full sm:w-auto mt-4 sm:mt-0">
                  {comp.business_model && comp.business_model !== "Unknown" && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 rounded-xl border border-primary/20 shadow-sm max-w-[200px]">
                      <Activity className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                      <span className="text-xs font-bold text-primary uppercase tracking-wider line-clamp-1 break-all" title={comp.business_model}>{comp.business_model}</span>
                    </div>
                  )}
                  {comp.pricing && comp.pricing !== "Unknown" && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-success/10 rounded-xl border border-success/20 shadow-sm max-w-[200px]">
                      <DollarSign className="w-3.5 h-3.5 text-success flex-shrink-0" />
                      <span className="text-xs font-bold text-success uppercase tracking-wider line-clamp-1 break-all" title={comp.pricing}>{comp.pricing}</span>
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
                              {typeof str === 'string' ? str : (str?.description || str?.strength || JSON.stringify(str))}
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
                              {typeof wk === 'string' ? wk : (wk?.description || wk?.weakness || JSON.stringify(wk))}
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
