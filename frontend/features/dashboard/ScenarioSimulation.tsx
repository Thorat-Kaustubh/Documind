"use client";

import { useState } from "react";
import { Card, Button, Input, Badge } from "@/components/ui/core";
import { Play, RotateCcw, Info, Sliders } from "lucide-react";

export function ScenarioSimulation() {
  const [params, setParams] = useState({
    interestRate: 4.5,
    inflation: 3.2,
    growth: 2.1
  });

  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const simulate = () => {
    setIsLoading(true);
    // Simulate API delay
    setTimeout(() => {
      setResult("Based on a neuro-symbolic projection, an interest rate hike to " + params.interestRate + "% combined with " + params.inflation + "% inflation would likely compress tech multiples by 8-12% while boosting regional bank margins.");
      setIsLoading(false);
    }, 1500);
  };

  return (
    <Card className="p-6 bg-card/40 border-border/50">
      <div className="flex items-center gap-2 mb-6">
        <Sliders className="text-primary" size={20} />
        <h3 className="font-bold text-lg">Scenario Simulator (What-If?)</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <label className="text-muted-foreground">Interest Rate (%)</label>
                <span className="font-bold">{params.interestRate}</span>
              </div>
              <input 
                type="range" min="0" max="10" step="0.1" 
                value={params.interestRate}
                onChange={(e) => setParams({ ...params, interestRate: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <label className="text-muted-foreground">Expected Inflation (%)</label>
                <span className="font-bold">{params.inflation}</span>
              </div>
              <input 
                type="range" min="0" max="10" step="0.1" 
                value={params.inflation}
                onChange={(e) => setParams({ ...params, inflation: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <label className="text-muted-foreground">GDP Growth (%)</label>
                <span className="font-bold">{params.growth}</span>
              </div>
              <input 
                type="range" min="-5" max="10" step="0.1" 
                value={params.growth}
                onChange={(e) => setParams({ ...params, growth: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <Button onClick={simulate} className="flex-1 gap-2" disabled={isLoading}>
              {isLoading ? "Analyzing..." : <><Play size={16} /> Run Simulation</>}
            </Button>
            <Button variant="outline" onClick={() => setParams({ interestRate: 4.5, inflation: 3.2, growth: 2.1 })}>
              <RotateCcw size={16} />
            </Button>
          </div>
        </div>

        <div className="bg-muted/30 rounded-xl p-6 border border-border/50 relative overflow-hidden">
          {!result && !isLoading && (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
              <Info size={32} className="mb-2" />
              <p className="text-sm">Adjust parameters and run simulation to see results.</p>
            </div>
          )}

          {isLoading && (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="w-12 h-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin mb-4" />
              <p className="text-sm font-medium animate-pulse">Running Monte Carlo Simulations...</p>
            </div>
          )}

          {result && !isLoading && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
               <Badge variant="success">Simulation Complete</Badge>
               <h4 className="font-bold">Neural Projection Result:</h4>
               <p className="text-sm text-foreground/80 leading-relaxed italic">
                 "{result}"
               </p>
               <div className="pt-4 border-t border-border mt-4 flex justify-between items-center">
                 <span className="text-[10px] text-muted-foreground uppercase font-bold">Confidence: 84%</span>
                 <Button variant="ghost" size="sm" className="text-[10px] h-6 px-2">Export Data</Button>
               </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
