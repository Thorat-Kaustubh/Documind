import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, Search, Upload, TrendingUp, Zap, Newspaper, 
  ArrowUpRight, ArrowDownRight, ArrowRight, Loader2, Plus, 
  ChevronRight, BrainCircuit, MessageSquare
} from 'lucide-react';
import api from '../lib/api';
import { MainLayout } from '../components/MainLayout';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [pulse, setPulse] = useState<any[]>([]);
  const [vitals, setVitals] = useState({ nifty: 22000, repo_rate: '6.50%' });
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [researchInput, setResearchInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analyzingFile, setAnalyzingFile] = useState(false);

  const handleFileUpload = async (file: File) => {
    setAnalyzingFile(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('prompt', "Analyze this financial document for key risks and opportunities.");
      formData.append('mode', 'deep');

      await api.post('/api/analyze-file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      navigate(`/report/EXTRACTED_${Date.now()}`);
    } catch (err) {
      console.error("File Analysis Failed", err);
    } finally {
      setAnalyzingFile(false);
    }
  };

  useEffect(() => {
    if (selectedFile) handleFileUpload(selectedFile);
  }, [selectedFile]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [pulseData, vitalsData, watchlistData] = await Promise.all([
          api.get('/api/market-pulse'),
          api.get('/api/market-vitals'),
          api.get('/api/watchlist')
        ]);
        setPulse(pulseData.data);
        setVitals(vitalsData.data);
        setWatchlist(watchlistData.data);
      } catch (err) {
        console.error("Dashboard Sync Failed", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleQuickResearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (researchInput.trim()) {
      navigate(`/report/${researchInput.trim().toUpperCase()}`);
    }
  };

  const Skeleton = ({ className }: { className: string }) => (
    <div className={`skeleton ${className}`} />
  );

  return (
    <MainLayout>
      <div className="relative space-y-12 pb-32">
        {/* Cinematic Backdrop Layer */}
        <div className="absolute -top-48 -left-48 w-128 h-128 nebula-glow bg-blue-600/10 blur-[160px] pointer-events-none" />
        <div className="absolute top-1/2 right-[-10%] w-96 h-96 nebula-glow bg-purple-600/5 blur-[140px] pointer-events-none" />

        {/* Intelligence Orchestration Header */}
        <header className="relative flex flex-col lg:flex-row items-end justify-between gap-10 py-6 border-b border-white/5">
          <div className="space-y-4">
             <motion.div 
               initial={{ opacity: 0, x: -20 }} 
               animate={{ opacity: 1, x: 0 }} 
               className="flex items-center gap-3 text-blue-500 font-black text-[10px] uppercase tracking-[0.4em]"
             >
                <div className="w-2 h-2 bg-blue-500 rounded-full active-ring animate-pulse" />
                Fleet Intel Phase 2.5 Active
             </motion.div>
             <h1 className="text-6xl md:text-7xl font-black text-white tracking-tighter leading-none uppercase font-outfit">
               Welcome, <span className="shimmer-text italic">Analyst.</span>
             </h1>
             <p className="text-zinc-500 text-base font-bold tracking-tight max-w-xl opacity-70">
                Synchronizing 25k+ high-frequency asset signals across global market indexes. 
                <span className="text-blue-500/60 ml-2 italic">Discovery fleet operational.</span>
             </p>
          </div>

          <div className="flex items-center gap-12 bg-white/[0.02] border border-white/5 p-6 rounded-[32px] backdrop-blur-2xl">
            <div className="text-right">
              <span className="sublabel-fin block mb-2 text-zinc-600">NIFTY 50 PULSE</span>
              {loading ? <Skeleton className="h-8 w-32 ml-auto" /> : (
                <div className="flex items-center gap-4 justify-end">
                   <div className="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-[9px] font-black text-emerald-400 uppercase tracking-widest">Live</div>
                   <div className="text-4xl font-black text-white tracking-tighter">{(vitals.nifty || 0).toLocaleString()}</div>
                </div>
              )}
            </div>
            <div className="text-right border-l border-white/10 pl-12">
              <span className="sublabel-fin block mb-2 text-blue-500">REPO RATE</span>
              {loading ? <Skeleton className="h-8 w-20 ml-auto" /> : (
                <div className="text-4xl font-black text-white tracking-tighter italic">{vitals.repo_rate}</div>
              )}
            </div>
          </div>
        </header>

        {/* Discovery & Monitoring Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 relative z-10">
            {/* Deep Discovery Engine - The Core Interaction Hub */}
            <div className="lg:col-span-8 glass-card rounded-[56px] p-12 relative overflow-hidden group shadow-[0_40px_100px_-20px] shadow-black">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/[0.03] to-transparent pointer-events-none" />
                <div className="absolute -top-24 -right-24 p-8 opacity-[0.02] group-hover:opacity-10 group-hover:scale-110 transition-all duration-1000 group-hover:rotate-12">
                  <BrainCircuit className="w-96 h-96" />
                </div>
                
                <div className="relative z-10">
                    <h3 className="text-4xl font-black text-white tracking-tighter mb-12 uppercase font-outfit">Deep <span className="text-blue-500 italic">Discovery</span> Engine</h3>
                    
                    <form onSubmit={handleQuickResearch} className="space-y-10">
                        <div className="relative group/input">
                            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-[34px] blur opacity-0 group-focus-within/input:opacity-100 transition duration-1000" />
                            <Search className="absolute left-8 top-1/2 -translate-y-1/2 w-8 h-8 text-zinc-700 group-focus-within/input:text-blue-500 transition-colors z-20" />
                            <input 
                                type="text" 
                                value={researchInput}
                                onChange={(e) => setResearchInput(e.target.value)}
                                placeholder="Identify Tickers, Trends, or IPO Signals..."
                                className="relative z-10 w-full bg-black/60 border border-white/10 rounded-[32px] py-8 pl-20 pr-24 text-3xl text-white placeholder:text-zinc-800 focus:outline-none focus:border-blue-500/50 transition-all font-black tracking-tighter"
                            />
                             <button type="submit" className="absolute right-6 top-6 h-16 w-16 bg-blue-600 rounded-2xl flex items-center justify-center hover:bg-blue-500 transition-all shadow-2xl shadow-blue-600/40 active:scale-95 group/btn z-20">
                                 <ArrowRight className="text-white w-8 h-8 group-hover/btn:translate-x-1 transition-transform" />
                             </button>
                        </div>

                        <div className="flex items-center gap-6">
                            <input type="file" ref={fileInputRef} onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} className="hidden" />
                            <button 
                                type="button"
                                onClick={() => fileInputRef.current?.click()}
                                disabled={analyzingFile}
                                className="px-10 py-4.5 rounded-[24px] bg-white/[0.03] border border-white/5 text-[12px] font-black text-zinc-400 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all flex items-center gap-4 uppercase tracking-widest"
                            >
                                {analyzingFile ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5 text-blue-500" />} 
                                {selectedFile ? selectedFile.name : "Inject Intelligence Protocol (.pdf)"}
                            </button>
                            {selectedFile && (
                                <div className="text-[10px] font-black text-blue-500 uppercase tracking-widest animate-pulse flex items-center gap-2">
                                    <Zap className="w-3 h-3" /> Readiness High
                                </div>
                            )}
                        </div>
                    </form>
                </div>
            </div>

            {/* Watchlist Intelligence Pane */}
            <div className="lg:col-span-4 flex flex-col">
                <div className="glass-card rounded-[56px] p-10 flex-1 group border-white/5 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-600/[0.01] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="flex items-center justify-between mb-12 relative z-10">
                        <h3 className="text-xl font-black text-white tracking-widest uppercase italic">Fleet Watchlist</h3>
                        <button className="p-3 bg-blue-600/10 rounded-2xl text-blue-500 hover:bg-blue-600 hover:text-white hover:shadow-xl hover:shadow-blue-600/20 transition-all active:scale-90"><Plus className="w-6 h-6" /></button>
                    </div>
                    
                    <div className="space-y-5 relative z-10">
                        {loading ? [1,2,3,4].map(i => (
                            <div key={i} className="flex items-center justify-between p-6 rounded-[28px] bg-white/[0.02] border border-white/5">
                                <Skeleton className="h-5 w-28" />
                                <Skeleton className="h-5 w-14" />
                            </div>
                        )) : watchlist.length === 0 ? (
                          <div className="p-16 text-center border-2 border-dashed border-white/5 rounded-[40px] group-hover:border-blue-500/20 transition-all flex flex-col items-center gap-4">
                            <Zap className="w-8 h-8 text-zinc-800" />
                            <p className="sublabel-fin !text-[10px] uppercase tracking-widest opacity-40">Intelligence Fleet Idle</p>
                          </div>
                        ) : (
                          watchlist.map((asset) => (
                            <div 
                              key={asset.ticker} 
                              onClick={() => navigate(`/report/${asset.ticker}`)}
                              className="flex items-center justify-between p-6 rounded-[28px] bg-white/[0.02] border border-white/5 group/row hover:bg-blue-600/10 hover:border-blue-500/40 transition-all cursor-pointer shadow-sm hover:shadow-blue-600/5"
                            >
                               <div className="flex flex-col">
                                   <span className="font-black text-lg tracking-tighter text-white uppercase font-outfit">{asset.ticker}</span>
                                   <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">Active Tracking</span>
                               </div>
                               <div className={`flex items-center gap-2 text-xs font-black px-3 py-1.5 rounded-xl ${asset.change_percent >= 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                                  {asset.change_percent >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                  {asset.change_percent?.toFixed(2)}%
                               </div>
                            </div>
                          ))
                        )}
                    </div>
                </div>
            </div>
        </div>

        {/* Intelligence Pulse Feed - High Detail Section */}
        <section className="space-y-10">
            <div className="flex items-center justify-between border-b border-white/5 pb-8">
                <div className="flex items-center gap-6">
                   <div className="w-16 h-16 glass-card rounded-[24px] flex items-center justify-center text-blue-500 shadow-2xl shadow-blue-600/10">
                      <Newspaper className="w-8 h-8" />
                   </div>
                   <div className="space-y-1">
                      <h3 className="text-4xl font-black text-white tracking-tighter uppercase font-outfit">Live Pulse <span className="text-zinc-800">Intelligence</span></h3>
                      <div className="flex items-center gap-2 sublabel-fin !text-[9px] text-zinc-600">
                         <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                         Synchronized with NSE Corporate Discovery Core
                      </div>
                   </div>
                </div>
                <button 
                  onClick={() => navigate('/market')}
                  className="px-8 py-3 rounded-2xl glass-card sublabel-fin !text-[10px] text-blue-500 flex items-center gap-3 group hover:bg-blue-600 hover:text-white transition-all uppercase font-black tracking-widest"
                >
                   Discovery Core <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                <AnimatePresence>
                    {loading ? (
                        Array(6).fill(0).map((_, i) => (
                           <div key={i} className="h-80 glass-card rounded-[48px] p-10 flex flex-col justify-between">
                               <div className="space-y-6">
                                   <div className="flex justify-between">
                                       <Skeleton className="h-4 w-20" />
                                       <Skeleton className="h-4 w-24" />
                                   </div>
                                   <Skeleton className="h-16 w-full" />
                                   <Skeleton className="h-4 w-full" />
                                   <Skeleton className="h-4 w-4/5" />
                               </div>
                               <Skeleton className="h-12 w-full mt-8 rounded-2xl" />
                           </div>
                        ))
                    ) : (
                        pulse.map((item, i) => (
                            <motion.div 
                                key={item.id}
                                initial={{ opacity: 0, y: 30 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.05 }}
                                whileHover={{ y: -8 }}
                                className="glass-card rounded-[48px] p-10 hover:bg-white/[0.03] border-white/5 flex flex-col justify-between transition-all duration-500 group/card shadow-lg hover:shadow-blue-600/5"
                            >
                                <div className="space-y-6 relative">
                                    <div className="flex items-center justify-between">
                                        <div className="px-4 py-1.5 bg-white/5 rounded-xl sublabel-fin !text-[9px] text-zinc-500 uppercase font-black">{item.category}</div>
                                        <div className="flex items-center gap-2 text-[11px] font-black text-blue-400 tracking-[0.2em] uppercase">
                                            <Activity className="w-4 h-4 animate-pulse" /> {item.ticker}
                                        </div>
                                    </div>
                                    <h4 className="text-2xl font-black text-white leading-tight tracking-tighter group-hover/card:text-blue-500 transition-colors uppercase font-outfit line-clamp-2">{item.title}</h4>
                                    <p className="text-zinc-500 text-base font-medium leading-relaxed line-clamp-3 opacity-80 group-hover/card:opacity-100 transition-opacity italic">"{item.content}"</p>
                                </div>
                                <div className="mt-10 pt-8 border-t border-white/5 flex flex-col gap-4">
                                    <div className="flex items-center justify-between">
                                        <div className="sublabel-fin !text-[10px] text-zinc-600">SENTIMENT INTENSITY</div>
                                        <div className={`text-[12px] font-black uppercase tracking-tighter ${item.sentiment_score > 0.5 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                            {(item.sentiment_score * 100).toFixed(0)}% Precise
                                        </div>
                                    </div>
                                    {/* Sentiment Mini-Bar */}
                                    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                                        <motion.div 
                                            initial={{ width: 0 }}
                                            animate={{ width: `${item.sentiment_score * 100}%` }}
                                            className={`h-full ${item.sentiment_score > 0.5 ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]'}`}
                                        />
                                    </div>
                                    <div className="flex justify-between items-center mt-2">
                                        <span className="sublabel-fin !text-[9px] opacity-40">DCMND-PULSE-ID: {item.id.slice(0, 8)}</span>
                                        <span className="sublabel-fin !text-[9px] opacity-40">{new Date(item.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    )}
                </AnimatePresence>
            </div>
        </section>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
