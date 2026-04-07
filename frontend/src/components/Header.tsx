import React, { useState } from 'react';
import { Search, Bell, User, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/report/${query.trim().toUpperCase()}`);
    }
  };

  return (
    <header className="h-16 bg-[#0d0d0d] border-b border-[#1f1f1f] flex items-center justify-between px-8 sticky top-0 z-40 ml-64">
      {/* Search Input */}
      <form onSubmit={handleSearch} className="flex-1 max-w-xl group">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-500 transition-colors" />
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search symbols or insights..."
            className="w-full bg-[#141414] border border-[#1f1f1f] rounded-xl py-2 pl-12 pr-4 text-sm text-slate-300 focus:outline-none focus:border-blue-500/50 transition-all font-medium placeholder:text-slate-600"
          />
        </div>
      </form>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-xl text-slate-500 hover:text-white hover:bg-[#1f1f1f] transition-all relative">
          <Bell className="w-5 h-5" />
          <div className="absolute top-2.5 right-2.5 w-1.5 h-1.5 bg-blue-500 rounded-full border border-[#0d0d0d]"></div>
        </button>
        <button className="p-2 rounded-xl text-slate-500 hover:text-white hover:bg-[#1f1f1f] transition-all">
          <MessageSquare className="w-5 h-5" />
        </button>
        
        <div className="h-8 w-px bg-[#1f1f1f] mx-2"></div>

        <button className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 p-[2px] shadow-lg group-hover:scale-105 transition-transform">
            <div className="w-full h-full rounded-full bg-[#141414] flex items-center justify-center font-bold text-[10px] text-white">
              JD
            </div>
          </div>
          <span className="text-sm font-semibold text-slate-300 group-hover:text-white transition-colors">Jane Doe</span>
        </button>
      </div>
    </header>
  );
};
