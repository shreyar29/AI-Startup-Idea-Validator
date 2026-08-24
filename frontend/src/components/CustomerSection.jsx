import React from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Target, 
  Lightbulb, 
  Frown, 
  CreditCard,
  Briefcase,
  Crosshair,
  UserCheck,
  Zap,
  Activity,
  DollarSign
} from 'lucide-react';

const CustomerSection = ({ data }) => {
  if (!data || Object.keys(data).length === 0) return null;

  // Safe data extraction
  const personas = data.customer_personas || [];
  let primaryPersona = personas[0] || {};
  
  // Map nested attributes if they exist
  if (primaryPersona.inferred_attributes) {
    primaryPersona = { ...primaryPersona, ...primaryPersona.inferred_attributes };
  }
  if (primaryPersona.evidence_based_attributes) {
    primaryPersona = { ...primaryPersona, ...primaryPersona.evidence_based_attributes };
  }

  const additionalPersonas = personas.slice(1);
  const unmetNeeds = data.unmet_needs || [];
  const painPoints = data.pain_points || [];
  const segments = data.target_customer_segments || [];
  const featureDemand = data.feature_demand || [];
  const goals = primaryPersona.goals || [];

  // 1. Generate Executive Summary dynamically
  const safeString = (val) => {
    if (typeof val === 'string') return val;
    if (typeof val === 'object' && val !== null) {
      return val.insight || val.goal || val.feature || val.name || val.description || Object.values(val).find(v => typeof v === 'string') || String(val);
    }
    return String(val || '');
  };

  const topSegment = segments[0] ? safeString(segments[0]) : 'target demographics';
  const topPainRaw = painPoints[0];
  const topPain = topPainRaw ? safeString(topPainRaw).toLowerCase() : 'unidentified challenges';
  const firstFeat = featureDemand[0];
  const topFeatureRaw = typeof firstFeat === 'object' && firstFeat !== null ? firstFeat.feature || firstFeat.name : firstFeat;
  const topFeature = topFeatureRaw ? safeString(topFeatureRaw).toLowerCase() : 'tailored solutions';
  
  const execSummary = `Our intelligence indicates the primary market consists of ${topSegment.toLowerCase()}. Their most critical friction point is ${topPain}, driving demand for ${topFeature}.`;

  // Parse buying behavior safely
  let buyingBehaviours = [];
  if (Array.isArray(primaryPersona.buying_behaviour)) {
    buyingBehaviours = primaryPersona.buying_behaviour;
  } else if (typeof primaryPersona.buying_behaviour === 'string' && primaryPersona.buying_behaviour !== "Unknown") {
    buyingBehaviours = primaryPersona.buying_behaviour.split(',').map(s => s.trim()).filter(Boolean);
  }

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
          <Users className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-textMain tracking-tight">Customer Intelligence</h2>
      </div>

      {/* 1: Executive Customer Insight Hero */}
      <div className="relative overflow-hidden rounded-3xl p-8 md:p-10 border border-border/50 bg-gradient-to-br from-surface to-background shadow-2xl">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-success"></div>
        <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10">
          <h3 className="text-xs font-bold text-primary uppercase tracking-widest mb-4 flex items-center gap-2">
            <Target className="w-4 h-4" /> Executive Customer Insight
          </h3>
          <p className="text-lg md:text-xl text-textMain leading-relaxed font-light">
            {execSummary}
          </p>
        </div>
      </div>

      {/* 2: Primary Persona Profile Card */}
      <div className="glass-panel p-8 rounded-3xl border-border/50 relative overflow-hidden shadow-lg">
        <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl pointer-events-none -mr-10 -mt-10"></div>
        <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest mb-6 flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-primary" /> Primary Persona Profile
        </h3>
        <div className="flex flex-col md:flex-row gap-8 items-start relative z-10">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center flex-shrink-0 border border-primary/30 shadow-inner">
            <Users className="w-10 h-10 text-primary" />
          </div>
          <div className="space-y-4">
            <h4 className="text-3xl md:text-4xl font-extrabold text-textMain tracking-tight">
              {primaryPersona.name || 'Ideal Customer Profile'}
            </h4>
            <div className="flex flex-wrap gap-3">
              {primaryPersona.occupation && primaryPersona.occupation !== 'Unknown' && (
                <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-textMain bg-surface/80 px-3 py-1.5 rounded-lg border border-border/50">
                  <Briefcase className="w-3.5 h-3.5 text-primary" /> {primaryPersona.occupation}
                </span>
              )}
              {primaryPersona.demographics && primaryPersona.demographics !== 'Unknown' && (
                <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-textMain bg-surface/80 px-3 py-1.5 rounded-lg border border-border/50">
                  <Activity className="w-3.5 h-3.5 text-success" /> {primaryPersona.demographics}
                </span>
              )}
              {primaryPersona.location && primaryPersona.location !== 'Unknown' && (
                <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-textMain bg-surface/80 px-3 py-1.5 rounded-lg border border-border/50">
                  <Target className="w-3.5 h-3.5 text-warning" /> {primaryPersona.location}
                </span>
              )}
              {primaryPersona.income && primaryPersona.income !== 'Unknown' && (
                <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-textMain bg-surface/80 px-3 py-1.5 rounded-lg border border-border/50">
                  <CreditCard className="w-3.5 h-3.5 text-success" /> {primaryPersona.income}
                </span>
              )}
              {primaryPersona.budget && primaryPersona.budget !== 'Unknown' && (
                <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-textMain bg-surface/80 px-3 py-1.5 rounded-lg border border-border/50">
                  <DollarSign className="w-3.5 h-3.5 text-error" /> {primaryPersona.budget}
                </span>
              )}
              {primaryPersona.decision_drivers && primaryPersona.decision_drivers.length > 0 && (
                <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-textMain bg-surface/80 px-3 py-1.5 rounded-lg border border-border/50">
                  <Lightbulb className="w-3.5 h-3.5 text-primary" /> {primaryPersona.decision_drivers.join(', ')}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 3: Customer Motivation (Pain Points, Goals, Needs) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-border/50 flex flex-col h-full hover:bg-surface transition-colors shadow-md">
          <h3 className="text-xs font-bold text-error uppercase tracking-widest mb-5 flex items-center gap-2">
            <Frown className="w-4 h-4" /> Core Pain Points
          </h3>
          <div className="flex flex-col gap-3 flex-grow">
            {painPoints.length > 0 ? painPoints.slice(0, 3).map((pt, i) => (
              <div key={i} className="text-sm font-medium text-textMain leading-relaxed p-4 bg-error/5 rounded-xl border border-error/10">
                {safeString(pt)}
              </div>
            )) : <div className="text-sm text-textDim italic">Evidence insufficient. Conduct customer interviews to validate pain points.</div>}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-border/50 flex flex-col h-full hover:bg-surface transition-colors shadow-md">
          <h3 className="text-xs font-bold text-primary uppercase tracking-widest mb-5 flex items-center gap-2">
            <Crosshair className="w-4 h-4" /> Primary Goals
          </h3>
          <div className="flex flex-col gap-3 flex-grow">
            {goals.length > 0 ? goals.slice(0, 3).map((goal, i) => (
              <div key={i} className="text-sm font-medium text-textMain leading-relaxed p-4 bg-primary/5 rounded-xl border border-primary/10">
                {safeString(goal)}
              </div>
            )) : <div className="text-sm text-textDim italic">Evidence insufficient. Validate customer goals through surveys.</div>}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-border/50 flex flex-col h-full hover:bg-surface transition-colors shadow-md">
          <h3 className="text-xs font-bold text-success uppercase tracking-widest mb-5 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" /> Unmet Needs
          </h3>
          <div className="flex flex-col gap-3 flex-grow">
            {unmetNeeds.length > 0 ? unmetNeeds.slice(0, 3).map((need, i) => (
              <div key={i} className="text-sm font-medium text-textMain leading-relaxed p-4 bg-success/5 rounded-xl border border-success/10">
                {safeString(need)}
              </div>
            )) : <div className="text-sm text-textDim italic">Evidence insufficient. Assess unmet market needs.</div>}
          </div>
        </div>
      </div>

      {/* 4 & 5: Buying Behaviour and Feature Demand */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Willingness to Pay & Buying Behaviour */}
        <div className="space-y-5">
          <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
            <DollarSign className="w-4 h-4 text-warning" /> Willingness To Pay & Buying Behaviour
          </h3>
          
          {/* Willingness To Pay Visualizer */}
          {data.willingness_to_pay && (
            <div className="glass-panel p-5 rounded-2xl border-border/50 bg-gradient-to-br from-surface to-background flex flex-col gap-3 shadow-md mb-4">
              <div className="text-[10px] text-textMuted font-bold uppercase tracking-widest text-center">Estimated Pricing Bands</div>
              <div className="flex justify-between items-center relative">
                <div className="absolute left-0 right-0 top-1/2 h-1 bg-border/50 -translate-y-1/2 rounded-full"></div>
                <div className="z-10 flex flex-col items-center bg-surface px-2 rounded-lg">
                  <span className="text-[10px] uppercase text-textMuted font-bold">Low</span>
                  <span className="text-sm font-bold text-textMain">{data.willingness_to_pay.low === 'Unknown' || !data.willingness_to_pay.low ? 'Data Confidence: Low' : data.willingness_to_pay.low}</span>
                </div>
                <div className="z-10 flex flex-col items-center bg-primary/10 border border-primary/30 px-3 py-1 rounded-lg shadow-sm">
                  <span className="text-[10px] uppercase text-primary font-bold">Expected</span>
                  <span className="text-base font-black text-primary">{data.willingness_to_pay.expected === 'Unknown' || !data.willingness_to_pay.expected ? 'Data Confidence: Low' : data.willingness_to_pay.expected}</span>
                </div>
                <div className="z-10 flex flex-col items-center bg-surface px-2 rounded-lg">
                  <span className="text-[10px] uppercase text-warning font-bold">Premium</span>
                  <span className="text-sm font-bold text-warning">{data.willingness_to_pay.premium === 'Unknown' || !data.willingness_to_pay.premium ? 'Data Confidence: Low' : data.willingness_to_pay.premium}</span>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 gap-3">
            {buyingBehaviours.length > 0 ? buyingBehaviours.map((bb, i) => (
              <div key={i} className="bg-surface/30 px-4 py-3 rounded-xl border-l-2 border-l-warning/50">
                <p className="text-sm text-textMain font-medium leading-relaxed">{safeString(bb)}</p>
              </div>
            )) : <div className="text-sm text-textDim italic px-2">Evidence insufficient. Research target demographic spending habits.</div>}
          </div>
        </div>

        {/* Feature Demand */}
        <div className="space-y-5">
          <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
            <Zap className="w-4 h-4 text-success" /> High-Priority Features
          </h3>
          <div className="grid grid-cols-1 gap-4">
            {featureDemand.length > 0 ? featureDemand.map((feat, i) => {
              const isObj = typeof feat === 'object' && feat !== null;
              const name = isObj ? feat.feature || feat.insight || 'Unknown Feature' : feat;
              const priority = isObj ? feat.priority || 'Medium' : 'Medium';
              const reason = isObj ? feat.reason || '' : '';
              
              const isHigh = priority.toLowerCase() === 'high';
              const badgeColor = isHigh ? 'bg-success/10 border-success/30 text-success' : 'bg-primary/10 border-primary/30 text-primary';
              
              return (
                <div key={i} className="glass-panel p-5 rounded-xl flex flex-col gap-3 hover:-translate-y-0.5 transition-transform shadow-sm">
                  <div className="flex items-start justify-between gap-4">
                    <span className="text-sm font-bold text-textMain leading-tight">{name}</span>
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border flex-shrink-0 ${badgeColor}`}>
                      {priority}
                    </span>
                  </div>
                  {reason && <p className="text-xs text-textMuted leading-relaxed">{reason}</p>}
                </div>
              );
            }) : <div className="text-sm text-textDim italic px-2">Evidence insufficient. Map feature priorities with beta testers.</div>}
          </div>
        </div>
      </div>

      {/* 6 & 7: Supporting Data */}
      <div className="pt-10 mt-6 border-t border-border/30 grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Additional Personas */}
        {additionalPersonas.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-[10px] font-bold text-textDim uppercase tracking-widest flex items-center gap-2">
              Secondary Personas
            </h3>
            <div className="flex flex-wrap gap-3">
              {additionalPersonas.map((persona, i) => (
                <div key={i} className="bg-surface/30 border border-border/50 px-4 py-2.5 rounded-xl flex items-center gap-2">
                  <Users className="w-3 h-3 text-textMuted" />
                  <span className="text-xs font-bold text-textMain">{persona.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Target Segments */}
        {segments.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-[10px] font-bold text-textDim uppercase tracking-widest flex items-center gap-2">
              Target Segments
            </h3>
            <div className="flex flex-wrap gap-2">
              {segments.map((seg, i) => (
                <span key={i} className="text-[10px] font-bold text-textMuted uppercase tracking-wider bg-surface/50 border border-border/50 px-3 py-1.5 rounded-md">
                  {safeString(seg)}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

    </motion.div>
  );
};

export default CustomerSection;
