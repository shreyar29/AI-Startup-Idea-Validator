import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  FileSearch, TrendingUp, Users, ShieldAlert, 
  Target, Rocket, Crosshair, Trophy
} from 'lucide-react';
import { useDashboardData } from '../../contexts/DashboardContext';

const IntelligenceGrid = () => {
  const navigate = useNavigate();
  const { reportId } = useParams();
  const { requestId } = useDashboardData();
  const activeId = reportId || requestId;

  const cards = [
    {
      title: 'RESEARCH EVIDENCE',
      description: 'Curated insights and data from credible sources.',
      icon: FileSearch,
      color: 'blue',
      route: 'research'
    },
    {
      title: 'MARKET INTELLIGENCE',
      description: 'Market size, growth trends and opportunity assessment.',
      icon: TrendingUp,
      color: 'purple',
      route: 'market'
    },
    {
      title: 'CUSTOMER INTELLIGENCE',
      description: 'Target personas, needs, pain points and behaviors.',
      icon: Users,
      color: 'cyan',
      route: 'customer'
    },
    {
      title: 'COMPETITIVE INTELLIGENCE',
      description: 'Competitors, positioning, feature gaps and differentiation.',
      icon: Trophy,
      color: 'orange',
      route: 'competitor'
    },
    {
      title: 'RISK CENTER',
      description: 'Identify potential risks and their impact on your startup.',
      icon: ShieldAlert,
      color: 'red',
      route: 'risk'
    },
    {
      title: 'SWOT ANALYSIS',
      description: 'Strategic evaluation of internal and external factors.',
      icon: Crosshair,
      color: 'emerald',
      route: 'swot'
    },
    {
      title: 'MVP STRATEGY',
      description: 'Prioritized features and timeline to build your MVP.',
      icon: Rocket,
      color: 'yellow',
      route: 'mvp'
    },
    {
      title: 'GO-TO-MARKET',
      description: 'Strategies, channels and tactics to reach your audience.',
      icon: Target,
      color: 'pink',
      route: 'gtm'
    }
  ];

  const handleNavigate = (route) => {
    if (activeId) {
      navigate(`/report/${activeId}/${route}`);
    }
  };

  const getColorClasses = (color) => {
    const map = {
      blue: 'border-blue-500/50 hover:border-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.1)] hover:shadow-[0_0_30px_rgba(59,130,246,0.3)] text-blue-400',
      purple: 'border-purple-500/50 hover:border-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.1)] hover:shadow-[0_0_30px_rgba(168,85,247,0.3)] text-purple-400',
      cyan: 'border-cyan-500/50 hover:border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.1)] hover:shadow-[0_0_30px_rgba(6,182,212,0.3)] text-cyan-400',
      orange: 'border-orange-500/50 hover:border-orange-400 shadow-[0_0_15px_rgba(249,115,22,0.1)] hover:shadow-[0_0_30px_rgba(249,115,22,0.3)] text-orange-400',
      red: 'border-red-500/50 hover:border-red-400 shadow-[0_0_15px_rgba(239,68,68,0.1)] hover:shadow-[0_0_30px_rgba(239,68,68,0.3)] text-red-400',
      emerald: 'border-emerald-500/50 hover:border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)] hover:shadow-[0_0_30px_rgba(16,185,129,0.3)] text-emerald-400',
      yellow: 'border-yellow-500/50 hover:border-yellow-400 shadow-[0_0_15px_rgba(234,179,8,0.1)] hover:shadow-[0_0_30px_rgba(234,179,8,0.3)] text-yellow-400',
      pink: 'border-pink-500/50 hover:border-pink-400 shadow-[0_0_15px_rgba(236,72,153,0.1)] hover:shadow-[0_0_30px_rgba(236,72,153,0.3)] text-pink-400',
    };
    return map[color] || map.blue;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 relative z-10 px-4 xl:px-0 max-w-7xl mx-auto">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        const colorClass = getColorClasses(card.color);
        return (
          <button
            key={idx}
            onClick={() => handleNavigate(card.route)}
            className={`group relative flex flex-col items-center justify-center w-full h-full min-h-[260px] text-center p-8 rounded-2xl bg-[#070b14]/90 backdrop-blur-md border ${colorClass} transition-all duration-300 overflow-hidden`}
          >
            <div className="relative z-10 flex flex-col items-center h-full w-full">
              {/* Large Glowing Icon */}
              <div className={`mb-6 transform group-hover:scale-110 group-hover:-translate-y-1 transition-all duration-300`}>
                <Icon className={`w-12 h-12 drop-shadow-[0_0_10px_currentColor]`} />
              </div>
              
              <h3 className="text-sm font-bold tracking-widest text-white mb-3 leading-tight">{card.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed flex-grow">{card.description}</p>
              
              <div className="mt-6 text-sm font-medium opacity-80 group-hover:opacity-100 transition-opacity">
                Explore &rarr;
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
};

export default React.memo(IntelligenceGrid);
