import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Search, Database, LineChart, Target, Zap } from 'lucide-react';

const About = () => {
  const steps = [
    {
      icon: Search,
      title: '1. Intelligent Context Scraping',
      desc: 'Our Web Search Agent scours the internet for live data, extracting the most relevant industry reports and news.'
    },
    {
      icon: Database,
      title: '2. Market Sizing & Trends',
      desc: 'The Market Agent processes the raw data to identify Total Addressable Market (TAM) and emerging growth trends.'
    },
    {
      icon: Target,
      title: '3. Competitor Profiling',
      desc: 'The Competitor Agent identifies direct and indirect rivals, analyzing their weaknesses and pricing strategies.'
    },
    {
      icon: Cpu,
      title: '4. Target Customer Mapping',
      desc: 'The Customer Agent segments the market and identifies the deepest pain points for your ideal customer profile.'
    },
    {
      icon: LineChart,
      title: '5. Comparison Synthesis',
      desc: 'The Comparison Agent builds a feature matrix showing exactly how your idea stacks up against the market.'
    },
    {
      icon: Zap,
      title: '6. Guardrail Verification',
      desc: 'Our Orchestrator verifies every claim against the source material to prevent AI hallucinations before delivering the final report.'
    }
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-bold mb-6"
        >
          How VentureLens Works
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-textMuted"
        >
          VentureLens isn't just a simple wrapper around an LLM. It's a sophisticated Peer-to-Peer (P2P) Mesh Network of autonomous AI agents designed to ruthlessly validate startup ideas.
        </motion.p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {steps.map((step, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: idx * 0.1 }}
            className="glass-panel p-8 rounded-3xl"
          >
            <div className="bg-primary/10 w-14 h-14 rounded-2xl flex items-center justify-center mb-6 border border-primary/20">
              <step.icon className="h-7 w-7 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-3">{step.title}</h3>
            <p className="text-textMuted leading-relaxed">{step.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default About;
