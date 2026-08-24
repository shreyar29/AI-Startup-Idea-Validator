import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import MarketSection from '../../components/MarketSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const Market = () => {
  const { data } = useDashboardData();
  if (!data?.market_agent) return <SectionSkeleton />;
  return <MarketSection data={data.market_agent} />;
};

const MarketPage = () => {
  return (
    <ReportLayout title="Market Intelligence">
      <Market />
    </ReportLayout>
  );
};

export default MarketPage;
