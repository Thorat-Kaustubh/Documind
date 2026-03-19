import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, TrendingUp, BarChart2, Globe, ArrowRight, Briefcase, Zap, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState('');

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            // Navigate to the report page which will handle the data fetching
            navigate(`/report/${query.trim().toUpperCase()}`);
        }
    };

    const trendingStocks = [
        { name: 'Nvidia', ticker: 'NVDA' },
        { name: 'Reliance', ticker: 'RELIANCE' },
        { name: 'TCS', ticker: 'TCS' },
        { name: 'Apple', ticker: 'AAPL' },
        { name: 'HDFC Bank', ticker: 'HDFCBANK' }
    ];

    return (
        <div className="min-h-screen bg-[#020617] relative overflow-hidden flex flex-col items-center">
            {/* Background Orbs */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-600/10 blur-[120px] rounded-full pointer-events-none" />

            {/* Navigation */}
            <nav className="w-full max-w-7xl px-8 h-20 flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-2xl">
                        <BarChart2 className="text-white w-6 h-6" />
                    </div>
                    <span className="text-2xl font-black tracking-tighter text-white">DOCUMIND</span>
                </div>
                <div className="hidden md:flex items-center gap-10">
                    {['Screens', 'Themes', 'Tools'].map((item) => (
                        <a key={item} href="#" className="text-sm font-semibold text-slate-400 hover:text-white transition-colors">{item}</a>
                    ))}
                </div>
                <div className="flex items-center gap-4">
                    <button onClick={() => navigate('/login')} className="px-6 py-2.5 rounded-xl text-sm font-bold text-slate-300 hover:text-white transition-all bg-slate-900/50 border border-slate-800">LOGIN</button>
                    <button className="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-blue-600 hover:bg-blue-500 transition-all shadow-xl shadow-blue-600/20">GET FREE ACCOUNT</button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-1 w-full max-w-4xl px-6 flex flex-col items-center justify-center text-center z-10 pt-20">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-widest uppercase mb-8">
                        <Zap className="w-3 h-3" />
                        <span>Next-Gen Financial Intelligence</span>
                    </div>
                    <h1 className="text-6xl md:text-8xl font-black text-white tracking-tighter mb-6 leading-tight">
                        Stock analysis <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400">reimagined.</span>
                    </h1>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-12">
                        Real-time market insights, AI-powered financial reports, and deep PDF research for serious investors.
                    </p>

                    {/* Search Bar */}
                    <form onSubmit={handleSearch} className="w-full max-w-2xl mx-auto relative group">
                        <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
                            <Search className="w-6 h-6 text-slate-500 group-focus-within:text-blue-500 transition-colors" />
                        </div>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search for a company, ticker or insight..."
                            className="w-full bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-3xl py-6 pl-16 pr-8 text-xl text-white placeholder:text-slate-600 focus:outline-none focus:ring-4 focus:ring-blue-600/20 focus:border-blue-500/50 transition-all shadow-2xl"
                        />
                        <button type="submit" className="absolute right-4 top-4 h-12 w-12 bg-blue-600 rounded-2xl flex items-center justify-center hover:bg-blue-500 transition-colors">
                            <ArrowRight className="text-white w-6 h-6" />
                        </button>
                    </form>

                    {/* Trending Stocks */}
                    <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
                        <span className="text-sm font-bold text-slate-500 uppercase tracking-widest mr-2">Or analyze:</span>
                        {trendingStocks.map((stock) => (
                            <button
                                key={stock.ticker}
                                onClick={() => navigate(`/report/${stock.ticker}`)}
                                className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm font-bold text-slate-300 hover:border-blue-500 hover:text-white transition-all"
                            >
                                {stock.name}
                            </button>
                        ))}
                    </div>
                </motion.div>
            </main>

            {/* Feature Highlights */}
            <section className="w-full max-w-7xl px-8 pb-32 grid grid-cols-1 md:grid-cols-3 gap-8 mt-40">
                {[
                    { icon: Globe, title: 'Live Market Sync', desc: 'Real-time price feeding from yfinance and NSE/BSE global connectors.' },
                    { icon: Briefcase, title: 'Deep RAG Analysis', desc: 'Our AI reads the fine print in 100+ page annual reports so you don’t have to.' },
                    { icon: ShieldCheck, title: 'Verified Intelligence', desc: 'Multi-source cross-verification between Screener, Reuters, and Yahoo.' }
                ].map((feature, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: idx * 0.1 }}
                        className="glass-panel p-8 rounded-3xl group hover:border-blue-500/50 transition-all"
                    >
                        <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <feature.icon className="w-6 h-6 text-blue-500" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                        <p className="text-slate-400 text-sm leading-relaxed">{feature.desc}</p>
                    </motion.div>
                ))}
            </section>
        </div>
    );
};

export default LandingPage;
