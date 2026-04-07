import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api, { getAuthHeader } from '../lib/api';
import { 
    Activity, BarChart3, ChevronRight, Globe, FileText, Zap, Brain, Loader2, 
    Upload, CheckCircle2, MessageSquare, ExternalLink, ArrowUpRight, Search,
    Download, Share2, MoreHorizontal, Plus
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { MainLayout } from '../components/MainLayout';

const StockReport: React.FC = () => {
    const { ticker } = useParams();
    const navigate = useNavigate();
    const chatEndRef = useRef<HTMLDivElement>(null);

    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [chatQuery, setChatQuery] = useState('');
    const [chatLoading, setChatLoading] = useState(false);
    const [chatHistory, setChatHistory] = useState<{role: string, content: string, citations?: any[]}[]>([]);
    const [ingesting, setIngesting] = useState(false);

    useEffect(() => {
        const initResearch = async () => {
            setLoading(true);
            try {
                const res = await api.post('/api/research', { ticker, company_name: ticker });
                const result = res.data;
                
                if (result.status === 'research_initiated') setIngesting(true);

                const m = result.metrics || {};
                setData({
                    companyName: ticker,
                    metrics: { 
                        price: m.price ? `₹${m.price.toLocaleString()}` : '...', 
                        cap: m.market_cap ? `${(m.market_cap / 1e12).toFixed(1)}T` : '...', 
                        pe: m.pe_ratio ? m.pe_ratio.toFixed(1) : '...', 
                        change: m.change_pct ? `${m.change_pct.toFixed(2)}%` : '...' 
                    },
                    research: result.context || "Discovering insights across world indexes...",
                    sources: result.pdfs || [],
                });
            } catch (error) { 
                console.error("Research Initialization Failed", error); 
            } finally { 
                setLoading(false); 
            }
        };
        if (ticker) initResearch();
    }, [ticker]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory]);

    const handleChat = async (query: string) => {
        if (!query.trim()) return;
        setChatLoading(true);
        const userMessage = { role: 'user', content: query };
        setChatHistory(prev => [...prev, userMessage]);
        setChatQuery('');

        let aiFullContent = "";
        setChatHistory(prev => [...prev, { role: 'ai', content: "" }]);

        try {
            const token = await getAuthHeader();
            const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
            const response = await fetch(`${backendUrl}/api/chat-stream`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': token
                },
                body: JSON.stringify({ prompt: query, ticker, mode: 'visual' })
            });

            if (!response.body) return;
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                aiFullContent += chunk;

                setChatHistory(prev => {
                    const newHistory = [...prev];
                    const lastMsg = newHistory[newHistory.length - 1];
                    if (lastMsg.role === 'ai') {
                        lastMsg.content = aiFullContent;
                    }
                    return newHistory;
                });
            }
        } catch (error) {
            setChatHistory(prev => [...prev, { role: 'ai', content: "Failed to access research index." }]);
        } finally {
            setChatLoading(false);
        }
    };

    const toggleWatchlist = async () => {
        try {
            await api.post('/api/watchlist', { ticker, action: 'ADD' });
            alert(`${ticker} added to watchlist.`);
        } catch (error) { 
            console.error("Watchlist Update Failed", error); 
        }
    };

    const Skeleton = ({ className }: { className: string }) => (
        <div className={`skeleton ${className}`} />
    );


    return (
        <MainLayout>
            <div className="relative flex flex-col gap-12 pb-32">
                {/* Visual Anchors - Cinematic Depth Layer */}
                <div className="absolute -top-48 -left-48 w-128 h-128 nebula-glow bg-blue-600/10 blur-[160px] pointer-events-none" />
                <div className="absolute top-1/2 right-[-5%] w-96 h-96 nebula-glow bg-blue-600/5 blur-[140px] pointer-events-none" />

                {/* Intelligence Orchestration Header */}
                <header className="flex flex-col md:flex-row items-end justify-between gap-10 pt-6 border-b border-white/5 pb-10">
                   <div className="flex flex-col gap-6">
                      <div className="flex items-center gap-4">
                         <div className="px-4 py-1.5 bg-blue-600/10 border border-blue-500/20 rounded-full sublabel-fin !text-[10px] text-blue-400 tracking-[0.4em] uppercase font-black animate-pulse">
                            Discovery Protocol Phase 2.5 Active
                         </div>
                         <span className="text-zinc-800 font-extrabold text-xl">/</span>
                         <span className="text-zinc-500 font-black tracking-widest text-[11px] uppercase opacity-60">Fleet Intelligence Node</span>
                      </div>
                      <h1 className="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase leading-[0.7] font-outfit">
                        {ticker} <span className="shimmer-text italic">Synthesis.</span>
                      </h1>
                   </div>

                   <div className="flex items-center gap-6 bg-white/[0.02] p-5 rounded-[32px] border border-white/5 backdrop-blur-2xl">
                        <button 
                            onClick={toggleWatchlist} 
                            className="px-8 py-4 rounded-2xl glass-card text-zinc-400 font-black text-[12px] hover:text-white hover:bg-white/5 transition-all flex items-center gap-4 uppercase tracking-widest group shadow-sm active:scale-95"
                        >
                            <Plus className="w-5 h-5 text-blue-500 group-hover:scale-125 transition-transform" /> Add to Fleet
                        </button>
                        <button 
                            className="bg-blue-600 px-10 py-4 rounded-2xl text-white font-black text-[13px] shadow-[0_20px_40px_-10px] shadow-blue-600/40 hover:bg-blue-500 transition-all uppercase tracking-widest active:scale-95"
                        >
                            Finalize Intelligence
                        </button>
                   </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start relative z-10">
                    {/* Primary Intelligence Core */}
                    <div className="lg:col-span-8 space-y-16">
                        {/* High-Resolution Performance Matrix */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            {loading ? [1,2,3,4].map(idx => (
                                <div key={idx} className="glass-card rounded-[32px] p-8 h-[120px] shadow-lg">
                                    <Skeleton className="h-3 w-16 mb-4" />
                                    <Skeleton className="h-10 w-24" />
                                </div>
                            )) : Object.entries(data.metrics).map(([k, v]) => (
                                <motion.div 
                                    key={k} 
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="glass-card rounded-[32px] p-8 group border-white/5 hover:border-blue-500/20 transition-all shadow-lg hover:shadow-blue-600/5"
                                >
                                    <div className="sublabel-fin !text-[10px] mb-3 text-zinc-500 uppercase tracking-[0.2em]">{k}</div>
                                    <div className="text-4xl font-black text-white tracking-tighter uppercase font-outfit">{v as string}</div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Synthesis Report Area */}
                        <div className="glass-card rounded-[64px] p-16 relative overflow-hidden group min-h-[800px] shadow-[0_40px_100px_-20px] shadow-black">
                             <div className="absolute top-0 right-0 p-16 opacity-[0.02] -z-10 group-hover:opacity-10 transition-all duration-1000 group-hover:scale-110 group-hover:rotate-6">
                                <Brain className="w-128 h-128" />
                             </div>
                             
                             <div className="relative z-10">
                                {loading ? (
                                    <div className="space-y-10">
                                        <Skeleton className="h-16 w-3/4 mb-16 rounded-2xl" />
                                        <div className="space-y-4">
                                            <Skeleton className="h-5 w-full" />
                                            <Skeleton className="h-5 w-full" />
                                            <Skeleton className="h-5 w-5/6" />
                                        </div>
                                        <div className="pt-16 space-y-6">
                                            <Skeleton className="h-10 w-1/4 mb-10 rounded-xl" />
                                            <Skeleton className="h-5 w-full" />
                                            <Skeleton className="h-5 w-5/6" />
                                        </div>
                                    </div>
                                ) : (
                                    <article className="prose prose-invert max-w-none">
                                        <ReactMarkdown
                                            components={{
                                                h1: ({...props}) => <h1 className="text-5xl font-black text-white mt-16 mb-12 tracking-tighter uppercase italic border-b border-white/5 pb-8 font-outfit" {...props} />,
                                                h2: ({...props}) => <h2 className="text-xs font-black text-blue-500 mt-14 mb-8 uppercase tracking-[0.5em] flex items-center gap-4 before:w-1.5 before:h-6 before:bg-blue-600 before:rounded-full" {...props} />,
                                                p: ({...props}) => <p className="text-zinc-500 leading-relaxed text-xl mb-10 font-bold tracking-tight opacity-90 first-letter:text-4xl first-letter:text-blue-500 first-letter:font-black first-letter:italic" {...props} />,
                                                li: ({...props}) => <li className="text-zinc-400 mb-5 list-none pl-8 relative before:content-[''] before:absolute before:left-0 before:top-3.5 before:w-3 before:h-0.5 before:bg-blue-600/50 hover:before:bg-blue-500 transition-colors" {...props} />,
                                                strong: ({...props}) => <strong className="text-white font-black px-1 border-b-2 border-blue-500/30 bg-blue-500/5" {...props} />,
                                                ul: ({...props}) => <ul className="my-10 space-y-4" {...props} />
                                            }}
                                        >
                                            {data.research}
                                        </ReactMarkdown>
                                    </article>
                                )}
                             </div>
                        </div>

                        {/* Verification Matrix */}
                        <div className="space-y-8">
                            <div className="flex items-center gap-4 pl-6">
                                <FileText className="w-6 h-6 text-blue-500" />
                                <h4 className="text-xs font-black text-white uppercase tracking-[0.4em]">Evidence Registry & Neural Proofs</h4>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {data.sources.map((s: string, i: number) => (
                                    <motion.a 
                                        key={i} 
                                        href={s} 
                                        target="_blank" 
                                        whileHover={{ y: -5 }}
                                        className="glass-card p-8 rounded-[36px] flex items-center justify-between hover:bg-white/[0.05] border-white/5 transition-all shadow-lg"
                                    >
                                        <div className="flex items-center gap-6">
                                           <div className="w-14 h-14 bg-blue-600/10 border border-blue-500/20 rounded-2xl flex items-center justify-center text-blue-500 group-hover:bg-blue-600 group-hover:text-white transition-all"><FileText className="w-8 h-8" /></div>
                                           <div className="flex flex-col gap-1">
                                              <span className="text-base font-black text-white uppercase tracking-tight font-outfit">Annual Extract {2024 - i}</span>
                                              <span className="sublabel-fin !text-[9px] text-zinc-500 tracking-widest uppercase">Certified Intelligence Source</span>
                                           </div>
                                        </div>
                                        <ExternalLink className="w-5 h-5 text-zinc-700 group-hover:text-blue-500 transition-colors" />
                                    </motion.a>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Operational Counsel Sidebar */}
                    <aside className="lg:col-span-4 sticky top-24 space-y-8">
                        <div className="glass-card rounded-[40px] h-[720px] flex flex-col relative overflow-hidden group">
                           {/* Neural Gradient Background */}
                           <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-blue-600/5 to-transparent pointer-events-none" />

                           <div className="p-8 border-b border-white/5 flex items-center justify-between relative z-10">
                               <div className="flex items-center gap-4">
                                   <div className="w-12 h-12 glass-card rounded-2xl flex items-center justify-center text-blue-500 active-ring"><Brain className="w-6 h-6" /></div>
                                   <div>
                                      <h3 className="text-xs font-black text-white uppercase tracking-[0.3em]">AI Counsel</h3>
                                      <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mt-1">L4 Intelligence</div>
                                   </div>
                               </div>
                               {ingesting && <div className="text-[10px] font-black text-blue-500 animate-pulse tracking-widest">SYNCING</div>}
                           </div>

                           <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar relative z-10">
                               {chatHistory.length === 0 && (
                                   <div className="h-full flex flex-col items-center justify-center text-center opacity-30 px-6">
                                       <Activity className="w-12 h-12 mb-6 text-zinc-800" />
                                       <p className="sublabel-fin leading-relaxed">Neural Index Initialized. <br />Awaiting specific inquiries.</p>
                                   </div>
                               )}
                               {chatHistory.map((chat, i) => (
                                   <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                                       <div className={`p-6 rounded-[28px] text-sm font-medium leading-relaxed ${chat.role === 'user' ? 'bg-blue-600 text-white ml-8 shadow-2xl shadow-blue-600/30' : 'bg-white/[0.04] text-zinc-300 mr-8 border border-white/5'}`}>
                                            <ReactMarkdown>{chat.content}</ReactMarkdown>
                                       </div>
                                   </motion.div>
                               ))}
                               {chatLoading && (
                                   <div className="flex items-center gap-3 p-6 bg-white/[0.04] rounded-[28px] mr-8 animate-pulse">
                                       <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
                                       <span className="sublabel-fin">Synthesizing...</span>
                                   </div>
                               )}
                               <div ref={chatEndRef} />
                           </div>

                           <div className="p-8 bg-black/40 backdrop-blur-3xl border-t border-white/5">
                               <form onSubmit={(e) => { e.preventDefault(); handleChat(chatQuery); }} className="relative group">
                                   <input 
                                       type="text" 
                                       value={chatQuery}
                                       onChange={(e) => setChatQuery(e.target.value)}
                                       placeholder="Query the index..."
                                       className="w-full bg-white/[0.03] border border-white/5 rounded-2xl py-5 pl-8 pr-16 text-md text-white placeholder:text-zinc-700 focus:outline-none focus:border-blue-500/40 transition-all font-bold"
                                   />
                                   <button disabled={chatLoading} className="absolute right-3 top-3 h-11 w-11 bg-blue-600 rounded-xl flex items-center justify-center hover:bg-blue-500 transition-all shadow-xl shadow-blue-600/30">
                                      <ChevronRight className="w-6 h-6 text-white" />
                                   </button>
                               </form>
                           </div>
                        </div>
                    </aside>
                </div>
            </div>
        </MainLayout>
    );
};

export default StockReport;
