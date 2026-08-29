import React, { useState } from 'react';
import { useDashboardData } from '../../contexts/DashboardContext';
import { Loader2, Zap, ArrowRight, PenTool, Search, RefreshCw, BarChart2, Star, Sparkles } from 'lucide-react';
import api from '../../services/api';

const SimulatorSection = () => {
  const { data, requestId } = useDashboardData();
  const [assumption, setAssumption] = useState("What if I change my target customers from students to enterprises?");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  
  const reportId = requestId || data?.metadata?.request_id || "demo-uuid";

  const handleSimulate = async () => {
    if (!assumption.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/api/simulator/score', {
        report_id: reportId, 
        assumption,
        startup_idea: data?.metadata?.startup_idea,
        current_score: data?.startup_score_agent?.overall_score
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderScenarioValue = (current, scenario) => {
    const isNumberStr = (str) => /^\d+%?$/.test(str);
    if (isNumberStr(current) && isNumberStr(scenario)) {
      const currVal = parseInt(current);
      const scenVal = parseInt(scenario);
      if (scenVal > currVal) return <span className="text-emerald-400">{scenario}</span>;
      if (scenVal < currVal) return <span className="text-red-400">{scenario}</span>;
    }
    
    // For qualitative things like "Medium" vs "High" risk
    if (current === 'Medium' && scenario === 'High') return <span className="text-red-400">{scenario}</span>;
    if (current === 'High' && scenario === 'Medium') return <span className="text-emerald-400">{scenario}</span>;
    if (current === 'Low' && scenario === 'High') return <span className="text-red-400">{scenario}</span>;
    if (current === 'High' && scenario === 'Low') return <span className="text-emerald-400">{scenario}</span>;
    
    return <span className="text-white">{scenario}</span>;
  };

  if (!isExpanded) {
    return (
      <div className="relative w-full max-w-7xl mx-auto my-16 px-4 xl:px-0">
        <div className="relative border border-amber-500/60 rounded-3xl p-10 md:p-16 flex flex-col items-center justify-center bg-[#070b14]/80 backdrop-blur-xl shadow-[0_0_50px_rgba(245,158,11,0.15)] overflow-hidden">
          
          {/* Top badge */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-amber-500/20 border border-amber-500/50 flex items-center justify-center shadow-[0_0_20px_rgba(245,158,11,0.5)] z-20">
            <Zap className="w-5 h-5 text-amber-400" />
          </div>

          {/* Golden glows */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-amber-500/10 blur-[100px] rounded-full pointer-events-none" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-amber-600/10 blur-[120px] rounded-full pointer-events-none" />

          {/* Bottom Arc */}
          <div className="absolute bottom-[20%] left-1/2 -translate-x-1/2 w-[120%] md:w-[80%] h-[500px] rounded-[100%] border-b-[2px] border-amber-500/30 shadow-[0_20px_50px_rgba(245,158,11,0.2)] pointer-events-none" />
          
          <div className="relative z-10 text-center mb-12 w-full">
            <h2 className="text-3xl md:text-4xl font-bold text-amber-400 mb-3 drop-shadow-[0_0_10px_rgba(245,158,11,0.3)]">What-If Simulator</h2>
            <p className="text-slate-300 text-sm md:text-base">Explore alternative startup scenarios by changing an assumption.</p>
          </div>

          {/* Steps Process */}
          <div className="relative z-10 flex flex-wrap justify-center items-center gap-4 md:gap-8 lg:gap-12 mb-16 w-full max-w-4xl">
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-[24px] left-[10%] right-[10%] h-[1px] border-t border-dashed border-amber-500/30 -z-10" />
            
            {[
              { icon: PenTool, text: 'Change ONE\nassumption', color: 'text-purple-400', border: 'border-purple-500/30' },
              { icon: Search, text: 'Identify affected\nanalyses', color: 'text-blue-400', border: 'border-blue-500/30' },
              { icon: RefreshCw, text: 'Re-run relevant\nanalysis', color: 'text-cyan-400', border: 'border-cyan-500/30' },
              { icon: BarChart2, text: 'Compare with\noriginal', color: 'text-orange-400', border: 'border-orange-500/30' },
              { icon: Star, text: 'New\nrecommendation', color: 'text-yellow-400', border: 'border-yellow-500/30' }
            ].map((step, i) => (
              <div key={i} className="flex flex-col items-center w-[120px] text-center">
                <div className={`w-12 h-12 rounded-full border ${step.border} bg-[#0a0f1e] flex items-center justify-center mb-4 shadow-[0_0_15px_rgba(255,255,255,0.05)]`}>
                  <step.icon className={`w-5 h-5 ${step.color}`} />
                </div>
                <span className="text-[11px] text-slate-400 leading-tight whitespace-pre-wrap font-medium">{step.text}</span>
              </div>
            ))}
          </div>

          <div className="relative z-10 text-center">
            <h3 className="text-3xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-100 to-amber-200 mb-8 drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">
              Is your idea ahead of time?
            </h3>
            
            <button 
              onClick={() => setIsExpanded(true)}
              className="group flex items-center justify-center gap-2 mx-auto px-8 py-3 bg-transparent border border-amber-500/50 hover:bg-amber-500/10 text-amber-400 rounded-lg font-bold tracking-wider text-sm transition-all shadow-[0_0_20px_rgba(245,158,11,0.15)] hover:shadow-[0_0_30px_rgba(245,158,11,0.3)]"
            >
              LET'S SIMULATE
              <Sparkles className="w-4 h-4 group-hover:rotate-12 transition-transform" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="my-16 p-[1px] rounded-3xl bg-gradient-to-b from-amber-500/50 via-orange-500/20 to-transparent shadow-2xl transition-all duration-500 animate-in fade-in slide-in-from-top-4">
      <div className="bg-[#0f1219] rounded-[23px] p-8 md:p-10 relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-amber-500/10 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center border border-amber-500/30">
                <Zap className="w-6 h-6 text-amber-400" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white">What-If Simulator</h2>
                <p className="text-slate-400 mt-1">Explore alternative startup scenarios by changing an assumption.</p>
              </div>
            </div>
            <button 
              onClick={() => setIsExpanded(false)}
              className="text-slate-400 hover:text-white px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 text-sm font-medium"
            >
              Close Simulator
            </button>
          </div>
          
          <div className="mt-10 grid grid-cols-1 xl:grid-cols-2 gap-10">
            {/* Input Form */}
            <div className="flex flex-col space-y-6">
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <label className="block text-sm font-medium text-slate-300 mb-3">
                  Change ONE assumption:
                </label>
                <textarea 
                  value={assumption}
                  onChange={(e) => setAssumption(e.target.value)}
                  placeholder="e.g. What if I reduce my price from $99 to $49?"
                  className="w-full h-32 bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-amber-500 outline-none resize-none mb-4"
                />
                
                <div className="flex flex-wrap gap-2 mb-6">
                  <button onClick={() => setAssumption("What if I change my target customers from students to enterprises?")} className="text-xs px-3 py-1.5 rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors">
                    Target Enterprise
                  </button>
                  <button onClick={() => setAssumption("What if I reduce my price from $99 to $49?")} className="text-xs px-3 py-1.5 rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors">
                    Reduce Price
                  </button>
                  <button onClick={() => setAssumption("What if my main competitor launches a similar feature?")} className="text-xs px-3 py-1.5 rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors">
                    Competitor Threat
                  </button>
                </div>

                <button 
                  onClick={handleSimulate}
                  disabled={loading || !assumption.trim()}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                  Simulate Scenario
                </button>
              </div>
              <div className="text-xs text-slate-500 flex flex-col space-y-1 ml-2">
                <span className="flex items-center"><ArrowRight className="w-3 h-3 mr-1" /> Identifies affected agents</span>
                <span className="flex items-center"><ArrowRight className="w-3 h-3 mr-1" /> Re-runs relevant analysis logic</span>
                <span className="flex items-center"><ArrowRight className="w-3 h-3 mr-1" /> Compares with original metrics</span>
              </div>
            </div>
            
            {/* Results Panel */}
            <div>
              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-6 h-full flex flex-col relative overflow-hidden">
                {loading && (
                  <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center rounded-2xl">
                    <Loader2 className="w-8 h-8 text-amber-500 animate-spin mb-4" />
                    <span className="text-sm font-medium text-amber-400">Re-evaluating AI Mesh Analysis...</span>
                  </div>
                )}
                
                <h3 className="text-lg font-semibold text-white mb-6">Simulation Impact</h3>
                
                {error ? (
                  <div className="text-red-400 text-sm bg-red-400/10 p-4 rounded-xl">{error}</div>
                ) : result ? (
                  <div className="flex-grow flex flex-col">
                    
                    {/* Metrics Table */}
                    <div className="overflow-hidden rounded-xl border border-slate-700 mb-6">
                      <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-slate-800 text-slate-400 uppercase text-xs">
                          <tr>
                            <th className="px-4 py-3 font-medium">Metric</th>
                            <th className="px-4 py-3 font-medium">Current</th>
                            <th className="px-4 py-3 font-medium">Scenario</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50 bg-slate-900/50">
                          {result.metrics?.map((m, idx) => (
                            <tr key={idx} className="hover:bg-slate-800/50 transition-colors">
                              <td className="px-4 py-3 font-medium text-white">{m.name}</td>
                              <td className="px-4 py-3 text-slate-400">{m.current}</td>
                              <td className="px-4 py-3 font-semibold">
                                {renderScenarioValue(m.current, m.scenario)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    
                    {/* Recommendations and Affected Areas */}
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Affected Areas</h4>
                        <div className="flex flex-wrap gap-2">
                          {result.affected_areas?.map((area, i) => (
                            <span key={i} className="px-2.5 py-1 rounded-md bg-white/5 border border-white/10 text-xs font-medium text-amber-200/80">
                              {area}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
                        <h4 className="text-xs font-bold text-amber-500 uppercase tracking-wider mb-2">New Recommendation</h4>
                        <p className="text-sm text-slate-300 leading-relaxed">
                          {result.recommendation}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex-grow flex items-center justify-center text-slate-500 text-sm text-center">
                    Enter an assumption and click simulate to view the re-evaluated metrics.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(SimulatorSection);
