import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Card({
  children,
  variant = 'default',
  className = '',
  onClick,
  ...props
}) {
  const variantStyles = {
    default: 'bg-white border border-surface-border/70 shadow-spatial rounded-3xl',
    interactive:
      'bg-white border border-surface-border/70 shadow-spatial hover:shadow-spatial-lg hover:-translate-y-0.5 rounded-3xl cursor-pointer transition-all duration-200',
    elevated: 'bg-white border border-surface-border/80 shadow-spatial-lg rounded-3.5xl',
    sunken: 'bg-canvas-subtle/80 border border-surface-border/60 rounded-3xl',
    heroEmerald:
      'bg-gradient-to-br from-[#065F46] via-[#044E3B] to-[#022C22] text-white border border-emerald-600/30 shadow-[0_18px_38px_rgba(4,78,59,0.25)] rounded-3.5xl',
    heroAmber:
      'bg-gradient-to-br from-[#FB923C] via-[#EA580C] to-[#C2410C] text-white border border-orange-400/40 shadow-[0_18px_38px_rgba(234,88,12,0.25)] rounded-3.5xl',
    accentWarm:
      'bg-gradient-to-br from-[#FFFDF9] via-[#FAF6EE] to-[#F5EFE4] border border-[#EAE2D3] shadow-spatial-sm rounded-3xl',
  };

  return (
    <div
      onClick={onClick}
      className={twMerge(clsx('relative overflow-hidden', variantStyles[variant] || variantStyles.default, className))}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '', action }) {
  return (
    <div className={twMerge(clsx('flex items-center justify-between p-5 sm:p-6 pb-3.5 border-b border-surface-border/50', className))}>
      <div>{children}</div>
      {action && <div>{action}</div>}
    </div>
  );
}

export function CardTitle({ children, subtitle, className = '', titleClassName = '' }) {
  return (
    <div className={className}>
      <h3 className={twMerge(clsx('text-sm sm:text-base font-extrabold text-ink-primary tracking-tight font-sans', titleClassName))}>
        {children}
      </h3>
      {subtitle && <p className="text-xs text-ink-muted mt-0.5 font-normal leading-relaxed">{subtitle}</p>}
    </div>
  );
}

export function CardContent({ children, className = '' }) {
  return <div className={twMerge(clsx('p-5 sm:p-6', className))}>{children}</div>;
}
