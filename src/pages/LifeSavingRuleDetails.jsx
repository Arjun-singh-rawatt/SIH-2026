import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Building2,
  Activity,
  FileText,
  ShieldAlert,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SIFPotentialBadge } from '../components/ui/RiskBadge';
import { ReportTable } from '../components/reports/ReportTable';
import { lifeSavingRuleService } from '../services/lifeSavingRuleService';
import { formatNumber } from '../utils/formatters';

export function LifeSavingRuleDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ruleData, setRuleData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await lifeSavingRuleService.getRuleById(id);
        setRuleData(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (!ruleData) {
    return (
      <div className="p-12 text-center space-y-4">
        <h3 className="text-lg font-bold text-ink-primary">Life-Saving Rule Not Found</h3>
        <Button variant="secondary" size="sm" onClick={() => navigate('/life-saving-rules')}>
          Back to Life-Saving Rules Directory
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title={ruleData.name}
        subtitle={ruleData.shortDescription}
        breadcrumbs={[
          { label: 'Overview', path: '/dashboard' },
          { label: 'Life-Saving Rules', path: '/life-saving-rules' },
          { label: ruleData.name },
        ]}
        badge={<SIFPotentialBadge potential={ruleData.riskLevel} size="md" />}
        actions={
          <Button
            variant="secondary"
            size="sm"
            icon={ArrowLeft}
            onClick={() => navigate('/life-saving-rules')}
          >
            Back to Directory
          </Button>
        }
      />

      {/* Overview Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">
        <div className="lg:col-span-8 space-y-6">
          <Card className="p-6 sm:p-7 border-surface-border/80 rounded-3.5xl shadow-spatial">
            <h3 className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-2.5">
              Rule Scope & Full Standard Description
            </h3>
            <p className="text-sm sm:text-base text-ink-primary leading-relaxed font-normal">
              {ruleData.fullDescription}
            </p>

            <div className="mt-6 pt-5 border-t border-surface-border/60">
              <h4 className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-3">
                Mandatory Operational Safeguards & Protocols
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {ruleData.keyRequirements?.map((req, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-2xl bg-[#FAF7F2] border border-surface-border/80 flex items-start gap-2.5 text-xs text-ink-primary shadow-spatial-xs"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-800 shrink-0 mt-0.5" />
                    <span className="font-medium leading-relaxed">{req}</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>

        {/* Stats Column */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="p-6 border-surface-border/80 rounded-3.5xl shadow-spatial space-y-4">
            <h4 className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              Rule Safety Intelligence Metrics
            </h4>

            <div className="space-y-3">
              <div className="p-3.5 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 flex justify-between items-center shadow-spatial-xs">
                <span className="text-xs text-ink-muted font-medium">Total Associated Reports:</span>
                <span className="text-sm font-mono font-black text-ink-primary">
                  {formatNumber(ruleData.totalReports)}
                </span>
              </div>

              <div className="p-3.5 rounded-2.5xl bg-amber-50/60 border border-amber-200/90 flex justify-between items-center text-amber-950 shadow-spatial-xs">
                <span className="text-xs font-black">SIF Precursor Density:</span>
                <span className="text-sm font-mono font-black">
                  {ruleData.sifPercentage}% ({ruleData.sifReports})
                </span>
              </div>

              <div className="p-3.5 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
                <span className="text-[10px] text-ink-muted uppercase font-extrabold tracking-widest block mb-1">
                  Most Impacted Operational Facility
                </span>
                <span className="text-xs font-bold text-ink-primary block">{ruleData.topFacility}</span>
              </div>

              <div className="p-3.5 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
                <span className="text-[10px] text-ink-muted uppercase font-extrabold tracking-widest block mb-1">
                  Dominant Associated Activity
                </span>
                <span className="text-xs font-bold text-ink-primary block">{ruleData.topActivity}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Associated Reports Table */}
      <div className="space-y-3 pt-2">
        <div>
          <h3 className="text-lg font-black text-ink-primary tracking-tight font-sans">
            Associated Field Reports ({ruleData.associatedReports?.length || 0})
          </h3>
          <p className="text-xs text-ink-muted">
            Recent observations and incidents classified under {ruleData.name}.
          </p>
        </div>

        <ReportTable
          reports={ruleData.associatedReports || []}
          sortBy="createdAt"
          sortOrder="desc"
          onSort={() => {}}
          onResetFilters={() => {}}
        />
      </div>
    </div>
  );
}
