import React from 'react';
import { SearchX, AlertCircle } from 'lucide-react';
import { Button } from './Button';

export function EmptyState({
  title = 'No reports found',
  description = 'Try adjusting your search criteria, filters, or date range.',
  icon: Icon = SearchX,
  actionLabel,
  onAction,
  className = '',
}) {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center rounded-2xl bg-white border border-dashed border-surface-border ${className}`}>
      <div className="w-14 h-14 rounded-2xl bg-canvas-subtle border border-surface-border flex items-center justify-center text-ink-muted mb-4 shadow-xs">
        <Icon className="w-7 h-7 stroke-[1.5]" />
      </div>
      <h3 className="text-base font-semibold text-ink-primary tracking-tight">{title}</h3>
      <p className="text-xs text-ink-muted mt-1 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <Button variant="secondary" size="sm" onClick={onAction} className="mt-4">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export function LoadingState({ message = 'Loading safety intelligence data...' }) {
  return (
    <div className="flex flex-col items-center justify-center p-16 text-center">
      <div className="relative w-12 h-12 mb-4">
        <div className="absolute inset-0 rounded-full border-4 border-surface-border" />
        <div className="absolute inset-0 rounded-full border-4 border-brand-800 border-t-transparent animate-spin" />
      </div>
      <p className="text-xs font-medium text-ink-secondary">{message}</p>
    </div>
  );
}

export function SkeletonRow({ cols = 6 }) {
  return (
    <div className="flex items-center gap-4 py-3.5 px-4 border-b border-surface-border/50 animate-pulse">
      {Array.from({ length: cols }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-canvas-muted rounded-full"
          style={{ width: `${Math.max(40, (i + 1) * 18)}%` }}
        />
      ))}
    </div>
  );
}
