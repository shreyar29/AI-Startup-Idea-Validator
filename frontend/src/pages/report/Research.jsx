import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import WebSearchSection from '../../components/WebSearchSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const Research = () => {
  const { data } = useDashboardData();
  if (!data?.web_search_agent) return <SectionSkeleton />;
  return <WebSearchSection data={data.web_search_agent} />;
};

const ResearchPage = () => {
  return (
    <ReportLayout title="Research Evidence">
      <Research />
    </ReportLayout>
  );
};

export default ResearchPage;
