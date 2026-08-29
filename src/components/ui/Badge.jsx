import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  icon: Icon,
  className = '',
}) {
  const sizeStyles = {
    xs: 'text-[10px] px-2.5 py-0.5 font-bold tracking-wide',
    sm: 'text-xs px-3 py-0.5 font-bold',
    md: 'text-xs px-3.5 py-1 font-bold',
    lg: 'text-sm px-4 py-1.5 font-bold',
  };

  const variantStyles = {
    neutral: 'bg-[#EFEAE1] text-ink-secondary border border-surface-border',
    primary: 'bg-emerald-50 text-emerald-900 border border-emerald-200/80',
    amber: 'bg-amber-50 text-amber-900 border border-amber-200/80',
    orange: 'bg-orange-50 text-orange-950 border border-orange-200/80',
    crimson: 'bg-red-50 text-red-900 border border-red-200/80',
    success: 'bg-emerald-50 text-emerald-900 border border-emerald-200/80',
    sky: 'bg-sky-50 text-sky-900 border border-sky-200/80',
    purple: 'bg-purple-50 text-purple-900 border border-purple-200/80',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 rounded-full border shadow-spatial-xs select-none',
          sizeStyles[size] || sizeStyles.md,
          variantStyles[variant] || variantStyles.neutral,
          className
        )
      )}
    >
      {dot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full shrink-0',
            variant === 'crimson' && 'bg-red-600 animate-pulse',
            variant === 'amber' && 'bg-amber-500',
            variant === 'orange' && 'bg-orange-500',
            variant === 'success' && 'bg-emerald-600',
            variant === 'primary' && 'bg-emerald-600',
            variant === 'sky' && 'bg-sky-600',
            variant === 'neutral' && 'bg-ink-muted'
          )}
        />
      )}
      {Icon && <Icon className="w-3.5 h-3.5 shrink-0" />}
      <span>{children}</span>
    </span>
  );
}
