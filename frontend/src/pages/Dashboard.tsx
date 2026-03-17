import React, { useState, useRef } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Cpu, Zap, Search, Bell, LogOut, ArrowRight, Loader2, FileText, Upload, Globe, BrainCircuit } from 'lucide-react';
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

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const askDocumind = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() && !selectedFile) return;

    setLoading(true);
    try {
      let response;
      if (selectedFile) {
        // Handle File Upload Analysis
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('prompt', query || "Analyze this financial document.");
        formData.append('mode', researchMode);

        response = await fetch('http://localhost:8000/api/analyze-file', {
          method: 'POST',
          body: formData,
        });
      } else {
        // Handle Standard Chat
        response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: query, mode: researchMode }),
        });
      }
      
      const data = await response.json();
      setAiResponse(data);
      setSelectedFile(null); // Reset after upload
    } catch (error) {
      console.error('Error asking Documind:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-blue-500/30">
      <nav className="border-b border-slate-800/50 bg-[#020617]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white uppercase tracking-wider">DOCUMIND</span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center bg-slate-900 rounded-xl p-1 border border-slate-800">
              <button 
                onClick={() => setResearchMode('fast')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${researchMode === 'fast' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
              >
                INSTANT
              </button>
              <button 
                onClick={() => setResearchMode('deep')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${researchMode === 'deep' ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
              >
                DEEP RSRCH
              </button>
            </div>
            <Bell className="w-5 h-5 text-slate-400 cursor-pointer hover:text-white transition-colors" />
            <button onClick={handleLogout} className="flex items-center gap-2 text-slate-400 hover:text-red-400 transition-colors text-sm font-semibold">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <header className="mb-12">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-blue-400 text-sm font-bold tracking-widest uppercase">
              <BrainCircuit className="w-4 h-4" />
              <span>Multi-Agent Swarm Active</span>
            </div>
            <h1 className="text-5xl font-extrabold text-white tracking-tight">
              Intelligence <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Workstation</span>
            </h1>
            
            <div className="mt-8 max-w-3xl flex flex-col gap-4">
              <form onSubmit={askDocumind} className="relative group">
                <input 
                  type="text" 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={selectedFile ? `Analyze ${selectedFile.name}...` : "Query market intelligence or upload financial reports..."}
                  className="w-full bg-slate-900/80 border border-slate-800 rounded-2xl py-5 pl-7 pr-32 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-white placeholder:text-slate-500 transition-all backdrop-blur-md text-lg"
                />
                
                <div className="absolute right-3 top-3 flex items-center gap-2">
                   <button 
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className={`h-12 w-12 rounded-xl flex items-center justify-center transition-all ${selectedFile ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                  >
                    <Upload className="w-5 h-5" />
                  </button>
                  <button 
                    type="submit"
                    disabled={loading}
                    className="h-12 px-6 bg-blue-600 rounded-xl flex items-center gap-2 hover:bg-blue-500 transition-colors shadow-lg shadow-blue-500/20 disabled:opacity-50 text-white font-bold"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><span className="hidden sm:inline">RUN</span> <ArrowRight className="w-5 h-5" /></>}
                  </button>
                </div>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf,.csv" />
              </form>
              
              {selectedFile && (
                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl w-fit">
                  <FileText className="w-5 h-5 text-emerald-400" />
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-tighter">{selectedFile.name} ready for analysis</span>
                  <button onClick={() => setSelectedFile(null)} className="text-slate-500 hover:text-white text-xs ml-2">Remove</button>
                </motion.div>
              )}
            </div>
          </motion.div>
        </header>

        <AnimatePresence>
          {aiResponse && (
            <div key="response">
              <VisualPortal data={aiResponse} />
              <button 
                onClick={() => setAiResponse(null)}
                className="mt-8 text-slate-500 hover:text-blue-400 text-sm font-bold uppercase tracking-widest flex items-center gap-2 transition-colors"
              >
                <Globe className="w-4 h-4" /> Clear Workspace
              </button>
            </div>
          )}
        </AnimatePresence>

        {!aiResponse && (
           <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-1 lg:grid-cols-2 gap-8 py-12">
              <div className="glass-card p-8 rounded-3xl border border-blue-500/10">
                <h3 className="text-xl font-bold text-white mb-4">Instant Intelligence</h3>
                <p className="text-slate-400 leading-relaxed text-sm">
                  Powered by <b>Llama 3.3 70b</b> on Groq. Get millisecond responses for market updates, sentiment shifts, and quick summaries of live trends.
                </p>
              </div>
              <div className="glass-card p-8 rounded-3xl border border-emerald-500/10">
                <h3 className="text-xl font-bold text-white mb-4">Deep Research</h3>
                <p className="text-slate-400 leading-relaxed text-sm">
                  Full multi-stage pipeline. Context is distilled by <b>Gemini Flash</b> and analyzed by <b>Llama High-Precision</b>. Best for complex reports and balance sheet analysis.
                </p>
              </div>
           </motion.div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
