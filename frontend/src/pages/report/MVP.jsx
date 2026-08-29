import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import MVPSection from '../../components/MVPSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const MVP = () => {
  const { data } = useDashboardData();
  if (!data?.mvp_agent) return <SectionSkeleton />;
  return <MVPSection data={data.mvp_agent} />;
};

const MVPPage = () => {
  return (
    <ReportLayout title="MVP Strategy">
      <MVP />
    </ReportLayout>
  );
};

export default MVPPage;
