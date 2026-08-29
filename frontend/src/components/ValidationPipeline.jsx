import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, CircleDashed, Loader2, XCircle, Terminal, WifiOff } from 'lucide-react';
import { VeraLoader } from './vera/VeraLoader';

const STAGES = [
  { id: 'Query Strategist', label: 'Research Strategy', type: 'single', agents: ['Query Strategist'] },
  { id: 'Web Search Agent', label: 'Evidence Collection', type: 'single', agents: ['Web Search Agent'] },
  { 
    id: 'Parallel Analysis', 
    label: 'Parallel Intelligence', 
    type: 'parallel',
    agents: ['Market Agent', 'Customer Agent', 'Competitor Agent']
  },
  { id: 'Comparison Agent', label: 'Strategic Synthesis', type: 'single', agents: ['Comparison Agent'] },
  { id: 'Guardrails', label: 'Fact Verification', type: 'single', agents: ['Guardrails'] },
  { id: 'Report Generator', label: 'Executive Report', type: 'single', agents: ['Report Generator'] }
];

const ValidationPipeline = ({ requestId }) => {
  const [agentStatuses, setAgentStatuses] = useState({});
  const [pipelineStatus, setPipelineStatus] = useState('running'); // running, completed, failed
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // connecting, connected, reconnecting, closed
  const [currentActiveStep, setCurrentActiveStep] = useState(null);

  useEffect(() => {
    if (!requestId) return;

    const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');
    const eventSource = new EventSource(`${API_BASE_URL}/api/progress/${requestId}`);

    eventSource.onopen = () => {
      setConnectionStatus('connected');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { agent, status, message, id } = data;
        const eventId = id || event.lastEventId || `${Date.now()}-${Math.random()}`;

        if (agent && agent !== 'Orchestrator') {
          setCurrentActiveStep(agent);
        }

        setAgentStatuses(prev => ({
          ...prev,
          [agent]: status
        }));

        if (agent === 'Orchestrator' && (status === 'completed' || status === 'failed')) {
          setPipelineStatus(status);
          eventSource.close();
          setConnectionStatus('closed');
        }
      } catch (err) {
        console.error('Error parsing SSE data', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('EventSource failed:', err);
      if (eventSource.readyState === EventSource.CLOSED) {
        setConnectionStatus('closed');
      } else {
        setConnectionStatus('reconnecting');
      }
    };

    return () => {
      eventSource.close();
    };
  }, [requestId]);



  const getStageStatus = useCallback((stage) => {
    if (stage.type === 'single') {
      const status = agentStatuses[stage.agents[0]];
      return status || 'waiting'; // waiting, running, completed, failed
    } else {
      // Parallel stage
      const statuses = stage.agents.map(a => agentStatuses[a] || 'waiting');
      if (statuses.some(s => s === 'failed')) return 'failed';
      if (statuses.every(s => s === 'completed')) return 'completed';
      if (statuses.some(s => s === 'running' || s === 'completed')) return 'running';
      return 'waiting';
    }
  }, [agentStatuses]);

  const progressPercentage = useMemo(() => {
    let completedWeight = 0;
    
    STAGES.forEach(stage => {
      if (stage.type === 'single') {
        const status = agentStatuses[stage.agents[0]];
        if (status === 'completed') completedWeight += 1;
      } else {
        let parallelCompleted = 0;
        stage.agents.forEach(a => {
          if (agentStatuses[a] === 'completed') parallelCompleted += 1;
        });
        completedWeight += (parallelCompleted / stage.agents.length);
      }
    });

    return (completedWeight / STAGES.length) * 100;
  }, [agentStatuses]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 w-full max-w-5xl mx-auto space-y-8 py-12">
      
      {/* Vera Intelligence Loader */}
      <div className="w-full">
        {pipelineStatus !== 'completed' && pipelineStatus !== 'failed' && (
          <VeraLoader currentStep={currentActiveStep} />
        )}
        
        {pipelineStatus === 'completed' && (
           <h2 className="text-3xl font-bold text-textMain tracking-tight text-center">
             Validation Complete
           </h2>
        )}
        {pipelineStatus === 'failed' && (
           <h2 className="text-3xl font-bold text-textMain tracking-tight text-center">
             Validation Failed
           </h2>
        )}
      </div>

      <div className="w-full text-center space-y-4">
        <div 
          className="w-full h-2 bg-surface/50 rounded-full overflow-hidden border border-border"
          role="progressbar"
          aria-valuenow={Math.round(progressPercentage)}
          aria-valuemin="0"
          aria-valuemax="100"
        >
          <motion.div 
            className={`h-full ${pipelineStatus === 'failed' ? 'bg-red-500' : 'bg-primary'}`}
            initial={{ width: 0 }}
            animate={{ width: `${progressPercentage}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      <div className="w-full max-w-2xl mx-auto">
        {/* Pipeline Orchestration UI */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col space-y-4">
          <h3 className="text-xl font-semibold text-textMain mb-2 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-primary" />
            Orchestration Flow
          </h3>
          
          <div className="space-y-3 relative">
            {/* Connecting line */}
            <div className="absolute left-[1.3rem] top-6 bottom-6 w-0.5 bg-border -z-10" />

            {STAGES.map((stage, index) => {
              const status = getStageStatus(stage);
              
              const isCompleted = status === 'completed';
              const isFailed = status === 'failed';
              const isRunning = status === 'running';
              const isWaiting = status === 'waiting';

              return (
                <motion.div
                  key={stage.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex items-center gap-4 p-4 rounded-xl border relative bg-surface/80 backdrop-blur-sm ${
                    isRunning ? 'border-primary/50 shadow-[0_0_15px_rgba(var(--color-primary),0.1)]' : 
                    isCompleted ? 'border-success/30' : 
                    isFailed ? 'border-red-500/30' : 'border-border/50 opacity-60'
                  }`}
                >
                  <div className={`shrink-0 flex items-center justify-center rounded-full bg-background ${isRunning ? 'animate-pulse' : ''}`}>
                    {isCompleted ? (
                      <CheckCircle2 className="w-6 h-6 text-success" />
                    ) : isFailed ? (
                      <XCircle className="w-6 h-6 text-red-500" />
                    ) : isRunning ? (
                      <Loader2 className="w-6 h-6 text-primary animate-spin" />
                    ) : (
                      <CircleDashed className="w-6 h-6 text-textDim" />
                    )}
                  </div>
                  
                  <div className="flex-grow">
                    <span className={`font-medium block ${
                      isCompleted ? 'text-textMain' : 
                      isFailed ? 'text-red-400' :
                      isRunning ? 'text-primary' : 'text-textMuted'
                    }`}>
                      {stage.label}
                    </span>
                    {stage.type === 'parallel' && (
                      <div className="flex gap-2 mt-1">
                        {stage.agents.map(agent => {
                          const agentStat = agentStatuses[agent] || 'waiting';
                          return (
                            <div key={agent} className="text-[10px] uppercase tracking-wider font-semibold flex items-center gap-1">
                              <span className={`w-1.5 h-1.5 rounded-full ${
                                agentStat === 'completed' ? 'bg-success' : 
                                agentStat === 'running' ? 'bg-primary animate-pulse' : 
                                agentStat === 'failed' ? 'bg-red-500' : 'bg-border'
                              }`} />
                              <span className={
                                agentStat === 'completed' ? 'text-success/80' : 
                                agentStat === 'running' ? 'text-primary/80' : 
                                agentStat === 'failed' ? 'text-red-500/80' : 'text-textDim'
                              }>{agent.split(' ')[0]}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                  
                  <div className="shrink-0 text-xs font-medium">
                    {isRunning && <span className="text-primary animate-pulse">Running...</span>}
                    {isCompleted && <span className="text-success">Done</span>}
                    {isFailed && <span className="text-red-500">Failed</span>}
                    {isWaiting && <span className="text-textDim">Pending</span>}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValidationPipeline;
