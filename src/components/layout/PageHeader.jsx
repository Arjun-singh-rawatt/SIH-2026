import React from 'react';
import { ChevronRight } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export function PageHeader({
  title,
  subtitle,
  badge,
  breadcrumbs = [],
  actions,
  className = '',
}) {
  return (
    <div className={`mb-6 sm:mb-8 ${className}`}>
      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-1.5 text-xs text-ink-muted mb-2.5 font-medium">
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={crumb.label || idx}>
              {crumb.path ? (
                <NavLink
                  to={crumb.path}
                  className="hover:text-ink-primary transition-colors font-semibold"
                >
                  {crumb.label}
                </NavLink>
              ) : (
                <span className="text-ink-primary font-bold">{crumb.label}</span>
              )}
              {idx < breadcrumbs.length - 1 && (
                <ChevronRight className="w-3.5 h-3.5 text-ink-muted/50" />
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      {/* Main Title Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl sm:text-3xl lg:text-[32px] font-black text-ink-primary tracking-tight font-sans">
              {title}
            </h1>
            {badge && <div>{badge}</div>}
          </div>
          {subtitle && (
            <p className="text-xs sm:text-sm text-ink-secondary/80 mt-1 max-w-2xl font-normal leading-relaxed">
              {subtitle}
            </p>
          )}
        </div>

        {/* Action buttons */}
        {actions && <div className="flex items-center gap-3 shrink-0 flex-wrap">{actions}</div>}
      </div>
    </div>
  );
}
