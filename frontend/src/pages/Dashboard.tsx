import React from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';
import { Activity, Shield, Cpu, Zap, Search, Bell, LogOut } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';

const marketData = [
  { time: '09:30', value: 24200 },
  { time: '10:30', value: 24350 },
  { time: '11:30', value: 24280 },
  { time: '12:30', value: 24450 },
  { time: '13:30', value: 24520 },
  { time: '14:30', value: 24480 },
  { time: '15:30', value: 24600 },
];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-blue-500/30">
      {/* Navigation */}
      <nav className="border-b border-slate-800/50 bg-[#020617]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white uppercase tracking-wider">DOCUMIND</span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="relative group hidden md:block">
              <Search className="w-5 h-5 text-slate-400 group-hover:text-blue-400 transition-colors cursor-pointer" />
            </div>
            <Bell className="w-5 h-5 text-slate-400 cursor-pointer hover:text-white transition-colors" />
            <button 
                onClick={handleLogout}
                className="flex items-center gap-2 text-slate-400 hover:text-red-400 transition-colors text-sm font-semibold"
            >
                <LogOut className="w-4 h-4" />
                <span className="hidden md:inline">Logout</span>
            </button>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-500 to-emerald-500 p-[1px]">
              <div className="h-full w-full rounded-full bg-slate-950" />
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <header className="mb-12">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-2"
          >
            <div className="flex items-center gap-2 text-blue-400 text-sm font-medium tracking-wider uppercase">
              <Zap className="w-4 h-4" />
              <span>Hyper-Sprint Active</span>
            </div>
            <h1 className="text-5xl font-extrabold text-white tracking-tight">
              Financial <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Intelligence</span> Agent
            </h1>
            <p className="text-slate-400 text-lg max-w-2xl">
              Autonomous analysis engine powered by multi-LLM orchestration. 
              Real-time market monitoring and deep-sentiment extraction.
            </p>
          </motion.div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Chart Card */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2 glass-card rounded-3xl p-8 shadow-2xl shadow-blue-500/5 transition-all hover:bg-slate-900/40"
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-xl font-semibold text-white">NIFTY 50 Performance</h3>
                <p className="text-slate-400 text-sm">Real-time index heartbeat</p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-mono font-bold text-emerald-400">+1.24%</span>
                <p className="text-slate-500 text-xs mt-1">Today's Delta</p>
              </div>
            </div>
            
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={marketData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis 
                    dataKey="time" 
                    stroke="#475569" 
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#475569" 
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    domain={['dataMin - 100', 'dataMax + 100']}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      border: '1px solid #1e293b',
                      borderRadius: '12px',
                      color: '#f8fafc'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorValue)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Side Info Cards */}
          <div className="flex flex-col gap-6">
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card rounded-2xl p-6 hover:shadow-xl hover:shadow-blue-500/5 transition-all"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-blue-500/10 rounded-xl">
                  <Activity className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h4 className="font-semibold text-white">Sentiment Score</h4>
                  <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">Bullish</p>
                </div>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full w-[78%] shadow-[0_0_12px_rgba(59,130,246,0.5)]" />
              </div>
              <p className="text-slate-400 text-sm mt-4 italic">
                "Market sentiment remains strong across major indices despite global volatility."
              </p>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="glass-card rounded-2xl p-6 hover:shadow-xl hover:shadow-emerald-500/5 transition-all"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-emerald-500/10 rounded-xl">
                  <Shield className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h4 className="font-semibold text-white">Security Scan</h4>
                  <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">Verified</p>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Data Sources</span>
                <span className="text-emerald-400 font-mono">12 Active</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-slate-400">Integrity Check</span>
                <span className="text-emerald-400 font-mono">PASS</span>
              </div>
            </motion.div>
          </div>

        </div>
      </main>
    </div>
  );
};

export default Dashboard;
