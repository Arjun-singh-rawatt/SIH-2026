import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Sparkles,
  ChevronRight as ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import { SIFPotentialBadge, ReviewStatusBadge, UrgencyScoreBadge } from '../ui/RiskBadge';
import { formatDate } from '../../utils/formatters';
import { EmptyState } from '../ui/EmptyState';

export function ReportTable({
  reports,
  sortBy,
  sortOrder,
  onSort,
  onResetFilters,
}) {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const totalPages = Math.ceil(reports.length / pageSize) || 1;
  const paginatedReports = reports.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const handleSortClick = (field) => {
    onSort(field);
    setCurrentPage(1);
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) {
      return <ArrowUpDown className="w-3 h-3 text-ink-muted/50" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="w-3 h-3 text-emerald-900" />
    ) : (
      <ArrowDown className="w-3 h-3 text-emerald-900" />
    );
  };

  if (reports.length === 0) {
    return (
      <EmptyState
        title="No matching safety reports found"
        description="No reports match your current filter selection. Try clearing some filters to explore other reports."
        actionLabel="Reset All Filters"
        onAction={onResetFilters}
      />
    );
  }

  return (
    <div className="bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial overflow-hidden flex flex-col justify-between">
      {/* Table responsive viewport */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-surface-border/60 bg-[#FAF7F2]/70 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted select-none">
              <th
                onClick={() => handleSortClick('reportId')}
                className="py-4 px-5 cursor-pointer hover:text-ink-primary transition-colors"
              >
                <div className="flex items-center gap-1.5">
                  <span>Report ID</span>
                  {getSortIcon('reportId')}
                </div>
              </th>

              <th
                onClick={() => handleSortClick('createdAt')}
                className="py-4 px-3 cursor-pointer hover:text-ink-primary transition-colors"
              >
                <div className="flex items-center gap-1.5">
                  <span>Date</span>
                  {getSortIcon('createdAt')}
                </div>
              </th>

              <th className="py-4 px-3">Facility & Location</th>
              <th className="py-4 px-3">Type</th>
              <th className="py-4 px-3">Activity</th>
              <th className="py-4 px-3">Primary Hazard</th>
              <th className="py-4 px-3 text-center">SIF Potential</th>

              <th
                onClick={() => handleSortClick('urgencyScore')}
                className="py-4 px-3 cursor-pointer hover:text-ink-primary transition-colors text-center"
              >
                <div className="flex items-center justify-center gap-1.5">
                  <span>Urgency</span>
                  {getSortIcon('urgencyScore')}
                </div>
              </th>

              <th className="py-4 px-3">Life-Saving Rule</th>
              <th className="py-4 px-5 text-center">Review Status</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-surface-border/40">
            {paginatedReports.map((report) => {
              return (
                <tr
                  key={report.id}
                  onClick={() => navigate(`/reports/${report.id}`)}
                  className="hover:bg-[#FAF7F2] cursor-pointer transition-colors group"
                >
                  {/* Report ID */}
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-extrabold text-ink-primary group-hover:text-emerald-900 transition-colors">
                        {report.reportId}
                      </span>
                    </div>
                  </td>

                  {/* Date */}
                  <td className="py-4 px-3 text-ink-muted whitespace-nowrap text-[11px] font-medium">
                    {formatDate(report.createdAt)}
                  </td>

                  {/* Facility & Location */}
                  <td className="py-4 px-3 max-w-[200px]">
                    <div className="font-bold text-ink-primary truncate text-xs">
                      {report.facilityName}
                    </div>
                    <div className="text-[10px] text-ink-muted truncate mt-0.5">
                      {report.location}
                    </div>
                  </td>

                  {/* Report Type */}
                  <td className="py-4 px-3 whitespace-nowrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#FAF7F2] text-ink-secondary border border-surface-border">
                      {report.reportType}
                    </span>
                  </td>

                  {/* Activity */}
                  <td className="py-4 px-3 font-medium text-ink-secondary truncate max-w-[150px]">
                    {report.activity}
                  </td>

                  {/* Primary Hazard */}
                  <td className="py-4 px-3 text-ink-primary font-bold truncate max-w-[200px]">
                    {report.primaryHazard}
                  </td>

                  {/* SIF Potential */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <SIFPotentialBadge potential={report.sifPotential} size="xs" />
                  </td>

                  {/* Urgency Score */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <UrgencyScoreBadge score={report.urgencyScore} size="xs" />
                  </td>

                  {/* Life-Saving Rule */}
                  <td className="py-4 px-3 whitespace-nowrap">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-ink-secondary">
                      {report.lifeSavingRule}
                    </span>
                  </td>

                  {/* Review Status */}
                  <td className="py-4 px-5 text-center whitespace-nowrap">
                    <ReviewStatusBadge status={report.reviewStatus} size="xs" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 sm:p-5 border-t border-surface-border/60 bg-[#FAF7F2]/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-ink-muted">
        <div>
          Showing <span className="font-bold text-ink-primary font-mono">{(currentPage - 1) * pageSize + 1}</span> to{' '}
          <span className="font-bold text-ink-primary font-mono">
            {Math.min(currentPage * pageSize, reports.length)}
          </span>{' '}
          of <span className="font-bold text-ink-primary font-mono">{reports.length}</span> reports
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-2 rounded-2xl border border-surface-border/80 bg-white text-ink-primary hover:bg-[#FAF7F2] disabled:opacity-40 disabled:pointer-events-none transition-colors shadow-spatial-xs cursor-pointer"
            aria-label="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="text-xs font-bold px-2 text-ink-secondary">
            Page <span className="font-mono font-extrabold text-ink-primary">{currentPage}</span> of{' '}
            <span className="font-mono font-extrabold text-ink-primary">{totalPages}</span>
          </span>

          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-2 rounded-2xl border border-surface-border/80 bg-white text-ink-primary hover:bg-[#FAF7F2] disabled:opacity-40 disabled:pointer-events-none transition-colors shadow-spatial-xs cursor-pointer"
            aria-label="Next page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
