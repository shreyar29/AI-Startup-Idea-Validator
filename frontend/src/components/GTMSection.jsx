import React from 'react';
import { motion } from 'framer-motion';
import { Rocket, Megaphone, Users, Target, CheckCircle2 } from 'lucide-react';

const GTMSection = ({ data }) => {
  if (!data) return null;

  const channels = Array.isArray(data.acquisition_channels) ? data.acquisition_channels : Array.isArray(data.launch_channels) ? data.launch_channels : [];
  const growthHacks = Array.isArray(data.launch_plan) ? data.launch_plan : Array.isArray(data.growth_hacks) ? data.growth_hacks : [];
  const targetAudience = typeof data.target_segment === 'string' && data.target_segment 
    ? [data.target_segment] 
    : typeof data.target_segment === 'object' && data.target_segment !== null && !Array.isArray(data.target_segment)
      ? [data.target_segment]
    : Array.isArray(data.target_segment)
      ? data.target_segment
    : Array.isArray(data.target_audience) 
      ? data.target_audience 
      : [];

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3 mb-6 border-b border-white/5 pb-4">
        <div className="p-2.5 bg-orange-500/10 rounded-xl text-orange-500">
          <Rocket className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-textMain tracking-tight">Go-To-Market Strategy</h2>
          <p className="text-sm text-textMuted mt-1">Acquisition channels and growth tactics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Launch Channels */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/5 bg-surface/30">
          <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
            <Megaphone className="w-5 h-5 text-orange-400" />
            Primary Launch Channels
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {channels.map((channel, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-black/20 border border-white/5 p-4 rounded-xl shadow-inner"
              >
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-4 h-4 text-orange-400" />
                  <h4 className="font-bold text-textMain text-sm">
                    {typeof channel === 'string' ? channel : channel.channel || channel.name}
                  </h4>
                </div>
                {typeof channel === 'object' && channel.strategy && (
                  <p className="text-xs text-textMuted leading-relaxed pl-6">
                    {channel.strategy}
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Audience / Growth Hacks */}
        <div className="space-y-6 lg:col-span-1">
          {growthHacks.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
                <Target className="w-5 h-5 text-green-400" />
                Growth Tactics
              </h3>
              <ul className="space-y-3">
                {growthHacks.map((hack, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-textMuted">
                    <span className="text-green-400 mt-0.5 font-bold">⚡</span>
                    <span>{typeof hack === 'string' ? hack : hack.tactic || hack.description || JSON.stringify(hack)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {targetAudience.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-white/5">
              <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-4">
                <Users className="w-5 h-5 text-blue-400" />
                Early Adopters
              </h3>
              <div className="flex flex-wrap gap-2">
                {targetAudience.map((aud, i) => (
                  <span key={i} className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-bold rounded-full">
                    {typeof aud === 'string' ? aud : aud.segment || aud.name || aud.description || JSON.stringify(aud)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 90-Day Action Plan / Roadmap */}
      {data.action_plan && (data.action_plan.first_30_days?.length > 0 || data.action_plan.first_90_days?.length > 0) && (
        <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-surface/30 mt-6">
          <h3 className="flex items-center gap-2 text-lg font-bold text-textMain mb-6">
            <Rocket className="w-5 h-5 text-purple-400" />
            90-Day Execution Roadmap
          </h3>
          <div className="grid md:grid-cols-2 gap-6 relative">
            
            {/* 30 Days */}
            {data.action_plan.first_30_days?.length > 0 && (
              <div className="relative pl-6 border-l-2 border-purple-500/30">
                <div className="absolute w-4 h-4 bg-purple-500 rounded-full -left-[9px] top-0 shadow-[0_0_10px_rgba(168,85,247,0.5)]"></div>
                <h4 className="font-bold text-purple-400 text-sm tracking-wider uppercase mb-4">First 30 Days</h4>
                <ul className="space-y-3">
                  {data.action_plan.first_30_days.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-textMuted bg-black/20 p-3 rounded-lg border border-white/5">
                      <span className="text-purple-400 font-bold mt-0.5">•</span>
                      <span>{typeof item === 'string' ? item : item.description || JSON.stringify(item)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 90 Days */}
            {data.action_plan.first_90_days?.length > 0 && (
              <div className="relative pl-6 border-l-2 border-indigo-500/30">
                <div className="absolute w-4 h-4 bg-indigo-500 rounded-full -left-[9px] top-0 shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                <h4 className="font-bold text-indigo-400 text-sm tracking-wider uppercase mb-4">First 90 Days</h4>
                <ul className="space-y-3">
                  {data.action_plan.first_90_days.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-textMuted bg-black/20 p-3 rounded-lg border border-white/5">
                      <span className="text-indigo-400 font-bold mt-0.5">•</span>
                      <span>{typeof item === 'string' ? item : item.description || JSON.stringify(item)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
};

export default GTMSection;
