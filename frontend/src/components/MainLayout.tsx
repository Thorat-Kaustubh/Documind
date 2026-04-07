import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-200">
      <Sidebar />
      <Header />
      <main className="ml-64 p-8 max-w-7xl mx-auto min-h-[calc(100vh-4rem)]">
        {children}
      </main>
    </div>
  );
};
