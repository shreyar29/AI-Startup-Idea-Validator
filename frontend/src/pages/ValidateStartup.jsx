import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, CheckCircle2, ChevronRight, BarChart3, Globe, Target, AlertCircle, Sparkles, TrendingUp, Lightbulb, Zap, ExternalLink } from 'lucide-react';
import { validateStartup } from '../services/api';

const STAGES = [
  { id: 'query', label: 'Query Agent' },
  { id: 'search', label: 'Web Search Agent' },
  { id: 'result', label: 'Result' }
];

const SAMPLE_IDEAS = [
  "AI-powered platform that detects skin diseases using smartphone images",
  "Mobile app that helps college students find affordable PGs using AI recommendations",
  "AI assistant that creates personalized interview preparation plans based on job descriptions",
  "Platform connecting local farmers directly with consumers for fresh produce delivery",
  "AI-powered waste segregation system for smart cities using computer vision",
  "Blockchain-based academic certificate verification platform for universities",
  "AI tool that predicts startup success by analyzing market trends and competitor data",
  "Wearable device that monitors stress levels and suggests personalized mental wellness activities",
];

const ValidateStartup = () => {
  const [idea, setIdea] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [placeholder] = useState(() => SAMPLE_IDEAS[Math.floor(Math.random() * SAMPLE_IDEAS.length)]);

  const handleValidate = async (e) => {
    e.preventDefault();
    if (!idea.trim()) return;

    setIsProcessing(true);
    setError(null);
    setResults(null);
    setCurrentStage(0);

    // Simulate pipeline stages for UX
    const stageInterval = setInterval(() => {
      setCurrentStage((prev) => {
        if (prev < STAGES.length - 1) return prev + 1;
        clearInterval(stageInterval);
        return prev;
      });
    }, 1500);

    try {
      const data = await validateStartup(idea);
      clearInterval(stageInterval);
      setCurrentStage(STAGES.length - 1);
      setTimeout(() => {
        setResults(data);
        setIsProcessing(false);
      }, 500);
    } catch (err) {
      clearInterval(stageInterval);
      setError(err.message || 'An error occurred during validation.');
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <div className="inline-flex items-center space-x-2 bg-primary/10 border border-primary/20 text-primary px-4 py-1.5 rounded-full mb-6 text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>AI-Powered Market Intelligence</span>
        </div>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
          Validate Your Idea in <span className="text-gradient animate-gradient-x">Seconds</span>
        </h1>
        <p className="text-textMuted max-w-2xl mx-auto text-lg md:text-xl font-light">
          Describe your startup concept below. Our autonomous agents will perform live web research to surface competitors, market size, and trends.
        </p>
      </motion.div>

      <div className="max-w-4xl mx-auto mb-16">
        <form onSubmit={handleValidate} className="relative">
          <div className="relative group">
            <Search className="absolute left-6 top-6 w-6 h-6 text-textMuted group-focus-within:text-primary transition-colors duration-300" />
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder={placeholder}
              rows="4"
              className="w-full bg-surface/50 backdrop-blur-sm border border-white/10 rounded-2xl py-6 pl-16 pr-6 pb-20 text-white text-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 focus:bg-surface/80 shadow-[0_0_40px_-15px_rgba(6,182,212,0.3)] transition-all duration-300 placeholder:text-gray-500 resize-none"
              disabled={isProcessing}
            />
            <button
              type="submit"
              disabled={isProcessing || !idea.trim()}
              className="absolute right-3 bottom-3 bg-gradient-to-r from-cyan-600 to-fuchsia-600 hover:from-cyan-500 hover:to-fuchsia-500 disabled:from-gray-700 disabled:to-gray-800 disabled:cursor-not-allowed text-white font-medium py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-primary/25 flex items-center space-x-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Validating...</span>
                </>
              ) : (
                <>
                  <span>Validate</span>
                  <Zap className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Sample Ideas Chips */}
        {!isProcessing && !results && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-6"
          >
            <p className="text-textMuted text-xs mb-4 font-medium uppercase tracking-wider flex items-center">
              <Lightbulb className="w-3 h-3 mr-2" /> Try an example:
            </p>
            <div className="flex flex-wrap gap-2.5">
              {SAMPLE_IDEAS.slice(0, 4).map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => setIdea(sample)}
                  className="text-xs px-4 py-2 rounded-full border border-white/5 bg-white/[0.03] hover:bg-primary/10 hover:border-primary/30 hover:text-primary text-textMuted transition-all duration-300"
                >
                  {sample.length > 55 ? sample.slice(0, 55) + '…' : sample}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {isProcessing && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-8 overflow-hidden"
            >
              <div className="glass-panel rounded-xl p-6 border border-white/10">
                <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-6">Processing Pipeline</h3>
                <div className="space-y-4">
                  {STAGES.map((stage, idx) => {
                    const isCompleted = currentStage > idx;
                    const isActive = currentStage === idx;
                    return (
                      <div key={stage.id} className="flex items-center space-x-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                          isCompleted ? 'bg-primary border-primary text-white' : 
                          isActive ? 'border-primary text-primary' : 'border-white/10 text-white/20'
                        }`}>
                          {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : 
                           isActive ? <Loader2 className="w-4 h-4 animate-spin" /> : 
                           <span>{idx + 1}</span>}
                        </div>
                        <span className={`font-medium ${isCompleted || isActive ? 'text-white' : 'text-textMuted'}`}>
                          {stage.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-8 bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-center space-x-3"
            >
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            {/* Context Header */}
            <div className="grid grid-cols-1 gap-6 max-w-4xl mx-auto">
              <div className="glass-panel p-8 rounded-2xl border-t border-white/10">
                <div className="flex items-center space-x-3 text-primary mb-6">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Target className="w-5 h-5" />
                  </div>
                  <span className="font-semibold text-lg text-white font-outfit">Identified Context</span>
                </div>
                {results.identified_context && (
                  <ul className="space-y-4">
                    {Object.entries(results.identified_context).map(([key, value]) => (
                      <li key={key} className="flex flex-col">
                        <span className="text-textMuted text-xs uppercase tracking-wider mb-1 font-medium">{key.replace(/_/g, ' ')}</span>
                        <span className="text-white/90 font-medium leading-relaxed">{value}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* Categorized Search Results */}
            <div className="pt-8">
              <h2 className="text-3xl font-bold text-white mb-8 flex items-center space-x-3 font-outfit">
                <BarChart3 className="w-8 h-8 text-primary" />
                <span>Market Intelligence Report</span>
              </h2>
              {results.search_results && Object.entries(results.search_results).map(([category, items]) => (
                <div key={category} className="mb-12">
                  <div className="flex items-center mb-6">
                    <h3 className="text-2xl font-semibold text-white capitalize font-outfit mr-4">
                      {category.replace(/_/g, ' ')}
                    </h3>
                    <div className="h-px bg-white/10 flex-grow"></div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {items && items.length > 0 ? items.map((res, idx) => (
                      <a
                        key={idx}
                        href={res.url || res.cleaned_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="glass-panel glass-panel-hover p-6 rounded-2xl group flex flex-col h-full"
                      >
                        <div className="flex justify-between items-start mb-4">
                          <h4 className="text-base font-semibold text-white/90 group-hover:text-primary transition-colors line-clamp-2 leading-snug">
                            {res.title || 'Source Reference'}
                          </h4>
                          <ExternalLink className="w-4 h-4 text-textMuted opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-3 mt-1" />
                        </div>
                        <p className="text-sm text-textMuted line-clamp-4 leading-relaxed mb-6 flex-grow">{res.content}</p>
                        <div className="text-xs font-medium text-primary/70 bg-primary/10 py-1.5 px-3 rounded-lg truncate mt-auto">
                          {new URL(res.url || res.cleaned_url).hostname}
                        </div>
                      </a>
                    )) : (
                      <div className="col-span-full glass-panel p-8 rounded-2xl text-center">
                        <TrendingUp className="w-8 h-8 text-textMuted/50 mx-auto mb-3" />
                        <div className="text-textMuted text-sm">No significant data returned for this category.</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ValidateStartup;
