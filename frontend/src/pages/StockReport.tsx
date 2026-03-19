import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Activity, BarChart3, ChevronRight, Globe, FileText, Zap, Brain, Loader2, 
    Upload, CheckCircle2, MessageSquare, ExternalLink, ArrowUpRight, Search
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const StockReport: React.FC = () => {
    const { ticker } = useParams();
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const chatEndRef = useRef<HTMLDivElement>(null);

    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [chatQuery, setChatQuery] = useState('');
    const [chatLoading, setChatLoading] = useState(false);
    const [chatHistory, setChatHistory] = useState<{role: string, content: string, followUps?: string[]}[]>([]);
    const [ingesting, setIngesting] = useState(false);

    useEffect(() => {
        const initResearch = async () => {
            setLoading(true);
            try {
                const res = await fetch('http://localhost:8000/api/research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticker, company_name: ticker })
                });
                const result = await res.json();
                
                if (result.ingestion_status === 'started') setIngesting(true);

                setData({
                    companyName: ticker,
                    metrics: { price: '135.20', cap: '3.3T', pe: '72.4', roe: '55%' },
                    research: result.context?.ai_answer || "Discovering insights...",
                    sources: result.pdfs || [],
                });
            } catch (error) { console.error(error); } finally { setLoading(false); }
        };
        if (ticker) initResearch();
    }, [ticker]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory]);

    const [thinkingSteps, setThinkingSteps] = useState<string[]>([]);

    const handleChat = async (query: string) => {
        if (!query.trim()) return;
        setChatLoading(true);
        const userMessage = { role: 'user', content: query };
        setChatHistory(prev => [...prev, userMessage]);
        setChatQuery('');
        setThinkingSteps(["Consulting Global Index...", "Retrieving Annual Report Chunks...", "Synthesizing Financial Ratios..."]);

        // Final response placeholder for streaming
        let aiFullContent = "";
        setChatHistory(prev => [...prev, { role: 'ai', content: "" }]);

        try {
            const response = await fetch('http://localhost:8000/api/chat-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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

                // Update the last message in history with the stream progress
                setChatHistory(prev => {
                    const newHistory = [...prev];
                    const lastMsg = newHistory[newHistory.length - 1];
                    if (lastMsg.role === 'ai') {
                        lastMsg.content = aiFullContent;
                    }
                    return newHistory;
                });
                
                // Once we have data, we're no longer "thinking"
                if (thinkingSteps.length > 0) setThinkingSteps([]);
            }
        } catch (error) {
            setChatHistory(prev => [...prev, { role: 'ai', content: "I encountered an error accessing my neural index." }]);
        } finally {
            setChatLoading(false);
            setThinkingSteps([]);
        }
    };

    if (loading) return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center">
            <div className="flex flex-col items-center gap-6">
                <div className="relative">
                    <div className="w-20 h-20 border-4 border-blue-600/10 border-t-blue-600 rounded-full animate-spin" />
                    <Brain className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-blue-500 w-8 h-8 animate-pulse" />
                </div>
                <p className="text-blue-500 font-black tracking-[0.2em] uppercase text-xs">Simulating Neural Discovery...</p>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-blue-500/30">
            {/* Nav */}
            <nav className="border-b border-slate-800/10 bg-[#020617]/40 backdrop-blur-2xl sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
                             <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center shadow-2xl shadow-blue-600/20">
                                <Activity className="text-white w-5 h-5" />
                             </div>
                             <span className="text-lg font-black tracking-tighter text-white uppercase">DOCUMIND</span>
                        </div>
                        <div className="flex items-center gap-3 px-4 py-1.5 rounded-full bg-white/5 border border-white/5 text-[10px] font-bold text-slate-400">
                           <Globe className="w-3 h-3" />
                           <span>WORLD INDEX ACTIVE</span>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-8 py-10 grid grid-cols-1 lg:grid-cols-12 gap-10">
                {/* Left: Knowledge Feed (Google Search Style) */}
                <div className="lg:col-span-12 xl:col-span-8 space-y-8">
                    <header>
                        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-end gap-4 mb-6">
                            <h1 className="text-7xl font-black text-white tracking-tighter uppercase">{ticker}</h1>
                            <div className="mb-2 px-4 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-xs font-bold uppercase tracking-widest">
                                VERIFIED INTEL
                            </div>
                        </motion.div>
                        
                        {/* Quick Insight Bar */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                            {Object.entries(data.metrics).map(([k, v]) => (
                                <div key={k} className="glass-panel p-6 rounded-[24px] border-white/5 group hover:border-blue-500/30 transition-all">
                                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 group-hover:text-blue-400 transition-colors">{k}</div>
                                    <div className="text-2xl font-black text-white">{v as string}</div>
                                </div>
                            ))}
                        </div>
                    </header>

                    {/* Main Report Body (Markdown) */}
                    <section className="glass-panel p-10 rounded-[40px] border-white/5 relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 opacity-5"><Brain className="w-40 h-40" /></div>
                        <div className="prose prose-invert max-w-none">
                            <ReactMarkdown
                                components={{
                                    h1: ({...props}) => <h1 className="text-4xl font-black text-white mt-12 mb-6" {...props} />,
                                    h2: ({...props}) => <h2 className="text-2xl font-black text-blue-500 mt-10 mb-4 uppercase tracking-tight" {...props} />,
                                    p: ({...props}) => <p className="text-slate-400 leading-relaxed text-lg mb-6" {...props} />,
                                    li: ({...props}) => <li className="text-slate-400 mb-2 list-disc" {...props} />,
                                    strong: ({...props}) => <strong className="text-white font-bold" {...props} />
                                }}
                            >
                                {data.research}
                            </ReactMarkdown>
                        </div>
                    </section>
                </div>

                {/* Right: AI Assistant Sidebar (Gemini Style) */}
                <div className="lg:col-span-12 xl:col-span-4 space-y-6">
                    <div className="glass-panel h-[700px] rounded-[40px] border-blue-500/10 flex flex-col relative overflow-hidden">
                        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-600/20 rounded-lg"><Brain className="w-5 h-5 text-blue-500" /></div>
                                <h3 className="text-sm font-black text-white uppercase tracking-widest">Assistant</h3>
                            </div>
                            {ingesting && <div className="flex items-center gap-2 text-[10px] font-bold text-blue-400 animate-pulse"><Loader2 className="w-3 h-3 animate-spin" /> INDEXING...</div>}
                        </div>

                        {/* Chat Feed */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                            {chatHistory.length === 0 && (
                                <div className="h-full flex flex-col items-center justify-center text-center opacity-40 px-10">
                                    <MessageSquare className="w-12 h-12 mb-4 text-slate-500" />
                                    <p className="text-xs font-black uppercase tracking-[0.2em] leading-loose">
                                        I have indexed the world data for {ticker}. <br />Ask for trends, risks, or projections.
                                    </p>
                                </div>
                            )}
                            {chatHistory.map((chat: any, i) => (
                                <motion.div key={i} initial={{ opacity: 0, x: chat.role === 'user' ? 20 : -20 }} animate={{ opacity: 1, x: 0 }}>
                                    <div className={`p-4 rounded-3xl text-sm leading-relaxed ${chat.role === 'user' ? 'bg-blue-600 text-white ml-8 shadow-xl shadow-blue-600/20' : 'bg-white/5 text-slate-300 border border-white/5 mr-8'}`}>
                                        <ReactMarkdown>{chat.content}</ReactMarkdown>
                                    </div>
                                    
                                    {chat.citations && (
                                        <div className="mt-3 flex gap-2 flex-wrap">
                                            {chat.citations.map((c: any, ci: number) => (
                                                <div key={ci} className="px-2 py-1 rounded-lg bg-white/5 border border-white/5 text-[9px] font-bold text-slate-500 hover:text-blue-400 transition-colors cursor-pointer">
                                                    Ref: {c.source}
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {chat.followUps && (
                                        <div className="mt-4 flex flex-wrap gap-2">
                                            {chat.followUps.map((q: any, idx: number) => (
                                                <button key={idx} onClick={() => handleChat(q)} className="px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] font-bold text-blue-400 hover:bg-blue-500 hover:text-white transition-all">
                                                    {q}
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                            {chatLoading && (
                                <div className="flex flex-col gap-3 mr-12">
                                    {thinkingSteps.map((step, i) => (
                                        <motion.div key={i} initial={{opacity: 0, x: -5}} animate={{opacity: [0, 1, 0.5]}} transition={{repeat: Infinity, duration: 2, delay: i * 0.4}} className="flex items-center gap-2 text-[10px] font-black text-blue-600 uppercase tracking-widest">
                                            <div className="w-1 h-1 bg-blue-600 rounded-full" />
                                            {step}
                                        </motion.div>
                                    ))}
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-6 bg-slate-950/80 backdrop-blur-xl border-t border-white/5">
                            <form onSubmit={(e) => { e.preventDefault(); handleChat(chatQuery); }} className="relative">
                                <input 
                                    type="text" 
                                    value={chatQuery}
                                    onChange={(e) => setChatQuery(e.target.value)}
                                    placeholder="Ask for deeper intelligence..."
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-14 focus:outline-none focus:border-blue-500 transition-all text-sm text-white"
                                />
                                <button disabled={chatLoading} type="submit" className="absolute right-2 top-2 h-10 w-10 bg-blue-600 rounded-xl flex items-center justify-center hover:bg-blue-500 transition-all shadow-lg active:scale-95">
                                    {chatLoading ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <ChevronRight className="w-5 h-5 text-white" />}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default StockReport;
