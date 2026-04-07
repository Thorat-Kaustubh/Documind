import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { motion } from 'framer-motion';
import { Mail, ArrowRight, Loader2, KeyRound, CheckCircle2 } from 'lucide-react';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      if (error) throw error;
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950 to-slate-950">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none opacity-20">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500 rounded-full blur-[120px]" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[440px] glass-card rounded-[32px] p-10 border border-white/10 shadow-2xl relative overflow-hidden"
      >
        <div className="flex flex-col items-center gap-4 mb-10">
          <div className="w-14 h-14 bg-gradient-to-tr from-blue-600 to-blue-400 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/20">
            <KeyRound className="w-8 h-8 text-white" />
          </div>
          <div className="text-center px-4">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Recovery</h1>
            <p className="text-slate-400 text-sm mt-1">Restore access to your Documind brain</p>
          </div>
        </div>

        {submitted ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center space-y-6"
          >
            <div className="flex justify-center">
              <CheckCircle2 className="w-16 h-16 text-emerald-500" />
            </div>
            <div className="space-y-2">
              <p className="text-white font-bold text-lg">Check your inbox</p>
              <p className="text-slate-400 text-sm">
                If an account exists for <span className="text-blue-400 font-semibold">{email}</span>, you will receive a password reset link shortly.
              </p>
            </div>
            <Link 
              to="/login"
              className="inline-flex items-center gap-2 text-blue-400 font-bold hover:text-blue-300 transition-colors"
            >
              Return to Login
            </Link>
          </motion.div>
        ) : (
          <>
            {error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleResetRequest} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest px-1">Email Address</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                  <input 
                    type="email" 
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all font-semibold"
                    placeholder="name@company.com"
                  />
                </div>
              </div>

              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 group disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  <>
                    <span>Send Recovery Link</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>

            <p className="mt-10 text-center text-slate-400 text-sm">
              Remember your password?{' '}
              <Link 
                to="/login"
                className="text-blue-400 font-bold hover:text-blue-300 transition-colors"
              >
                Sign In
              </Link>
            </p>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default ForgotPasswordPage;
