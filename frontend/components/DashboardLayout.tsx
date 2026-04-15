"use client";

import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import { cn } from "@/components/ui/core";
import { 
  BarChart2, 
  MessageSquare, 
  Bell, 
  Settings, 
  LogOut, 
  Search,
  Menu,
  ChevronLeft
} from "lucide-react";
import { useEffect } from "react";
import Link from "next/link";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isSidebarOpen, toggleSidebar, activeTab, setActiveTab, notifications } = useUIStore();
  const { user, initialize, signOut } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  const menuItems = [
    { id: "dashboard", icon: <BarChart2 size={20} />, label: "Pulse" },
    { id: "chat", icon: <MessageSquare size={20} />, label: "Intelligence" },
    { id: "alerts", icon: <Bell size={20} />, label: "Alerts", count: notifications.length },
    { id: "settings", icon: <Settings size={20} />, label: "Settings" },
  ];

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside 
        className={cn(
          "relative flex flex-col border-r border-border transition-all duration-300 ease-in-out bg-card/30 backdrop-blur-md",
          isSidebarOpen ? "w-64" : "w-20"
        )}
      >
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex-shrink-0 flex items-center justify-center font-bold text-white">D</div>
          {isSidebarOpen && <span className="font-bold text-xl tracking-tight">Documind</span>}
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                "flex items-center gap-4 w-full p-3 rounded-xl transition-all group relative",
                activeTab === item.id ? "bg-primary/10 text-primary" : "hover:bg-muted text-muted-foreground hover:text-foreground"
              )}
            >
              <div className={cn(activeTab === item.id && "drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]")}>
                {item.icon}
              </div>
              {isSidebarOpen && <span className="font-medium">{item.label}</span>}
              {item.count ? (
                <span className="absolute right-2 top-2 w-4 h-4 bg-red-500 rounded-full text-[10px] flex items-center justify-center text-white font-bold">
                  {item.count}
                </span>
              ) : null}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-border mt-auto">
          {isSidebarOpen && (
            <div className="mb-4 px-2">
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
            </div>
          )}
          <button 
            onClick={() => signOut()}
            className="flex items-center gap-4 w-full p-3 rounded-xl text-muted-foreground hover:text-red-400 hover:bg-red-400/10 transition-all"
          >
            <LogOut size={20} />
            {isSidebarOpen && <span className="font-medium">Sign Out</span>}
          </button>
        </div>

        <button 
          onClick={toggleSidebar}
          className="absolute -right-3 top-20 w-6 h-6 bg-border rounded-full flex items-center justify-center text-muted-foreground hover:text-foreground"
        >
          {isSidebarOpen ? <ChevronLeft size={16} /> : <Menu size={16} />}
        </button>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-card/20 backdrop-blur-sm">
          <div className="flex items-center gap-4 flex-1 max-w-xl">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <input 
                placeholder="Search stocks, reports, or data..."
                className="w-full bg-muted/50 border border-border rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
             <Bell className="text-muted-foreground hover:text-foreground cursor-pointer" size={20} />
             <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent border border-white/20" />
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-8 relative">
          {children}
        </main>
      </div>
    </div>
  );
}
