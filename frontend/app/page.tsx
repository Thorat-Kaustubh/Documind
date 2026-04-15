"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/core";
import Link from "next/link";
import { ArrowRight, BarChart3, Shield, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-primary/10 blur-[120px] rounded-full" />
      <div className="absolute bottom-0 -right-1/4 w-1/2 h-1/2 bg-accent/10 blur-[120px] rounded-full" />

      <header className="fixed top-0 w-full z-50 px-6 py-4 flex justify-between items-center bg-background/50 backdrop-blur-md border-b border-border/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center font-bold text-white">D</div>
          <span className="text-xl font-bold tracking-tight">Documind</span>
        </div>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="pt-32 px-6 max-w-7xl mx-auto">
        <section className="text-center mb-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge variant="default" className="mb-4 py-1 px-4">Beta Release v2.0</Badge>
            <h1 className="text-6xl md:text-7xl font-bold tracking-tighter mb-6 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent">
              Institutional AI <br /> For Everyone.
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
              Documind leverages hybrid AI execution (SQL + RAG) to provide real-time financial insights with full explainability.
            </p>
            <div className="flex justify-center gap-4">
              <Link href="/dashboard">
                <Button className="h-12 px-8 text-lg gap-2">
                  Launch Terminal <ArrowRight size={20} />
                </Button>
              </Link>
            </div>
          </motion.div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: <Zap className="text-primary" />, title: "Real-time Pulse", desc: "Live market data streaming with sub-second latency." },
            { icon: <Shield className="text-primary" />, title: "Verified RAG", desc: "Every AI claim is backed by institutional-grade sources." },
            { icon: <BarChart3 className="text-primary" />, title: "What-If Analysis", desc: "Simulate market scenarios with neuro-symbolic logic." }
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.1 }}
              className="glass-card p-8 group hover:border-primary/50 transition-colors"
            >
              <div className="mb-4 p-3 bg-muted w-fit rounded-xl group-hover:glow-accent transition-all">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.desc}</p>
            </motion.div>
          ))}
        </section>
      </main>
    </div>
  );
}

const Badge = ({ children, className, variant = "default" }: any) => (
  <span className={cn("px-3 py-1 rounded-full text-xs font-semibold border", 
    variant === "default" ? "bg-primary/10 border-primary/20 text-primary" : "border-border text-muted-foreground",
    className
  )}>
    {children}
  </span>
);
const cn = (...inputs: any[]) => inputs.filter(Boolean).join(" ");
