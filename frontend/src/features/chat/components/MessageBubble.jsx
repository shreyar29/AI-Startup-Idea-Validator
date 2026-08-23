import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Info, RefreshCw } from 'lucide-react';

export const MessageBubble = ({ message, onRetry }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
      <div 
        className={`max-w-[85%] p-4 rounded-2xl ${
          isUser 
            ? 'bg-blue-600 text-white rounded-tr-sm shadow-md' 
            : message.isError 
              ? 'bg-red-500/10 border border-red-500/30 text-red-200 rounded-tl-sm'
              : 'bg-surface/60 border border-white/10 text-textMain rounded-tl-sm shadow-sm'
        }`}
        role={message.isError ? "alert" : "article"}
      >
        {message.role === 'vera' ? (
          <div className="prose prose-invert prose-sm max-w-none leading-relaxed">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm font-medium">{message.content}</p>
        )}
      </div>
      
      <div className="flex items-center gap-2 mt-1 px-2">
        <span className="text-[10px] text-textDim">
          {message.timestamp}
        </span>
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold text-textMuted">
            <Info className="w-3 h-3 text-blue-400" />
            <span>Sources: {message.sources.join(', ')}</span>
          </div>
        )}
        
        {message.isError && onRetry && (
          <button 
            onClick={onRetry}
            className="flex items-center gap-1 text-[10px] uppercase font-bold text-red-400 hover:text-red-300 transition-colors"
            aria-label="Retry message"
          >
            <RefreshCw className="w-3 h-3" /> Retry
          </button>
        )}
      </div>
    </div>
  );
};
