import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  pill = true,
  className = '',
  disabled = false,
  isLoading = false,
  icon: Icon,
  iconRight: IconRight,
  onClick,
  type = 'button',
  ...props
}) {
  const baseStyles =
    'inline-flex items-center justify-center font-bold tracking-tight transition-all duration-150 active:scale-[0.97] disabled:opacity-45 disabled:pointer-events-none disabled:active:scale-100 focus:outline-none focus:ring-2 focus:ring-offset-1 select-none cursor-pointer';

  const sizeStyles = {
    xs: 'text-[11px] px-3 py-1 gap-1.5',
    sm: 'text-xs px-3.5 py-1.5 gap-1.5',
    md: 'text-xs sm:text-sm px-4.5 py-2.2 gap-2',
    lg: 'text-sm sm:text-base px-6 py-2.8 gap-2.5',
  };

  const roundedStyles = pill ? 'rounded-full' : 'rounded-2xl';

  const variantStyles = {
    primary:
      'bg-gradient-to-b from-[#058867] to-[#046B4F] text-white hover:from-[#06936F] hover:to-[#057758] focus:ring-emerald-600/40 shadow-btn-emerald border border-[#045D44]',
    emerald:
      'bg-gradient-to-b from-[#058867] to-[#046B4F] text-white hover:from-[#06936F] hover:to-[#057758] focus:ring-emerald-600/40 shadow-btn-emerald border border-[#045D44]',
    amber:
      'bg-gradient-to-b from-[#F59E0B] via-[#EE6F12] to-[#D97706] text-white hover:from-[#FBBF24] hover:to-[#EA580C] focus:ring-amber-500/40 shadow-btn-amber border border-[#C25E00]',
    orange:
      'bg-gradient-to-b from-[#FB923C] to-[#EA580C] text-white hover:from-[#F97316] hover:to-[#C2410C] focus:ring-orange-500/40 shadow-btn-orange border border-[#C2410C]',
    secondary:
      'bg-white text-ink-primary hover:bg-[#FAF7F2] focus:ring-brand-700/20 border border-surface-border shadow-spatial-xs hover:shadow-spatial-sm',
    outline:
      'bg-transparent text-ink-secondary hover:text-ink-primary hover:bg-canvas-subtle focus:ring-brand-700/20 border border-surface-border',
    ghost:
      'bg-transparent text-ink-secondary hover:text-ink-primary hover:bg-canvas-subtle/80 focus:ring-slate-300 border border-transparent',
    danger:
      'bg-gradient-to-b from-[#EF4444] to-[#DC2626] text-white hover:from-[#F87171] hover:to-[#B91C1C] focus:ring-red-500/40 shadow-[0_4px_14px_-1px_rgba(220,38,38,0.35)] border border-[#B91C1C]',
    success:
      'bg-gradient-to-b from-[#10B981] to-[#059669] text-white hover:from-[#34D399] hover:to-[#047857] focus:ring-emerald-500/40 shadow-btn-emerald border border-[#047857]',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={twMerge(
        clsx(
          baseStyles,
          sizeStyles[size] || sizeStyles.md,
          roundedStyles,
          variantStyles[variant] || variantStyles.primary,
          className
        )
      )}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin h-4 w-4 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : Icon ? (
        <Icon className={size === 'xs' || size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
      ) : null}
      <span>{children}</span>
      {!isLoading && IconRight && (
        <IconRight className={size === 'xs' || size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
      )}
    </button>
  );
}
