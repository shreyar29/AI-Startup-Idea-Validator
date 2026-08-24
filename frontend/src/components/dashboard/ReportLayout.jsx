import React from 'react';
import { useLocation, useNavigate, useParams, Link } from 'react-router-dom';
import { useStartupAnalysis } from '../../hooks/useStartupAnalysis';
import { useReportExport } from '../../hooks/useReportExport';
import { DashboardDataProvider } from '../../contexts/DashboardContext';
import ValidationPipeline from '../ValidationPipeline';
import ErrorState from '../ErrorState';
import { ArrowLeft } from 'lucide-react';
import DashboardActions from './DashboardActions';

const ReportLayout = ({ children, title }) => {
  const navigate = useNavigate();
  const { reportId } = useParams();

  // Load the report data so subpages can access it via useDashboardData
  const { data, loading, error, requestId, retry } = useStartupAnalysis(null, reportId);
  const { handleExport } = useReportExport();

  if (loading) return <ValidationPipeline requestId={requestId || reportId} />;
  
  if (error) return <ErrorState message={error} onRetry={() => navigate('/')} />;
  
  if (!data || !data.metadata) return <ErrorState message="Invalid or no data received" onRetry={() => navigate('/')} />;

  return (
    <DashboardDataProvider 
      data={data} 
      loading={loading} 
      error={error} 
      requestId={requestId} 
      retry={retry}
      idea={data?.metadata?.startup_idea}
      handleExport={handleExport}
    >
      <div className="min-h-screen bg-[#020617] text-slate-50 pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Breadcrumbs & Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
              <Link to={`/report/${reportId}`} className="text-blue-400 hover:text-blue-300 flex items-center gap-2 mb-3 font-medium transition-colors">
                <ArrowLeft className="w-4 h-4" /> Back to Workspace Hub
              </Link>
              <h1 className="text-4xl font-bold text-white tracking-tight">{title}</h1>
            </div>
            <div className="flex gap-3">
              <DashboardActions />
            </div>
          </div>
          
          {/* Main Content Workspace */}
          <div className="bg-[#0B1120]/80 border border-slate-800/60 rounded-3xl p-6 md:p-8 backdrop-blur-xl shadow-2xl">
            {children}
          </div>
        </div>
      </div>
    </DashboardDataProvider>
  );
};

export default ReportLayout;
