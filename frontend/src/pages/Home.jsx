import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Zap, Target, Search, Activity } from 'lucide-react';

const Home = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl mx-auto"
      >
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-primary/10 text-primary mb-8 border border-primary/20">
          <Zap className="w-4 h-4" />
          <span className="text-sm font-medium">Powered by Agentic AI</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6">
          Validate Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Startup Idea</span>
          <br />in Minutes.
        </h1>
        
        <p className="text-lg md:text-xl text-textMuted mb-10 max-w-2xl mx-auto">
          VentureLens utilizes advanced AI agents to perform deep web research. The pipeline consists of Query Agent, Web Search Agent, and Result.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Link
            to="/validate"
            className="flex items-center space-x-2 bg-primary hover:bg-primaryHover text-white px-8 py-4 rounded-lg font-medium transition-colors w-full sm:w-auto justify-center"
          >
            <span>Start Validation</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto"
      >
        {[
          { icon: Target, title: 'Query Agent', desc: 'Identifies context and structures search strategies.' },
          { icon: Search, title: 'Web Search Agent', desc: 'Live web scraping to fetch accurate data based on queries.' },
          { icon: Activity, title: 'Result Generation', desc: 'Aggregates and formats the search results for review.' }
        ].map((feature, idx) => {
          const Icon = feature.icon || Zap;
          return (
            <div key={idx} className="glass-panel p-6 rounded-xl text-left border border-white/5">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-textMuted leading-relaxed">{feature.desc}</p>
            </div>
          )
        })}
      </motion.div>
    </div>
  );
};

export default Home;
