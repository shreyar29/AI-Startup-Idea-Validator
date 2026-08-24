import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, ShieldAlert, Zap, Target, Crosshair, Shield, Activity, Plus } from 'lucide-react';
import { useDashboardData } from '../contexts/DashboardContext';
import { useWorkspaceActions } from '../hooks/useWorkspaceActions';

const SWOTSection = ({ data }) => {
  const { requestId, idea } = useDashboardData();
  const { handleAddTask, isAddingTask } = useWorkspaceActions(requestId, idea);
  
  if (!data) return null;
  
  const [activeTowsQuad, setActiveTowsQuad] = useState('so');

  const categories = [
    { title: 'Strengths', key: 'strengths', icon: Zap, color: 'text-green-400', bg: 'bg-green-400/10', border: 'border-green-400/20' },
    { title: 'Weaknesses', key: 'weaknesses', icon: ArrowDownRight, color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20' },
    { title: 'Opportunities', key: 'opportunities', icon: ArrowUpRight, color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20' },
    { title: 'Threats', key: 'threats', icon: ShieldAlert, color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/20' }
  ];

  const towsTabs = [
    { id: 'so', title: 'S-O Strategies', desc: 'Maxi-Maxi: Use strengths to maximize opportunities', icon: Target, color: 'text-emerald-400', bg: 'bg-emerald-400/10', activeClass: 'bg-surface border-emerald-500/50 shadow-lg shadow-emerald-500/10' },
    { id: 'wo', title: 'W-O Strategies', desc: 'Mini-Maxi: Improve weaknesses by taking advantage of opportunities', icon: Crosshair, color: 'text-cyan-400', bg: 'bg-cyan-400/10', activeClass: 'bg-surface border-cyan-500/50 shadow-lg shadow-cyan-500/10' },
    { id: 'st', title: 'S-T Strategies', desc: 'Maxi-Mini: Use strengths to minimize threats', icon: Shield, color: 'text-amber-400', bg: 'bg-amber-400/10', activeClass: 'bg-surface border-amber-500/50 shadow-lg shadow-amber-500/10' },
    { id: 'wt', title: 'W-T Strategies', desc: 'Mini-Mini: Defensive strategies to minimize weaknesses and avoid threats', icon: Activity, color: 'text-rose-400', bg: 'bg-rose-400/10', activeClass: 'bg-surface border-rose-500/50 shadow-lg shadow-rose-500/10' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-white/5 pb-4">
        <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
          <Zap className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">SWOT & TOWS Analysis</h2>
          <p className="text-sm text-textMuted mt-1">Strategic evaluation mapping internal factors against external environment</p>
        </div>
      </div>

      {/* Standard SWOT Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {categories.map((cat, i) => {
          const items = Array.isArray(data[cat.key]) ? data[cat.key] : [];

          return (
            <motion.div
              key={cat.key}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={`glass-panel p-6 rounded-2xl border transition-all ${cat.border} hover:bg-surface/80 flex flex-col h-full`}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-lg ${cat.bg} ${cat.color}`}>
                  <cat.icon className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-textMain">{cat.title}</h3>
                <div className="ml-auto text-xs font-medium text-textMuted bg-surface/50 px-2 py-1 rounded-md">
                  {items.length} identified
                </div>
              </div>
              <ul className="space-y-3 flex-grow">
                {items.length > 0 ? items.map((item, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm text-textMuted bg-black/20 p-3 rounded-xl shadow-inner border border-white/5">
                    <span className={`mt-0.5 font-bold ${cat.color}`}>•</span>
                    <span className="leading-relaxed w-full">
                      {typeof item === 'string' 
                        ? item 
                        : (
                          <div className="flex flex-col gap-1.5 w-full">
                            <div className="flex justify-between items-start gap-2 w-full">
                              <span className="text-textMain font-medium">{item.insight || item.title || item.factor || item.name || item.description || ''}</span>
                              {item.impact && (
                                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border flex-shrink-0 ${
                                  item.impact === 'Critical' ? 'bg-error/10 border-error/30 text-error' :
                                  item.impact === 'High' ? 'bg-warning/10 border-warning/30 text-warning' :
                                  item.impact === 'Medium' ? 'bg-primary/10 border-primary/30 text-primary' :
                                  'bg-surface/50 border-border/50 text-textMuted'
                                }`}>
                                  {item.impact}
                                </span>
                              )}
                            </div>
                            {item.evidence && item.evidence.length > 0 && (
                              <div className="text-[10px] text-textMuted mt-1 border-l-2 border-border/50 pl-2">
                                {item.evidence.join(', ')}
                              </div>
                            )}
                          </div>
                        )
                      }
                    </span>
                  </li>
                )) : (
                  <li className="flex items-center justify-center h-full text-sm text-textDim italic py-4">
                    No {cat.title.toLowerCase()} identified.
                  </li>
                )}
              </ul>
            </motion.div>
          );
        })}
      </div>

      {/* Actionable TOWS Matrix */}
      {data.tows_matrix && Object.keys(data.tows_matrix).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 pt-8 border-t border-white/5"
        >
          <div className="mb-6">
            <h3 className="text-xl font-bold text-textMain mb-2">TOWS Action Matrix</h3>
            <p className="text-sm text-textMuted">Translating SWOT factors into actionable strategic directives.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
            {towsTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTowsQuad(tab.id)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  activeTowsQuad === tab.id 
                    ? tab.activeClass
                    : 'bg-surface/30 border-white/5 hover:bg-surface/60'
                }`}
              >
                <div className={`p-2 rounded-lg ${tab.bg} ${tab.color} w-fit mb-3`}>
                  <tab.icon className="w-5 h-5" />
                </div>
                <h4 className={`font-bold mb-1 ${activeTowsQuad === tab.id ? 'text-textMain' : 'text-textMuted'}`}>
                  {tab.title}
                </h4>
                <p className="text-[11px] text-textDim leading-snug">{tab.desc}</p>
              </button>
            ))}
          </div>

          <div className="glass-panel p-6 rounded-2xl border-white/10 relative overflow-hidden min-h-[250px]">
            <AnimatePresence mode="wait">
              {towsTabs.map((tab) => activeTowsQuad === tab.id && (
                <motion.div
                  key={tab.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-4"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <tab.icon className={`w-6 h-6 ${tab.color}`} />
                    <h3 className="text-lg font-bold text-textMain">Recommended Actions</h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.tows_matrix[tab.id]?.length > 0 ? (
                      data.tows_matrix[tab.id].map((action, idx) => (
                        <div key={idx} className="bg-black/20 p-5 rounded-xl border border-white/5 group hover:border-primary/30 transition-all flex flex-col h-full">
                          <div className="flex justify-between items-start gap-4 mb-3">
                            <h4 className="text-sm font-semibold text-textMain leading-relaxed">
                              {action.action}
                            </h4>
                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border flex-shrink-0 ${
                              action.impact === 'Critical' ? 'bg-error/10 border-error/30 text-error' :
                              action.impact === 'High' ? 'bg-warning/10 border-warning/30 text-warning' :
                              action.impact === 'Medium' ? 'bg-primary/10 border-primary/30 text-primary' :
                              'bg-surface/50 border-border/50 text-textMuted'
                            }`}>
                              {action.impact} Impact
                            </span>
                          </div>
                          
                          <div className="mt-auto pt-4 flex justify-end">
                            <button 
                              onClick={() => {
                                const btn = document.getElementById(`btn-${tab.id}-${idx}`);
                                btn.innerText = "Added ✓";
                                btn.classList.add("text-green-400");
                                handleAddTask(
                                  `Execute ${tab.id.toUpperCase()} Strategy`, 
                                  action.action, 
                                  { agent: 'swot', module: 'tows', strategy: tab.id, impact: action.impact }
                                );
                              }}
                              id={`btn-${tab.id}-${idx}`}
                              disabled={isAddingTask}
                              className="flex items-center gap-1.5 text-xs font-medium text-primary hover:text-primaryLight transition-colors disabled:opacity-50"
                            >
                              <Plus className="w-3.5 h-3.5" />
                              Add to Workspace
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="col-span-2 py-8 text-center text-textMuted text-sm italic">
                        No explicit actions generated for this intersection.
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default SWOTSection;
