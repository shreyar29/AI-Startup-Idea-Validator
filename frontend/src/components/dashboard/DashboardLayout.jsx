import React from 'react';
import Sidebar from '../Sidebar';
import { useScrollSpy } from '../../hooks/useScrollSpy';
import { useDashboardData } from '../../contexts/DashboardContext';

const DashboardLayout = ({ children }) => {
  const { data, requestId, handleExport, loading, error } = useDashboardData();
  
  // Use scroll spy specifically for sections within the layout
  const activeSection = useScrollSpy('section[id]', { rootMargin: '-20% 0px -60% 0px' }, [!loading, !error, !!data]);

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8 xl:gap-12">
      <div className="md:w-64 lg:w-72 flex-shrink-0 hidden md:block">
        <Sidebar 
          activeSection={activeSection} 
          sessionId={requestId || data?.metadata?.request_id} 
          onDownload={() => handleExport(data?.metadata?.startup_idea, data)} 
        />
      </div>
      <div className="flex-grow space-y-12 pb-16 min-w-0">
        {children}
      </div>
    </div>
  );
};

export default DashboardLayout;
