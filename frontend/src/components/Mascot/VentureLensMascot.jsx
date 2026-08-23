import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Info, X } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const TOOLTIPS = {
  'overview': "Welcome to your Dashboard! Scroll down to see the AI's full breakdown of your startup idea.",
  'executive-summary': "The Executive Summary is a quick 1-pager for investors.",
  'market': "Market Analysis looks at TAM, SAM, and SOM. It helps prove you are building in a growing space.",
  'customers': "Customer profiles identify exactly who feels the pain point you are solving.",
  'competitors': "Competitor Analysis maps out the landscape. Look for the 'Gaps' to find your wedge.",
  'risks': "Be transparent about these risks. Investors love founders who know their weak spots.",
  'swot': "SWOT analysis breaks down internal vs external factors.",
  'mvp': "Focus on building ONLY what is in this MVP roadmap. Avoid feature creep!",
  'gtm': "Go-to-Market is how you get your first 100 users. Follow these channels closely."
};

export const VentureLensMascot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleSectionChange = (e) => {
      const activeSection = e.detail;
      if (activeSection && TOOLTIPS[activeSection]) {
        setCurrentMessage(TOOLTIPS[activeSection]);
        setIsOpen(true);
        
        const timer = setTimeout(() => {
          setIsOpen(false);
        }, 8000);
        return () => clearTimeout(timer);
      }
    };

    window.addEventListener('sectionChange', handleSectionChange);
    return () => window.removeEventListener('sectionChange', handleSectionChange);
  }, []);

  // Don't show Mascot inside Vera Workspace to avoid UI clutter
  if (location.pathname === '/vera') return null;

  return (
    <div className="fixed bottom-8 right-8 z-40 flex items-end justify-end pointer-events-none">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.9 }}
            className="pointer-events-auto mr-4 mb-2 bg-surface/90 backdrop-blur-md border border-primary/30 p-4 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] max-w-xs relative group"
          >
            <button 
              onClick={() => setIsOpen(false)}
              className="absolute -top-2 -right-2 bg-background border border-border rounded-full p-1 text-textMuted hover:text-textMain hover:bg-surface transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
            <div className="flex gap-3">
              <Info className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <p className="text-sm text-textMain leading-relaxed font-medium">
                {currentMessage}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button 
        onClick={() => navigate('/vera')}
        className="pointer-events-auto group focus:outline-none relative flex items-center justify-center w-14 h-14"
        aria-label="Open Vera AI Co-Founder"
      >
        <div className="absolute inset-0 rounded-full bg-blue-500/20 animate-ping" style={{ animationDuration: '3s' }}></div>
        <div className="relative w-12 h-12 bg-gradient-to-tr from-blue-600 to-indigo-400 rounded-full flex items-center justify-center shadow-lg border border-white/20 group-hover:scale-110 transition-transform duration-300">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
      </button>
    </div>
  );
};

export default VentureLensMascot;
