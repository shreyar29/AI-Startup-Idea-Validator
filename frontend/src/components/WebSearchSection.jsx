import React from 'react';
import { motion } from 'framer-motion';
import { 
  Globe, 
  Search, 
  Link2, 
  ShieldCheck, 
  BookOpen, 
  Newspaper, 
  Users, 
  FileText, 
  ExternalLink,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

const WebSearchSection = ({ data }) => {
  const { sourceCounts, displayEvidence, totalEvidence, totalCategories } = React.useMemo(() => {
    const results = data?.search_results || {};
    const categories = Object.keys(results);
    
    const evidenceMap = new Map();
    const counts = {
      'Official Website': 0,
      'Research Report': 0,
      'News': 0,
      'Community': 0
    };
    
    categories.forEach(cat => {
      const items = results[cat] || [];
      items.forEach(item => {
        if (!item.url || !item.title) return;
        
        let domain = 'Unknown Source';
        let normalizedUrl = item.url;
        
        try {
          const urlObj = new URL(item.url);
          domain = urlObj.hostname.toLowerCase().replace(/^www\./, '');
          normalizedUrl = urlObj.origin + urlObj.pathname; 
        } catch(e) {}
        
        if (evidenceMap.has(normalizedUrl)) return;
        
        let sourceType = 'Official Website';
        let SourceIcon = Globe;
        
        if (domain.endsWith('.gov') || domain.endsWith('.edu') || domain.includes('research') || domain.includes('statista') || domain.includes('gartner') || domain.includes('forrester') || domain.includes('mckinsey')) {
          sourceType = 'Research Report';
          SourceIcon = FileText;
        } else if (domain.includes('news') || domain.includes('techcrunch') || domain.includes('forbes') || domain.includes('bloomberg') || domain.includes('wsj')) {
          sourceType = 'News';
          SourceIcon = Newspaper;
        } else if (domain.includes('reddit') || domain.includes('quora') || domain.includes('forum') || domain.includes('community')) {
          sourceType = 'Community';
          SourceIcon = Users;
        }
        
        counts[sourceType]++;
        
        evidenceMap.set(normalizedUrl, {
          ...item,
          normalizedUrl,
          category: cat,
          domain,
          sourceType,
          SourceIcon
        });
      });
    });

    const evidenceList = Array.from(evidenceMap.values());
    
    return {
      sourceCounts: counts,
      displayEvidence: evidenceList.slice(0, 12),
      totalEvidence: evidenceList.length,
      totalCategories: categories.length
    };
  }, [data?.search_results]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      whileInView={{ opacity: 1, y: 0 }} 
      viewport={{ once: true }} 
      className="space-y-10"
    >
      
      {/* Section Header */}
      <div className="flex items-center gap-3 border-b border-border/50 pb-4">
        <div className="bg-primary/10 p-2 rounded-xl">
          <BookOpen className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-textMain tracking-tight">Research Evidence</h2>
      </div>

      {totalEvidence === 0 ? (
        <div className="glass-panel p-10 rounded-3xl border-border/50 flex flex-col items-center justify-center text-center space-y-5 shadow-lg bg-surface/30">
          <div className="w-16 h-16 rounded-full bg-surface border border-border flex items-center justify-center mb-2 shadow-inner">
            <AlertCircle className="w-8 h-8 text-textMuted" />
          </div>
          <h3 className="text-xl md:text-2xl font-bold text-textMain tracking-tight">No external evidence was available for this analysis.</h3>
          <p className="text-textMuted max-w-2xl leading-relaxed text-sm md:text-base">
            The AI validation pipeline relied primarily on synthesized zero-shot analysis and embedded knowledge, as live web retrieval returned no direct URLs. Richer evidence metadata will automatically populate here when external connections are re-established.
          </p>
        </div>
      ) : (
        <>
          {/* Evidence Overview */}
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <div className="glass-panel p-5 rounded-2xl border-border/50 shadow-lg relative overflow-hidden group hover:border-primary/30 transition-colors">
              <h3 className="text-[9px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5 relative z-10">
                <Link2 className="w-3 h-3 text-primary" /> Total Sources
              </h3>
              <div className="text-3xl font-black text-textMain tracking-tight relative z-10">{totalEvidence}</div>
            </div>
            
            <div className="glass-panel p-5 rounded-2xl border-border/50 shadow-lg relative overflow-hidden group hover:border-success/30 transition-colors">
              <h3 className="text-[9px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5 relative z-10">
                <Globe className="w-3 h-3 text-success" /> Official Sites
              </h3>
              <div className="text-3xl font-black text-textMain tracking-tight relative z-10">{sourceCounts['Official Website']}</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border-border/50 shadow-lg relative overflow-hidden group hover:border-info/30 transition-colors">
              <h3 className="text-[9px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5 relative z-10">
                <FileText className="w-3 h-3 text-blue-400" /> Research Reports
              </h3>
              <div className="text-3xl font-black text-textMain tracking-tight relative z-10">{sourceCounts['Research Report']}</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border-border/50 shadow-lg relative overflow-hidden group hover:border-warning/30 transition-colors">
              <h3 className="text-[9px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5 relative z-10">
                <Newspaper className="w-3 h-3 text-warning" /> News Articles
              </h3>
              <div className="text-3xl font-black text-textMain tracking-tight relative z-10">{sourceCounts['News']}</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border-border/50 shadow-lg relative overflow-hidden group hover:border-purple-400/30 transition-colors">
              <h3 className="text-[9px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5 relative z-10">
                <Users className="w-3 h-3 text-purple-400" /> Community
              </h3>
              <div className="text-3xl font-black text-textMain tracking-tight relative z-10">{sourceCounts['Community']}</div>
            </div>
            
            <div className="glass-panel p-5 rounded-2xl border-border/50 shadow-lg relative overflow-hidden group hover:border-primary/30 transition-colors">
              <h3 className="text-[9px] font-bold text-textMuted uppercase tracking-widest mb-2 flex items-center gap-1.5 relative z-10">
                <Search className="w-3 h-3 text-primary" /> Categories
              </h3>
              <div className="text-3xl font-black text-textMain tracking-tight relative z-10">{totalCategories}</div>
            </div>
          </div>

          {/* Evidence Cards */}
          <div className="space-y-6 pt-6">
            <h3 className="text-[10px] font-bold text-textMuted uppercase tracking-widest flex items-center gap-2 border-b border-border/30 pb-3">
              <Globe className="w-3.5 h-3.5 text-primary" /> Verified External Citations
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {displayEvidence.map((evidence) => (
                <div key={evidence.normalizedUrl} className="glass-panel rounded-3xl border-border/50 shadow-lg overflow-hidden flex flex-col group hover:border-primary/40 transition-colors bg-gradient-to-br from-surface to-background/50">
                  
                  {/* Card Header (Source info) */}
                  <div className="p-6 border-b border-border/30 flex justify-between items-start gap-4">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1.5 line-clamp-1">
                        {evidence.domain}
                      </span>
                      <h4 className="text-sm font-bold text-textMain line-clamp-2 leading-relaxed group-hover:text-primary transition-colors">
                        {evidence.title}
                      </h4>
                    </div>
                    
                  </div>
                  
                  {/* Card Body (Summary) */}
                  <div className="p-6 flex-grow">
                    <p className="text-xs text-textMain leading-relaxed line-clamp-3 font-medium">
                      {evidence.content || "No detailed summary available for this source."}
                    </p>
                  </div>
                  
                  {/* Card Footer (Metadata & Link) */}
                  <div className="p-4 bg-surface/30 border-t border-border/30 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {/* Source Type Badge */}
                      <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-surface border border-border/80 shadow-sm">
                        <evidence.SourceIcon className="w-3.5 h-3.5 text-textMuted" />
                        <span className="text-[9px] font-bold text-textMuted uppercase tracking-wider">{evidence.sourceType}</span>
                      </div>
                      
                      {/* Category Badge */}
                      <span className="text-[9px] font-bold text-textMuted uppercase tracking-wider line-clamp-1">
                        {evidence.category.replace(/_/g, ' ')}
                      </span>
                    </div>
                    
                    <a 
                      href={evidence.url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="p-2 rounded-xl bg-primary/10 text-primary hover:bg-primary hover:text-textMain transition-colors shadow-sm"
                      title="Open Source"
                      aria-label={`Open external source: ${evidence.title}`}
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
            
            {totalEvidence > 12 && (
              <div className="pt-6 text-center">
                <span className="text-[10px] font-bold text-textMuted uppercase tracking-widest bg-surface/50 px-4 py-2 rounded-full border border-border/50">
                  Showing top 12 of {totalEvidence} sources analyzed
                </span>
              </div>
            )}
          </div>
        </>
      )}
    </motion.div>
  );
};

export default WebSearchSection;
