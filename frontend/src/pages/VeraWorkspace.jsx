import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { chatService } from '../features/chat/services/chatService';
import { getProjects, getTasks } from '../services/api';
import { MessageBubble } from '../features/chat/components/MessageBubble';
import { 
  Send, BrainCircuit, FileText, Target, LineChart, 
  ShieldAlert, Sparkles, Plus, Copy, RotateCcw, 
  LayoutDashboard, ArrowLeft
} from 'lucide-react';
import { storageService } from '../services/storageService';

const VeraWorkspace = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract sessionId from router state or storage
  const [activeSessionId, setActiveSessionId] = useState(location.state?.sessionId || storageService.getActiveReportId() || null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [veraMode, setVeraMode] = useState('Founder');
  const [sessions, setSessions] = useState([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [workspaceTasks, setWorkspaceTasks] = useState([]);
  
  const [localThreads, setLocalThreads] = useState([]);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [currentSessionName, setCurrentSessionName] = useState('');
  const [newSessionName, setNewSessionName] = useState('');
  const messagesEndRef = useRef(null);

  // Load local threads when report ID changes
  const currentReportId = location.state?.sessionId || storageService.getActiveReportId();
  useEffect(() => {
    if (currentReportId) {
      const savedStr = localStorage.getItem(`vera_threads_${currentReportId}`);
      if (savedStr) {
        setLocalThreads(JSON.parse(savedStr));
      } else {
        setLocalThreads([]);
      }
    }
  }, [currentReportId]);

  // Load workspace tasks
  useEffect(() => {
    const fetchWorkspace = async () => {
      if (!currentReportId) return;
      try {
        const projects = await getProjects();
        const p = projects.find(x => x.report_id === currentReportId);
        if (p) {
          const tasks = await getTasks(p.id);
          setWorkspaceTasks(tasks.slice(0, 5));
        }
      } catch (err) {}
    };
    fetchWorkspace();
    const interval = setInterval(fetchWorkspace, 10000);
    return () => clearInterval(interval);
  }, [currentReportId]);
  
  // Fetch sessions on mount
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/reports`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (res.ok) {
          const data = await res.json();
          setSessions(data);
          // If no active session, pick the first one
          if (!activeSessionId && data.length > 0) {
            setActiveSessionId(data[0].id);
          }
        }
      } catch (err) {
        console.error("Failed to fetch sessions", err);
      }
    };
    fetchSessions();
  }, []);

  // Fetch chat history when active session changes
  useEffect(() => {
    const fetchHistory = async () => {
      if (!activeSessionId) return;
      setIsHistoryLoading(true);
      try {
        const historyData = await chatService.getSessionHistory(activeSessionId);
        if (historyData.messages && historyData.messages.length > 0) {
          const formatted = historyData.messages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }));
          setMessages(formatted);
        } else {
          setMessages([{
            role: 'vera',
            content: "I am Vera, your AI Co-Founder. I have loaded your entire startup validation report into my working memory. How can we improve this idea today?",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]);
        }
      } catch (err) {
        console.error("Failed to load chat history", err);
        setMessages([{
          role: 'vera',
          content: "I am Vera. Failed to load chat history.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
      } finally {
        setIsHistoryLoading(false);
      }
    };
    fetchHistory();
  }, [activeSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (e, forcedInput = null) => {
    if (e) e.preventDefault();
    const query = forcedInput || input;
    if (!query.trim() || loading || !activeSessionId) return;
    
    setInput('');
    const userTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setMessages(prev => [...prev, { role: 'user', content: query, timestamp: userTimestamp }]);
    
    setLoading(true);
    const veraTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    setMessages(prev => [...prev, { 
      role: 'vera', 
      content: '', 
      sources: [],
      timestamp: veraTimestamp 
    }]);
    
    try {
      await chatService.streamMessage(
        activeSessionId, 
        currentReportId || activeSessionId,
        query, 
        'overview',
        veraMode,
        (chunk) => {
          setMessages(prev => {
            const newMessages = [...prev];
            const last = newMessages.length - 1;
            if (newMessages[last].role === 'vera') {
              newMessages[last] = { ...newMessages[last], content: newMessages[last].content + chunk };
            }
            return newMessages;
          });
        },
        () => setLoading(false),
        (error) => {
          setMessages(prev => {
            const newMessages = [...prev];
            const last = newMessages.length - 1;
            if (newMessages[last].role === 'vera') {
              newMessages[last] = { ...newMessages[last], content: `Error: ${error.message}`, isError: true };
            }
            return newMessages;
          });
          setLoading(false);
        }
      );
    } catch (err) {
      setLoading(false);
    }
  };

  const handleQuickAction = (action) => {
    handleSubmit(null, action);
  };

  const handleOpenSessionModal = () => {
    if (!activeSessionId || !currentReportId) return;
    const existing = localThreads.find(t => t.id === activeSessionId);
    setCurrentSessionName(existing ? existing.name : 'Initial Strategy');
    setNewSessionName('');
    setShowSessionModal(true);
  };

  const submitNewSession = () => {
    if (!currentSessionName.trim() || !newSessionName.trim() || !activeSessionId || !currentReportId) return;
    
    let savedThreads = [...localThreads];
    
    // Add current session if not exists
    if (!savedThreads.find(t => t.id === activeSessionId)) {
        savedThreads.push({ id: activeSessionId, name: currentSessionName.trim(), reportId: currentReportId });
    } else {
        const idx = savedThreads.findIndex(t => t.id === activeSessionId);
        savedThreads[idx].name = currentSessionName.trim();
    }

    // Create a new session ID
    const newSessionId = (typeof crypto !== 'undefined' && crypto.randomUUID) 
      ? crypto.randomUUID() 
      : 'session-' + Math.random().toString(36).substring(2, 15);
    
    savedThreads.push({ id: newSessionId, name: newSessionName.trim(), reportId: currentReportId });
    
    localStorage.setItem(`vera_threads_${currentReportId}`, JSON.stringify(savedThreads));
    setLocalThreads(savedThreads);
    setActiveSessionId(newSessionId);
    setShowSessionModal(false);
    
    setMessages([{
      role: 'vera',
      content: `I am Vera, your AI Co-Founder. I have loaded your entire startup validation report into my working memory. We are now in a new strategic session: "${newSessionName.trim()}". How can we improve this idea today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
  };

  if (!activeSessionId && sessions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] p-8 bg-background">
        <ShieldAlert className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-textMain">No Active Startup Report</h2>
        <p className="text-textMuted mt-2">Vera requires an active validation report to provide context-aware insights.</p>
        <button onClick={() => navigate('/dashboard', { state: { sessionId: currentReportId } })} className="mt-6 bg-primary text-white px-6 py-2 rounded-lg">
          Go to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-64px)] w-full overflow-hidden bg-background">
      
      {/* LEFT SIDEBAR: History & Sessions */}
      <div className="hidden lg:flex w-64 border-r border-border flex-col bg-surface/30">
        <div className="p-4 border-b border-border">
          <button onClick={() => navigate('/dashboard', { state: { sessionId: currentReportId } })} className="flex items-center gap-2 text-textMuted hover:text-textMain transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>
        </div>
        <div className="p-4">
          <button onClick={handleOpenSessionModal} className="flex items-center gap-2 w-full bg-primary/10 text-primary border border-primary/20 rounded-lg p-3 font-medium hover:bg-primary/20 transition-colors">
            <Plus className="w-4 h-4" /> New Strategic Session
          </button>
        </div>
        {localThreads.length > 0 && (
          <div className="px-4 pb-2 space-y-1">
            <h4 className="text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Saved Threads</h4>
            {localThreads.map(t => (
              <div 
                key={t.id} 
                onClick={() => setActiveSessionId(t.id)}
                className={`px-3 py-2 rounded-md border cursor-pointer transition-colors text-xs truncate ${
                  activeSessionId === t.id ? 'bg-primary/20 border-primary/50 text-primary' : 'bg-transparent border-transparent hover:bg-surface text-textMuted'
                }`}
              >
                {t.name}
              </div>
            ))}
          </div>
        )}
        <div className="flex-1 overflow-y-auto p-4 space-y-2 border-t border-border">
          <h4 className="text-xs font-bold text-textDim uppercase tracking-wider mb-2">Previous Sessions</h4>
          {sessions.map(s => (
            <div 
              key={s.id} 
              onClick={() => setActiveSessionId(s.id)}
              className={`p-3 rounded-lg border cursor-pointer transition-colors text-sm truncate ${
                activeSessionId === s.id ? 'bg-surface border-primary/50 text-textMain' : 'bg-transparent border-transparent hover:bg-surface text-textMuted'
              }`}
            >
              {s.startup_idea}
            </div>
          ))}
        </div>
      </div>

      {/* CENTER: Chat Interface */}
      <div className="flex-1 flex flex-col relative bg-background">
        {/* Header */}
        <div className="h-16 border-b border-border flex items-center justify-between px-6 bg-surface/50 backdrop-blur-sm z-10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-textMain">Vera AI Workspace</h2>
              <p className="text-xs text-textMuted">Connected to Report ID: {activeSessionId?.slice(0, 8)}...</p>
            </div>
          </div>
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-textMuted">Persona:</span>
              <select 
                value={veraMode}
                onChange={(e) => setVeraMode(e.target.value)}
                className="bg-surface border border-border text-sm text-primary font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
              >
                <option value="Founder Mode">Founder</option>
                <option value="Investor Mode">Investor</option>
                <option value="VC Partner Mode">VC Partner</option>
                <option value="Competitor Mode">Competitor</option>
                <option value="Customer Mode">Customer</option>
              </select>
            </div>
            <span className="text-[10px] text-textMuted mt-1">Choose a perspective for Vera's responses.</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="max-w-3xl mx-auto w-full space-y-6">
            {isHistoryLoading ? (
              <div className="flex items-center justify-center p-8 text-textMuted">Loading history...</div>
            ) : (
              messages.map((msg, idx) => (
                <MessageBubble key={idx} message={msg} />
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 bg-background">
          <div className="max-w-3xl mx-auto relative">
            <form onSubmit={handleSubmit} className="relative flex items-center">
              <input 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
                placeholder="Ask Vera about your market, competitors, or roadmap..."
                className="w-full bg-surface border border-border rounded-xl pl-4 pr-12 py-4 text-sm text-textMain placeholder-textMuted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all shadow-lg"
              />
              <button 
                type="submit"
                disabled={!input.trim() || loading}
                className="absolute right-2 p-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors shadow-md"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="text-center mt-2">
              <span className="text-[10px] text-textDim">Vera can make mistakes. Consider verifying strategic advice.</span>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT SIDEBAR: Context & Quick Actions */}
      <div className="hidden xl:flex w-80 border-l border-border flex-col bg-surface/30">
        <div className="p-4 border-b border-border bg-surface/50">
          <h3 className="font-semibold text-textMain flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-primary" /> Active Context
          </h3>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-textDim uppercase tracking-wider">Quick Actions</h4>
            <div className="grid grid-cols-1 gap-2">
              <button onClick={() => handleQuickAction("Challenge my core assumptions")} className="text-left px-3 py-2 text-sm text-textMain bg-surface border border-border rounded-lg hover:border-primary/50 hover:text-primary transition-colors flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" /> Challenge Assumptions
              </button>
              <button onClick={() => handleQuickAction("Draft a 60-second elevator pitch")} className="text-left px-3 py-2 text-sm text-textMain bg-surface border border-border rounded-lg hover:border-primary/50 hover:text-primary transition-colors flex items-center gap-2">
                <FileText className="w-4 h-4" /> Elevator Pitch
              </button>
              <button onClick={() => handleQuickAction("Identify my weakest market gap")} className="text-left px-3 py-2 text-sm text-textMain bg-surface border border-border rounded-lg hover:border-primary/50 hover:text-primary transition-colors flex items-center gap-2">
                <Target className="w-4 h-4" /> Weakest Gap
              </button>
              <button onClick={() => handleQuickAction("Suggest a pivot for higher margins")} className="text-left px-3 py-2 text-sm text-textMain bg-surface border border-border rounded-lg hover:border-primary/50 hover:text-primary transition-colors flex items-center gap-2">
                <LineChart className="w-4 h-4" /> Pivot Opportunity
              </button>
            </div>
          </div>
          
          <div className="space-y-3 border-t border-border pt-4">
            <h4 className="text-xs font-bold text-textDim uppercase tracking-wider">Report Intelligence</h4>
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <p className="text-xs text-blue-400 font-medium leading-relaxed">
                Vera is synchronized with your database record. Every prompt automatically cross-references your live Validation Score, GTM Strategy, and Competitor Matrix.
              </p>
            </div>
          </div>
          
          {workspaceTasks.length > 0 && (
            <div className="space-y-3 border-t border-border pt-4">
              <h4 className="text-xs font-bold text-textDim uppercase tracking-wider">Added to Workspace</h4>
              <div className="grid grid-cols-1 gap-2">
                {workspaceTasks.map(t => (
                  <button 
                    key={t.id} 
                    onClick={() => handleQuickAction(`Help me execute this strategy from my workspace: "${t.title}". Details: ${t.description || "N/A"}`)}
                    className="p-2.5 bg-surface border border-border rounded-lg flex flex-col gap-1 shadow-sm text-left hover:border-primary/50 transition-all cursor-pointer group"
                  >
                    <span className="text-xs font-medium text-textMain leading-snug group-hover:text-primary transition-colors">{t.title}</span>
                    <span className="text-[10px] text-textMuted line-clamp-2 group-hover:text-textMuted transition-colors">{t.description || "No description provided."}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Session Modal */}
      <AnimatePresence>
        {showSessionModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-surface border border-border p-6 rounded-2xl shadow-2xl max-w-md w-full"
            >
              <h3 className="text-xl font-bold text-textMain mb-4">Start New Strategic Session</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-textMuted mb-1">Name for Current Session</label>
                  <input
                    type="text"
                    value={currentSessionName}
                    onChange={(e) => setCurrentSessionName(e.target.value)}
                    placeholder="e.g. Initial Strategy"
                    className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:border-primary/50"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-textMuted mb-1">Name for New Session</label>
                  <input
                    type="text"
                    value={newSessionName}
                    onChange={(e) => setNewSessionName(e.target.value)}
                    placeholder="e.g. Marketing Pivot"
                    className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-8">
                <button
                  onClick={() => setShowSessionModal(false)}
                  className="px-4 py-2 rounded-lg text-sm font-medium text-textMuted hover:bg-surface/80 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={submitNewSession}
                  disabled={!currentSessionName.trim() || !newSessionName.trim()}
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-primary text-white hover:bg-primary/90 disabled:opacity-50 transition-colors shadow-lg"
                >
                  Start Session
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default VeraWorkspace;
