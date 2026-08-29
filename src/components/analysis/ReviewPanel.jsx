import React, { useState } from 'react';
import {
  CheckCircle2,
  Edit3,
  XCircle,
  AlertOctagon,
  Clock,
  ShieldCheck,
  UserCheck,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { ReviewStatusBadge } from '../ui/RiskBadge';
import { ReclassifyModal } from './ReclassifyModal';
import { useAuth } from '../../context/AuthContext';
import { formatDateTime } from '../../utils/formatters';

export function ReviewPanel({ report, onUpdateReview, onCreateActionClick }) {
  const { currentUser } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState(null);

  if (!report) return null;

  const isPending = report.reviewStatus === 'PENDING';
  const isApproved = report.reviewStatus === 'APPROVED';

  const showNotification = (msg) => {
    setFeedbackMessage(msg);
    setTimeout(() => setFeedbackMessage(null), 3500);
  };

  const handleApprove = async () => {
    setIsUpdating(true);
    try {
      await onUpdateReview(report.id, {
        reviewStatus: 'APPROVED',
        reviewer: `${currentUser.name} (${currentUser.role})`,
      });
      showNotification('Classification validated & approved successfully');
    } catch (err) {
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleMarkNonSIF = async () => {
    setIsUpdating(true);
    try {
      await onUpdateReview(report.id, {
        sifPotential: 'NON-SIF',
        sifPrecursor: 'NO',
        reviewStatus: 'MODIFIED',
        reviewer: `${currentUser.name} (${currentUser.role})`,
        reviewNotes: 'Marked as Non-SIF by HSE Reviewer (Low energy exposure).',
      });
      showNotification('Report marked as Non-SIF');
    } catch (err) {
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleEscalate = async () => {
    setIsUpdating(true);
    try {
      await onUpdateReview(report.id, {
        reviewStatus: 'NEEDS CORRECTION',
        reviewer: `${currentUser.name} (${currentUser.role})`,
        urgencyScore: Math.min(100, (report.urgencyScore || 80) + 5),
      });
      if (onCreateActionClick) {
        onCreateActionClick();
      }
      showNotification('Report flagged for Immediate Investigation & CAPA');
    } catch (err) {
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <>
      <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
        <CardHeader action={<ReviewStatusBadge status={report.reviewStatus} size="sm" />}>
          <CardTitle subtitle="Human-in-the-Loop review & classification verification">
            HSE Review & Triage
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-4 p-5 sm:p-6">
          {/* Active Reviewer Status Info */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 text-xs shadow-spatial-xs">
            <div className="flex items-center gap-2.5">
              <UserCheck className="w-4 h-4 text-emerald-800" />
              <div>
                <span className="text-ink-muted">Assigned Reviewer: </span>
                <span className="font-extrabold text-ink-primary">
                  {report.reviewer || `${currentUser.name} (${currentUser.role})`}
                </span>
              </div>
            </div>

            {report.reviewedAt && (
              <div className="text-[11px] text-ink-muted">
                Last reviewed: <span className="font-mono font-bold">{formatDateTime(report.reviewedAt)}</span>
              </div>
            )}
          </div>

          {feedbackMessage && (
            <div className="p-3.5 bg-emerald-50 text-emerald-950 border border-emerald-200/80 rounded-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in shadow-spatial-xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
              <span>{feedbackMessage}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="pt-2 flex flex-wrap items-center gap-2.5">
            <Button
              variant="primary"
              size="sm"
              icon={CheckCircle2}
              onClick={handleApprove}
              isLoading={isUpdating}
              disabled={isApproved}
            >
              Approve Classification
            </Button>

            <Button
              variant="secondary"
              size="sm"
              icon={Edit3}
              onClick={() => setIsModalOpen(true)}
              disabled={isUpdating}
            >
              Modify Classification
            </Button>

            <Button
              variant="outline"
              size="sm"
              icon={XCircle}
              onClick={handleMarkNonSIF}
              disabled={isUpdating || report.sifPotential === 'NON-SIF'}
              className="text-ink-secondary hover:text-ink-primary"
            >
              Mark as Non-SIF
            </Button>

            <Button
              variant="danger"
              size="sm"
              icon={AlertOctagon}
              onClick={handleEscalate}
              disabled={isUpdating}
              className="ml-auto"
            >
              Escalate / Issue CAPA
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Modal for modifying classification */}
      <ReclassifyModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        report={report}
        onSave={(updatedData) => onUpdateReview(report.id, updatedData)}
      />
    </>
  );
}
