import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, Sparkles, Loader2 } from 'lucide-react';
import { useDashboardData } from '../../contexts/DashboardContext';

const DashboardActions = () => {
  const navigate = useNavigate();
  const { data, requestId, idea, handleExport } = useDashboardData();
  const [isExporting, setIsExporting] = React.useState(false);

  const onExportClick = async () => {
    setIsExporting(true);
    await handleExport(idea, data);
    setIsExporting(false);
  };

  const onVeraClick = () => {
    navigate('/vera', { state: { sessionId: requestId || data?.metadata?.request_id } });
  };

  return (
    <div className="mt-8 flex justify-between items-center bg-surface/30 p-6 rounded-2xl border border-white/5">
      <div className="flex gap-4">
        <button
          onClick={() => handleExport(idea, data, 'pdf')}
          className="flex items-center gap-2 px-6 py-3 bg-surface hover:bg-surface/80 border border-border rounded-xl transition-all"
        >
          <Download className="w-5 h-5 text-textMuted" />
          <span className="font-medium">Export PDF</span>
        </button>
        <button
          onClick={() => handleExport(idea, data, 'ppt')}
          className="flex items-center gap-2 px-6 py-3 bg-surface hover:bg-surface/80 border border-border rounded-xl transition-all"
        >
          <Download className="w-5 h-5 text-textMuted" />
          <span className="font-medium">Export Pitch Deck</span>
        </button>
      </div>
      
      <button
        onClick={onVeraClick}
        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-500 hover:to-indigo-500 transition-all shadow-lg shadow-blue-500/25"
      >
        <Sparkles className="w-5 h-5" />
        <span>Open AI Co-Founder Workspace</span>
      </button>
    </div>
  );
};

export default React.memo(DashboardActions);
