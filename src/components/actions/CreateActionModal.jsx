import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { mockUsers } from '../../data/mockUsers';
import { mockFacilities } from '../../data/mockFacilities';

export function CreateActionModal({ isOpen, onClose, defaultReport, onSave }) {
  const [reportId, setReportId] = useState(defaultReport?.reportId || '');
  const [reportTitle, setReportTitle] = useState(defaultReport?.primaryHazard || 'Corrective Safety Action');
  const [assignedTo, setAssignedTo] = useState(mockUsers[0].userId);
  const [facilityId, setFacilityId] = useState(defaultReport?.facilityId || mockFacilities[0].facilityId);
  const [actionType, setActionType] = useState('CAPA Enforcement & Barrier Re-instatement');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('HIGH');
  const [dueDate, setDueDate] = useState(
    new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const user = mockUsers.find((u) => u.userId === assignedTo) || mockUsers[0];
    const fac = mockFacilities.find((f) => f.facilityId === facilityId) || mockFacilities[0];

    try {
      await onSave({
        reportId: reportId || 'SIF-GENERAL',
        reportTitle: reportTitle || 'General Operational Safety Action',
        assignedTo: user.userId,
        assigneeName: user.name,
        assigneeRole: user.role,
        facilityId: fac.facilityId,
        facilityName: fac.facilityName,
        actionType,
        description,
        priority,
        dueDate: new Date(dueDate).toISOString(),
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
      title="Create CAPA Safety Action Item"
      subtitle="Assign corrective action and risk mitigation owner"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Linked Report ID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
              Linked Report ID
            </label>
            <input
              type="text"
              value={reportId}
              onChange={(e) => setReportId(e.target.value)}
              placeholder="e.g. SIF-2026-00124"
              className="sift-input text-xs font-mono"
            />
          </div>

          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
              Action Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="sift-select w-full font-bold"
            >
              <option value="CRITICAL">CRITICAL (Immediate 24-48 hr resolution)</option>
              <option value="HIGH">HIGH (1-Week target)</option>
              <option value="MEDIUM">MEDIUM (Standard tracking)</option>
              <option value="LOW">LOW</option>
            </select>
          </div>
        </div>

        {/* Action Type */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            Action Type & Category
          </label>
          <input
            type="text"
            value={actionType}
            onChange={(e) => setActionType(e.target.value)}
            placeholder="e.g. Isolation Audit, LOTO Enforcement, Equipment Overhaul"
            className="sift-input text-xs"
            required
          />
        </div>

        {/* Assigned Owner & Facility */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
              Assigned Safety Owner
            </label>
            <select
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
              className="sift-select w-full font-bold"
            >
              {mockUsers.map((u) => (
                <option key={u.userId} value={u.userId}>
                  {u.name} ({u.role})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
              Operational Facility
            </label>
            <select
              value={facilityId}
              onChange={(e) => setFacilityId(e.target.value)}
              className="sift-select w-full font-medium"
            >
              {mockFacilities.map((f) => (
                <option key={f.facilityId} value={f.facilityId}>
                  {f.shortName}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Due Date */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            Completion Due Date
          </label>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="sift-input text-xs"
            required
          />
        </div>

        {/* Detailed Scope / Description */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-secondary mb-1">
            Action Description & Required Deliverables
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detail required engineering controls, audits, equipment replacements, or training..."
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
            Assign Action Item
          </Button>
        </div>
      </form>
    </Modal>
  );
}
