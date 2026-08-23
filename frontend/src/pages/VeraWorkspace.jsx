import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { chatService } from '../features/chat/services/chatService';
import { MessageBubble } from '../features/chat/components/MessageBubble';
import { 
  Send, BrainCircuit, FileText, Target, LineChart, 
  ShieldAlert, Sparkles, Plus, Copy, RotateCcw, 
  LayoutDashboard, ArrowLeft
} from 'lucide-react';

const VeraWorkspace = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract sessionId from router state or local storage (stubbed for now)
  const sessionId = location.state?.sessionId || localStorage.getItem('active_report_id');
  
  const [messages, setMessages] = useState([
    {
      role: 'vera',
      content: "I am Vera, your AI Co-Founder. I have loaded your entire startup validation report into my working memory. How can we improve this idea today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [veraMode, setVeraMode] = useState('Founder');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (e, forcedInput = null) => {
    if (e) e.preventDefault();
    const query = forcedInput || input;
    if (!query.trim() || loading || !sessionId) return;
    
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
        sessionId, 
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

  const handleNewSession = async () => {
    if (!sessionId) return;
    try {
      await chatService.clearSession(sessionId);
      setMessages([{
        role: 'vera',
        content: "I am Vera, your AI Co-Founder. I have cleared my memory for this report. Let's start a fresh strategic session. How can we improve this idea today?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } catch (err) {
      console.error("Failed to clear session", err);
    }
  };

  if (!sessionId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] p-8">
        <ShieldAlert className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-textMain">No Active Startup Report</h2>
        <p className="text-textMuted mt-2">Vera requires an active validation report to provide context-aware insights.</p>
        <button onClick={() => navigate('/dashboard')} className="mt-6 bg-primary text-white px-6 py-2 rounded-lg">
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
          <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 text-textMuted hover:text-textMain transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>
        </div>
        <div className="p-4">
          <button onClick={handleNewSession} className="flex items-center gap-2 w-full bg-primary/10 text-primary border border-primary/20 rounded-lg p-3 font-medium hover:bg-primary/20 transition-colors">
            <Plus className="w-4 h-4" /> New Strategic Session
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <h4 className="text-xs font-bold text-textDim uppercase tracking-wider mb-2">Previous Sessions</h4>
          <div className="p-3 rounded-lg bg-surface border border-border cursor-pointer hover:border-primary/50 transition-colors text-sm text-textMain truncate">
            Market Expansion Strategy
          </div>
          <div className="p-3 rounded-lg bg-transparent cursor-pointer hover:bg-surface transition-colors text-sm text-textMuted truncate">
            Investor Pitch Polish
          </div>
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
              <p className="text-xs text-textMuted">Connected to Report ID: {sessionId.slice(0, 8)}...</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-textMuted">Persona:</span>
            <select 
              value={veraMode}
              onChange={(e) => setVeraMode(e.target.value)}
              className="bg-surface border border-border text-sm text-primary font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
            >
              <option value="Founder">Founder Mode</option>
              <option value="Investor">Investor Mode</option>
              <option value="VC Partner">VC Partner Mode</option>
              <option value="Competitor">Competitor Mode</option>
              <option value="Customer">Customer Mode</option>
            </select>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="max-w-3xl mx-auto w-full space-y-6">
            {messages.map((msg, idx) => (
              <MessageBubble key={idx} message={msg} />
            ))}
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
        </div>
      </div>

    </div>
  );
};

export default VeraWorkspace;
