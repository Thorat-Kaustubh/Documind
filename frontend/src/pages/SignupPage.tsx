import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu, Mail, Lock, User, ArrowRight, Loader2, Github, AlertCircle, CheckCircle2 } from 'lucide-react';

const SignupPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error } = await supabase.auth.signUp({ 
        email, 
        password,
        options: {
            data: {
                full_name: fullName
            }
        }
      });
      
      if (error) throw error;
      
      setSuccess(true);
      // Optional: auto-login or wait for email verification
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider: 'github' | 'google') => {
    await supabase.auth.signInWithOAuth({ 
        provider,
        options: { redirectTo: window.location.origin + '/dashboard' }
    });
  };

  return (
    <div className="min-h-screen bg-[#020202] flex items-center justify-center p-6 relative overflow-hidden font-inter text-foreground">
      {/* Mesh Gradient Background */}
      <div className="absolute inset-0 z-0">
          <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[120px] rounded-full" />
          <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-emerald-600/5 blur-[120px] rounded-full" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[480px] glass-card rounded-[32px] p-10 z-10 relative"
      >
        <div className="flex flex-col items-center gap-4 mb-10">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="w-16 h-16 bg-gradient-to-tr from-emerald-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-emerald-500/20"
          >
            <Cpu className="w-9 h-9 text-white" />
          </motion.div>
          <div className="text-center">
            <h1 className="text-4xl font-black text-white tracking-tighter uppercase italic">Documind</h1>
            <p className="text-slate-500 text-xs font-bold uppercase tracking-[0.2em] mt-1">Intelligence Protocol v2.5</p>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {success ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center space-y-6 py-8"
            >
              <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Verification Sent</h2>
                <p className="text-slate-400 text-sm font-semibold max-w-[280px] mx-auto">
                  We've initialized your access keys. Please check your email to activate your intelligence fleet.
                </p>
              </div>
              <button 
                onClick={() => navigate('/login')}
                className="text-emerald-500 font-black uppercase text-xs tracking-widest hover:text-emerald-400 transition-colors"
              >
                Return to Login Terminal
              </button>
            </motion.div>
          ) : (
            <motion.div exit={{ opacity: 0, scale: 0.95 }}>
              <AnimatePresence mode="wait">
                {error && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center gap-3"
                  >
                    <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                    <p className="text-red-400 text-sm font-semibold leading-snug">{error}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={handleSignup} className="space-y-5">
                <div className="space-y-2">
                  <label className="text-xs font-black text-slate-500 uppercase tracking-widest px-1">Identity Tag</label>
                  <div className="relative group">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                    <input 
                      type="text" 
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-black/40 border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all font-semibold"
                      placeholder="Your Full Name"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-black text-slate-500 uppercase tracking-widest px-1">Email Terminal</label>
                  <div className="relative group">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                    <input 
                      type="email" 
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-black/40 border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all font-semibold"
                      placeholder="name@company.com"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-black text-slate-500 uppercase tracking-widest px-1">Access Key</label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                    <input 
                      type="password" 
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-black/40 border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all font-semibold"
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                <button 
                  type="submit"
                  disabled={loading}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-2xl transition-all shadow-xl shadow-emerald-600/20 flex items-center justify-center gap-2 group disabled:opacity-50 uppercase text-xs tracking-widest"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                    <>
                      <span>Initialize Account</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>

              <div className="mt-10 relative">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/5"></div></div>
                <div className="relative flex justify-center text-[10px] font-black uppercase tracking-[0.3em]">
                  <span className="bg-[#141414] px-4 text-slate-500">Cross-Sync Protocol</span>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 mt-8">
                <button 
                  onClick={() => handleOAuth('github')}
                  className="flex items-center justify-center gap-3 bg-white/5 border border-white/5 hover:bg-white/10 text-white font-bold py-4 rounded-2xl transition-all text-xs uppercase"
                >
                  <Github className="w-5 h-5" /> Sign up with GitHub
                </button>
              </div>

              <p className="mt-10 text-center text-slate-500 text-xs font-bold uppercase tracking-wider">
                Authorized already? <Link to="/login" className="text-emerald-500 hover:text-emerald-400 transition-colors">Login</Link>
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default SignupPage;
