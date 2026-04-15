"use client";

import { Card, Badge } from "@/components/ui/core";
import { Brain, Zap, Target, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export function InsightCards() {
  const insights = [
    {
      title: "Sentiment Shift",
      symbol: "NVDA",
      value: "Bullish",
      detail: "Social sentiment increased by 42% after Blackwell roadmap leak.",
      icon: <Brain size={18} className="text-primary" />,
      color: "border-primary/50"
    },
    {
      title: "Volatility Alert",
      symbol: "TSLA",
      value: "High",
      detail: "Option implied volatility suggests a 5% move by Friday.",
      icon: <AlertTriangle size={18} className="text-yellow-400" />,
      color: "border-yellow-500/50"
    },
    {
      title: "Volume Spike",
      symbol: "AAPL",
      value: "3.2x",
      detail: "Trading volume is 3.2x above the 50-day moving average.",
      icon: <Zap size={18} className="text-green-400" />,
      color: "border-green-500/50"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {insights.map((insight, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.1 }}
        >
          <Card className={`p-5 flex flex-col gap-4 border-l-4 ${insight.color} hover:bg-muted/30 transition-all cursor-pointer group`}>
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-muted rounded-lg group-hover:glow-accent transition-all">
                  {insight.icon}
                </div>
                <div>
                  <h4 className="font-bold text-sm">{insight.title}</h4>
                  <Badge variant="outline" className="text-[10px] h-4">{insight.symbol}</Badge>
                </div>
              </div>
              <span className="text-lg font-black tracking-tight">{insight.value}</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {insight.detail}
            </p>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
