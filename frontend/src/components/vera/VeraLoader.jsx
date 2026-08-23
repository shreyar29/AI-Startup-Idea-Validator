import React from 'react';
import { VeraAvatar } from './VeraAvatar';
import { motion, AnimatePresence } from 'framer-motion';

export const VeraLoader = ({ currentStep }) => {
  const stepMap = {
    'Web Search Agent': { state: 'researching', msg: 'Scanning the startup ecosystem...' },
    'Market Agent': { state: 'analyzing', msg: 'Evaluating market opportunity...' },
    'Customer Agent': { state: 'analyzing', msg: 'Understanding customer pain points...' },
    'Competitor Agent': { state: 'analyzing', msg: 'Mapping competitors...' },
    'Risk Agent': { state: 'cautious', msg: 'Stress-testing your business model...' },
    'SWOT Agent': { state: 'analyzing', msg: 'Evaluating strategic strengths and threats...' },
    'MVP Agent': { state: 'analyzing', msg: 'Designing your minimum viable product...' },
    'GTM Agent': { state: 'analyzing', msg: 'Building your launch strategy...' },
    'Startup Score Agent': { state: 'analyzing', msg: 'Calculating startup viability...' },
    'Comparison Agent': { state: 'researching', msg: 'Preparing final recommendation...' }
  };

  const current = stepMap[currentStep] || { state: 'analyzing', msg: 'Synthesizing intelligence...' };

  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[300px] gap-8 px-4 py-8">
      <VeraAvatar state={current.state} size="lg" />
      
      <div className="text-center h-24 flex flex-col items-center justify-center">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <h3 className="text-xl sm:text-2xl font-bold text-white mb-2">{currentStep || "Connecting..."}</h3>
            <p className="text-vera-cyan font-mono text-sm tracking-widest uppercase">{current.msg}</p>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};
