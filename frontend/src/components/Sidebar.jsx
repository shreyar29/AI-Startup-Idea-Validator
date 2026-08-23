import React, { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';

const Sidebar = ({ activeSection, sessionId }) => {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const SCROLL_OFFSET_PX = 100;

  const sections = [
    { id: 'overview', label: 'Executive Summary' },
    { id: 'web-search', label: 'Research Evidence' },
    { id: 'market', label: 'Market Intelligence' },
    { id: 'customers', label: 'Customer Intelligence' },
    { id: 'competitors', label: 'Competitive Intelligence' },
    { id: 'risks', label: 'Risk Matrix' },
    { id: 'swot', label: 'SWOT Analysis' },
    { id: 'mvp', label: 'MVP Roadmap' },
    { id: 'gtm', label: 'Go-To-Market' },
    { id: 'comparison', label: 'Final Strategy' }
  ];

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - SCROLL_OFFSET_PX;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  const handleDownloadPdf = async () => {
    if (!sessionId) return;
    setDownloading(true);
    setError(null);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')}/api/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      if (!res.ok) throw new Error('Failed to generate report');
      const data = await res.json();
      
      const downloadUrl = `${import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')}${data.download_url}`;
      
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = 'venturelens_report.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
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
          const isActive = activeSection === section.id;
          return (
            <button
              key={section.id}
              onClick={() => scrollTo(section.id)}
              aria-current={isActive ? 'step' : undefined}
              className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-primary/10 text-primary' 
                  : 'text-textMuted hover:text-textMain hover:bg-surface'
              }`}
            >
              {section.label}
            </button>
          );
        })}
      </nav>

      {sessionId && (
        <div className="pt-4 border-t border-border space-y-2">
          <button 
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="w-full flex items-center justify-center gap-2 bg-surface hover:bg-surface/80 border border-border text-textMain px-4 py-2.5 rounded-lg text-sm font-bold transition-all disabled:opacity-50"
          >
            {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            {downloading ? 'Generating...' : 'Export PDF'}
          </button>
          {error && <p className="text-xs text-red-400 text-center">{error}</p>}
        </div>
      )}
    </div>
  );
};

export default Sidebar;
