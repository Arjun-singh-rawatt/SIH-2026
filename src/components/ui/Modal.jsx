import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Modal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 'max-w-xl',
  className = '',
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Soft warm backdrop */}
      <div
        className="fixed inset-0 bg-stone-950/30 backdrop-blur-xs transition-opacity animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div
        className={twMerge(
          clsx(
            'relative w-full bg-white rounded-4xl border border-surface-border/80 shadow-spatial-xl z-10 overflow-hidden transform transition-all animate-in zoom-in-95 duration-200',
            maxWidth,
            className
          )
        )}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 sm:p-7 border-b border-surface-border/60 bg-gradient-to-b from-[#FFFDF9] to-[#FAF6EE]">
          <div>
            <h2 className="text-base sm:text-lg font-extrabold text-ink-primary tracking-tight">{title}</h2>
            {subtitle && <p className="text-xs text-ink-muted mt-1 leading-relaxed">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="text-ink-muted hover:text-ink-primary p-2 rounded-full hover:bg-canvas-subtle transition-colors cursor-pointer"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 sm:p-7">{children}</div>
      </div>
    </div>
  );
}
