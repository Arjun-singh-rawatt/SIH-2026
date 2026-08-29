import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  ShieldAlert,
  AlertOctagon,
  ListTodo,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Download,
  Filter,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { MetricCard } from '../components/dashboard/MetricCard';
import { RiskTrendChart } from '../components/dashboard/RiskTrendChart';
import { PrecursorChart } from '../components/dashboard/PrecursorChart';
import { FacilityRiskTable } from '../components/dashboard/FacilityRiskTable';
import { PriorityAttention } from '../components/dashboard/PriorityAttention';
import { BarrierFailures } from '../components/dashboard/BarrierFailures';
import { ActivityRiskChart } from '../components/dashboard/ActivityRiskChart';
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

      {/* Priority Attention Alert Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-3">
          <PriorityAttention />
        </div>
      </div>

      {/* Primary Analytics Section: SIF Trend & SIF Precursor Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <RiskTrendChart />
        </div>
        <div className="lg:col-span-5">
          <PrecursorChart />
        </div>
      </div>

      {/* Secondary Analytics Section: Facility SIF Density & High-Risk Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <FacilityRiskTable />
        </div>
        <div className="lg:col-span-5">
          <ActivityRiskChart />
        </div>
      </div>

      {/* Tertiary Analytics Section: Barrier Failures & Triage Trigger */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <BarrierFailures />
        </div>

        {/* Human Review Triage Callout Card */}
        <div className="lg:col-span-6 flex flex-col justify-between p-6 sm:p-7 rounded-3.5xl bg-gradient-to-br from-[#065F46] via-[#044E3B] to-[#022C22] text-white border border-emerald-600/30 shadow-[0_18px_38px_rgba(4,78,59,0.25)]">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-black uppercase tracking-widest text-emerald-200">
                Human-In-The-Loop Triage
              </span>
              <span className="text-xs font-mono font-extrabold px-3 py-0.5 rounded-full bg-white/20 text-white border border-white/25 shadow-spatial-xs">
                {pendingReviewsCount} Pending Sign-off
              </span>
            </div>
            <h3 className="text-lg sm:text-xl font-black tracking-tight text-white font-sans">
              High-Urgency Reports Requiring HSE Validation
            </h3>
            <p className="text-xs sm:text-sm text-emerald-100/90 mt-2 leading-relaxed font-normal">
              AI NLP algorithms have flagged potential fatality precursors in recent field observations. HSE managers must validate barrier classifications and issue preventive action items.
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-emerald-500/30 flex items-center justify-between">
            <span className="text-xs text-emerald-200/80 font-medium">
              DEKRA SIF Precursor Protocol
            </span>
            <Button
              variant="secondary"
              size="sm"
              iconRight={ArrowRight}
              onClick={() => navigate('/review')}
              className="bg-white text-emerald-950 hover:bg-[#FAF7F2] border-white shadow-spatial font-extrabold"
            >
              Open Review Queue ({pendingReviewsCount})
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
