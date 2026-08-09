import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Sparkles, ArrowRight, Search, Target, Users, 
  BrainCircuit, CheckCircle2, Lightbulb, LineChart, ShieldCheck
} from 'lucide-react';

const SUGGESTIONS = [
  { industry: "Cybersecurity", title: "SOC2 Automation", desc: "A B2B SaaS platform that automates SOC2 compliance for startups." },
  { industry: "Health & Wellness", title: "Smart Meal Plans", desc: "An AI tool that generates personalized meal plans to minimize food waste." },
  { industry: "Entertainment", title: "Indie Venue Booking", desc: "A marketplace connecting local indie musicians with venue owners." }
];

const CAPABILITIES = [
  { icon: LineChart, title: "Market Intelligence", desc: "Analyzes industry trends, TAM, growth and demand." },
  { icon: Target, title: "Competitor Analysis", desc: "Finds competitors and identifies differentiation opportunities." },
  { icon: Users, title: "Customer Research", desc: "Builds customer personas using real market evidence." },
  { icon: BrainCircuit, title: "AI Recommendation", desc: "Provides a data-backed Go / No-Go recommendation." },
];

const FLOW_STEPS = [
  { icon: Lightbulb, title: "Idea", desc: "Submit concept" },
  { icon: Search, title: "Research", desc: "Live web analysis" },
  { icon: LineChart, title: "Market", desc: "Data analysis" },
  { icon: Target, title: "Competitors", desc: "Feature comparison" },
  { icon: CheckCircle2, title: "Verdict", desc: "Recommendation" },
];

const TRUST_ITEMS = [
  "Multi-Agent AI",
  "Real-time Market Intelligence",
  "Live Competitor Research",
  "Customer Persona Generation",
  "Strategic Recommendations"
];

const VALUE_PREVIEW = [
  "Validation Score", "Market Opportunity", "Competitor Landscape", "Customer Personas", "SWOT Analysis", "Product Recommendations"
];

const Home = () => {
  const [idea, setIdea] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [modifierKey, setModifierKey] = useState('⌘');
  const navigate = useNavigate();
  const textareaRef = useRef(null);

  useEffect(() => {
    if (typeof navigator !== 'undefined') {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0 || navigator.userAgent.toUpperCase().indexOf('MAC') >= 0;
      setModifierKey(isMac ? '⌘' : 'Ctrl');
    }
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '160px';
      const scrollHeight = textareaRef.current.scrollHeight;
      if (scrollHeight > 160) {
        textareaRef.current.style.height = `${scrollHeight}px`;
      }
    }
  }, [idea]);

  const submitForm = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (idea.trim().length >= 10) {
      navigate('/dashboard', { state: { idea: idea.trim() } });
    }
  };

  return (
    <div className="relative min-h-[calc(100vh-4rem)] flex flex-col items-center justify-start overflow-x-hidden pt-8 pb-16">
      {/* Background elements */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden bg-background">
        <div className="absolute top-[-20%] left-[10%] w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] opacity-60 pointer-events-none" />
        <div className="absolute top-[30%] right-[-10%] w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[100px] opacity-40 pointer-events-none" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_0%,#000_60%,transparent_100%)]" />
      </div>
      
      {/* 1. Increased maximum content width to 1440px for large desktop screens */}
      <div className="relative z-10 w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 text-center mt-8 sm:mt-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-8"
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface/80 border border-white/10 backdrop-blur-md shadow-xl text-primary text-sm font-semibold mb-2">
            <Sparkles className="w-4 h-4" />
            <span>VentureLens AI Version 2.0</span>
          </div>
          
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-textMain mb-6 leading-[1.1]">
            Know if your startup is <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-primary to-blue-400">
              worth building.
            </span>
          </h1>
          
          <p className="text-lg sm:text-xl text-textMuted max-w-3xl mx-auto font-medium leading-relaxed">
            Deploy an intelligent swarm of AI agents to gain evidence-backed confidence, real-time market validation, and data-driven decision making before writing a single line of code.
          </p>

          {/* 3. Significantly increased textarea width for dominance */}
          <form onSubmit={submitForm} className="relative max-w-5xl xl:max-w-6xl mx-auto mt-10 text-left">
            {/* Glow behind textarea */}
            <div className={`absolute -inset-1 rounded-3xl blur-xl transition-all duration-500 ${isFocused ? 'bg-primary/20 opacity-100' : 'opacity-0'}`} />
            
            <div className={`relative rounded-2xl transition-all duration-500 ${isFocused ? 'border-primary/50 bg-surface/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)]' : 'border-white/10 bg-surface/60 shadow-2xl'} border backdrop-blur-2xl overflow-hidden`}>
              
              <div className="p-1 relative">
                {/* Floating Label / AI Icon */}
                <div className="absolute top-6 left-6 text-primary flex items-center gap-2 pointer-events-none opacity-80">
                  <Sparkles className="w-5 h-5" />
                  {!idea && <span className="text-lg sm:text-xl font-medium tracking-wide text-textMuted/70">Describe your startup concept, target audience, and core features...</span>}
                </div>

                <textarea
                  ref={textareaRef}
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                      submitForm(e);
                    }
                  }}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  className="w-full bg-transparent text-textMain resize-none outline-none p-6 pt-12 text-lg sm:text-xl font-medium leading-relaxed min-h-[160px] transition-all duration-200 overflow-hidden relative z-10 placeholder-transparent focus:ring-0"
                  maxLength={1000}
                  required
                />
              </div>

              {/* Footer of Textarea */}
              <div className="flex flex-col sm:flex-row justify-between items-center gap-4 px-6 pb-6 pt-4 border-t border-white/5 bg-black/20">
                
                <div className="flex flex-col gap-1 w-full sm:w-auto text-center sm:text-left">
                  <span className={`text-xs font-medium ${idea.length > 900 ? 'text-warning' : 'text-textMuted'}`}>
                    {idea.length} <span className="opacity-40">/ 1000 characters</span>
                  </span>
                  <span className="hidden sm:inline text-[11px] text-textMuted/40 font-mono tracking-widest uppercase mt-0.5">
                    Press {modifierKey} ↵ to analyze
                  </span>
                </div>
                
                <button
                  type="submit"
                  disabled={idea.trim().length < 10}
                  className="relative group w-full sm:w-auto overflow-hidden inline-flex items-center justify-center gap-2 bg-white text-background hover:bg-gray-100 disabled:bg-surface disabled:text-textMuted disabled:cursor-not-allowed px-8 py-3.5 rounded-xl font-bold transition-all duration-300 shadow-md hover:shadow-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:shadow-none"
                >
                  <span className="relative z-10">Analyze My Startup</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform relative z-10" />
                </button>
              </div>
            </div>
          </form>

          {/* Value Preview */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-8 flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm text-textMuted font-medium"
          >
            {VALUE_PREVIEW.map((val, i) => (
              <div key={i} className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-primary/70" />
                <span>{val}</span>
              </div>
            ))}
          </motion.div>

          {/* 4. Smart Suggestions - Expanded width and gap */}
          <div className="mt-16 text-left max-w-5xl xl:max-w-6xl mx-auto">
            <p className="text-sm font-semibold text-textMuted tracking-wider uppercase mb-6 pl-1">Or start with a proven example</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => { setIdea(s.desc); setIsFocused(true); }}
                  className="group text-left p-6 rounded-2xl bg-surface/30 border border-white/5 hover:bg-surface/50 hover:border-primary/30 hover:-translate-y-1 transition-all duration-300 relative overflow-hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-primary shadow-sm hover:shadow-lg"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-[10px] uppercase tracking-widest text-primary font-bold px-2.5 py-1 rounded-sm bg-primary/10">{s.industry}</span>
                    </div>
                    <h4 className="text-textMain font-semibold mb-2 group-hover:text-primary transition-colors">{s.title}</h4>
                    <p className="text-sm text-textMuted leading-relaxed">{s.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* 7 & 8. Trust Section - Distribute width and reduce vertical margin */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="mt-16 lg:mt-20 pt-8 border-t border-white/5 max-w-6xl xl:max-w-7xl mx-auto"
        >
          <p className="text-center text-sm font-semibold text-textMuted tracking-widest uppercase mb-10">Powered By Enterprise-Grade Technology</p>
          <div className="flex flex-wrap justify-center lg:justify-between gap-x-10 gap-y-8 opacity-70 px-4 xl:px-8">
            {TRUST_ITEMS.map((item, i) => (
              <div key={i} className="flex items-center gap-2.5 text-textMain font-medium text-sm sm:text-base">
                <ShieldCheck className="w-5 h-5 text-textMuted" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* 5. AI Capabilities - Increase grid width and gaps */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="mt-16 lg:mt-20 w-full max-w-6xl xl:max-w-7xl mx-auto text-left"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-textMain mb-4">Comprehensive AI Intelligence</h2>
            <p className="text-textMuted text-lg max-w-2xl mx-auto">Four specialized AI agents analyze your idea from every angle, delivering a complete validation report in seconds.</p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 xl:gap-10">
            {CAPABILITIES.map((cap, i) => (
              <div key={i} className="p-8 rounded-3xl bg-surface/40 border border-white/5 hover:border-primary/20 hover:bg-surface/60 transition-all duration-300 shadow-sm hover:shadow-md flex flex-col sm:flex-row gap-6 items-start">
                <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0 text-textMain shadow-inner">
                  <cap.icon className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-textMain mb-3">{cap.title}</h3>
                  <p className="text-textMuted leading-relaxed">{cap.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* 6. How It Works Timeline - Extended max-width */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="mt-16 lg:mt-20 mb-8 w-full max-w-6xl xl:max-w-7xl mx-auto"
        >
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-textMain mb-4">How it works</h2>
            <p className="text-textMuted text-lg max-w-2xl mx-auto">A seamless, automated pipeline from idea to validation.</p>
          </div>
          
          <div className="flex flex-col md:flex-row justify-between relative px-4">
            {/* Desktop Connector Line */}
            <div className="hidden md:block absolute top-[28px] left-[10%] right-[10%] h-[2px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            
            {FLOW_STEPS.map((step, i) => (
              <div key={i} className="relative z-10 flex flex-col items-center text-center flex-1 mb-12 md:mb-0">
                <div className="w-14 h-14 rounded-full bg-surface border-4 border-background flex items-center justify-center text-primary mb-5 shadow-[0_0_20px_rgba(var(--color-primary),0.15)]">
                  <step.icon className="w-6 h-6" />
                </div>
                <h4 className="text-textMain font-bold mb-2">{step.title}</h4>
                <p className="text-sm text-textMuted max-w-[140px] mx-auto">{step.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

      </div>
    </div>
  );
};

export default Home;
