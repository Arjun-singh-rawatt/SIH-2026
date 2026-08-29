import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Users,
  ShieldAlert,
  AlertOctagon,
  ListTodo,
  Activity,
  Flame,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SIFPotentialBadge } from '../components/ui/RiskBadge';
import { ReportTable } from '../components/reports/ReportTable';
import { ProgressBar } from '../components/ui/ProgressBar';
import { facilityService } from '../services/facilityService';
import { formatNumber } from '../utils/formatters';

export function FacilityDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [facility, setFacility] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await facilityService.getFacilityById(id);
        setFacility(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (!facility) {
    return (
      <div className="p-12 text-center space-y-4">
        <h3 className="text-lg font-bold text-ink-primary">Facility Not Found</h3>
        <Button variant="secondary" size="sm" onClick={() => navigate('/facilities')}>
          Back to Facilities Directory
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title={facility.facilityName}
        subtitle={`${facility.type} · ${facility.region}`}
        breadcrumbs={[
          { label: 'Overview', path: '/dashboard' },
          { label: 'Facilities', path: '/facilities' },
          { label: facility.shortName },
        ]}
        badge={<SIFPotentialBadge potential={facility.riskLevel} size="md" />}
        actions={
          <Button
            variant="secondary"
            size="sm"
            icon={ArrowLeft}
            onClick={() => navigate('/facilities')}
          >
            Back to Directory
          </Button>
        }
      />

      {/* Facility KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-5">
        <Card className="p-5 sm:p-6 bg-white rounded-3.5xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
            Total Logged Reports
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-ink-primary font-mono">
              {formatNumber(facility.totalReports)}
            </span>
          </div>
        </Card>

        <Card className="p-5 sm:p-6 bg-amber-50/40 border-amber-200/80 rounded-3.5xl">
          <span className="text-[10px] font-black uppercase tracking-widest text-amber-950 block">
            SIF Precursor Density
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-amber-950 font-mono">
              {facility.sifDensity}%
            </span>
            <span className="text-[10px] text-amber-900 font-extrabold font-mono">
              ({facility.sifReports} SIF)
            </span>
          </div>
        </Card>

        <Card className="p-5 sm:p-6 bg-red-50/40 border-red-200/80 rounded-3.5xl">
          <span className="text-[10px] font-black uppercase tracking-widest text-red-950 block">
            High Urgency Cases
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-red-950 font-mono">
              {facility.highUrgencyCount}
            </span>
            <span className="text-[10px] text-red-800 font-extrabold bg-red-100/90 px-2 py-0.2 rounded-full shadow-spatial-xs">
              Priority Triage
            </span>
          </div>
        </Card>

        <Card className="p-5 sm:p-6 bg-white rounded-3.5xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
            Open Actions (CAPA)
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-ink-primary font-mono">
              {facility.openActions}
            </span>
            <span className="text-[10px] text-emerald-800 font-bold bg-emerald-50 px-2 py-0.2 rounded-full border border-emerald-200/60">
              In Progress
            </span>
          </div>
        </Card>
      </div>

      {/* Safety Intelligence Profile Card */}
      <Card className="p-6 sm:p-7 border-surface-border/80 rounded-3.5xl shadow-spatial">
        <CardTitle subtitle="Localized risk drivers and predominant precursor failure modes">
          Facility Risk Profile & Precursors
        </CardTitle>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5 pt-4 border-t border-surface-border/60">
          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-1">
              Dominant Precursor Category
            </span>
            <p className="text-sm font-extrabold text-ink-primary flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
              <span>{facility.topPrecursor}</span>
            </p>
          </div>

          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-1">
              Most Vulnerable Activity
            </span>
            <p className="text-sm font-extrabold text-ink-primary flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-800 shrink-0" />
              <span>{facility.topActivity}</span>
            </p>
          </div>

          <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-1">
              Primary Hazard Exposure
            </span>
            <p className="text-sm font-extrabold text-ink-primary flex items-center gap-2">
              <Flame className="w-4 h-4 text-red-600 shrink-0" />
              <span>{facility.primaryHazard}</span>
            </p>
          </div>
        </div>
      </Card>

      {/* Recent Field Reports from this Facility */}
      <div className="space-y-3 pt-2">
        <div>
          <h3 className="text-lg font-black text-ink-primary tracking-tight font-sans">
            Facility Safety Reports ({facility.recentReports?.length || 0})
          </h3>
          <p className="text-xs text-ink-muted">
            Live reports logged from {facility.facilityName}.
          </p>
        </div>

        <ReportTable
          reports={facility.recentReports || []}
          sortBy="createdAt"
          sortOrder="desc"
          onSort={() => {}}
          onResetFilters={() => {}}
        />
      </div>
    </div>
  );
}
