import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Network,
  BellRing,
  ListTodo,
  ShieldAlert,
  Settings,
  LogOut,
  Shield,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const { currentUser, logout } = useAuth();

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard, exact: true },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Patterns', path: '/intelligence', icon: Network },
    { name: 'Alerts', path: '/review', icon: BellRing },
    { name: 'Actions', path: '/actions', icon: ListTodo },
    { name: 'Life-Saving Rules', path: '/life-saving-rules', icon: ShieldAlert },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-stone-950/30 backdrop-blur-xs lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-72 bg-[#FAF7F2]/95 backdrop-blur-md border-r border-surface-border/80 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-5 sm:p-6 border-b border-surface-border/60 flex items-center justify-between">
          <NavLink to="/dashboard" className="flex items-center gap-3 group" onClick={() => onClose && onClose()}>
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-b from-[#058867] to-[#046B4F] flex items-center justify-center text-white shadow-btn-emerald border border-[#045D44] group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 text-emerald-100" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-black text-lg text-ink-primary tracking-tight font-sans">SIFT</span>
                <span className="text-[10px] uppercase font-extrabold tracking-widest px-2 py-0.2 rounded-full bg-amber-100 text-amber-950 border border-amber-200/80">
                  OIL
                </span>
              </div>
              <p className="text-[10px] text-ink-muted leading-tight font-medium">Safety Intelligence & Fatality-risk</p>
            </div>
          </NavLink>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-4">
          <div className="space-y-1">
            {navItems.map((item) => {
              const isActive =
                item.exact || item.path === '/dashboard'
                  ? location.pathname === item.path || location.pathname === '/'
                  : location.pathname.startsWith(item.path);

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => onClose && onClose()}
                  className={`flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-bold transition-all duration-150 ${
                    isActive
                      ? 'bg-gradient-to-b from-[#058867] to-[#046B4F] text-white shadow-btn-emerald border border-[#045D44]'
                      : 'text-ink-secondary hover:text-ink-primary hover:bg-[#EFEAE1]/80'
                  }`}
                >
                  <item.icon className={`w-4 h-4 ${isActive ? 'text-emerald-100' : 'text-ink-muted'}`} />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </div>
        </div>

        <div className="p-3.5 border-t border-surface-border/60 bg-[#FAF7F2]/90">
          <div className="flex items-center justify-between rounded-2xl border border-surface-border/80 bg-white p-3 shadow-spatial-xs">
            <div className="flex items-center gap-3 overflow-hidden">
              <img
                src={currentUser?.avatar}
                alt={currentUser?.name}
                className="h-9 w-9 rounded-full object-cover border border-surface-border/80"
              />
              <div className="overflow-hidden">
                <div className="truncate text-xs font-extrabold text-ink-primary">{currentUser?.name}</div>
                <div className="truncate text-[10px] font-medium text-ink-muted">{currentUser?.role}</div>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign out"
              className="rounded-xl p-1.5 text-ink-muted transition-colors hover:bg-red-50 hover:text-red-700"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
