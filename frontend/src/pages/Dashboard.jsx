import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Download, Sparkles } from 'lucide-react';
import { validateIdea, saveToHistory } from '../services/api';
import ValidationPipeline from '../components/ValidationPipeline';
import ErrorState from '../components/ErrorState';
import Sidebar from '../components/Sidebar';
import OverviewSection from '../components/OverviewSection';
import WebSearchSection from '../components/WebSearchSection';
import MarketSection from '../components/MarketSection';
import CustomerSection from '../components/CustomerSection';
import CompetitorSection from '../components/CompetitorSection';
import ComparisonSection from '../components/ComparisonSection';
import RiskSection from '../components/RiskSection';
import SWOTSection from '../components/SWOTSection';
import MVPSection from '../components/MVPSection';
import GTMSection from '../components/GTMSection';
import { VeraVerdict } from '../components/vera/VeraVerdict';
import ExecutiveSummarySection from '../components/dashboard/ExecutiveSummarySection';
import StartupScoreSection from '../components/dashboard/StartupScoreSection';
import { useScrollSpy } from '../hooks/useScrollSpy';
import { exportToPDF } from '../services/exportService';
import { storageService } from '../services/storageService';

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [requestId, setRequestId] = useState(null);

  const idea = location.state?.idea;
  const initialResult = React.useRef(location.state?.result).current;
  const fetched = React.useRef(false);

  // Use the extracted scroll spy hook
  const activeSection = useScrollSpy('section[id]', { rootMargin: '-20% 0px -60% 0px' }, [!loading, !error, !!data]);

  const handleExport = async () => {
    try {
      const success = await exportToPDF(idea, data);
      if (!success) {
        console.error('[Dashboard] PDF Export failed gracefully. Check exportService logs.');
      }
    } catch (e) {
      console.error('[Dashboard] Unexpected PDF export error:', e.name);
    }
  };

  useEffect(() => {
    if (!idea && !initialResult) {
      navigate('/');
      return;
    }

    if (initialResult && !fetched.current) {
      fetched.current = true;
      setData(initialResult);
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      if (fetched.current) return;
      fetched.current = true;
      
      setError(null);
      setLoading(true);
      
      try {
        const result = await validateIdea(idea, (id) => {
          setRequestId(id);
          storageService.setActiveReportId(id);
        });
        setData(result);
        
        if (result?.metadata?.request_id) {
          storageService.setActiveReportId(result.metadata.request_id);
        }
        
        const userId = storageService.getUserId();
        if (userId) {
          try {
            await saveToHistory(userId, idea, result);
          } catch (e) {
            console.error('[Dashboard] Failed to sync session with history service. Error: ' + e.name);
          }
        }
      } catch (err) {
        console.error('[Dashboard] Validation pipeline terminated with error: ' + (err.message || err.name));
        setError(err.message || 'Validation failed');
      } finally {
        setLoading(false);
      }
    };

    if (!initialResult) {
      fetchData();
    }
  }, [idea, initialResult, navigate]);

  if (loading) return <ValidationPipeline requestId={requestId} />;
  if (error) return <ErrorState message={error} onRetry={() => navigate('/')} />;
  if (!data || !data.metadata) return <ErrorState message="Invalid or no data received" onRetry={() => navigate('/')} />;

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8 xl:gap-12">
      <div className="md:w-64 lg:w-72 flex-shrink-0 hidden md:block">
        <Sidebar activeSection={activeSection} sessionId={requestId || data.metadata?.request_id} />
      </div>
      <div className="flex-grow space-y-12 pb-16 min-w-0">
        
        {data.startup_score_agent && (
          <VeraVerdict 
            score={data.startup_score_agent.overall_score} 
            verdict={data.startup_score_agent.verdict} 
            explanation={data.startup_score_agent.score_explanation} 
          />
        )}

        {data.executive_summary && (
          <section id="executive-summary">
            <ExecutiveSummarySection summary={data.executive_summary} />
          </section>
        )}

        {data.startup_score_agent && (
          <section id="startup-score">
            <StartupScoreSection data={data.startup_score_agent} />
          </section>
        )}

        <section id="overview">
          <OverviewSection metadata={data.metadata} finalEval={data.final_evaluation} />
        </section>
        
        {data.web_search_agent && (
          <section id="web-search">
            <WebSearchSection data={data.web_search_agent} />
          </section>
        )}
        
        {data.market_agent && (
          <section id="market">
            <MarketSection data={data.market_agent} />
          </section>
        )}
        
        {data.customer_agent && (
          <section id="customers">
            <CustomerSection data={data.customer_agent} />
          </section>
        )}
        
        {data.competitor_agent && (
          <section id="competitors">
            <CompetitorSection data={data.competitor_agent} />
          </section>
        )}
          {/* Action Panel */}
        <div className="mt-8 flex justify-between items-center bg-surface/30 p-6 rounded-2xl border border-white/5">
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-6 py-3 bg-surface hover:bg-surface/80 border border-border rounded-xl transition-all"
          >
            <Download className="w-5 h-5 text-textMuted" />
            <span className="font-medium">Export Report</span>
          </button>
          
          <button
            onClick={() => navigate('/vera', { state: { sessionId: requestId || data.metadata?.request_id } })}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-500 hover:to-indigo-500 transition-all shadow-lg shadow-blue-500/25"
          >
            <Sparkles className="w-5 h-5" />
            <span>Open AI Co-Founder Workspace</span>
          </button>
        </div>
        
        {data.risk_agent && (
          <section id="risks">
            <RiskSection data={data.risk_agent} />
          </section>
        )}
        
        {data.swot_agent && (
          <section id="swot">
            <SWOTSection data={data.swot_agent} />
          </section>
        )}
        
        {data.mvp_agent && (
          <section id="mvp">
            <MVPSection data={data.mvp_agent} />
          </section>
        )}
        
        {data.gtm_agent && (
          <section id="gtm">
            <GTMSection data={data.gtm_agent} />
          </section>
        )}
        
        {data.comparison_agent && (
          <section id="comparison">
            <ComparisonSection data={data.comparison_agent} />
          </section>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
