import { create } from "zustand";

interface DashboardState {
  watchlist: string[];
  addToWatchlist: (stock: string) => void;
  removeFromWatchlist: (stock: string) => void;
  selectedStock: string | null;
  setSelectedStock: (stock: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  watchlist: ["AAPL", "TSLA", "NVDA", "MSFT"],
  addToWatchlist: (stock) => set((state) => ({ 
    watchlist: state.watchlist.includes(stock) ? state.watchlist : [...state.watchlist, stock] 
  })),
  removeFromWatchlist: (stock) => set((state) => ({ 
    watchlist: state.watchlist.filter(s => s !== stock) 
  })),
  selectedStock: null,
  setSelectedStock: (stock) => set({ selectedStock: stock }),
}));
