import React, { useState, useEffect } from 'react';
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
  Loader2,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Tabs } from '../components/ui/Tabs';
import { Button } from '../components/ui/Button';
import { SIFPotentialBadge, ReviewStatusBadge, UrgencyScoreBadge } from '../components/ui/RiskBadge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { formatDate } from '../utils/formatters';
import { reportService } from '../services/reportService';
import { useReportsContext } from '../context/ReportsContext';

export function ReviewQueue() {
  const navigate = useNavigate();
  const { lastUpdated } = useReportsContext();

  const [activeTab, setActiveTab] = useState('PENDING');
  const [queueItems, setQueueItems] = useState([]);
  const [summary, setSummary] = useState({
    pendingCount: 0,
    criticalCount: 0,
    lowConfidenceCount: 0,
    totalCount: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadQueueData() {
      setLoading(true);
      try {
        const [items, sum] = await Promise.all([
          reportService.getReviewQueue(activeTab, 1, 50),
          reportService.getReviewSummary(),
        ]);
        if (isMounted) {
          setQueueItems(items);
          setSummary(sum);
        }
      } catch (err) {
        console.error('Error fetching review queue from backend:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadQueueData();
    return () => {
      isMounted = false;
    };
  }, [activeTab, lastUpdated]);

  const tabs = [
    { id: 'PENDING', label: 'Pending Review', count: summary.pendingCount },
    { id: 'CRITICAL', label: 'High / Critical SIF', count: summary.criticalCount },
    { id: 'LOW_CONF', label: 'Model Review Required (<94% Conf)', count: summary.lowConfidenceCount },
    { id: 'ALL', label: 'All Reports', count: summary.totalCount },
  ];

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="Human-in-the-Loop Review Queue"
        subtitle="HSE safety professionals triage, validate, and sign off on AI-classified fatality precursors and barrier assessments."
        badge={
          <span className="px-3.5 py-1 rounded-full text-xs font-black bg-amber-100 text-amber-950 border border-amber-300 shadow-spatial-xs">
            {summary.pendingCount} Pending Sign-off
          </span>
        }
      />

      {/* Tabs Filter Bar */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
      </div>

      {/* Queue List Cards */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-16 text-center text-ink-muted bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-emerald-800 animate-spin" />
            <p className="text-xs font-bold text-ink-muted">Loading review queue items...</p>
          </div>
        ) : queueItems.length === 0 ? (
          <div className="p-12 text-center text-ink-muted bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
            <h3 className="text-base font-extrabold text-ink-primary">Queue Clear</h3>
            <p className="text-xs text-ink-muted mt-1">
              All safety reports in this category have been verified and approved.
            </p>
          </div>
        ) : (
          queueItems.map((report) => {
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
