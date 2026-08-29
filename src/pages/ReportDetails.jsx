import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  User,
  ShieldAlert,
  Sparkles,
  ListTodo,
  Plus,
  AlertOctagon,
  CheckCircle2,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SIFPotentialBadge, ReviewStatusBadge, UrgencyScoreBadge } from '../components/ui/RiskBadge';
import { EvidencePhrase } from '../components/analysis/EvidencePhrase';
import { AIClassificationCard } from '../components/analysis/AIClassificationCard';
import { BarrierAssessment } from '../components/analysis/BarrierAssessment';
import { ReviewPanel } from '../components/analysis/ReviewPanel';
import { ActionTable } from '../components/actions/ActionTable';
import { CreateActionModal } from '../components/actions/CreateActionModal';
import { formatDateTime } from '../utils/formatters';
import { useReportsContext } from '../context/ReportsContext';

export function ReportDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { reports, actions, updateReportReview, updateActionStatus, addAction } = useReportsContext();

  const [report, setReport] = useState(null);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);

  useEffect(() => {
    const found = reports.find(
      (r) => r.id === id || r.reportId.toUpperCase() === id?.toUpperCase()
    );
    if (found) {
      setReport(found);
    }
  }, [id, reports]);

  if (!report) {
    return (
      <div className="p-12 text-center space-y-4">
        <h3 className="text-lg font-bold text-ink-primary">Report Not Found</h3>
        <p className="text-xs text-ink-muted">The requested safety report ID does not exist in the database.</p>
        <Button variant="secondary" size="sm" onClick={() => navigate('/reports')}>
          Return to Reports Explorer
        </Button>
      </div>
    );
  }

  // Linked actions for this report
  const linkedActions = actions.filter(
    (a) => a.reportId.toUpperCase() === report.reportId.toUpperCase()
  );

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Page Header & Breadcrumb */}
      <PageHeader
        title={`Safety Report #${report.reportId}`}
        subtitle={`Submitted from ${report.facilityName} (${report.location})`}
        breadcrumbs={[
          { label: 'Overview', path: '/dashboard' },
          { label: 'All Reports', path: '/reports' },
          { label: report.reportId },
        ]}
        badge={
          <div className="flex items-center gap-2">
            <SIFPotentialBadge potential={report.sifPotential} size="md" />
            <ReviewStatusBadge status={report.reviewStatus} size="md" />
          </div>
        }
        actions={
          <Button
            variant="secondary"
            size="sm"
            icon={ArrowLeft}
            onClick={() => navigate('/reports')}
          >
            Back to Reports
          </Button>
        }
      />

      {/* Metadata Banner */}
      <div className="bg-white border border-surface-border/80 rounded-3.5xl p-5 sm:p-6 shadow-spatial grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#FAF7F2] border border-surface-border/80 flex items-center justify-center text-ink-secondary shrink-0 shadow-spatial-xs">
            <Building2 className="w-4 h-4 text-emerald-800" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-extrabold tracking-widest text-ink-muted block">Facility & Region</span>
            <span className="font-extrabold text-ink-primary block truncate">{report.facilityName}</span>
            <span className="text-[11px] text-ink-muted">{report.region}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#FAF7F2] border border-surface-border/80 flex items-center justify-center text-ink-secondary shrink-0 shadow-spatial-xs">
            <MapPin className="w-4 h-4 text-emerald-800" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-extrabold tracking-widest text-ink-muted block">Specific Location</span>
            <span className="font-extrabold text-ink-primary block truncate">{report.location}</span>
            <span className="text-[11px] text-ink-muted">Type: {report.reportType}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#FAF7F2] border border-surface-border/80 flex items-center justify-center text-ink-secondary shrink-0 shadow-spatial-xs">
            <User className="w-4 h-4 text-emerald-800" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-extrabold tracking-widest text-ink-muted block">Reported By</span>
            <span className="font-extrabold text-ink-primary block truncate">{report.reporterName}</span>
            <span className="text-[11px] text-ink-muted font-mono">{report.reporterId}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#FAF7F2] border border-surface-border/80 flex items-center justify-center text-ink-secondary shrink-0 shadow-spatial-xs">
            <Calendar className="w-4 h-4 text-emerald-800" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-extrabold tracking-widest text-ink-muted block">Timestamp</span>
            <span className="font-extrabold text-ink-primary block">{formatDateTime(report.createdAt)}</span>
            <span className="text-[11px] text-ink-muted">Language: {report.language}</span>
          </div>
        </div>
      </div>

      {/* Main Dual-Pane Section: Original Narrative vs AI Safety Assessment */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">
        {/* Left Column: Human Narrative & Reviewer Action Panel */}
        <div className="lg:col-span-6 space-y-6">
          {/* Original Human Report with Highlighting */}
          <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
            <CardHeader
              action={
                <span className="text-[10px] font-extrabold text-ink-muted bg-[#FAF7F2] px-3 py-1 rounded-full border border-surface-border uppercase tracking-widest">
                  Original Field Text
                </span>
              }
            >
              <CardTitle subtitle="Exact text logged by field operator with highlighted AI evidence phrases">
                Field Observation Narrative
              </CardTitle>
            </CardHeader>

            <CardContent className="p-5 sm:p-6 space-y-4">
              <EvidencePhrase
                rawText={report.rawReportText}
                evidencePhrases={report.evidencePhrases || [report.evidencePhrase]}
              />

              <div className="p-4 rounded-2.5xl bg-amber-50/50 border border-amber-200/80 flex items-start gap-3 text-xs text-amber-950 shadow-spatial-xs">
                <Sparkles className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <strong className="block font-black text-[11px] uppercase tracking-wider">Extracted Evidence Snippets:</strong>
                  <p className="text-xs text-amber-950 mt-1 leading-relaxed font-mono font-bold">
                    "{report.evidencePhrase}"
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Barrier Failure & Consequences */}
          <BarrierAssessment report={report} />

          {/* HSE Review & Validation Action Panel */}
          <ReviewPanel
            report={report}
            onUpdateReview={updateReportReview}
            onCreateActionClick={() => setIsActionModalOpen(true)}
          />
        </div>

        {/* Right Column: AI Risk Intelligence & Assessment */}
        <div className="lg:col-span-6 space-y-6">
          <AIClassificationCard report={report} />
        </div>
      </div>

      {/* Linked CAPA Action Items Section */}
      <div className="pt-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-extrabold text-ink-primary tracking-tight font-sans">
              Linked Corrective & Preventative Actions (CAPA)
            </h3>
            <p className="text-xs text-ink-muted">
              Remediation tasks assigned to eliminate recurring precursor hazards for this report.
            </p>
          </div>

          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setIsActionModalOpen(true)}
          >
            Assign Action Item
          </Button>
        </div>

        <ActionTable
          actions={linkedActions}
          onStatusChange={updateActionStatus}
        />
      </div>

      {/* Action Creation Modal */}
      <CreateActionModal
        isOpen={isActionModalOpen}
        onClose={() => setIsActionModalOpen(false)}
        defaultReport={report}
        onSave={addAction}
      />
    </div>
  );
}
