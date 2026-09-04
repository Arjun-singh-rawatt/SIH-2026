import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, ChevronDown, ClipboardPlus, FileText, LogOut, Shield, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const navItems = [
  { label: 'Report', path: '/report', icon: ClipboardPlus },
  { label: 'My Reports', path: '/my-reports', icon: FileText },
  { label: 'Life Saving Rules', path: '/field-life-saving-rules', icon: ShieldCheck },
];

export function FieldShell({ activePage, children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f5f1e9] text-[#121827]">
      <div
        className="pointer-events-none fixed inset-0 bg-cover bg-center bg-no-repeat opacity-[0.18]"
        style={{ backgroundImage: 'url(/assets/oil-refinery-bg.png)' }}
      />
      <div className="pointer-events-none fixed inset-0 bg-[linear-gradient(90deg,rgba(248,245,239,0.91)_0%,rgba(249,246,240,0.78)_55%,rgba(248,244,236,0.88)_100%)]" />

      <aside className="fixed inset-y-0 left-0 z-20 flex w-[260px] shrink-0 flex-col bg-[linear-gradient(180deg,#075b49_0%,#034c3a_100%)] px-5 py-6 text-white shadow-[8px_0_26px_rgba(3,54,42,0.1)]">
        <div className="flex items-center gap-3 border-b border-white/20 pb-6">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/40 bg-white/10">
            <Shield className="h-7 w-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <p className="text-xl font-black tracking-tight">SIFT</p>
              <span className="rounded-full border border-[#f1c477]/80 bg-[#f1c477] px-1.5 py-0.5 text-[9px] font-black tracking-[0.12em] text-[#5f3b13]">OIL</span>
            </div>
            <p className="text-sm font-semibold">Safety Intelligence</p>
            <p className="mt-1 text-[10px] text-emerald-100/75">Safety Today. Safer Tomorrow.</p>
          </div>
        </div>

        <nav className="mt-7 space-y-3">
          {navItems.map((item) => {
            const isActive = activePage === item.path || location.pathname === item.path;
            return (
              <button
                key={item.path}
                type="button"
                onClick={() => navigate(item.path)}
                className={`flex w-full items-center gap-4 rounded-xl px-4 py-3.5 text-left text-sm font-semibold transition-colors ${isActive ? 'border-l-2 border-white bg-white/15 text-white' : 'text-emerald-50/90 hover:bg-white/10'}`}
              >
                <item.icon className={`h-5 w-5 ${item.label === 'Life Saving Rules' ? 'text-orange-300' : ''}`} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="mt-auto border-t border-white/20 pt-5">
          <button type="button" onClick={handleLogout} className="flex items-center gap-4 px-4 py-3 text-sm font-semibold text-white/90">
            <LogOut className="h-5 w-5" /> Logout
          </button>
          <p className="mt-5 px-2 text-xs leading-5 text-emerald-50/85">Oil India Limited<br />HSE Digital Initiative</p>
        </div>
      </aside>

      <div className="relative z-10 ml-[260px] min-h-screen">
        <header className="flex h-[72px] items-center justify-between border-b border-[#ddd5c9] bg-[#fbf9f5]/90 px-5 backdrop-blur-sm sm:px-8">
          <div>
            <p className="text-lg font-black tracking-tight text-[#073f34]">SIF Intelligence Hub</p>
            <p className="text-xs text-[#6e6a63]">Detect &nbsp;|&nbsp; Analyze &nbsp;|&nbsp; Prevent</p>
          </div>
          <div className="flex items-center gap-4">
            <button type="button" className="relative rounded-full p-2 text-[#14211e] hover:bg-[#efeae1]" aria-label="Notifications">
              <Bell className="h-5 w-5" />
              <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-[#ef7b30]" />
            </button>
            <div className="hidden h-8 border-l border-[#d9d2c7] sm:block" />
            <div className="flex items-center gap-2.5">
              <img src={currentUser?.avatar} alt="" className="h-9 w-9 rounded-full border border-[#d9d2c7] object-cover" />
              <span className="hidden text-sm font-semibold sm:block">Field User</span>
              <ChevronDown className="hidden h-4 w-4 sm:block" />
            </div>
          </div>
        </header>

        {children}

        <footer className="px-5 pb-5 text-xs text-[#72716e] sm:px-8 lg:pb-7">Copyright 2024 Oil India Limited. SIF Intelligence Platform. High-Risk Environment Protocol.</footer>
      </div>
    </div>
  );
}
