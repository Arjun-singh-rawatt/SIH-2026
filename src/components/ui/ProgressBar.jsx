import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function ProgressBar({
  value,
  max = 100,
  variant = 'default',
  showLabel = false,
  size = 'md',
  className = '',
}) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const heightStyles = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3.5',
  };

  const getVariantBar = () => {
    if (variant === 'dynamic-urgency') {
      if (percentage >= 90) return 'bg-gradient-to-r from-[#EF4444] to-[#DC2626] shadow-sm';
      if (percentage >= 75) return 'bg-gradient-to-r from-[#F97316] to-[#EA580C] shadow-sm';
      if (percentage >= 50) return 'bg-gradient-to-r from-[#FBBF24] to-[#F59E0B]';
      return 'bg-gradient-to-r from-[#34D399] to-[#059669]';
    }
    if (variant === 'dynamic-confidence') {
      if (percentage >= 90) return 'bg-gradient-to-r from-[#10B981] to-[#047857] shadow-sm';
      if (percentage >= 75) return 'bg-gradient-to-r from-[#059669] to-[#065F46]';
      return 'bg-gradient-to-r from-[#FBBF24] to-[#D97706]';
    }
    if (variant === 'amber') return 'bg-gradient-to-r from-[#FBBF24] to-[#D97706]';
    if (variant === 'orange') return 'bg-gradient-to-r from-[#FB923C] to-[#EA580C]';
    if (variant === 'crimson') return 'bg-gradient-to-r from-[#EF4444] to-[#DC2626]';
    if (variant === 'emerald') return 'bg-gradient-to-r from-[#10B981] to-[#047857]';
    return 'bg-gradient-to-r from-[#058867] to-[#046B4F]';
  };

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex justify-between items-center text-xs mb-1.5 font-bold text-ink-secondary">
          <span>Progress</span>
          <span className="font-mono font-extrabold">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={clsx('w-full bg-[#EAE3D6] rounded-full overflow-hidden border border-surface-border/40 p-0.5', heightStyles[size])}>
        <div
          className={clsx('h-full rounded-full transition-all duration-500', getVariantBar())}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
