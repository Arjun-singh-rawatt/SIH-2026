import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Tabs({ tabs, activeTab, onChange, className = '' }) {
  return (
    <div
      className={twMerge(
        clsx(
          'inline-flex p-1.5 bg-[#EFEAE1]/90 border border-surface-border/80 rounded-full shadow-spatial-xs',
          className
        )
      )}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={clsx(
              'inline-flex items-center gap-2 px-4 py-1.8 rounded-full text-xs font-bold transition-all duration-150 select-none cursor-pointer',
              isActive
                ? 'bg-white text-ink-primary shadow-spatial-sm border border-surface-border/50'
                : 'text-ink-secondary hover:text-ink-primary hover:bg-white/50'
            )}
          >
            {tab.icon && <tab.icon className="w-3.5 h-3.5" />}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                className={clsx(
                  'px-2 py-0.2 rounded-full text-[10px] font-extrabold font-mono',
                  isActive ? 'bg-emerald-50 text-emerald-900 border border-emerald-200/60' : 'bg-[#E5DFD4] text-ink-muted'
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
