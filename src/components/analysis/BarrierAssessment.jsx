import React from 'react';
import { ShieldX, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { BarrierStatusBadge } from '../ui/RiskBadge';

export function BarrierAssessment({ report }) {
  if (!report) return null;

  const isFailed = report.barrierStatus === 'FAILED';

  return (
    <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
      <CardHeader
        action={<BarrierStatusBadge status={report.barrierStatus} size="sm" />}
      >
        <CardTitle subtitle="Critical safety barriers integrity and failure analysis">
          Barrier Assessment
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4 p-5 sm:p-6">
        {/* Failed Barrier Identifier */}
        <div className="p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 shadow-spatial-xs">
          <div className="flex items-center gap-2 mb-1.5 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
            <ShieldX className="w-3.5 h-3.5 text-red-600" />
            <span>Identified Barrier Defect / Failure Mode</span>
          </div>
          <p className="text-sm sm:text-base font-extrabold text-ink-primary">{report.failedBarrier}</p>
        </div>

        {/* Potential Worst-Case Consequence */}
        <div className="p-4 rounded-2.5xl bg-red-50/50 border border-red-200/80 shadow-spatial-xs">
          <div className="flex items-center gap-2 mb-1.5 text-[10px] font-black uppercase tracking-widest text-red-950">
            <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
            <span>Potential Fatal / Serious Injury Consequence</span>
          </div>
          <p className="text-xs sm:text-sm font-bold text-red-950 leading-relaxed">
            {report.potentialConsequence}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
