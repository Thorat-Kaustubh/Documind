"use client";

import { useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { Button, Card, Input, Badge } from "@/components/ui/core";
import { Shield, Mail, Lock, Ghost, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/api/client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(error.message);
      setIsLoading(false);
    } else {
      router.push("/dashboard");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-6 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.05)_0%,transparent_100%)]Pointer-events-none" />
      
      <Link href="/" className="absolute top-8 left-8 flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft size={18} /> Back to home
      </Link>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md z-10"
      >
        <Card className="p-8 border-border/50 shadow-2xl bg-card/60 backdrop-blur-2xl">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-primary rounded-xl mx-auto flex items-center justify-center mb-4 shadow-glow">
              <Shield className="text-white" size={24} />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Access Terminal</h1>
            <p className="text-muted-foreground text-sm mt-1">Institutional-grade identity verification.</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                <Input 
                  type="email" placeholder="name@company.com" 
                  className="pl-10" required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Password</label>
                <Link href="#" className="text-[10px] uppercase font-bold text-primary hover:underline">Forgot?</Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                <Input 
                  type="password" placeholder="••••••••" 
                  className="pl-10" required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {error && <p className="text-xs text-red-400 text-center">{error}</p>}

            <Button type="submit" className="w-full h-11 text-sm font-bold gap-2" disabled={isLoading}>
              {isLoading ? "Verifying..." : "Sign in to Terminal"}
            </Button>
          </form>

          <div className="mt-8 pt-6 border-t border-border flex flex-col gap-4">
             <Button variant="outline" className="h-10 text-xs font-bold gap-2 w-full" onClick={() => supabase.auth.signInWithOAuth({ provider: 'google' })}>
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" /><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" /><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" /><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Identity with SSO
             </Button>
             <p className="text-center text-[10px] text-muted-foreground uppercase font-bold tracking-widest">
               Don't have access? <Link href="/signup" className="text-primary hover:underline">Request Invite</Link>
             </p>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
