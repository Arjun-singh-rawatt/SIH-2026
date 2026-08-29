import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckSquare,
  AlertTriangle,
  Flame,
  Clock,
  Sparkles,
  ChevronRight,
  ShieldCheck,
  CheckCircle2,
  Filter,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Tabs } from '../components/ui/Tabs';
import { Button } from '../components/ui/Button';
import { SIFPotentialBadge, ReviewStatusBadge, UrgencyScoreBadge } from '../components/ui/RiskBadge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { formatDate } from '../utils/formatters';
import { useReportsContext } from '../context/ReportsContext';

export function ReviewQueue() {
  const navigate = useNavigate();
  const { reports, updateReportReview } = useReportsContext();

  const [activeTab, setActiveTab] = useState('PENDING');

  const pendingList = reports.filter((r) => r.reviewStatus === 'PENDING');
  const criticalList = reports.filter((r) => r.sifPotential === 'CRITICAL' || r.sifPotential === 'HIGH');
  const lowConfidenceList = reports.filter((r) => (r.confidence || 0) < 94);
  const reviewedList = reports.filter((r) => r.reviewStatus === 'APPROVED' || r.reviewStatus === 'MODIFIED');

  const tabs = [
    { id: 'PENDING', label: 'Pending Review', count: pendingList.length },
    { id: 'CRITICAL', label: 'High / Critical SIF', count: criticalList.length },
    { id: 'LOW_CONF', label: 'Model Review Required (<94% Conf)', count: lowConfidenceList.length },
    { id: 'ALL', label: 'All Reports', count: reports.length },
  ];

  let displayReports = reports;
  if (activeTab === 'PENDING') {
    displayReports = pendingList;
  } else if (activeTab === 'CRITICAL') {
    displayReports = criticalList;
  } else if (activeTab === 'LOW_CONF') {
    displayReports = lowConfidenceList;
  }

  // Sort by urgency descending
  displayReports.sort((a, b) => b.urgencyScore - a.urgencyScore);

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="Human-in-the-Loop Review Queue"
        subtitle="HSE safety professionals triage, validate, and sign off on AI-classified fatality precursors and barrier assessments."
        badge={
          <span className="px-3.5 py-1 rounded-full text-xs font-black bg-amber-100 text-amber-950 border border-amber-300 shadow-spatial-xs">
            {pendingList.length} Pending Sign-off
          </span>
        }
      />

      {/* Tabs Filter Bar */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
      </div>

      {/* Queue List Cards */}
      <div className="space-y-4">
        {displayReports.length === 0 ? (
          <div className="p-12 text-center text-ink-muted bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
            <h3 className="text-base font-extrabold text-ink-primary">Queue Clear</h3>
            <p className="text-xs text-ink-muted mt-1">
              All safety reports in this category have been verified and approved.
            </p>
          </div>
        ) : (
          displayReports.map((report) => {
            const isPending = report.reviewStatus === 'PENDING';
            return (
              <div
                key={report.id}
                onClick={() => navigate(`/reports/${report.id}`)}
                className={`p-5 sm:p-6 rounded-3.5xl border transition-all duration-200 cursor-pointer group bg-white shadow-spatial hover:shadow-spatial-lg hover:-translate-y-0.5 ${
                  isPending
                    ? 'border-amber-200/90 hover:border-amber-300'
                    : 'border-surface-border/80 hover:border-surface-border'
                }`}
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  {/* Left info */}
                  <div className="space-y-2.5 flex-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className="font-mono font-black text-ink-primary group-hover:text-emerald-950 text-xs">
                        #{report.reportId}
                      </span>
                      <SIFPotentialBadge potential={report.sifPotential} size="xs" />
                      <UrgencyScoreBadge score={report.urgencyScore} size="xs" />
                      <ReviewStatusBadge status={report.reviewStatus} size="xs" />
                      <span className="text-[11px] text-ink-muted">· {formatDate(report.createdAt)}</span>
                    </div>

                    <div>
                      <h4 className="text-sm sm:text-base font-black text-ink-primary group-hover:text-emerald-950 transition-colors font-sans">
                        {report.primaryHazard}
                      </h4>
                      <p className="text-xs text-ink-muted line-clamp-2 mt-1 leading-relaxed font-sans">
                        "{report.rawReportText}"
                      </p>
                    </div>

                    <div className="flex items-center gap-4 text-[11px] text-ink-secondary flex-wrap pt-1">
                      <span><strong>Facility:</strong> {report.facilityName}</span>
                      <span><strong>Activity:</strong> {report.activity}</span>
                      <span><strong>Life-Saving Rule:</strong> {report.lifeSavingRule}</span>
                    </div>
                  </div>

                  {/* Right Action & Confidence */}
                  <div className="flex sm:flex-col items-end justify-between gap-3 shrink-0 border-t sm:border-t-0 pt-3 sm:pt-0 border-surface-border/60">
                    <div className="text-right">
                      <span className="text-[10px] text-ink-muted uppercase font-extrabold tracking-widest block">
                        AI Confidence
                      </span>
                      <span className="text-xs font-mono font-black text-emerald-950">
                        {report.confidence}%
                      </span>
                    </div>

                    <Button
                      variant={isPending ? 'amber' : 'secondary'}
                      size="sm"
                      iconRight={ChevronRight}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/reports/${report.id}`);
                      }}
                      className="font-black"
                    >
                      {isPending ? 'Triage & Validate' : 'Inspect Report'}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
