import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import SWOTSection from '../../components/SWOTSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const SWOT = () => {
  const { data } = useDashboardData();
  if (!data?.swot_agent) return <SectionSkeleton />;
  return <SWOTSection data={data.swot_agent} />;
};

const SWOTPage = () => {
  return (
    <ReportLayout title="SWOT Analysis">
      <SWOT />
    </ReportLayout>
  );
};

export default SWOTPage;
