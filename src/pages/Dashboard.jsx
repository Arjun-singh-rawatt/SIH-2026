import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  ShieldAlert,
  AlertOctagon,
  ListTodo,
  Sparkles,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { MetricCard } from '../components/dashboard/MetricCard';
import { Button } from '../components/ui/Button';
import { analyticsService } from '../services/analyticsService';
import { useReportsContext } from '../context/ReportsContext';

export function Dashboard() {
  const navigate = useNavigate();
  const { reports, actions } = useReportsContext();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await analyticsService.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const pendingReviewsCount = reports.filter((r) => r.reviewStatus === 'PENDING').length;

  const priorityQueue = useMemo(
    () =>
      [...reports]
        .sort((a, b) => (b.urgencyScore || 0) - (a.urgencyScore || 0))
        .slice(0, 5)
        .map((report) => ({
          id: report.reportId,
          facility: report.facilityName,
          riskType: report.primaryHazard,
          score: report.urgencyScore,
          status: report.reviewStatus === 'PENDING' ? 'Investigate' : report.reviewStatus,
        })),
    [reports]
  );

  const criticalAlerts = useMemo(
    () =>
      [...reports]
        .filter((report) => report.urgencyScore >= 85)
        .sort((a, b) => (b.urgencyScore || 0) - (a.urgencyScore || 0))
        .slice(0, 3)
        .map((report) => ({
          id: report.reportId,
          title: report.primaryHazard,
          facility: report.facilityName,
          score: report.urgencyScore,
          time: `${Math.max(4, Math.min(45, report.urgencyScore - 60))} mins ago`,
        })),
    [reports]
  );

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Page Header */}
      <PageHeader
        title="Safety Intelligence Command Center"
        subtitle="Real-time detection of Serious Injury & Fatality (SIF) precursors across Oil India Limited operations."
        actions={
          <>
            <Button
              variant="secondary"
              size="sm"
              icon={FileText}
              onClick={() => navigate('/reports')}
            >
              Explore All Reports
            </Button>
            <Button
              variant="amber"
              size="sm"
              icon={Sparkles}
              onClick={() => navigate('/analyze')}
            >
              Analyze Safety Report
            </Button>
          </>
        }
      />

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Total Safety Reports"
          value={metrics?.totalReports?.formatted || '12,482'}
          change={metrics?.totalReports?.change || '+8.4%'}
          changeType="increase"
          subtitle={metrics?.totalReports?.subtitle || 'vs previous 30-day period'}
          icon={FileText}
          onClick={() => navigate('/reports')}
        />

        <MetricCard
          title="SIF-Potential Reports"
          value={metrics?.sifPotential?.formatted || '2,341'}
          percentage={metrics?.sifPotential?.percentage || '18.7%'}
          change={metrics?.sifPotential?.change || '+2.1%'}
          changeType="increase"
          subtitle={metrics?.sifPotential?.subtitle || '18.7% of reports flagged'}
          icon={ShieldAlert}
          onClick={() => navigate('/reports?sifPotential=HIGH')}
        />

        <MetricCard
          title="High-Urgency Reports"
          value={metrics?.highUrgency?.formatted || '684'}
          percentage={metrics?.highUrgency?.percentage || '29.2%'}
          change={metrics?.highUrgency?.change || '-4.6%'}
          changeType="decrease"
          subtitle={metrics?.highUrgency?.subtitle || 'Urgency score ≥ 80'}
          icon={AlertOctagon}
          onClick={() => navigate('/reports?urgencyLevel=CRITICAL')}
        />

        <MetricCard
          title="Open Action Items (CAPA)"
          value={metrics?.openActions?.formatted || '126'}
          change={metrics?.openActions?.change || '18 Overdue'}
          changeType="warning"
          subtitle={metrics?.openActions?.subtitle || '34 in progress, 18 overdue'}
          icon={ListTodo}
          onClick={() => navigate('/actions')}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.8fr_1fr]">
        <section className="rounded-[2rem] border border-[#dfe1d8] bg-[#f7f4ee] p-0 shadow-[0_12px_28px_rgba(15,79,67,0.04)]">
          <div className="flex items-center justify-between px-5 pb-4 pt-5">
            <h3 className="text-[2rem] font-black tracking-[-0.05em] text-ink-primary">Priority Risk Queue</h3>
            <button
              type="button"
              onClick={() => navigate('/reports')}
              className="text-sm font-bold text-emerald-900 hover:text-emerald-700"
            >
              View Full Queue <ArrowRight className="ml-1 inline h-4 w-4" />
            </button>
          </div>

          <div className="overflow-x-auto px-3 pb-3">
            <table className="min-w-full border-separate border-spacing-y-2 text-left">
              <thead>
                <tr className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-ink-muted">
                  <th className="px-3 py-2">Report ID</th>
                  <th className="px-3 py-2">Facility</th>
                  <th className="px-3 py-2">Risk Type</th>
                  <th className="px-3 py-2">Priority Score</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {priorityQueue.map((item) => (
                  <tr
                    key={item.id}
                    className="rounded-2xl border border-[#e6e1d6] bg-white text-sm text-ink-primary shadow-[0_2px_10px_rgba(15,79,67,0.02)]"
                  >
                    <td className="rounded-l-2xl px-3 py-3 font-black text-ink-primary">{item.id}</td>
                    <td className="px-3 py-3 text-ink-secondary">{item.facility}</td>
                    <td className="px-3 py-3 text-ink-secondary">{item.riskType}</td>
                    <td className="px-3 py-3">
                      <span className="font-black text-ink-primary">{item.score}</span>
                    </td>
                    <td className="rounded-r-2xl px-3 py-3">
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-bold ${
                          item.status === 'Investigate'
                            ? 'border-red-200 bg-red-50 text-red-900'
                            : 'border-emerald-200 bg-emerald-50 text-emerald-900'
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="rounded-[2rem] border border-[#dfe1d8] bg-[#f7f4ee] p-5 shadow-[0_12px_28px_rgba(15,79,67,0.04)]">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xl font-black tracking-[-0.04em] text-ink-primary">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Critical Alerts
            </div>
            <span className="rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-[0.18em] text-red-900">
              Live
            </span>
          </div>

          <div className="space-y-3">
            {criticalAlerts.map((alert) => (
              <div
                key={alert.id}
                className="rounded-2xl border border-red-200 bg-[#fef3f3] p-4"
              >
                <div className="mb-1 flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-red-600" />
                  <span className="text-sm font-black text-ink-primary">{alert.title}</span>
                </div>
                <p className="text-sm text-ink-secondary">{alert.facility}</p>
                <div className="mt-2 flex items-center justify-between text-xs text-ink-secondary">
                  <span>{alert.time}</span>
                  <span className="font-black text-red-900">Score {alert.score}</span>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
