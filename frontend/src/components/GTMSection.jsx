import React from 'react';
import { motion } from 'framer-motion';
import { Rocket, Megaphone, Users, Target, CheckCircle2, DollarSign, Activity, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, Tooltip as RechartsTooltip } from 'recharts';

const GTMSection = ({ data }) => {
  if (!data) return null;

  const funnel = data.funnel_pipeline || [];
  const cac = data.cac_ltv_metrics?.cac || 0;
  const ltv = data.cac_ltv_metrics?.ltv || 0;
  const cacRisk = data.estimated_cac_risk || "Medium";
  
  // Dummy data for visual LTV/CAC chart trend
  const trendData = [
    { month: 'M1', value: cac },
    { month: 'M2', value: cac * 0.8 },
    { month: 'M3', value: ltv * 0.3 },
    { month: 'M6', value: ltv * 0.6 },
    { month: 'M12', value: ltv }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      whileInView={{ opacity: 1, y: 0 }} 
      viewport={{ once: true }} 
      className="space-y-10"
    >
      <div className="flex items-center gap-3 mb-6 border-b border-border/50 pb-4">
        <div className="p-2 bg-orange-500/10 rounded-xl text-orange-500">
          <Rocket className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">Go-To-Market Strategy</h2>
        </div>
        {data.go_to_market_score && (
          <div className="ml-auto px-4 py-1.5 rounded-full bg-surface border border-border/50 text-sm font-semibold flex items-center gap-2 shadow-sm">
            <span className="text-textMuted uppercase text-[10px] tracking-widest">GTM Score</span>
            <span className="text-orange-400 font-bold">
              {data.go_to_market_score}/100
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Funnel Pipeline */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border-border/50 shadow-lg relative overflow-hidden">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6">
            <Activity className="w-4 h-4 text-orange-400" /> Customer Acquisition Pipeline
          </h3>
          
          <div className="space-y-4">
            {funnel.map((stage, idx) => {
              const width = 100 - (idx * 15);
              return (
                <div key={idx} className="flex flex-col items-center">
                  <div 
                    className="bg-surface border border-border/30 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-inner relative overflow-hidden transition-all duration-300 hover:border-orange-500/50"
                    style={{ width: `${width}%`, minWidth: '60%' }}
                  >
                    {/* Background tint */}
                    <div className="absolute inset-0 bg-gradient-to-r from-orange-500/5 to-transparent opacity-50"></div>
                    
                    <span className="text-[10px] font-bold text-orange-400 uppercase tracking-widest mb-1 z-10">
                      {stage.stage}
                    </span>
                    
                    <div className="z-10 flex flex-wrap justify-center gap-2 mt-2">
                      {(stage.channels || stage.tactics || []).map((item, i) => (
                        <span key={i} className="px-2 py-1 bg-black/40 rounded-md border border-white/5 text-xs text-textMuted font-medium">
                          {item.channel || item}
                        </span>
                      ))}
                    </div>
                    
                    {stage.metrics && (
                      <div className="z-10 flex gap-4 mt-2">
                        <span className="text-xs font-black text-error">CAC: {stage.metrics.cac}</span>
                        <span className="text-xs font-black text-success">LTV: {stage.metrics.ltv}</span>
                      </div>
                    )}
                    
                    {stage.conversion_rate && (
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-textDim hidden sm:block">
                        {stage.conversion_rate}
                      </div>
                    )}
                  </div>
                  {idx < funnel.length - 1 && (
                    <div className="w-px h-6 bg-border/50 my-1"></div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* CAC vs LTV Economics */}
        <div className="glass-panel p-6 rounded-3xl border-border/50 flex flex-col shadow-lg bg-gradient-to-br from-surface to-background/80">
          <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-6 border-b border-border/30 pb-3">
            <TrendingUp className="w-4 h-4 text-success" /> Unit Economics (Est.)
          </h3>
          
          <div className="flex gap-4 mb-6">
            <div className="flex-1 bg-error/10 border border-error/20 rounded-xl p-3 text-center">
              <div className="text-[10px] text-error uppercase font-bold mb-1">CAC</div>
              <div className="text-xl font-black text-error">${cac}</div>
            </div>
            <div className="flex-1 bg-success/10 border border-success/20 rounded-xl p-3 text-center">
              <div className="text-[10px] text-success uppercase font-bold mb-1">LTV</div>
              <div className="text-xl font-black text-success">${ltv}</div>
            </div>
          </div>
          
          <div className="bg-surface/50 border border-border/30 rounded-xl p-3 mb-6 text-center">
            <div className="text-[10px] text-textMuted uppercase font-bold mb-1">LTV:CAC Ratio</div>
            <div className={`text-lg font-black ${ltv/cac >= 3 ? 'text-success' : 'text-warning'}`}>
              {(ltv / (cac || 1)).toFixed(1)}x
            </div>
            <div className="text-[9px] text-textDim mt-1">Target: 3.0x+</div>
          </div>

          <div className="flex-1 w-full min-h-[100px] bg-black/20 rounded-xl border border-border/30 p-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 5, right: 5, bottom: 0, left: 5 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" tick={{fontSize: 9, fill: 'rgba(255,255,255,0.5)'}} axisLine={false} tickLine={false} />
                <RechartsTooltip contentStyle={{backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '8px', fontSize: '12px'}} />
                <Area type="monotone" dataKey="value" stroke="#22c55e" fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Action Plan */}
      {data.action_plan && (data.action_plan.first_30_days?.length > 0 || data.action_plan.first_90_days?.length > 0) && (
        <div className="grid md:grid-cols-2 gap-8 pt-6 border-t border-border/30">
          {data.action_plan.first_30_days?.length > 0 && (
            <div>
              <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-4">
                <Target className="w-4 h-4 text-purple-400" /> First 30 Days (Launch)
              </h3>
              <ul className="space-y-3">
                {data.action_plan.first_30_days.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-3 bg-surface/30 p-3 rounded-lg border border-border/30">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 flex-shrink-0"></span>
                    <span className="text-sm font-medium text-textMain">{typeof item === 'string' ? item : item.description}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {data.action_plan.first_90_days?.length > 0 && (
            <div>
              <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 mb-4">
                <Users className="w-4 h-4 text-blue-400" /> First 90 Days (Growth)
              </h3>
              <ul className="space-y-3">
                {data.action_plan.first_90_days.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-3 bg-surface/30 p-3 rounded-lg border border-border/30">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 flex-shrink-0"></span>
                    <span className="text-sm font-medium text-textMain">{typeof item === 'string' ? item : item.description}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default GTMSection;
