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
    <div className="relative overflow-hidden rounded-3xl bg-[#0a0f1e] border border-blue-500/20 p-8 shadow-[0_0_40px_rgba(37,99,235,0.1)] mb-12">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-indigo-900/10 to-transparent pointer-events-none" />
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex flex-col xl:flex-row gap-8 justify-between items-start xl:items-center">
        {/* Left */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-300">VentureLens</h2>
            <p className="text-blue-200/70 text-sm font-medium tracking-wide uppercase">Validate. Strategize. Execute.</p>
          </div>
        </div>

        {/* Center */}
        <div className="text-center xl:max-w-2xl">
          <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-3">AI Startup Intelligence Report</h1>
          <p className="text-blue-100/80 text-lg max-w-xl mx-auto leading-relaxed">
            Comprehensive founder intelligence across market, customer, competition, risk, MVP and GTM dimensions.
          </p>
        </div>

        {/* Right */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => handleExport(idea, data, 'pdf')}
            className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all text-white backdrop-blur-sm shadow-[0_0_15px_rgba(255,255,255,0.05)] hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]"
          >
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="font-bold text-xs tracking-wider">EXPORT PDF</span>
          </button>
          <button
            onClick={() => handleExport(idea, data, 'ppt')}
            className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all text-white backdrop-blur-sm shadow-[0_0_15px_rgba(255,255,255,0.05)] hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]"
          >
            <Presentation className="w-4 h-4 text-purple-400" />
            <span className="font-bold text-xs tracking-wider">EXPORT PPT</span>
          </button>
          <button
            onClick={onVeraClick}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-500 hover:to-indigo-500 transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_30px_rgba(37,99,235,0.5)]"
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
