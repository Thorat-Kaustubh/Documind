import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, Shield, Cpu, Zap, Search, Bell, LogOut, ArrowRight, Loader2, 
  FileText, Upload, Globe, BrainCircuit, BarChart3, PieChart, TrendingUp, 
  Landmark, Newspaper, Coins, ChevronRight, Info
} from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';
import { VisualPortal } from '../components/VisualPortal';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [researchMode, setResearchMode] = useState<'fast' | 'deep'>('fast');
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
    try {
      let response;
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('prompt', query || "Analyze this financial document.");
        formData.append('mode', researchMode);
        response = await fetch('http://localhost:8000/api/analyze-file', { method: 'POST', body: formData });
      } else {
        response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: query, mode: researchMode }),
        });
      }
      const data = await response.json();
      setAiResponse(data);
      setSelectedFile(null);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-blue-500/30">
      <nav className="border-b border-white/5 bg-[#020617]/40 backdrop-blur-2xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3" onClick={() => navigate('/')}>
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
              Master your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-indigo-400 to-emerald-400">Capital.</span>
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

        {!aiResponse && (
          <section className="space-y-20">
            {/* Category Cluster */}
            <div>
              <div className="flex items-center justify-between mb-10">
                <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em]">Neural Intelligence Subsystems</h3>
                <div className="h-[1px] flex-1 mx-8 bg-gradient-to-r from-white/10 to-transparent" />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {categories.map((cat, i) => (
                  <motion.button 
                    key={cat.name} 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="glass-panel p-8 rounded-[36px] flex flex-col items-start gap-4 hover:bg-white/[0.03] hover:border-blue-500/30 transition-all group border border-white/5"
                  >
                    <div className={`w-14 h-14 rounded-2xl bg-${cat.color}-500/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-500`}>
                      <cat.icon className={`w-7 h-7 text-${cat.color}-500`} />
                    </div>
                    <div className="text-left">
                      <span className="text-sm font-black text-white uppercase tracking-tight block mb-1">{cat.name}</span>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{cat.desc}</span>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* System Status */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 pb-20">
               <div className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-[40px] opacity-10 group-hover:opacity-20 transition duration-500" />
                  <div className="relative glass-panel p-10 rounded-[40px] border-white/5 h-full">
                    <div className="flex items-center gap-4 mb-8">
                       <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center"><Globe className="text-blue-500 w-6 h-6" /></div>
                       <h3 className="text-2xl font-black text-white tracking-tighter">Live Web Crawling</h3>
                    </div>
                    <p className="text-slate-400 text-base leading-relaxed mb-6 font-medium">Our fleet of specialized bots is now crawling global exchanges, legal filings, and news sentiment every 60 seconds.</p>
                    <div className="flex items-center gap-2 text-emerald-400 text-[10px] font-black uppercase tracking-widest">
                       <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                       CRAWLER SERVICE: NOMINAL
                    </div>
                  </div>
               </div>
               
               <div className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-[40px] opacity-10 group-hover:opacity-20 transition duration-500" />
                  <div className="relative glass-panel p-10 rounded-[40px] border-white/5 h-full">
                    <div className="flex items-center gap-4 mb-8">
                       <div className="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center"><Shield className="text-emerald-500 w-6 h-6" /></div>
                       <h3 className="text-2xl font-black text-white tracking-tighter">Neural RAG Core</h3>
                    </div>
                    <p className="text-slate-400 text-base leading-relaxed mb-6 font-medium">Your private intelligence vault. Ingested PDFs and scraped intelligence are cross-referenced using high-dimensional vector math.</p>
                    <div className="flex items-center gap-2 text-blue-400 text-[10px] font-black uppercase tracking-widest">
                       <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                       RAG ENGINE: READY
                    </div>
                  </div>
               </div>
            </div>
          </section>
        )}

        <AnimatePresence>
          {aiResponse && (
            <motion.div initial={{opacity: 0, scale: 0.98}} animate={{opacity: 1, scale: 1}} exit={{opacity: 0, scale: 0.98}} className="mt-8">
              <VisualPortal data={aiResponse} />
              <button onClick={() => setAiResponse(null)} className="mt-12 group flex items-center gap-3 text-slate-500 hover:text-white transition-all">
                <div className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center group-hover:border-white/30"><Search className="w-4 h-4" /></div>
                <span className="text-xs font-black uppercase tracking-widest">Reset Discovery Workspace</span>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default Dashboard;
