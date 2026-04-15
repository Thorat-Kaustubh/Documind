import { create } from "zustand";

interface UIState {
  isSidebarOpen: boolean;
  activeTab: string;
  notifications: any[];
  toggleSidebar: () => void;
  setActiveTab: (tab: string) => void;
  addNotification: (notification: any) => void;
  dismissNotification: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  activeTab: "dashboard",
  notifications: [],
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setActiveTab: (tab) => set({ activeTab: tab }),
  addNotification: (n) => set((state) => ({ notifications: [n, ...state.notifications] })),
  dismissNotification: (id) => set((state) => ({ 
    notifications: state.notifications.filter(n => n.id !== id) 
  })),
}));
