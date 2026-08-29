import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, ArrowUpRight } from 'lucide-react';
import { Card } from '../ui/Card';

export function MetricCard({
  title,
  value,
  percentage,
  change,
  changeType = 'neutral',
  subtitle,
  icon: Icon,
  variant = 'default',
  onClick,
}) {
  const getChangeBadge = () => {
    if (!change) return null;

    let badgeClasses = 'bg-[#EFEAE1] text-ink-secondary border-surface-border';
    let ChangeIcon = TrendingUp;

    if (changeType === 'increase') {
      badgeClasses = 'bg-amber-50 text-amber-950 border-amber-200 font-extrabold shadow-spatial-xs';
      ChangeIcon = TrendingUp;
    } else if (changeType === 'decrease') {
      badgeClasses = 'bg-emerald-50 text-emerald-900 border-emerald-200 font-bold shadow-spatial-xs';
      ChangeIcon = TrendingDown;
    } else if (changeType === 'warning') {
      badgeClasses = 'bg-red-50 text-red-900 border-red-200 font-extrabold shadow-spatial-xs';
      ChangeIcon = AlertTriangle;
    }

    return (
      <span className={`inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full border ${badgeClasses}`}>
        <ChangeIcon className="w-3 h-3" />
        <span>{change}</span>
      </span>
    );
  };

  return (
    <Card
      variant={onClick ? 'interactive' : 'default'}
      onClick={onClick}
      className="p-6 sm:p-7 flex flex-col justify-between rounded-3.5xl"
    >
      <div>
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-ink-muted">{title}</span>
          <div className="w-10 h-10 rounded-2xl bg-[#FAF7F2] border border-surface-border/80 flex items-center justify-center text-emerald-900 shadow-spatial-xs">
            {Icon && <Icon className="w-4 h-4 text-emerald-800" />}
          </div>
        </div>

        <div className="mt-3.5 flex items-baseline gap-2.5">
          <span className="text-3xl sm:text-4xl font-black text-ink-primary tracking-tight font-sans">
            {value}
          </span>
          {percentage && (
            <span className="text-xs font-black text-emerald-950 bg-emerald-50 border border-emerald-200/90 px-2.5 py-0.5 rounded-full shadow-spatial-xs">
              {percentage}
            </span>
          )}
        </div>
      </div>

      <div className="mt-5 pt-3.5 border-t border-surface-border/60 flex items-center justify-between text-xs">
        <span className="text-ink-muted text-[11px] truncate max-w-[170px] font-medium">{subtitle}</span>
        <div>{getChangeBadge()}</div>
      </div>
    </Card>
  );
}
