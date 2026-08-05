import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { validateIdea } from '../services/api';
import ValidationPipeline from '../components/ValidationPipeline';
import ErrorState from '../components/ErrorState';
import Sidebar from '../components/Sidebar';
import OverviewSection from '../components/OverviewSection';
import WebSearchSection from '../components/WebSearchSection';
import MarketSection from '../components/MarketSection';
import CustomerSection from '../components/CustomerSection';
import CompetitorSection from '../components/CompetitorSection';
import ComparisonSection from '../components/ComparisonSection';

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState('overview');
  const [requestId, setRequestId] = useState(null);

  const fetched = React.useRef(false);

  useEffect(() => {
    const idea = location.state?.idea;
    const existingResult = location.state?.result;
    
    if (!idea && !existingResult) {
      navigate('/');
      return;
    }

    if (existingResult && !fetched.current) {
      fetched.current = true;
      setData(existingResult);
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      if (fetched.current) return;
      fetched.current = true;
      
      try {
        setLoading(true);
        const result = await validateIdea(idea, (id) => {
          setRequestId(id);
        });
        setData(result);
      } catch (err) {
        setError(err.message || 'Validation failed');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [location.state, navigate]);

  if (loading) return <ValidationPipeline requestId={requestId} />;
  if (error) return <ErrorState message={error} onRetry={() => navigate('/')} />;
  if (!data || !data.metadata) return <ErrorState message="Invalid or no data received" onRetry={() => navigate('/')} />;

  const onSectionEnter = (id) => setActiveSection(id);

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8 xl:gap-12">
      <div className="md:w-64 lg:w-72 flex-shrink-0 hidden md:block">
        <Sidebar activeSection={activeSection} />
      </div>
      <div className="flex-grow space-y-12 pb-16 min-w-0">
        <section id="overview" onMouseEnter={() => onSectionEnter('overview')}>
          <OverviewSection metadata={data.metadata} finalEval={data.final_evaluation} />
        </section>
        
        {data.web_search_agent && (
          <section id="web-search" onMouseEnter={() => onSectionEnter('web-search')}>
            <WebSearchSection data={data.web_search_agent} />
          </section>
        )}
        
        {data.market_agent && (
          <section id="market" onMouseEnter={() => onSectionEnter('market')}>
            <MarketSection data={data.market_agent} />
          </section>
        )}
        
        {data.customer_agent && (
          <section id="customers" onMouseEnter={() => onSectionEnter('customers')}>
            <CustomerSection data={data.customer_agent} />
          </section>
        )}
        
        {data.competitor_agent && (
          <section id="competitors" onMouseEnter={() => onSectionEnter('competitors')}>
            <CompetitorSection data={data.competitor_agent} />
          </section>
        )}
        
        {data.comparison_agent && (
          <section id="comparison" onMouseEnter={() => onSectionEnter('comparison')}>
            <ComparisonSection data={data.comparison_agent} />
          </section>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
