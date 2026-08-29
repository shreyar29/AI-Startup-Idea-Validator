import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import CompetitorSection from '../../components/CompetitorSection';
import ComparisonSection from '../../components/ComparisonSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const Competitor = () => {
  const { data } = useDashboardData();
  
  if (!data?.competitor_agent) return <SectionSkeleton />;
  
  return (
    <div className="space-y-12">
      <CompetitorSection data={data.competitor_agent} />
      {data.comparison_agent && <ComparisonSection data={data.comparison_agent} />}
    </div>
  );
};

const CompetitorPage = () => {
  return (
    <ReportLayout title="Competitive Intelligence">
      <Competitor />
    </ReportLayout>
  );
};

export default CompetitorPage;
