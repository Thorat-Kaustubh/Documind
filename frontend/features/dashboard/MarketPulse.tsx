"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, Skeleton, Badge } from "@/components/ui/core";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";
import { TrendingUp, TrendingDown, Clock } from "lucide-react";

export function MarketPulse() {
  const { data: vitals, isLoading } = useQuery({
    queryKey: ["marketVitals"],
    queryFn: () => apiClient("/api/market-vitals"),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  if (isLoading) return <MarketPulseSkeleton />;

  // Mock chart history since /api/market-vitals returns current snapshot
  const chartData = [
    { time: "09:00", value: 5000 },
    { time: "10:00", value: 5200 },
    { time: "11:00", value: 5100 },
    { time: "12:00", value: 5400 },
    { time: "13:00", value: 5300 },
    { time: "14:00", value: 5600 },
    { time: "15:00", value: 5800 },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2 p-6 h-[400px] flex flex-col">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-xl font-bold">System Pulse</h3>
            <p className="text-sm text-muted-foreground flex items-center gap-1">
              <Clock size={14} /> Real-time market index tracking
            </p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-primary">{vitals?.nifty ? `NIFTY ${vitals.nifty}` : "$5,820.42"}</span>
            <div className="flex items-center gap-1 text-green-500 text-sm font-medium justify-end">
              <TrendingUp size={16} /> {vitals?.repo_rate ? `Repo: ${vitals.repo_rate}` : "+1.24%"}
            </div>
          </div>
        </div>
        
        <div className="flex-1 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(226, 70%, 55%)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="hsl(226, 70%, 55%)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 47%, 12%)" vertical={false} />
              <XAxis 
                dataKey="time" 
                stroke="hsl(215, 20%, 65%)" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false} 
              />
              <YAxis 
                stroke="hsl(215, 20%, 65%)" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false} 
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "hsl(222, 47%, 7%)", 
                  borderColor: "hsl(222, 47%, 12%)",
                  borderRadius: "12px",
                  fontSize: "12px"
                }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="hsl(226, 70%, 55%)" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorValue)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="p-6 flex flex-col gap-6">
        <h3 className="text-lg font-bold">Sector Performance</h3>
        <div className="space-y-4">
          {[
            { name: "Technology", value: "+2.4%", status: "up" },
            { name: "Energy", value: "-1.1%", status: "down" },
            { name: "Finance", value: "+0.8%", status: "up" },
            { name: "Healthcare", value: "+0.3%", status: "up" },
            { name: "Consumer", value: "-2.5%", status: "down" },
          ].map((sector) => (
            <div key={sector.name} className="flex justify-between items-center p-3 hover:bg-muted/50 rounded-xl transition-colors border border-transparent hover:border-border">
              <span className="font-medium">{sector.name}</span>
              <Badge variant={sector.status === "up" ? "success" : "warning"}>
                {sector.value}
              </Badge>
            </div>
          ))}
        </div>
        <div className="mt-auto pt-6 border-t border-border">
           <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4">
             <div className="w-2 h-2 rounded-full bg-green-500" /> Market Stability: High
           </div>
           <p className="text-xs leading-relaxed opacity-60">
             Overall market sentiment remains bullish driven by tech earnings and easing inflation reports.
           </p>
        </div>
      </Card>
    </div>
  );
}

function MarketPulseSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2 p-6 h-[400px]">
        <Skeleton className="w-48 h-8 mb-4" />
        <Skeleton className="w-full h-[300px]" />
      </Card>
      <Card className="p-6">
        <Skeleton className="w-48 h-8 mb-4" />
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="w-full h-12" />)}
        </div>
      </Card>
    </div>
  );
}
