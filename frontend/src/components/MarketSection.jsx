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
  Compass,
  Rocket,
  Scale
} from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer, Cell } from 'recharts';

const MarketSection = ({ data }) => {
  if (!data || Object.keys(data).length === 0) return null;

  const { growthNum, chartData } = React.useMemo(() => {
    let num = 0;
    if (data.growth_rate) {
      const match = String(data.growth_rate).match(/[\d.]+/);
      if (match) {
        num = parseFloat(match[0]) || 0;
      }
    }
    return {
      growthNum: num,
      chartData: [{ name: 'Growth', value: num }]
    };
  }, [data.growth_rate]);

  const evidenceLinks = React.useMemo(() => {
    const rawSources = data.evidence || data.sources || [];
    if (!Array.isArray(rawSources)) return [];
    
    return rawSources.reduce((acc, src) => {
      try {
        const urlObj = new URL(src);
        const hostname = urlObj.hostname.replace(/^www\./, '');
        acc.push({ url: src, hostname });
      } catch (e) {
        // Skip invalid URLs
      }
      return acc;
    }, []);
  }, [data.evidence, data.sources]);


  return (
    <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="space-y-10">
      {/* Section Header */}
      <div className="flex items-center gap-3 border-b border-border/50 pb-4">
        <div className="bg-primary/10 p-2 rounded-xl">
          <Activity className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-textMain tracking-tight">Executive Market Intelligence</h2>
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

      {/* 3: KPI Cards and Market Funnel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Side: Growth & Maturity */}
        <div className="flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors relative overflow-hidden flex flex-col h-auto min-h-[8rem]">
            <div className="text-textMuted text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2 z-10">
              <TrendingUp className="w-4 h-4 text-success"/> Growth Rate
            </div>
            <div className="text-3xl font-bold text-success leading-tight mt-auto z-10" title={data.growth_rate}>
              {data.growth_rate === 'Insufficient verified evidence.' ? 'Evidence insufficient' : (data.growth_rate || 'Unknown')}
            </div>
            {growthNum > 0 && (
              <div className="absolute inset-0 pt-16 px-4 opacity-20 pointer-events-none" aria-hidden="true">
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

          <div className="glass-panel p-6 rounded-2xl border-border/50 hover:bg-surface transition-colors flex flex-col h-auto min-h-[8rem]">
            <div className="text-textMuted text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
              <Target className="w-4 h-4 text-warning"/> Market Maturity
            </div>
            <div className="text-2xl font-bold text-textMain leading-tight capitalize mt-auto" title={data.market_maturity}>
              {data.market_maturity === 'Insufficient verified evidence.' ? 'Evidence insufficient' : (data.market_maturity || 'Unknown')}
            </div>
          </div>
        </div>

        {/* Right Side: Market Funnel */}
        <div className="glass-panel p-6 rounded-2xl border-border/50 bg-gradient-to-br from-surface to-background flex flex-col">
          <div className="text-textMuted text-xs font-bold uppercase tracking-widest mb-6 flex items-center justify-between">
            <span className="flex items-center gap-2"><PieChartIcon className="w-4 h-4 text-primary"/> Market Funnel</span>
            <span className="text-[10px] bg-primary/10 text-primary px-2 py-1 rounded-md cursor-pointer hover:bg-primary/20 transition-colors" title={data.methodology || "No methodology available"}>
              Methodology
            </span>
          </div>
          
          <div className="flex flex-col gap-4 mt-auto">
            {/* TAM */}
            <div className="relative p-4 rounded-xl border border-primary/30 bg-primary/5 flex justify-between items-center overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-2 bg-primary/80"></div>
              <div className="pl-3">
                <div className="text-[10px] text-primary font-bold uppercase tracking-wider mb-1">Total Addressable Market (TAM)</div>
                <div className="text-xl md:text-2xl font-black text-textMain">{data.tam === 'Unknown' ? data.market_size || 'Unknown' : data.tam}</div>
              </div>
            </div>

            {/* SAM */}
            <div className="relative p-4 rounded-xl border border-success/30 bg-success/5 flex justify-between items-center overflow-hidden mx-4">
              <div className="absolute left-0 top-0 bottom-0 w-2 bg-success/80"></div>
              <div className="pl-3">
                <div className="text-[10px] text-success font-bold uppercase tracking-wider mb-1">Serviceable Available Market (SAM)</div>
                <div className="text-lg md:text-xl font-bold text-textMain">{data.sam || 'Unknown'}</div>
              </div>
            </div>

            {/* SOM */}
            <div className="relative p-4 rounded-xl border border-warning/30 bg-warning/5 flex justify-between items-center overflow-hidden mx-8">
              <div className="absolute left-0 top-0 bottom-0 w-2 bg-warning/80"></div>
              <div className="pl-3">
                <div className="text-[10px] text-warning font-bold uppercase tracking-wider mb-1">Serviceable Obtainable Market (SOM)</div>
                <div className="text-md md:text-lg font-bold text-textMain">{data.som || 'Unknown'}</div>
              </div>
            </div>
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
              <div key={trend} className="glass-panel p-6 rounded-2xl border-t-4 border-t-primary/70 hover:-translate-y-1 transition-transform duration-300 shadow-lg bg-gradient-to-b from-surface to-background">
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
                  <p className="text-sm text-textMain leading-relaxed mt-1 font-medium">{typeof opp === 'string' ? opp : opp.description || opp.opportunity || JSON.stringify(opp)}</p>
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
                  <p className="text-sm text-textMain leading-relaxed mt-1 font-medium">{typeof chal === 'string' ? chal : chal.description || chal.challenge || JSON.stringify(chal)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-6">
        {/* Growth Drivers */}
        {Array.isArray(data.growth_drivers) && data.growth_drivers.length > 0 && (
          <div className="space-y-5">
            <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
              <Rocket className="w-4 h-4 text-primary"/> Key Growth Drivers
            </h3>
            <div className="flex flex-col gap-4">
              {data.growth_drivers.map((driver, i) => (
                <div key={i} className="flex gap-4 p-5 rounded-2xl bg-primary/5 border border-primary/20 items-start shadow-sm transition-colors hover:bg-primary/10">
                  <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 font-bold text-sm">
                    {i + 1}
                  </div>
                  <p className="text-sm text-textMain leading-relaxed mt-1 font-medium">{typeof driver === 'string' ? driver : driver.description || driver.driver || JSON.stringify(driver)}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Regulations / Industry Insights */}
        {Array.isArray(data.regulations) && data.regulations.length > 0 && (
          <div className="space-y-5">
            <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-2">
              <Scale className="w-4 h-4 text-warning"/> Regulatory Landscape
            </h3>
            <div className="flex flex-col gap-4">
              {data.regulations.map((reg, i) => (
                <div key={i} className="flex gap-4 p-5 rounded-2xl bg-warning/5 border border-warning/20 items-start shadow-sm transition-colors hover:bg-warning/10">
                  <div className="w-8 h-8 rounded-full bg-warning/20 text-warning flex items-center justify-center flex-shrink-0 font-bold text-sm">
                    §
                  </div>
                  <p className="text-sm text-textMain leading-relaxed mt-1 font-medium">{typeof reg === 'string' ? reg : reg.description || reg.regulation || JSON.stringify(reg)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 7: Evidence */}
      {evidenceLinks.length > 0 && (
        <div className="pt-8 mt-4 border-t border-border/30">
          <h3 className="text-[10px] font-bold text-textDim uppercase tracking-widest mb-4 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" /> Evidence used for this analysis
          </h3>
          <div className="flex flex-wrap gap-2">
            {evidenceLinks.map((src) => (
              <a 
                key={src.url} 
                href={src.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="flex items-center gap-1.5 text-xs bg-surface/40 border border-border/50 px-3 py-2 rounded-xl text-textMuted hover:text-textMain hover:bg-surface transition-colors truncate max-w-[220px]"
              >
                <Link2 className="w-3 h-3 flex-shrink-0" />
                {src.hostname}
              </a>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default MarketSection;
