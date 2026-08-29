import React from 'react';
import ReportLayout from '../../components/dashboard/ReportLayout';
import CustomerSection from '../../components/CustomerSection';
import { useDashboardData } from '../../contexts/DashboardContext';
import SectionSkeleton from '../../components/dashboard/SectionSkeleton';

const Customer = () => {
  const { data } = useDashboardData();
  if (!data?.customer_agent) return <SectionSkeleton />;
  return <CustomerSection data={data.customer_agent} />;
};

const CustomerPage = () => {
  return (
    <ReportLayout title="Customer Intelligence">
      <Customer />
    </ReportLayout>
  );
};

export default CustomerPage;
