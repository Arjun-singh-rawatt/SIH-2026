import React from 'react';
import {
  Sparkles,
  ShieldAlert,
  Flame,
  Gauge,
  CheckCircle2,
  AlertTriangle,
  Info,
  Layers,
  ArrowUpRight,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { SIFPotentialBadge, UrgencyScoreBadge } from '../ui/RiskBadge';
import { ProgressBar } from '../ui/ProgressBar';

export function AIClassificationCard({ report }) {
  if (!report) return null;

  return (
    <Card className="border-emerald-200/80 shadow-spatial-lg bg-gradient-to-b from-white via-white to-emerald-50/10 rounded-3.5xl">
      <CardHeader
        action={
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-950 border border-emerald-200 text-xs font-black shadow-spatial-xs">
            <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
            <span>AI Safety Assessment</span>
          </div>
        }
      >
        <CardTitle subtitle="Deterministic NLP model evaluation & feature extraction">
          AI Risk Intelligence
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6 p-6 sm:p-7">
        {/* Top Metric Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          {/* SIF Potential */}
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 flex flex-col justify-between shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              SIF Potential
            </span>
            <div className="mt-2.5">
              <SIFPotentialBadge potential={report.sifPotential} size="md" />
            </div>
          </div>

          {/* AI Confidence */}
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 flex flex-col justify-between shadow-spatial-xs">
            <div className="flex justify-between items-center text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              <span>AI Confidence</span>
              <span className="font-mono font-black text-emerald-950 text-xs">{report.confidence}%</span>
            </div>
            <div className="mt-2.5">
              <ProgressBar value={report.confidence} max={100} variant="dynamic-confidence" size="sm" />
            </div>
          </div>

          {/* Urgency Score */}
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 flex flex-col justify-between shadow-spatial-xs">
            <div className="flex justify-between items-center text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              <span>Urgency Score</span>
              <span className="font-mono font-black text-red-950 text-xs">{report.urgencyScore}/100</span>
            </div>
            <div className="mt-2.5">
              <ProgressBar value={report.urgencyScore} max={100} variant="dynamic-urgency" size="sm" />
            </div>
          </div>

          {/* SIF Precursor Flag */}
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 flex flex-col justify-between shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              SIF Precursor
            </span>
            <div className="mt-2.5">
              <span
                className={`inline-flex items-center gap-1 text-xs font-black px-3 py-1 rounded-full border shadow-spatial-xs ${
                  report.sifPrecursor === 'YES'
                    ? 'bg-amber-100 text-amber-950 border-amber-300'
                    : 'bg-[#EFEAE1] text-ink-secondary border-surface-border'
                }`}
              >
                {report.sifPrecursor === 'YES' ? 'FLAGGED (YES)' : 'NO PRECURSOR'}
              </span>
            </div>
          </div>
        </div>

        {/* Structured Classification Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
          {/* Activity */}
          <div className="p-4 rounded-2.5xl bg-white border border-surface-border/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-1">
              Operational Activity
            </span>
            <p className="text-xs sm:text-sm font-extrabold text-ink-primary">{report.activity}</p>
          </div>

          {/* Primary Hazard */}
          <div className="p-4 rounded-2.5xl bg-white border border-surface-border/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-1">
              Primary Hazard
            </span>
            <p className="text-xs sm:text-sm font-extrabold text-ink-primary">{report.primaryHazard}</p>
          </div>

          {/* Precursor Category */}
          <div className="p-4 rounded-2.5xl bg-amber-50/30 border border-amber-200/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-950 block mb-1">
              Precursor Category
            </span>
            <p className="text-xs sm:text-sm font-extrabold text-amber-950">{report.precursorCategory}</p>
          </div>

          {/* Life-Saving Rule */}
          <div className="p-4 rounded-2.5xl bg-white border border-surface-border/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-1">
              IOGP Life-Saving Rule
            </span>
            <p className="text-xs sm:text-sm font-extrabold text-ink-primary flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
              <span>{report.lifeSavingRule}</span>
            </p>
          </div>
        </div>

        {/* AI Explanation Callout */}
        <div className="p-5 rounded-3xl bg-[#FAF7F2] border border-surface-border/80 space-y-2 shadow-spatial-xs">
          <div className="flex items-center gap-2 text-xs font-extrabold text-emerald-950">
            <Sparkles className="w-4 h-4 text-emerald-700" />
            <span>AI Rationale & Model Explanation</span>
          </div>
          <p className="text-xs sm:text-sm text-ink-primary leading-relaxed font-normal">
            {report.aiExplanation}
          </p>
        </div>

        {/* AI Transparency Disclaimer */}
        <div className="flex items-center gap-2.5 text-[11px] text-ink-muted bg-white p-3.5 rounded-2xl border border-surface-border/70 shadow-spatial-xs">
          <Info className="w-4 h-4 text-ink-muted shrink-0" />
          <span>
            <strong>Human-in-the-Loop Safeguard:</strong> This assessment was generated by AI pattern detection algorithms and requires HSE professional validation before final risk closure.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
