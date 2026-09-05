import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Building2,
  Activity,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  ArrowUpRight,
  ShieldCheck,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { SIFPotentialBadge } from '../ui/RiskBadge';
import { ProgressBar } from '../ui/ProgressBar';
import { useReportsContext } from '../../context/ReportsContext';

const riskColors = {
  Critical: '#991b1b',
  High: '#c2410c',
  Moderate: '#d97706',
  Low: '#047857',
};

function riskBucket(value) {
  if (value === 'CRITICAL') return 'Critical';
  if (value === 'HIGH') return 'High';
  if (value === 'MEDIUM') return 'Moderate';
  return 'Low';
}

export function PatternCard({ pattern }) {
  const navigate = useNavigate();
  const { reports } = useReportsContext();
  const [isExpanded, setIsExpanded] = useState(false);

  const isCritical = pattern.riskLevel === 'CRITICAL';
  const isUp = pattern.trendDirection === 'up';

  const associatedReports = useMemo(() => {
    const matchingReports = reports.filter(
      (report) =>
        report.precursorCategory === pattern.category &&
        report.failedBarrier === pattern.commonBarrierFailure
    );
    if (matchingReports.length > 0) return matchingReports;
    return reports.filter((report) => pattern.sampleReportIds?.includes(report.reportId));
  }, [pattern.category, pattern.commonBarrierFailure, pattern.sampleReportIds, reports]);

  const riskDistribution = useMemo(() => {
    const counts = { Critical: 0, High: 0, Moderate: 0, Low: 0 };
    associatedReports.forEach((report) => {
      counts[riskBucket(report.sifPotential)] += 1;
    });
    return Object.entries(counts)
      .filter(([, count]) => count > 0)
      .map(([name, count]) => ({ name, count }));
  }, [associatedReports]);

  const occurrenceTrend = useMemo(() => {
    const periods = new Map();
    associatedReports.forEach((report) => {
      if (!report.createdAt) return;
      const date = new Date(report.createdAt);
      if (Number.isNaN(date.getTime())) return;
      const key = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
      const label = date.toLocaleDateString('en-IN', { month: 'short', year: 'numeric', timeZone: 'UTC' });
      periods.set(key, { period: label, reports: (periods.get(key)?.reports || 0) + 1 });
    });
    return [...periods.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([, value]) => value);
  }, [associatedReports]);

  return (
    <Card className="border-surface-border/80 shadow-spatial rounded-3.5xl transition-all duration-200">
      {/* Pattern Header */}
      <div className="p-5 sm:p-6 border-b border-surface-border/60 bg-[#FAF7F2]/60">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <SIFPotentialBadge potential={pattern.riskLevel} size="xs" />
              <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded-full bg-white text-ink-secondary border border-surface-border/80 font-mono shadow-spatial-xs">
                {pattern.patternId}
              </span>
              <span className="text-xs font-extrabold text-amber-950 bg-amber-50 border border-amber-200/80 px-2.5 py-0.5 rounded-full shadow-spatial-xs">
                {pattern.category}
              </span>
            </div>
            <h3 className="text-base sm:text-lg font-black text-ink-primary tracking-tight font-sans">
              {pattern.title}
            </h3>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            {/* Occurrences Pill */}
            <div className="text-right">
              <span className="text-xl sm:text-2xl font-black font-mono text-ink-primary">
                {pattern.occurrences}
              </span>
              <span className="text-[10px] text-ink-muted block uppercase font-extrabold tracking-widest">
                Reports
              </span>
            </div>

            {/* Trend Badge */}
            <div
              className={`px-3 py-1 rounded-full text-xs font-black flex items-center gap-1 border shadow-spatial-xs ${
                isUp
                  ? 'bg-amber-50 text-amber-950 border-amber-300'
                  : 'bg-emerald-50 text-emerald-950 border-emerald-300'
              }`}
            >
              {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              <span>{pattern.trend}</span>
            </div>
          </div>
        </div>
      </div>

      <CardContent className="p-5 sm:p-6 space-y-4">
        {/* Core Metrics Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {/* Affected Facilities */}
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
            <div className="flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-2.5">
              <Building2 className="w-3.5 h-3.5 text-emerald-800" />
              <span>Primary Facilities Affected</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {pattern.affectedFacilities.map((fac) => (
                <span
                  key={fac}
                  onClick={() => navigate(`/facilities`)}
                  className="text-xs font-bold px-2.5 py-1 rounded-xl bg-white border border-surface-border/80 text-ink-primary hover:border-emerald-700 hover:text-emerald-950 transition-colors cursor-pointer shadow-spatial-xs"
                >
                  {fac}
                </span>
              ))}
            </div>
          </div>

          {/* Affected Activities */}
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
            <div className="flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-2.5">
              <Activity className="w-3.5 h-3.5 text-emerald-800" />
              <span>Recurring Activities</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {pattern.affectedActivities.map((act) => (
                <span
                  key={act}
                  className="text-xs font-bold px-2.5 py-1 rounded-xl bg-white border border-surface-border/80 text-ink-primary shadow-spatial-xs"
                >
                  {act}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Failed Barrier Callout */}
        <div className="p-4 rounded-2.5xl bg-red-50/40 border border-red-200/80 shadow-spatial-xs">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[10px] font-black uppercase tracking-widest text-red-950">
              Common Failed Barrier Mode
            </span>
            <span className="font-mono font-black text-ink-primary text-xs">
              SIF Density: {pattern.sifDensity}%
            </span>
          </div>
          <p className="text-xs sm:text-sm font-extrabold text-ink-primary mt-1">{pattern.commonBarrierFailure}</p>
        </div>

        <div className="grid grid-cols-1 gap-3.5 lg:grid-cols-2">
          <div className="rounded-2.5xl border border-surface-border/80 bg-[#FAF7F2] p-4 shadow-spatial-xs">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <h4 className="text-xs font-black uppercase tracking-widest text-ink-primary">Occurrence Trend</h4>
                <p className="mt-1 text-[11px] text-ink-muted">Reports by recorded month</p>
              </div>
              <span className="text-[10px] font-bold text-ink-muted">{associatedReports.length} matched</span>
            </div>
            {occurrenceTrend.length < 2 ? (
              <div className="flex h-40 items-center justify-center rounded-xl border border-dashed border-surface-border-strong bg-white/60 px-4 text-center text-xs text-ink-muted">
                Not enough dated history for a trend.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={occurrenceTrend} margin={{ top: 4, right: 8, left: -22, bottom: 0 }}>
                  <XAxis dataKey="period" tick={{ fontSize: 10, fill: '#857E74' }} axisLine={false} tickLine={false} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#857E74' }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: '#E8E1D5', opacity: 0.45 }} contentStyle={{ borderRadius: 10, border: '1px solid #E8E1D5', fontSize: 12 }} />
                  <Bar dataKey="reports" name="Reports" fill="#047857" radius={[5, 5, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-2.5xl border border-surface-border/80 bg-[#FAF7F2] p-4 shadow-spatial-xs">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <h4 className="text-xs font-black uppercase tracking-widest text-ink-primary">Risk Distribution</h4>
                <p className="mt-1 text-[11px] text-ink-muted">Associated report severity</p>
              </div>
              <span className="text-[10px] font-bold text-ink-muted">{riskDistribution.reduce((total, item) => total + item.count, 0)} matched</span>
            </div>
            {riskDistribution.length === 0 ? (
              <div className="flex h-40 items-center justify-center rounded-xl border border-dashed border-surface-border-strong bg-white/60 px-4 text-center text-xs text-ink-muted">
                No associated report risk data available.
              </div>
            ) : (
              <div className="flex h-40 items-center gap-3">
                <ResponsiveContainer width="52%" height="100%">
                  <PieChart>
                    <Pie data={riskDistribution} dataKey="count" nameKey="name" innerRadius={38} outerRadius={62} paddingAngle={2}>
                      {riskDistribution.map((entry) => <Cell key={entry.name} fill={riskColors[entry.name]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: 10, border: '1px solid #E8E1D5', fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-2 text-[11px] font-bold text-ink-secondary">
                  {riskDistribution.map((entry) => (
                    <div key={entry.name} className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: riskColors[entry.name] }} />
                      <span>{entry.name}</span>
                      <span className="font-mono text-ink-primary">{entry.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Narrative Description */}
        <p className="text-xs sm:text-sm text-ink-secondary leading-relaxed font-normal">{pattern.description}</p>

        {/* Recommended HSE Intervention */}
        <div className="p-4 rounded-2.5xl bg-emerald-50/60 border border-emerald-200/80 space-y-1 shadow-spatial-xs">
          <div className="flex items-center gap-1.5 text-xs font-black text-emerald-950">
            <ShieldCheck className="w-4 h-4 text-emerald-700" />
            <span>Recommended HSE Intervention</span>
          </div>
          <p className="text-xs sm:text-sm text-emerald-900 leading-relaxed font-medium">
            {pattern.recommendedIntervention}
          </p>
        </div>

        {/* Expandable Report Drilldown */}
        {pattern.sampleReportIds && pattern.sampleReportIds.length > 0 && (
          <div className="pt-2 border-t border-surface-border/60">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full flex items-center justify-between text-xs font-extrabold text-ink-secondary hover:text-emerald-900 py-1 transition-colors cursor-pointer"
            >
              <span>Sample Associated Field Reports ({pattern.sampleReportIds.length})</span>
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {isExpanded && (
              <div className="mt-3 space-y-2 animate-in fade-in">
                {pattern.sampleReportIds.map((repId) => (
                  <div
                    key={repId}
                    onClick={() => navigate(`/reports/${repId}`)}
                    className="p-3 rounded-2xl bg-[#FAF7F2] hover:bg-white border border-surface-border/80 flex items-center justify-between text-xs cursor-pointer group transition-all shadow-spatial-xs hover:shadow-spatial-sm"
                  >
                    <div className="flex items-center gap-2 font-mono font-black text-ink-primary group-hover:text-emerald-950">
                      <span>#{repId}</span>
                    </div>
                    <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-800 group-hover:translate-x-0.5 transition-transform">
                      <span>Inspect Details</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
