"use client";

import { useState } from "react";
import { Button, Card, Input } from "@/components/ui/core";
import { Shield, Mail, Lock, User, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { supabase } from "@/lib/api/client";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setError(error.message);
      setIsLoading(false);
    } else {
      setError("Success! Check your email for verification.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-6 relative overflow-hidden">
      <Link href="/" className="absolute top-8 left-8 flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft size={18} /> Back to home
      </Link>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md z-10"
      >
        <Card className="p-8 border-border/50 shadow-2xl bg-card/60 backdrop-blur-2xl">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold tracking-tight">Create Account</h1>
            <p className="text-muted-foreground text-sm mt-1">Join the next-gen financial intelligence network.</p>
          </div>

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Corporate Email</label>
              <Input 
                type="email" placeholder="name@company.com" 
                required value={email} onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Secure Password</label>
              <Input 
                type="password" placeholder="••••••••" 
                required value={password} onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && <p className="text-xs text-center text-primary">{error}</p>}

            <Button type="submit" className="w-full h-11 text-sm font-bold" disabled={isLoading}>
              {isLoading ? "Provisioning..." : "Create Account"}
            </Button>
          </form>

          <p className="mt-6 text-center text-[10px] text-muted-foreground uppercase font-bold tracking-widest">
            Already have access? <Link href="/login" className="text-primary hover:underline">Log In</Link>
          </p>
        </Card>
      </motion.div>
    </div>
  );
}
