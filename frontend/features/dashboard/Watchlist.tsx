"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useDashboardStore } from "@/stores/dashboardStore";
import { Card, Button, Input, Badge } from "@/components/ui/core";
import { Plus, Trash2, Search, TrendingUp, TrendingDown } from "lucide-react";
import { useState } from "react";

export function Watchlist() {
  const queryClient = useQueryClient();
  const [newStock, setNewStock] = useState("");
  const { watchlist, addToWatchlist, removeFromWatchlist } = useDashboardStore();

  const { data: stockData, isLoading } = useQuery({
    queryKey: ["watchlistData", watchlist],
    queryFn: () => apiClient("/api/market/stocks", { 
      method: "POST", 
      body: JSON.stringify({ symbols: watchlist }) 
    }),
    enabled: watchlist.length > 0,
  });

  const addMutation = useMutation({
    mutationFn: (symbol: string) => apiClient("/api/watchlist/add", {
      method: "POST",
      body: JSON.stringify({ symbol })
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlistData"] });
    }
  });

  const handleAdd = () => {
    if (!newStock) return;
    addToWatchlist(newStock.toUpperCase());
    setNewStock("");
    // addMutation.mutate(newStock.toUpperCase());
  };

  return (
    <Card className="flex flex-col h-full bg-card/40 border-border/50">
      <div className="p-4 border-b border-border/50 flex items-center justify-between">
        <h3 className="font-bold flex items-center gap-2">
          <TrendingUp size={18} className="text-primary" /> My Watchlist
        </h3>
        <Badge variant="outline">{watchlist.length} Assets</Badge>
      </div>

      <div className="p-4 border-b border-border/50">
        <div className="flex gap-2">
          <Input 
            value={newStock}
            onChange={(e) => setNewStock(e.target.value)}
            placeholder="Add ticker..."
            className="h-9"
          />
          <Button onClick={handleAdd} size="sm" className="w-9 px-0">
            <Plus size={18} />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {watchlist.map((symbol) => {
          const data = stockData?.[symbol] || { price: 150.00 + Math.random() * 50, change: (Math.random() * 4 - 2).toFixed(2) };
          const isUp = parseFloat(data.change) >= 0;

          return (
            <div 
              key={symbol} 
              className="group flex items-center justify-between p-3 rounded-xl bg-muted/30 hover:bg-muted transition-all border border-transparent hover:border-border"
            >
              <div className="flex flex-col">
                <span className="font-bold text-sm">{symbol}</span>
                <span className="text-[10px] text-muted-foreground uppercase">Equity</span>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-sm font-bold">${data.price.toFixed(2)}</div>
                  <div className={cn(
                    "text-[10px] font-medium flex items-center justify-end gap-1",
                    isUp ? "text-green-500" : "text-red-400"
                  )}>
                    {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                    {isUp ? "+" : ""}{data.change}%
                  </div>
                </div>
                <button 
                  onClick={() => removeFromWatchlist(symbol)}
                  className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-400/20 text-muted-foreground hover:text-red-400 rounded-lg transition-all"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

const cn = (...inputs: any[]) => inputs.filter(Boolean).join(" ");
