import React from 'react';
import Sidebar from '../Sidebar';
import { useScrollSpy } from '../../hooks/useScrollSpy';
import { useDashboardData } from '../../contexts/DashboardContext';

const DashboardLayout = ({ children }) => {
  const { data, requestId, handleExport, loading, error } = useDashboardData();
  
  // Use scroll spy specifically for sections within the layout
  const activeSection = useScrollSpy('section[id]', { rootMargin: '-20% 0px -60% 0px' }, [!loading, !error, !!data]);

  return (
    <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-12 pb-16">
        {children}
      </div>
    </div>
  );
};

export default DashboardLayout;
