import React from 'react';
import { Card } from '../ui/Card';
import { formatNumber, formatPercent } from '../../utils/formatters';

export function ReportStatsBanner({ stats }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 mb-6">
      <Card className="p-4 bg-white rounded-3xl">
        <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
          Matching Reports
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-2xl font-black text-ink-primary font-sans">
            {formatNumber(stats.totalMatching)}
          </span>
          <span className="text-[10px] text-ink-muted font-medium">of {formatNumber(stats.totalDatabase)}</span>
        </div>
      </Card>

      <Card className="p-4 bg-amber-50/50 border-amber-200/80 rounded-3xl">
        <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-950 block">
          SIF Potential Flagged
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-2xl font-black text-amber-950 font-sans">
            {formatNumber(stats.sifCount)}
          </span>
          <span className="text-[10px] font-black text-amber-900 bg-amber-100/80 px-2 py-0.2 rounded-full">
            {formatPercent(stats.sifPercentage)}
          </span>
        </div>
      </Card>

      <Card className="p-4 bg-red-50/50 border-red-200/80 rounded-3xl">
        <span className="text-[10px] font-extrabold uppercase tracking-widest text-red-950 block">
          Critical / High Urgency
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-2xl font-black text-red-950 font-sans">
            {formatNumber(stats.criticalHighCount)}
          </span>
          <span className="text-[10px] font-black text-red-900 bg-red-100/80 px-2 py-0.2 rounded-full">
            Immediate Triage
          </span>
        </div>
      </Card>

      <Card className="p-4 bg-white rounded-3xl">
        <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
          Pending HSE Sign-off
        </span>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-2xl font-black text-emerald-950 font-sans">
            {formatNumber(stats.pendingReviewCount)}
          </span>
          <span className="text-[10px] text-emerald-800 font-bold bg-emerald-50 px-2 py-0.2 rounded-full border border-emerald-200/60">
            Awaiting Review
          </span>
        </div>
      </Card>
    </div>
  );
}
