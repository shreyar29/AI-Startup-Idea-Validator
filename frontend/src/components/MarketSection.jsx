import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Target, 
  Zap, 
  AlertTriangle, 
  Link2, 
  PieChart as PieChartIcon, 
  Activity, 
  ShieldCheck, 
  Lightbulb, 
  Compass
} from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer, Cell } from 'recharts';

const MarketSection = ({ data }) => {
  if (!data || Object.keys(data).length === 0) return null;

  // Extract numeric growth for calculations
  const getGrowthNumber = (str) => {
    if (!str) return 0;
    const match = str.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : 0;
  };
  
  const growthNum = getGrowthNumber(data.growth_rate);
  const chartData = [{ name: 'Growth', value: growthNum }];



  return (
    <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="space-y-10">
      {/* Section Header */}
      <div className="flex items-center gap-3 border-b border-border/50 pb-4">
        <div className="bg-primary/10 p-2 rounded-xl">
          <Activity className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Executive Market Intelligence</h2>
      </div>

      {/* 1: Executive Market Verdict */}
      <div className="glass-panel p-8 rounded-3xl border-border/50 bg-gradient-to-br from-surface to-background relative overflow-hidden">
        <div className="absolute top-0 right-0 p-32 bg-primary/5 blur-3xl rounded-full pointer-events-none"></div>
        <div className="relative z-10 flex flex-col h-full justify-center">
          <h3 className="text-xs font-bold text-primary uppercase tracking-widest mb-4 flex items-center gap-2">
            <Compass className="w-4 h-4" /> Market Verdict
          </h3>
          <p className="text-lg md:text-xl text-textMain leading-relaxed font-light">
            {data.market_summary || 'Market data is currently being processed. No summary available.'}
          </p>
        </div>
      </div>

      {/* 3: KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors flex flex-col h-32">
          <div className="text-textMuted text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
            <PieChartIcon className="w-4 h-4 text-primary"/> Market Size
          </div>
          <div className="text-3xl font-bold text-white leading-tight mt-auto truncate" title={data.market_size}>
            {data.market_size || 'Unknown'}
          </div>
        </div>
        
        <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors relative overflow-hidden flex flex-col h-32">
          <div className="text-textMuted text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2 z-10">
            <TrendingUp className="w-4 h-4 text-success"/> Growth Rate
          </div>
          <div className="text-3xl font-bold text-success leading-tight mt-auto z-10 truncate" title={data.growth_rate}>
            {data.growth_rate || 'Unknown'}
          </div>
          {growthNum > 0 && (
            <div className="absolute inset-0 pt-16 px-4 opacity-20 pointer-events-none">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                    <Cell fill="#22C55E" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors flex flex-col h-32">
          <div className="text-textMuted text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
            <Target className="w-4 h-4 text-warning"/> Market Maturity
          </div>
          <div className="text-3xl font-bold text-white leading-tight capitalize mt-auto truncate" title={data.market_maturity}>
            {data.market_maturity || 'Unknown'}
          </div>
        </div>
      </div>

      {/* 4: Market Trends (Engaging Trend Cards) */}
      {Array.isArray(data.market_trends) && data.market_trends.length > 0 && (
        <div className="space-y-5">
          <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
            <Zap className="w-4 h-4 text-warning"/> Strategic Market Trends
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {data.market_trends.map((trend, i) => (
              <div key={i} className="glass-panel p-6 rounded-2xl border-t-4 border-t-primary/70 hover:-translate-y-1 transition-transform duration-300 shadow-lg bg-gradient-to-b from-surface to-background">
                <div className="text-[10px] text-primary font-black uppercase tracking-widest mb-3 opacity-80">Trend 0{i + 1}</div>
                <p className="text-sm text-textMain leading-relaxed font-medium">{trend}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 5: Strategic Opportunities */}
        {Array.isArray(data.opportunities) && data.opportunities.length > 0 && (
          <div className="space-y-5">
            <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
              <Lightbulb className="w-4 h-4 text-success"/> Actionable Opportunities
            </h3>
            <div className="flex flex-col gap-4">
              {data.opportunities.map((opp, i) => (
                <div key={i} className="flex gap-4 p-5 rounded-2xl bg-success/5 border border-success/20 items-start shadow-sm transition-colors hover:bg-success/10">
                  <div className="w-8 h-8 rounded-full bg-success/20 text-success flex items-center justify-center flex-shrink-0 font-bold text-sm">
                    {i + 1}
                  </div>
                  <p className="text-sm text-textMain leading-relaxed mt-1 font-medium">{opp}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 6: Market Challenges */}
        {Array.isArray(data.challenges) && data.challenges.length > 0 && (
          <div className="space-y-5">
            <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
              <AlertTriangle className="w-4 h-4 text-error"/> Critical Risks & Challenges
            </h3>
            <div className="flex flex-col gap-4">
              {data.challenges.map((chal, i) => (
                <div key={i} className="flex gap-4 p-5 rounded-2xl bg-error/5 border border-error/20 items-start shadow-sm transition-colors hover:bg-error/10">
                  <div className="w-8 h-8 rounded-full bg-error/20 text-error flex items-center justify-center flex-shrink-0 font-bold text-sm">
                    !
                  </div>
                  <p className="text-sm text-textMain leading-relaxed mt-1 font-medium">{chal}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 7: Evidence */}
      {Array.isArray(data.sources) && data.sources.length > 0 && (
        <div className="pt-8 mt-4 border-t border-border/30">
          <h3 className="text-[10px] font-bold text-textDim uppercase tracking-widest mb-4 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" /> Evidence used for this analysis
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.sources.map((src, i) => {
              let hostname = '';
              try {
                hostname = new URL(src).hostname.replace('www.', '');
              } catch (e) {
                return null;
              }
              return (
                <a 
                  key={i} 
                  href={src} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="flex items-center gap-1.5 text-xs bg-surface/40 border border-border/50 px-3 py-2 rounded-xl text-textMuted hover:text-white hover:bg-surface transition-colors truncate max-w-[220px]"
                >
                  <Link2 className="w-3 h-3 flex-shrink-0" />
                  {hostname}
                </a>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default MarketSection;
