import React, { Suspense, lazy } from 'react';
import { Loader2 } from 'lucide-react';
import { useDashboardData } from '../../contexts/DashboardContext';
import ErrorBoundary from '../ErrorBoundary';
import DashboardActions from './DashboardActions';
import DashboardHero from './DashboardHero';
import IntelligenceGrid from './IntelligenceGrid';
import SimulatorSection from './SimulatorSection';

import { VeraVerdict } from '../vera/VeraVerdict';

// Lazy load modules
const WebSearchSection = lazy(() => import('../WebSearchSection'));
import SectionSkeleton from './SectionSkeleton';

const DashboardSections = () => {
  const { data } = useDashboardData();

  if (!data) return null;

  return (
    <>
      <ErrorBoundary>
        <DashboardHero />
      </ErrorBoundary>
      
      <ErrorBoundary>
        <IntelligenceGrid />
      </ErrorBoundary>
      
      <ErrorBoundary>
        <SimulatorSection />
      </ErrorBoundary>
      {data.startup_score_agent && (
        <ErrorBoundary>
          <VeraVerdict 
            score={data.startup_score_agent.overall_score} 
            verdict={data.startup_score_agent.verdict} 
            explanation={data.startup_score_agent.score_explanation} 
          />
        </ErrorBoundary>
      )}

    </>
  );
};

export default React.memo(DashboardSections);
