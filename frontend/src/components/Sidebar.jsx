import React, { useState } from 'react';
import { Download, Loader2, Home } from 'lucide-react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';

const Sidebar = ({ activeSection, sessionId, onDownload }) => {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { reportId } = useParams();
  const activeId = sessionId || reportId;

  const sections = [
    { id: 'summary', label: 'EXECUTIVE SUMMARY' },
    { id: 'research', label: 'RESEARCH EVIDENCE' },
    { id: 'market', label: 'MARKET INTELLIGENCE' },
    { id: 'customer', label: 'CUSTOMER INTELLIGENCE' },
    { id: 'competitor', label: 'COMPETITIVE INTELLIGENCE' },
    { id: 'risk', label: 'RISK CENTER' },
    { id: 'swot', label: 'SWOT ANALYSIS' },
    { id: 'mvp', label: 'MVP STRATEGY' },
    { id: 'gtm', label: 'GO-TO-MARKET' }
  ];

  const handleNavigate = (id) => {
    if (activeId) {
      navigate(`/report/${activeId}/${id}`);
    }
  };

  const handleDownloadPdf = async () => {
    if (!onDownload) return;
    setDownloading(true);
    setError(null);
    try {
      await onDownload();
    } catch (err) {
      console.error('Download error:', err);
      setError('PDF generation failed.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="sticky top-24">
      <nav className="space-y-2 mb-8" aria-label="Dashboard sections">
        {sections.map(section => {
          // Check if current route ends with section.id or if on dashboard root and it's the dashboard hub
          const isActive = location.pathname.endsWith(`/${section.id}`);
          return (
            <button
              key={section.id}
              onClick={() => handleNavigate(section.id)}
              aria-current={isActive ? 'page' : undefined}
              className={`w-full text-left px-4 py-3 rounded-xl text-xs font-bold tracking-wider transition-all duration-300 ${
                isActive 
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.15)]' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              {section.label}
            </button>
          );
        })}
      </nav>

      {sessionId && (
        <div className="pt-6 border-t border-slate-800 space-y-3">
          <button 
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_20px_rgba(37,99,235,0.2)] hover:shadow-[0_0_25px_rgba(37,99,235,0.4)] px-4 py-3 rounded-xl text-sm font-bold transition-all duration-300 disabled:opacity-50"
          >
            {downloading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
            {downloading ? 'GENERATING...' : 'EXPORT PDF'}
          </button>
          {error && <p className="text-xs text-red-400 text-center bg-red-400/10 py-2 rounded-lg">{error}</p>}
        </div>
      )}
    </div>
  );
};

export default Sidebar;
