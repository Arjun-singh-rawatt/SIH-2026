import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Menu,
  Search,
  Bell,
  Sparkles,
  AlertTriangle,
  ExternalLink,
  Shield,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useReportsContext } from '../../context/ReportsContext';
import { Button } from '../ui/Button';

export function Header({ onOpenSidebar }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser } = useAuth();
  const { reports } = useReportsContext();
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);

  const pendingReports = reports.filter((r) => r.reviewStatus === 'PENDING').slice(0, 4);
  const criticalCount = reports.filter((r) => r.sifPotential === 'CRITICAL').length;

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/reports?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-[#FAF7F2]/85 backdrop-blur-md border-b border-surface-border/80 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
      {/* Left section: Mobile menu + Search bar */}
      <div className="flex items-center gap-3 sm:gap-4 flex-1 max-w-xl">
        <button
          onClick={onOpenSidebar}
          className="p-2 -ml-1 text-ink-secondary hover:text-ink-primary hover:bg-[#EFEAE1] rounded-2xl lg:hidden cursor-pointer"
          aria-label="Open navigation sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full max-w-md hidden sm:block">
          <Search className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search reports, hazards, facilities, or precursors..."
            className="w-full bg-[#FAF7F2] border border-surface-border/80 text-xs sm:text-sm text-ink-primary placeholder:text-ink-muted/80 pl-10 pr-9 py-2.2 rounded-full focus:outline-none focus:ring-2 focus:ring-brand-700/20 focus:border-brand-700 focus:bg-white transition-all shadow-spatial-xs"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted hover:text-ink-primary p-0.5 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </form>
      </div>

      {/* Right Section: AI Analyze Quick Button + Notifications + User info */}
      <div className="flex items-center gap-3 sm:gap-4">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate('/analyze')}
          icon={Sparkles}
          className="hidden md:inline-flex border-emerald-300/80 text-emerald-950 bg-emerald-50/70 hover:bg-emerald-100/80 shadow-spatial-xs"
        >
          Analyze Report
        </Button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2.5 text-ink-secondary hover:text-ink-primary hover:bg-[#EFEAE1] rounded-full border border-surface-border/80 bg-white shadow-spatial-xs transition-all cursor-pointer"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            {pendingReports.length > 0 && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-amber-500 rounded-full ring-2 ring-white animate-pulse" />
            )}
          </button>

          {/* Notifications Dropdown Popover */}
          {showNotifications && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowNotifications(false)}
              />
              <div className="absolute right-0 mt-3 w-80 sm:w-96 bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial-xl p-5 z-50 animate-in fade-in zoom-in-95 duration-150">
                <div className="flex items-center justify-between pb-3 border-b border-surface-border/60">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <h3 className="text-xs font-extrabold text-ink-primary">Priority Triage Alerts</h3>
                  </div>
                  <span className="text-[10px] font-extrabold px-2.5 py-0.5 bg-amber-100 text-amber-950 rounded-full border border-amber-200">
                    {pendingReports.length} Pending
                  </span>
                </div>

                <div className="divide-y divide-surface-border/50 max-h-72 overflow-y-auto py-1">
                  {pendingReports.length === 0 ? (
                    <p className="text-xs text-ink-muted text-center py-5">All reports triaged & reviewed</p>
                  ) : (
                    pendingReports.map((r) => (
                      <div
                        key={r.id}
                        onClick={() => {
                          setShowNotifications(false);
                          navigate(`/reports/${r.id}`);
                        }}
                        className="py-3 px-2 hover:bg-[#FAF7F2] rounded-2xl cursor-pointer transition-colors"
                      >
                        <div className="flex items-center justify-between text-[10px] mb-1">
                          <span className="font-mono font-bold text-ink-secondary">#{r.reportId}</span>
                          <span className="text-red-900 font-extrabold bg-red-50 px-2 py-0.2 rounded-full border border-red-200">
                            Score: {r.urgencyScore}
                          </span>
                        </div>
                        <p className="text-xs font-bold text-ink-primary line-clamp-1">{r.primaryHazard}</p>
                        <p className="text-[10px] text-ink-muted mt-0.5">{r.facilityName}</p>
                      </div>
                    ))
                  )}
                </div>

                <div className="pt-3 border-t border-surface-border/60">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full text-xs"
                    onClick={() => {
                      setShowNotifications(false);
                      navigate('/review');
                    }}
                  >
                    View Complete Review Queue
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* User Avatar Pill */}
        <div className="flex items-center gap-2.5 pl-2 sm:pl-3 border-l border-surface-border/80">
          <img
            src={currentUser?.avatar}
            alt={currentUser?.name}
            className="w-8 h-8 rounded-full object-cover border border-surface-border/80 shadow-spatial-xs"
          />
          <div className="hidden xl:block text-left">
            <span className="block text-xs font-extrabold text-ink-primary leading-tight">{currentUser?.name}</span>
            <span className="block text-[10px] text-ink-muted font-medium">{currentUser?.role}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
