import React from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useStartupAnalysis } from '../../hooks/useStartupAnalysis';
import { useReportExport } from '../../hooks/useReportExport';
import { DashboardDataProvider } from '../../contexts/DashboardContext';
import DashboardLayout from './DashboardLayout';
import DashboardSections from './DashboardSections';
import ValidationPipeline from '../ValidationPipeline';
import ErrorState from '../ErrorState';

const DashboardContainer = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { reportId: routeReportId } = useParams();

  // state overrides or URL params
  const stateIdea = location.state?.idea;
  const stateReportId = location.state?.sessionId;
  
  // Use either the deep linked route param or the state
  const reportId = routeReportId || stateReportId;
  const idea = stateIdea;

  const { data, loading, error, requestId, retry } = useStartupAnalysis(idea, reportId);
  const { handleExport } = useReportExport();

  // If no idea and no report ID is available, kick them back to home
  React.useEffect(() => {
    if (!idea && !reportId) {
      navigate('/');
    }
  }, [idea, reportId, navigate]);

  if (!idea && !reportId) return null;

  if (loading) return <ValidationPipeline requestId={requestId || reportId} />;
  
  if (error) return <ErrorState message={error} onRetry={() => {
    if (idea || reportId) retry();
    else navigate('/');
  }} />;
  
  if (!data || (!data.metadata && !data.error)) return <ErrorState message="Invalid or no data received" onRetry={() => navigate('/')} />;

  if (data.error) {
    return <ErrorState message={data.message || data.error} onRetry={() => navigate('/')} />;
  }

  return (
    <DashboardDataProvider 
      data={data} 
      loading={loading} 
      error={error} 
      requestId={requestId} 
      retry={retry}
      idea={idea || data?.metadata?.startup_idea}
      handleExport={handleExport}
    >
      <DashboardLayout>
        <DashboardSections />
      </DashboardLayout>
    </DashboardDataProvider>
  );
};

export default DashboardContainer;
