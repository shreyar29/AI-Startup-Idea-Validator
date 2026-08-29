import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import ExecutiveSummarySection from '../../components/dashboard/ExecutiveSummarySection';
import StartupScoreSection from '../../components/dashboard/StartupScoreSection';
import { useDashboardData } from '../../contexts/DashboardContext';

const Summary = () => {
  const { data } = useDashboardData();
  
  return (
    <div className="space-y-12">
      {data?.executive_summary && <ExecutiveSummarySection summary={data.executive_summary} />}
      {data?.startup_score_agent && <StartupScoreSection data={data.startup_score_agent} />}
    </div>
  );
};

const SummaryPage = () => {
  return (
    <ReportLayout title="Executive Summary">
      <Summary />
    </ReportLayout>
  );
};

export default SummaryPage;
