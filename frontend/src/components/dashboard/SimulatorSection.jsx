import React, { useState } from 'react';
import { useDashboardData } from '../../contexts/DashboardContext';
import { Loader2, Zap, ArrowRight } from 'lucide-react';
import api from '../../services/api';

const SimulatorSection = () => {
  const { data, requestId } = useDashboardData();
  const [assumption, setAssumption] = useState("What if I change my target customers from students to enterprises?");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const reportId = requestId || data?.metadata?.request_id || "demo-uuid";

  const handleSimulate = async () => {
    if (!assumption.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/api/simulator/score', {
        report_id: reportId, assumption
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

  return (
    <div className="my-16 p-[1px] rounded-3xl bg-gradient-to-b from-amber-500/50 via-orange-500/20 to-transparent shadow-2xl">
      <div className="bg-[#0f1219] rounded-[23px] p-8 md:p-10 relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-amber-500/10 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-3">
            <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center border border-amber-500/30">
              <Zap className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">What-If Simulator</h2>
              <p className="text-slate-400 mt-1">Explore alternative startup scenarios by changing an assumption.</p>
            </div>
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
