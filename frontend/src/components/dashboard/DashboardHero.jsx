import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, FileText, Presentation } from 'lucide-react';
import { useDashboardData } from '../../contexts/DashboardContext';

const DashboardHero = () => {
  const navigate = useNavigate();
  const { data, requestId, idea, handleExport } = useDashboardData();

  const onVeraClick = () => {
    navigate('/vera', { state: { sessionId: requestId || data?.metadata?.request_id } });
  };

  return (
    <div className="relative w-full overflow-hidden mb-12 flex flex-col items-center justify-center pt-16 pb-32">
      {/* Earth Curve Background */}
      <div className="absolute top-[80%] left-1/2 -translate-x-1/2 w-[200vw] h-[1000px] bg-transparent border-t-[3px] border-blue-500/50 rounded-[100%] shadow-[0_-20px_100px_rgba(59,130,246,0.3)] pointer-events-none" />
      <div className="absolute top-[80%] left-1/2 -translate-x-1/2 w-[200vw] h-[1000px] bg-gradient-to-b from-blue-900/40 to-transparent rounded-[100%] pointer-events-none blur-xl" />
      
      {/* Stars/Glows */}
      <div className="absolute top-10 left-10 w-32 h-32 bg-blue-500/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute top-20 right-20 w-48 h-48 bg-indigo-500/20 rounded-full blur-[100px] pointer-events-none" />

      {/* Decorative Rocket (Mockup styling element) */}
      <div className="absolute right-[10%] top-[10%] opacity-20 pointer-events-none transform rotate-12 scale-150">
        <Sparkles className="w-32 h-32 text-blue-400" />
      </div>

      <div className="relative z-10 flex flex-col items-center text-center max-w-3xl mx-auto px-4">
        
        {/* Executive Summary Tag */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-[1px] bg-gradient-to-r from-transparent to-blue-400" />
          <span className="text-blue-300 uppercase tracking-[0.3em] text-xs font-semibold drop-shadow-[0_0_8px_rgba(96,165,250,0.8)]">
            EXECUTIVE SUMMARY
          </span>
          <div className="w-12 h-[1px] bg-gradient-to-l from-transparent to-blue-400" />
        </div>

        {/* Main Title */}
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white mb-6 tracking-tight">
          AI Startup Intelligence Report
        </h1>
        
        {/* Subtitle */}
        <p className="text-slate-300 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-10">
          Comprehensive founder intelligence across market, customer, competition, risk, MVP and GTM dimensions.
        </p>

        {/* Buttons */}
        <div className="flex flex-wrap justify-center items-center gap-4">
          <button
            onClick={() => handleExport(idea, data, 'pdf')}
            className="flex items-center gap-2 px-6 py-3 bg-transparent border border-blue-500/50 hover:bg-blue-500/10 rounded-xl transition-all text-white backdrop-blur-sm shadow-[0_0_15px_rgba(59,130,246,0.1)] hover:shadow-[0_0_20px_rgba(59,130,246,0.3)]"
          >
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="font-bold text-xs tracking-wider">EXPORT PDF</span>
          </button>

          <button
            onClick={() => handleExport(idea, data, 'ppt')}
            className="flex items-center gap-2 px-6 py-3 bg-transparent border border-purple-500/50 hover:bg-purple-500/10 rounded-xl transition-all text-white backdrop-blur-sm shadow-[0_0_15px_rgba(168,85,247,0.1)] hover:shadow-[0_0_20px_rgba(168,85,247,0.3)]"
          >
            <Presentation className="w-4 h-4 text-purple-400" />
            <span className="font-bold text-xs tracking-wider">EXPORT PPT</span>
          </button>

          <button
            onClick={onVeraClick}
            className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-500 text-white rounded-xl hover:from-blue-500 hover:to-indigo-400 transition-all shadow-[0_0_30px_rgba(79,70,229,0.5)] hover:shadow-[0_0_40px_rgba(79,70,229,0.7)] transform hover:-translate-y-0.5"
          >
            <Sparkles className="w-4 h-4" />
            <span className="font-bold text-xs tracking-wider">LAUNCH VERA</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default React.memo(DashboardHero);
