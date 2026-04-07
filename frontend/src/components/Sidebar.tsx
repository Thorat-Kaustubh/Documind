import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  BarChart2, LayoutDashboard, Briefcase, Bell, Settings, LogOut, 
  Search, BrainCircuit, Activity, TrendingUp, Cpu
} from 'lucide-react';
import { supabase } from '../lib/supabase';
import { motion } from 'framer-motion';

interface SidebarItemProps {
  icon: any;
  label: string;
  path: string;
  active?: boolean;
  onClick: () => void;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ icon: Icon, label, path, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
      active 
        ? 'bg-blue-600/10 text-blue-500 border border-blue-500/10' 
        : 'text-slate-500 hover:text-slate-200 hover:bg-white/5'
    }`}
  >
    <Icon className={`w-5 h-5 transition-transform duration-300 ${active ? 'scale-110' : 'group-hover:scale-110'}`} />
    <span className="text-sm font-semibold tracking-tight">{label}</span>
    {active && (
      <motion.div 
        layoutId="sidebar-active"
        className="ml-auto w-1.5 h-1.5 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.5)]"
      />
    )}
  </button>
);

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  const navItems = [
    { icon: LayoutDashboard, label: 'Overview', path: '/dashboard' },
    { icon: Briefcase, label: 'My Portfolio', path: '/portfolio' },
    { icon: TrendingUp, label: 'Markets', path: '/markets' },
    { icon: BrainCircuit, label: 'Intelligence', path: '/intelligence' },
  ];

  const subItems = [
    { icon: Bell, label: 'Alerts', path: '/alerts' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <aside className="w-64 h-screen bg-[#0d0d0d] border-r border-[#1f1f1f] flex flex-col p-4 fixed left-0 top-0 z-50">
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 mb-10 mt-2">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/20">
          <Cpu className="text-white w-6 h-6" />
        </div>
        <div className="flex flex-col">
          <span className="text-lg font-black tracking-tighter text-white uppercase leading-none">DOCUMIND</span>
          <span className="text-[10px] font-bold text-blue-500 tracking-[0.2em] uppercase mt-1">v2.2 Elite</span>
        </div>
      </div>

      {/* Main Nav */}
      <nav className="flex-1 space-y-2">
        <div className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em] px-4 mb-4">Main Menu</div>
        {navItems.map((item) => (
          <SidebarItem 
            key={item.label}
            {...item}
            active={location.pathname === item.path}
            onClick={() => navigate(item.path)}
          />
        ))}

        <div className="pt-8">
          <div className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em] px-4 mb-4">Support</div>
          {subItems.map((item) => (
            <SidebarItem 
              key={item.label}
              {...item}
              active={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            />
          ))}
        </div>
      </nav>

      {/* Profile/Logout */}
      <div className="pt-4 border-t border-[#1f1f1f]">
        <button 
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-rose-500/5 transition-all group"
        >
          <LogOut className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          <span className="text-sm font-semibold tracking-tight">Logout</span>
        </button>
      </div>
    </aside>
  );
};
