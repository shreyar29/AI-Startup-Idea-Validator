import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import RiskSection from '../../components/RiskSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const Risk = () => {
  const { data } = useDashboardData();
  if (!data?.risk_agent) return <SectionSkeleton />;
  return <RiskSection data={data.risk_agent} />;
};

const RiskPage = () => {
  return (
    <ReportLayout title="Risk Analysis">
      <Risk />
    </ReportLayout>
  );
};

export default RiskPage;
