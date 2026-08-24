import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  FileSearch, TrendingUp, Users, ShieldAlert, 
  Target, Rocket, Crosshair, Swords, FileText
} from 'lucide-react';
import { useDashboardData } from '../../contexts/DashboardContext';

const IntelligenceGrid = () => {
  const navigate = useNavigate();
  const { reportId } = useParams();
  const { requestId } = useDashboardData();
  const activeId = reportId || requestId;

  const cards = [
    {
      title: 'EXECUTIVE SUMMARY',
      description: 'High-level CEO view, scores, verdicts, and strategic insights.',
      icon: FileText,
      color: 'blue',
      route: 'summary'
    },
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
      color: 'indigo',
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
      icon: Swords,
      color: 'purple',
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
      color: 'orange',
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
      blue: 'from-blue-500/20 to-blue-900/10 border-blue-500/30 hover:border-blue-400 text-blue-400 hover:shadow-[0_0_30px_rgba(59,130,246,0.3)]',
      indigo: 'from-indigo-500/20 to-indigo-900/10 border-indigo-500/30 hover:border-indigo-400 text-indigo-400 hover:shadow-[0_0_30px_rgba(99,102,241,0.3)]',
      cyan: 'from-cyan-500/20 to-cyan-900/10 border-cyan-500/30 hover:border-cyan-400 text-cyan-400 hover:shadow-[0_0_30px_rgba(6,182,212,0.3)]',
      purple: 'from-purple-500/20 to-purple-900/10 border-purple-500/30 hover:border-purple-400 text-purple-400 hover:shadow-[0_0_30px_rgba(168,85,247,0.3)]',
      red: 'from-red-500/20 to-red-900/10 border-red-500/30 hover:border-red-400 text-red-400 hover:shadow-[0_0_30px_rgba(239,68,68,0.3)]',
      emerald: 'from-emerald-500/20 to-emerald-900/10 border-emerald-500/30 hover:border-emerald-400 text-emerald-400 hover:shadow-[0_0_30px_rgba(16,185,129,0.3)]',
      orange: 'from-orange-500/20 to-orange-900/10 border-orange-500/30 hover:border-orange-400 text-orange-400 hover:shadow-[0_0_30px_rgba(249,115,22,0.3)]',
      pink: 'from-pink-500/20 to-pink-900/10 border-pink-500/30 hover:border-pink-400 text-pink-400 hover:shadow-[0_0_30px_rgba(236,72,153,0.3)]',
    };
    return map[color] || map.blue;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        const colorClass = getColorClasses(card.color);
        return (
          <button
            key={idx}
            onClick={() => handleNavigate(card.route)}
            className={`group relative text-left p-6 rounded-2xl bg-gradient-to-b bg-[#0B1120]/80 backdrop-blur-md border transition-all duration-300 overflow-hidden ${colorClass}`}
          >
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 bg-gradient-to-b transition-opacity duration-500 ${colorClass.split(' ')[0]} ${colorClass.split(' ')[1]}`} />
            
            <div className="relative z-10 flex flex-col h-full">
              <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-5 border border-white/10 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold tracking-widest text-white mb-2">{card.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed flex-grow">{card.description}</p>
            </div>
          </button>
        );
      })}
    </div>
  );
};

export default React.memo(IntelligenceGrid);
