import React, { useState, useRef, Suspense, lazy } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, Shield, Cpu, Zap, LogOut, Upload, BrainCircuit, TrendingUp, Landmark, 
  Newspaper, Coins, BarChart3, ChevronRight, Loader2, Search 
} from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';

// PERFORMANCE: Lazy Load non-critical components
const VisualPortal = lazy(() => import('../components/VisualPortal').then(m => ({ default: m.VisualPortal })));

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [researchMode, setResearchMode] = useState<'fast' | 'deep'>('fast');
  const [streamedText, setStreamedText] = useState('');
  const [aiResponse, setAiResponse] = useState<any>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const categories = [
    { name: 'Equity', icon: TrendingUp, color: 'blue', desc: 'Stocks & Sector Intel' },
    { name: 'Mutual Funds', icon: Landmark, color: 'emerald', desc: 'NAV & Portfolio RAG' },
    { name: 'Commodities', icon: Coins, color: 'amber', desc: 'Gold, Oil & Forex' },
    { name: 'IPOs', icon: Zap, color: 'purple', desc: 'Upcoming Listings' },
    { name: 'News', icon: Newspaper, color: 'rose', desc: 'Sentiment Analysis' },
    { name: 'Derivatives', icon: BarChart3, color: 'indigo', desc: 'Option Chain Insights' }
  ];

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  const askDocumind = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() && !selectedFile) return;
    
    setLoading(true);
    setStreamedText('');
    setAiResponse(null);

    const token = (await supabase.auth.getSession()).data.session?.access_token;

    try {
      if (selectedFile) {
        // PERFORMANCE: No streaming for analysis yet (requires LLM to be done first for heavy doc parsing)
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('prompt', query || "Analyze this financial document.");
        formData.append('mode', researchMode);
        const resp = await fetch('http://localhost:8000/api/analyze-file', { 
            method: 'POST', 
            body: formData,
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await resp.json();
        setAiResponse(data);
      } else {
        // LAYER 1: STREAMING FIRST (Speed: <300ms for first token)
        const response = await fetch('http://localhost:8000/api/chat-stream', {
          method: 'POST',
          headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ prompt: query, mode: researchMode }),
        });

        if (!response.body) return;
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          setStreamedText(prev => prev + chunk);
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
      setSelectedFile(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-blue-500/30">
      <nav className="border-b border-white/5 bg-[#020617]/40 backdrop-blur-2xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-2xl shadow-blue-600/20 cursor-pointer active:scale-95 transition-all">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-black tracking-tighter text-white uppercase hidden sm:block">DOCUMIND</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex bg-slate-900/50 rounded-2xl p-1 border border-white/5">
              <button onClick={() => setResearchMode('fast')} className={`px-5 py-2 rounded-xl text-[10px] font-black tracking-widest transition-all ${researchMode === 'fast' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>FAST</button>
              <button onClick={() => setResearchMode('deep')} className={`px-5 py-2 rounded-xl text-[10px] font-black tracking-widest transition-all ${researchMode === 'deep' ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>DEEP</button>
            </div>
            <button onClick={handleLogout} className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-rose-400 transition-all active:scale-90"><LogOut className="w-5 h-5" /></button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <header className="mb-16">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3 text-blue-500 text-xs font-black tracking-[0.3em] uppercase mb-6">
              <BrainCircuit className="w-5 h-5" />
              <span>Omni-Discovery Fleet Online</span>
            </motion.div>
            <h1 className="text-6xl md:text-8xl font-black text-white tracking-tighter mb-10 leading-[0.9]">
              Hard Intelligence. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-indigo-400 to-emerald-400">Zero Latency.</span>
            </h1>
            
            <form onSubmit={askDocumind} className="max-w-4xl relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-[34px] blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={selectedFile ? `Analyzing ${selectedFile.name}...` : "Scan Assets, Trends, IPOs, or Commodities..."}
                className="relative w-full bg-[#0a0f1e] border border-white/10 rounded-[32px] py-8 pl-10 pr-44 text-xl text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500/50 transition-all backdrop-blur-3xl shadow-2xl"
              />
              <div className="absolute right-4 top-4 flex gap-3">
                <button type="button" onClick={() => fileInputRef.current?.click()} className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all ${selectedFile ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-white/5 text-slate-500 hover:bg-white/10 hover:text-white border border-white/5'}`}><Upload className="w-6 h-6" /></button>
                <button disabled={loading} className="px-10 bg-blue-600 rounded-2xl text-white font-black hover:bg-blue-500 transition-all shadow-xl shadow-blue-600/20 active:scale-95 flex items-center justify-center min-w-[120px]"> 
                  {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <ChevronRight className="w-8 h-8" />} 
                </button>
              </div>
              <input type="file" ref={fileInputRef} onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])} className="hidden" />
            </form>
        </header>

        <AnimatePresence>
            {!loading && !streamedText && !aiResponse && (
                <motion.div initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {categories.map((cat, i) => (
                        <button key={cat.name} className="glass-panel p-8 rounded-[36px] flex flex-col items-start gap-4 hover:bg-white/[0.03] hover:border-blue-500/30 transition-all group border border-white/5">
                            <div className={`w-12 h-12 rounded-xl bg-${cat.color}-500/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-500`}><cat.icon className={`w-6 h-6 text-${cat.color}-500`} /></div>
                            <span className="text-sm font-black text-white uppercase tracking-tight block">{cat.name}</span>
                        </button>
                    ))}
                </motion.div>
            )}
        </AnimatePresence>

        {/* LAYER 1: STREAMING OUTPUT DISPLAY */}
        {(streamedText || aiResponse || loading) && (
            <div className="mt-8 space-y-12 mb-20">
                <div className="max-w-4xl glass-card rounded-[40px] p-10 border border-white/5 relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-6 text-blue-500">
                        <Activity className="w-5 h-5" />
                        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Direct Analysis Feed</span>
                    </div>
                    
                    {loading && !streamedText && (
                        <div className="space-y-4 animate-pulse">
                            <div className="h-4 bg-slate-800 rounded w-3/4" />
                            <div className="h-4 bg-slate-800 rounded w-1/2" />
                            <div className="h-4 bg-slate-800 rounded w-5/6" />
                        </div>
                    )}
                    
                    <div className="text-xl text-slate-300 leading-relaxed font-medium whitespace-pre-wrap">
                        {streamedText || (aiResponse && aiResponse.summary)}
                    </div>

                    {((!loading && streamedText) || aiResponse) && (
                        <button onClick={() => {setStreamedText(''); setAiResponse(null)}} className="mt-8 text-xs font-black text-slate-600 hover:text-white uppercase tracking-widest transition-colors flex items-center gap-2">
                            <Search className="w-4 h-4" /> Reset Workspace
                        </button>
                    )}
                </div>

                {aiResponse && (
                    <Suspense fallback={<div className="h-[400px] bg-slate-900/50 rounded-[40px] animate-pulse" />}>
                        <VisualPortal data={aiResponse} />
                    </Suspense>
                )}
            </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
