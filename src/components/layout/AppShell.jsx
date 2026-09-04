import React, { useState } from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAuth } from '../../context/AuthContext';

export function AppShell() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // The frontline reporting flow has its own deliberately focused field shell.
  if (['/report', '/my-reports', '/field-life-saving-rules'].includes(location.pathname)) {
    return <Outlet />;
  }

  return (
    <div className="min-h-screen bg-canvas flex text-ink-primary font-sans antialiased selection:bg-brand-600/20 selection:text-brand-950 relative">
      {/* Subtle warm top ambient illumination */}
      <div className="fixed top-0 left-0 right-0 h-96 bg-gradient-to-b from-white/70 via-white/20 to-transparent pointer-events-none z-0" />

      {/* Sidebar navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content viewport */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-72 transition-all duration-200 relative z-10">
        <Header onOpenSidebar={() => setSidebarOpen(true)} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto animate-in fade-in duration-200">
          <Outlet />
        </main>

        {/* Tactile Soft Footer */}
        <footer className="border-t border-surface-border/60 bg-[#FAF7F2]/80 backdrop-blur-xs py-5 px-6 sm:px-8 text-center sm:flex sm:justify-between sm:items-center text-xs text-ink-muted">
          <div>
            <span className="font-extrabold text-ink-primary">SIFT</span> · Oil India Limited (OIL) Safety Intelligence Platform
          </div>
          <div className="mt-2 sm:mt-0 flex items-center justify-center gap-3 text-[11px] font-medium">
            <span>IOGP Standard Compliant</span>
            <span>·</span>
            <span>SIH Precursor Engine v2.4</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
