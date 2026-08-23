import React, { useMemo } from 'react';
import { ScoreGauge } from './ScoreGauge';
import { ScoreBreakdown } from './ScoreBreakdown';
import { KPICard } from './KPICard';
import { InsightCard } from './InsightCard';
import { StrengthWeaknessCard } from './StrengthWeaknessCard';
import { Sparkles, Activity } from 'lucide-react';
import { calculatePillars, generateVeraInsight, getScoreInterpretation, getInvestmentReadiness } from '../../utils/scoreUtils';

const StartupScoreSection = ({ data }) => {
  if (!data) return null;

  const { strongest, weakest } = useMemo(() => calculatePillars(data), [data]);
  const verasInsight = useMemo(() => generateVeraInsight(strongest, weakest), [strongest, weakest]);
  
  const overallScoreInterpretation = getScoreInterpretation(data.overall_score);
  const investmentReadiness = data.investment_readiness || getInvestmentReadiness(data.overall_score);

  return (
    <div className="w-full space-y-8 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-vera-cyan/10 flex items-center justify-center border border-vera-cyan/20">
          <Activity className="w-5 h-5 text-vera-cyan" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Executive Scorecard</h2>
          <p className="text-sm text-textMuted font-medium mt-1">Holistic viability analysis and readiness metrics</p>
        </div>
      </div>
      
      {/* Top Row: 4 Dynamic Gauges */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <ScoreGauge 
          score={data.overall_score} 
          title="Investor Score"
          subtitle={data.verdict} 
          size="sm"
        />
        <ScoreGauge 
          score={data.risk_score} 
          title="Risk Resilience"
          subtitle="Higher is safer"
          size="sm"
        />
        <ScoreGauge 
          score={data.market_score} 
          title="Market Opp."
          subtitle="Size & Growth"
          size="sm"
        />
        <ScoreGauge 
          score={data.execution_score} 
          title="Execution"
          subtitle="Feasibility & Scope"
          size="sm"
        />
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-2 gap-4 w-full">
        <KPICard 
          title="AI Confidence" 
          value={data.confidence_level || "N/A"} 
          valueColor="text-blue-400"
        />
        <KPICard 
          title="Investment Readiness" 
          value={investmentReadiness} 
          valueColor="text-purple-400"
        />
      </div>
      
      {/* Visualizations & Explanations */}
      <div className="bg-surface/30 rounded-2xl p-6 border border-white/5 shadow-lg w-full">
        <ScoreBreakdown scores={data} />
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
        <StrengthWeaknessCard type="strength" data={strongest} />
        <StrengthWeaknessCard type="weakness" data={weakest} />
      </div>

      {/* Vera's Insight */}
      <InsightCard 
        title="Vera's Executive Summary"
        insight={verasInsight}
        icon={Sparkles}
      />
    </div>
  );
};

export default StartupScoreSection;
