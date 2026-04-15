"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { useUIStore } from "@/stores/uiStore";
import { MarketPulse } from "@/features/dashboard/MarketPulse";
import { Watchlist } from "@/features/dashboard/Watchlist";
import { ChatTerminal } from "@/features/chat/ChatTerminal";
import { InsightCards } from "@/features/dashboard/InsightCards";
import { ScenarioSimulation } from "@/features/dashboard/ScenarioSimulation";
import { Badge } from "@/components/ui/core";
import { motion, AnimatePresence } from "framer-motion";

export default function Dashboard() {
  const { activeTab } = useUIStore();

  return (
    <DashboardLayout>
      <AnimatePresence mode="wait">
        {activeTab === "dashboard" && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-8"
          >
            <div className="flex justify-between items-end">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Market Intelligence</h1>
                <p className="text-muted-foreground italic">Observing 1.2M data points across SQ + RAG layers.</p>
              </div>
              <Badge className="bg-green-500/10 text-green-500 border-green-500/20 px-3 py-1 animate-pulse">
                System Online
              </Badge>
            </div>

            <InsightCards />

            <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
              <div className="xl:col-span-3">
                <MarketPulse />
              </div>
              <div className="xl:col-span-1">
                <Watchlist />
              </div>
            </div>

            <ScenarioSimulation />
          </motion.div>
        )}

        {activeTab === "chat" && (
          <motion.div
            key="chat"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="h-full"
          >
            <div className="mb-6">
              <h1 className="text-3xl font-bold tracking-tight">Intelligence Terminal</h1>
              <p className="text-muted-foreground">Direct interface with the Documind Swarm.</p>
            </div>
            <ChatTerminal />
          </motion.div>
        )}

        {activeTab === "alerts" && (
          <motion.div
            key="alerts"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-3xl mx-auto"
          >
             <h1 className="text-3xl font-bold tracking-tight mb-8">Intelligence Feed</h1>
             <div className="space-y-4">
                {[
                  { priority: "high", title: "Unusual Options Activity", symbol: "NVDA", time: "2m ago", desc: "Significant call buying detected for $1100 exp June." },
                  { priority: "med", title: "Institutional Accumulation", symbol: "AAPL", time: "15m ago", desc: "Large block trades detected across 3 dark pools." },
                  { priority: "low", title: "RAG Update", symbol: "Global", time: "1h ago", desc: "Updated vector database with latest FOMC minutes analysis." }
                ].map((alert, i) => (
                  <div key={i} className="glass-card p-6 flex gap-6 items-center">
                    <div className={`w-2 h-12 rounded-full ${alert.priority === 'high' ? 'bg-red-500' : alert.priority === 'med' ? 'bg-yellow-500' : 'bg-primary'}`} />
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <h4 className="font-bold">{alert.title}</h4>
                        <span className="text-xs text-muted-foreground">{alert.time}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{alert.desc}</p>
                    </div>
                    <Badge variant="outline">{alert.symbol}</Badge>
                  </div>
                ))}
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </DashboardLayout>
  );
}
