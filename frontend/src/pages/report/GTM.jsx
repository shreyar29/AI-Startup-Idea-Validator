import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import GTMSection from '../../components/GTMSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const GTM = () => {
  const { data } = useDashboardData();
  if (!data?.gtm_agent) return <SectionSkeleton />;
  return <GTMSection data={data.gtm_agent} />;
};

const GTMPage = () => {
  return (
    <ReportLayout title="Go-To-Market Strategy">
      <GTM />
    </ReportLayout>
  );
};

export default GTMPage;
