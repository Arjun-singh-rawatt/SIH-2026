import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { mockLifeSavingRules } from '../../data/mockLifeSavingRules';

export function ReclassifyModal({ isOpen, onClose, report, onSave }) {
  const [sifPotential, setSifPotential] = useState(report?.sifPotential || 'HIGH');
  const [lifeSavingRule, setLifeSavingRule] = useState(report?.lifeSavingRule || 'Energy Isolation');
  const [failedBarrier, setFailedBarrier] = useState(report?.failedBarrier || '');
  const [barrierStatus, setBarrierStatus] = useState(report?.barrierStatus || 'FAILED');
  const [reviewNotes, setReviewNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSave({
        sifPotential,
        sifPrecursor: sifPotential === 'NON-SIF' ? 'NO' : 'YES',
        lifeSavingRule,
        failedBarrier,
        barrierStatus,
        reviewStatus: 'MODIFIED',
        reviewNotes,
      });
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Modify AI Safety Classification"
      subtitle={`Overriding model classification for Report #${report?.reportId}`}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* SIF Potential */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            SIF Potential Classification
          </label>
          <select
            value={sifPotential}
            onChange={(e) => setSifPotential(e.target.value)}
            className="sift-select w-full font-bold"
          >
            <option value="CRITICAL">CRITICAL SIF (Fatality Precursor Present)</option>
            <option value="HIGH">HIGH SIF Potential</option>
            <option value="MEDIUM">MEDIUM SIF Potential</option>
            <option value="LOW">LOW SIF Potential</option>
            <option value="NON-SIF">NON-SIF (Low Energy Observation)</option>
          </select>
        </div>

        {/* IOGP Life-Saving Rule */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            IOGP Life-Saving Rule
          </label>
          <select
            value={lifeSavingRule}
            onChange={(e) => setLifeSavingRule(e.target.value)}
            className="sift-select w-full font-bold"
          >
            {mockLifeSavingRules.map((lsr) => (
              <option key={lsr.id} value={lsr.name}>
                {lsr.name}
              </option>
            ))}
          </select>
        </div>

        {/* Failed Barrier */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            Safety Barrier Assessment
          </label>
          <input
            type="text"
            value={failedBarrier}
            onChange={(e) => setFailedBarrier(e.target.value)}
            placeholder="e.g. Double Block & Bleed Isolation Verification"
            className="sift-input text-xs"
            required
          />
        </div>

        {/* Barrier Status */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            Barrier Integrity Status
          </label>
          <select
            value={barrierStatus}
            onChange={(e) => setBarrierStatus(e.target.value)}
            className="sift-select w-full font-bold"
          >
            <option value="FAILED">FAILED (Barrier Missing or Broken)</option>
            <option value="WEAK">WEAK / DEGRADED (Partial Protection Only)</option>
            <option value="EFFECTIVE">EFFECTIVE (Barrier Functioned As Designed)</option>
          </select>
        </div>

        {/* HSE Justification Notes */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            HSE Expert Justification Notes
          </label>
          <textarea
            rows={3}
            value={reviewNotes}
            onChange={(e) => setReviewNotes(e.target.value)}
            placeholder="Document reason for reclassification (e.g. verified secondary DBB valve was present)..."
            className="sift-input text-xs resize-none"
            required
          />
        </div>

        {/* Action Buttons */}
        <div className="pt-4 border-t border-surface-border/60 flex items-center justify-end gap-3">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
            Save Classification Override
          </Button>
        </div>
      </form>
    </Modal>
  );
}
