import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, BarChart2, Globe, ArrowRight, Briefcase, Zap, ShieldCheck, Activity, Brain, ChevronRight, TrendingDown } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../lib/api';

const LandingPage: React.FC = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState('');
    const [vitals, setVitals] = React.useState({ nifty: 0, repo_rate: '...' });

    React.useEffect(() => {
        const fetchVitals = async () => {
            try {
                const res = await api.get('/api/market-vitals');
                setVitals(res.data);
            } catch (e) {
                console.error("Failed to fetch market vitals");
            }
        };
        fetchVitals();
        const interval = setInterval(fetchVitals, 60000);
        return () => clearInterval(interval);
    }, []);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            navigate(`/report/${query.trim().toUpperCase()}`);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white flex flex-col font-inter selection:bg-blue-600/30 overflow-hidden relative">
          {/* Dynamic Nebula Anchors - Depth Layer */}
          <div className="absolute top-0 right-0 w-[800px] h-[800px] nebula-glow bg-blue-600/10 -translate-y-1/2 translate-x-1/3 z-0" />
          <div className="absolute top-[20%] left-[-10%] w-[600px] h-[600px] nebula-glow bg-purple-600/5 -translate-x-1/2 z-0" />
          <div className="absolute bottom-0 right-[10%] w-[500px] h-[500px] nebula-glow bg-emerald-600/5 translate-y-1/2 z-0" />

          {/* Modern High-Precision Navigation */}
          <nav className="relative z-50 px-8 py-8 flex items-center justify-between max-w-7xl mx-auto w-full border-b border-white/5">
            <motion.div 
               initial={{ opacity: 0, x: -20 }} 
               animate={{ opacity: 1, x: 0 }} 
               className="flex items-center gap-3 group cursor-pointer"
               onClick={() => navigate('/')}
            >
              <div className="w-10 h-10 glass-card rounded-xl flex items-center justify-center text-blue-500 group-hover:shadow-[0_0_20px] group-hover:shadow-blue-600/30 transition-all duration-500">
                 <Brain className="w-6 h-6 shrink-0" />
              </div>
              <span className="text-xl font-black text-white tracking-widest uppercase">Documind <span className="text-blue-500">2026</span></span>
            </motion.div>
            
            <div className="hidden md:flex items-center gap-10">
              {['Extraction', 'Pulse', 'Discovery', 'Security'].map((link) => (
                <a key={link} href="#" className="sublabel-fin !text-[9px] hover:text-blue-500 transition-colors uppercase tracking-[0.3em] font-black">{link}</a>
              ))}
              <Link to="/login" className="px-8 py-3 rounded-2xl glass-card text-[11px] font-black tracking-widest uppercase hover:bg-white/5 transition-all">Command Platform</Link>
            </div>
          </nav>

          {/* Kinetic Hero Section */}
          <main className="relative z-10 w-full">
            <section className="flex flex-col items-center justify-center px-6 max-w-7xl mx-auto text-center gap-12 py-32 md:py-48">
              <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="space-y-8"
              >
                <div className="flex justify-center">
                  <div className="sublabel-fin text-blue-400 bg-blue-600/10 px-6 py-2.5 rounded-full inline-flex items-center gap-3 border border-blue-500/20 backdrop-blur-xl animate-pulse">
                     <div className="w-1.5 h-1.5 bg-blue-500 rounded-full active-ring" />
                     <span className="tracking-[0.3em]">AI Multi-Asset Agentic Mesh 2.5.0</span>
                  </div>
                </div>
                
                <h1 className="text-7xl md:text-[140px] font-black tracking-tighter leading-[0.75] uppercase font-outfit text-white">
                  Discovery <br />
                  <span className="shimmer-text">Unchained.</span>
                </h1>
                
                <p className="text-zinc-500 text-lg md:text-xl font-bold tracking-tight max-w-2xl mx-auto mt-12 leading-relaxed opacity-80">
                  The next-generation financial research broker. Synthesizing billions of data points into high-frequency discovery signals for the documentation-heavy elite.
                </p>
              </motion.div>

              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3, duration: 0.6 }}
                className="flex flex-col md:flex-row items-center gap-6 mt-4"
              >
                <Link 
                  to="/signup" 
                  className="px-12 py-6 bg-blue-600 rounded-[32px] text-white font-black text-[14px] shadow-[0_20px_50px_-10px] shadow-blue-600/40 hover:bg-blue-500 hover:scale-105 active:scale-95 transition-all uppercase tracking-widest"
                >
                  Deploy My Discovery Fleet
                </Link>
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="px-10 py-6 rounded-[32px] glass-card text-zinc-300 font-black text-[12px] hover:text-white transition-all uppercase tracking-widest flex items-center gap-3 group"
                >
                  <Zap className="w-4 h-4 text-blue-500 group-hover:scale-110 transition-transform" /> Watch System Pulse
                </button>
              </motion.div>

              {/* Real-time Ticker Vitals */}
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-12 flex items-center gap-10 px-8 py-4 glass-card rounded-[32px] border border-white/10"
              >
                  <div className="flex items-center gap-3 border-r border-white/5 pr-10">
                     <div className="sublabel-fin !text-[8px] text-zinc-500 uppercase tracking-widest">Nifty 50</div>
                     <div className="text-sm font-black text-blue-400 uppercase tracking-tighter">
                        {vitals.nifty > 0 ? `₹${vitals.nifty.toLocaleString()}` : "Syncing..."}
                     </div>
                  </div>
                  <div className="flex items-center gap-3">
                     <div className="sublabel-fin !text-[8px] text-zinc-500 uppercase tracking-widest">Repo Rate</div>
                     <div className="text-sm font-black text-emerald-400 uppercase tracking-tighter">
                        {vitals.repo_rate}
                     </div>
                  </div>
                  <div className="hidden lg:flex items-center gap-3 pl-10 border-l border-white/5">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                      <div className="sublabel-fin !text-[8px] text-zinc-500">Live Telemetry Active</div>
                  </div>
              </motion.div>
            </section>

            {/* Trusted By Section (Trust Signals) */}
            <section className="border-y border-white/5 bg-white/[0.02] py-24 overflow-hidden relative">
               <div className="max-w-7xl mx-auto px-8 relative z-10">
                  <p className="sublabel-fin text-center mb-16 opacity-40 uppercase tracking-[0.4em]">Strategic Data Mesh Interconnects</p>
                  <div className="flex flex-wrap items-center justify-around gap-16 md:gap-24 opacity-40 grayscale hover:grayscale-0 transition-all duration-700">
                     {['Y Combinator', 'Vercel', 'Stripe', 'Anthropic', 'OpenAI'].map(logo => (
                       <span key={logo} className="font-black text-3xl md:text-4xl tracking-tighter text-zinc-500 uppercase hover:text-white transition-colors cursor-default select-none">{logo}</span>
                     ))}
                  </div>
               </div>
               <div className="absolute inset-0 bg-gradient-to-r from-black via-transparent to-black" />
            </section>

            {/* Feature Matrix */}
            <section className="py-48 px-8 max-w-7xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                    {[
                      { icon: Brain, title: 'Neural RAG Indexing', desc: 'Synthesizing every word across massive filings into a queryable semantic core with sub-second retrieval.' },
                      { icon: Activity, title: 'High-Frequency Pulse', desc: 'Real-time telemetry from global markets injected directly into your research stream without delay.' },
                      { icon: ShieldCheck, title: 'Compliance Audited', desc: 'Bank-grade Row Level Security (RLS) and full audit traceability ensuring your intelligence remains private.' }
                    ].map((feature, i) => (
                      <motion.div 
                        key={i} 
                        whileInView={{ opacity: 1, y: 0 }} 
                        initial={{ opacity: 0, y: 40 }} 
                        transition={{ delay: i * 0.1 }}
                        viewport={{ once: true }}
                        className="glass-card p-12 rounded-[56px] group relative overflow-hidden"
                      >
                         <div className="relative z-10">
                            <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center text-blue-500 mb-10 active-ring group-hover:bg-blue-600 group-hover:text-white transition-all duration-500">
                               <feature.icon className="w-8 h-8" />
                            </div>
                            <h3 className="text-3xl font-black text-white tracking-tighter mb-6 uppercase font-outfit">{feature.title}</h3>
                            <p className="text-zinc-500 text-lg font-medium leading-relaxed group-hover:text-zinc-400 transition-colors">{feature.desc}</p>
                         </div>
                         <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                      </motion.div>
                    ))}
                </div>
            </section>

            {/* Strategic Pricing Matrix */}
            <section className="py-48 px-8 max-w-7xl mx-auto bg-white/[0.01] rounded-[80px] border border-white/5 my-20">
               <div className="text-center mb-24 space-y-6">
                  <h2 className="text-6xl md:text-8xl font-black text-white tracking-tighter uppercase font-outfit">Discovery <span className="text-blue-500 italic">Tiering</span></h2>
                  <p className="sublabel-fin tracking-[0.5em] opacity-60">Select your intelligence depth</p>
               </div>

               <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                  {[
                    { tier: 'Discovery', price: '0', feat: ['10 PDF Extractions', 'Market Vitals', 'Standard AI Counsel'], btn: 'Deploy Discovery' },
                    { tier: 'Analyzer', price: '49', feat: ['Unlimited Analysis', 'High-Frequency Pulse', 'L4 Intelligence Hub'], prime: true, btn: 'Deploy Analyzer' },
                    { tier: 'Enterprise', price: '999', feat: ['Dedicated Discovery Fleet', 'Custom Training', 'Custom Discovery APIs'], btn: 'Deploy Enterprise' }
                  ].map((plan, i) => (
                    <motion.div 
                        key={i} 
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className={`glass-card p-12 rounded-[60px] flex flex-col justify-between transition-all duration-500 hover:scale-[1.02] ${plan.prime ? 'border-blue-600/40 border-2 shadow-[0_40px_100px_-20px] shadow-blue-600/20 z-10' : 'opacity-80 hover:opacity-100'}`}
                    >
                       <div className="space-y-8">
                          <div className={`sublabel-fin !text-[10px] ${plan.prime ? 'text-blue-400' : 'text-zinc-500'}`}>{plan.tier}</div>
                          <div className="text-6xl font-black text-white tracking-tighter uppercase font-outfit">
                            ${plan.price}<span className="text-lg text-zinc-600 font-bold tracking-normal italic">/mo</span>
                          </div>
                          <div className="space-y-5 pt-8 border-t border-white/5">
                             {plan.feat.map(f => (
                               <div key={f} className="flex items-center gap-4 text-sm font-bold text-zinc-400 group cursor-default">
                                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full group-hover:scale-150 transition-transform" /> {f}
                               </div>
                             ))}
                          </div>
                       </div>
                       <button className={`mt-14 py-5 rounded-3xl font-black text-[12px] uppercase tracking-widest transition-all ${plan.prime ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/20 hover:bg-blue-500' : 'bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-white'}`}>
                        {plan.btn}
                       </button>
                    </motion.div>
                  ))}
               </div>
            </section>
          </main>

          {/* Detailed Production Footer */}
          <footer className="relative z-10 border-t border-white/5 bg-black/40 backdrop-blur-3xl pt-32 pb-12">
            <div className="max-w-7xl mx-auto px-8">
               <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-16 pb-24">
                  <div className="col-span-2 space-y-8">
                    <div className="flex items-center gap-3">
                       <Brain className="w-10 h-10 text-blue-500" />
                       <span className="text-2xl font-black uppercase tracking-widest">Documind</span>
                    </div>
                    <p className="text-zinc-600 text-base font-bold max-w-sm leading-relaxed">Pioneering the boundary between documentation and executable intelligence. v2.5.0 Stable Protocol.</p>
                  </div>
                  <div>
                    <div className="sublabel-fin text-white mb-8">Discovery</div>
                    <div className="flex flex-col gap-5 sublabel-fin !text-[10px] !normal-case text-zinc-500">
                       <a href="#" className="hover:text-blue-500 transition-colors">Market Pulse</a>
                       <a href="#" className="hover:text-blue-500 transition-colors">Asset Map</a>
                       <a href="#" className="hover:text-blue-500 transition-colors">PDF Indexing</a>
                    </div>
                  </div>
                  <div>
                    <div className="sublabel-fin text-white mb-8">Resources</div>
                    <div className="flex flex-col gap-5 sublabel-fin !text-[10px] !normal-case text-zinc-500">
                       <a href="#" className="hover:text-blue-500 transition-colors">Discovery API Docs</a>
                       <a href="#" className="hover:text-blue-500 transition-colors">Support Index</a>
                       <a href="#" className="hover:text-blue-500 transition-colors">Status Core</a>
                    </div>
                  </div>
                  <div className="lg:col-span-1">
                    <div className="sublabel-fin text-white mb-8">Legal</div>
                    <div className="flex flex-col gap-5 sublabel-fin !text-[10px] !normal-case text-zinc-500">
                       <a href="#" className="hover:text-blue-500 transition-colors">Privacy Pulse</a>
                       <a href="#" className="hover:text-blue-500 transition-colors">Governance</a>
                       <a href="#" className="hover:text-blue-500 transition-colors">Security Audit</a>
                    </div>
                  </div>
               </div>
               <div className="pt-12 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-8">
                  <div className="sublabel-fin !text-[9px] opacity-40">Documind Intelligence Corp © 2026 // ALL SYSTEMS OPERATIONAL</div>
                  <div className="flex gap-10 sublabel-fin !text-[9px] uppercase font-black">
                     <span className="cursor-pointer hover:text-blue-500 transition-colors">Twitter</span>
                     <span className="cursor-pointer hover:text-blue-500 transition-colors">LinkedIn</span>
                     <span className="cursor-pointer hover:text-blue-500 transition-colors">GitHub</span>
                  </div>
               </div>
            </div>
          </footer>
        </div>
    );
};

export default LandingPage;
