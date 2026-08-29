import React from 'react';
import {
  AlertTriangle,
  Flame,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  CheckCircle2,
  Clock,
  HelpCircle,
  AlertOctagon,
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function SIFPotentialBadge({ potential, showIcon = true, size = 'sm', className = '' }) {
  const norm = (potential || '').toUpperCase();

  let label = potential || 'NON-SIF';
  let badgeStyle = 'bg-[#EFEAE1] text-ink-secondary border-[#E2DBD0]';
  let Icon = ShieldCheck;

  if (norm === 'CRITICAL' || norm === 'CRITICAL SIF') {
    label = 'CRITICAL SIF';
    badgeStyle = 'bg-red-50 text-red-900 border-red-200 font-extrabold shadow-spatial-xs';
    Icon = AlertOctagon;
  } else if (norm === 'HIGH' || norm === 'HIGH SIF' || norm === 'YES') {
    label = 'HIGH SIF';
    badgeStyle = 'bg-orange-50 text-orange-950 border-orange-200 font-extrabold shadow-spatial-xs';
    Icon = Flame;
  } else if (norm === 'MEDIUM' || norm === 'MEDIUM SIF') {
    label = 'MEDIUM SIF';
    badgeStyle = 'bg-amber-50 text-amber-900 border-amber-200 font-bold';
    Icon = AlertTriangle;
  } else if (norm === 'LOW') {
    label = 'LOW SIF';
    badgeStyle = 'bg-emerald-50 text-emerald-900 border-emerald-200 font-bold';
    Icon = ShieldCheck;
  } else if (norm === 'NON-SIF' || norm === 'NO') {
    label = 'NON-SIF';
    badgeStyle = 'bg-[#EFEAE1] text-ink-muted border-[#E2DBD0] font-medium';
    Icon = ShieldCheck;
  }

  const sizeClass =
    size === 'xs'
      ? 'text-[10px] px-2.5 py-0.5'
      : size === 'lg'
      ? 'text-sm px-4 py-1.5'
      : 'text-xs px-3 py-0.8';

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 rounded-full border tracking-tight select-none',
          sizeClass,
          badgeStyle,
          className
        )
      )}
    >
      {showIcon && <Icon className={size === 'xs' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />}
      <span>{label}</span>
    </span>
  );
}

export function ReviewStatusBadge({ status, size = 'sm', className = '' }) {
  const norm = (status || '').toUpperCase();

  let label = status || 'Pending';
  let badgeStyle = 'bg-[#EFEAE1] text-ink-secondary border-[#E2DBD0]';
  let Icon = Clock;

  if (norm === 'APPROVED' || norm === 'VALIDATED') {
    label = 'Approved';
    badgeStyle = 'bg-emerald-50 text-emerald-900 border-emerald-200 font-bold shadow-spatial-xs';
    Icon = CheckCircle2;
  } else if (norm === 'PENDING') {
    label = 'Pending Review';
    badgeStyle = 'bg-amber-50 text-amber-950 border-amber-200 font-bold shadow-spatial-xs';
    Icon = Clock;
  } else if (norm === 'NEEDS CORRECTION' || norm === 'REJECTED') {
    label = 'Needs Correction';
    badgeStyle = 'bg-red-50 text-red-900 border-red-200 font-bold shadow-spatial-xs';
    Icon = AlertTriangle;
  } else if (norm === 'MODIFIED') {
    label = 'Modified';
    badgeStyle = 'bg-sky-50 text-sky-900 border-sky-200 font-bold shadow-spatial-xs';
    Icon = CheckCircle2;
  }

  const sizeClass =
    size === 'xs'
      ? 'text-[10px] px-2.5 py-0.5'
      : size === 'lg'
      ? 'text-sm px-4 py-1.5'
      : 'text-xs px-3 py-0.8';

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 rounded-full border select-none',
          sizeClass,
          badgeStyle,
          className
        )
      )}
    >
      <Icon className="w-3.5 h-3.5 shrink-0" />
      <span>{label}</span>
    </span>
  );
}

export function BarrierStatusBadge({ status, size = 'sm', className = '' }) {
  const norm = (status || '').toUpperCase();

  let label = status || 'Unknown';
  let badgeStyle = 'bg-[#EFEAE1] text-ink-secondary border-[#E2DBD0]';
  let Icon = HelpCircle;

  if (norm === 'FAILED') {
    label = 'FAILED';
    badgeStyle = 'bg-red-50 text-red-900 border-red-200 font-extrabold shadow-spatial-xs';
    Icon = ShieldX;
  } else if (norm === 'WEAK' || norm === 'DEGRADED') {
    label = 'WEAK / DEGRADED';
    badgeStyle = 'bg-amber-50 text-amber-950 border-amber-200 font-extrabold shadow-spatial-xs';
    Icon = ShieldAlert;
  } else if (norm === 'EFFECTIVE') {
    label = 'EFFECTIVE';
    badgeStyle = 'bg-emerald-50 text-emerald-900 border-emerald-200 font-bold shadow-spatial-xs';
    Icon = ShieldCheck;
  }

  const sizeClass = size === 'xs' ? 'text-[10px] px-2.5 py-0.5' : 'text-xs px-3 py-0.8';

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 rounded-full border tracking-tight uppercase select-none',
          sizeClass,
          badgeStyle,
          className
        )
      )}
    >
      <Icon className="w-3.5 h-3.5 shrink-0" />
      <span>{label}</span>
    </span>
  );
}

export function UrgencyScoreBadge({ score, size = 'sm', className = '' }) {
  const s = Number(score) || 0;

  let badgeStyle = 'bg-[#EFEAE1] text-ink-secondary border-[#E2DBD0]';
  let level = 'Low';

  if (s >= 90) {
    badgeStyle = 'bg-red-50 text-red-900 border-red-200 font-extrabold shadow-spatial-xs';
    level = 'Critical';
  } else if (s >= 75) {
    badgeStyle = 'bg-orange-50 text-orange-950 border-orange-200 font-extrabold shadow-spatial-xs';
    level = 'High';
  } else if (s >= 50) {
    badgeStyle = 'bg-amber-50 text-amber-900 border-amber-200 font-bold';
    level = 'Med';
  } else {
    badgeStyle = 'bg-emerald-50 text-emerald-900 border-emerald-200 font-bold';
    level = 'Low';
  }

  const sizeClass = size === 'xs' ? 'text-[10px] px-2.5 py-0.5' : 'text-xs px-3 py-0.8';

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 rounded-full border font-mono select-none',
          sizeClass,
          badgeStyle,
          className
        )
      )}
    >
      <span className="font-sans font-bold text-[10px] uppercase">{level}</span>
      <span className="font-extrabold">{s}/100</span>
    </span>
  );
}
