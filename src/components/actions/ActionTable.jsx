import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  AlertOctagon,
  ArrowUpRight,
  User,
  Building2,
  Calendar,
} from 'lucide-react';
import { formatDate } from '../../utils/formatters';

export function ActionTable({ actions, onStatusChange }) {
  const navigate = useNavigate();

  const getPriorityBadge = (priority) => {
    switch (priority?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-950 border-red-200 font-black shadow-spatial-xs';
      case 'HIGH':
        return 'bg-amber-50 text-amber-950 border-amber-200 font-black shadow-spatial-xs';
      case 'MEDIUM':
        return 'bg-amber-50/60 text-amber-900 border-amber-200/80 font-bold';
      case 'LOW':
      default:
        return 'bg-emerald-50 text-emerald-950 border-emerald-200/80 font-bold';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-emerald-50 text-emerald-950 border-emerald-300 font-bold shadow-spatial-xs';
      case 'In Progress':
        return 'bg-sky-50 text-sky-950 border-sky-300 font-bold shadow-spatial-xs';
      case 'Overdue':
        return 'bg-red-50 text-red-950 border-red-300 font-black shadow-spatial-xs animate-pulse';
      case 'Open':
      default:
        return 'bg-amber-50 text-amber-950 border-amber-300 font-bold shadow-spatial-xs';
    }
  };

  if (!actions || actions.length === 0) {
    return (
      <div className="p-12 text-center text-xs text-ink-muted bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial">
        No action items match the active criteria.
      </div>
    );
  }

  return (
    <div className="bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-surface-border/60 bg-[#FAF7F2]/70 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted select-none">
              <th className="py-4 px-5">Action ID</th>
              <th className="py-4 px-3">Related Safety Report</th>
              <th className="py-4 px-3">Description & Scope</th>
              <th className="py-4 px-3">Assigned Owner</th>
              <th className="py-4 px-3">Facility</th>
              <th className="py-4 px-3 text-center">Priority</th>
              <th className="py-4 px-3">Due Date</th>
              <th className="py-4 px-5 text-center">Status / Update</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-surface-border/40">
            {actions.map((act) => {
              const isOverdue = act.status === 'Overdue' || (new Date(act.dueDate) < new Date() && act.status !== 'Completed');
              return (
                <tr key={act.actionId} className="hover:bg-[#FAF7F2] transition-colors">
                  {/* Action ID */}
                  <td className="py-4 px-5 font-mono font-extrabold text-ink-primary whitespace-nowrap">
                    {act.actionId}
                  </td>

                  {/* Related Report */}
                  <td className="py-4 px-3 max-w-[200px]">
                    <div
                      onClick={() => navigate(`/reports/${act.reportId}`)}
                      className="group/link cursor-pointer"
                    >
                      <div className="flex items-center gap-1 font-mono font-extrabold text-emerald-900 group-hover/link:underline">
                        <span>#{act.reportId}</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-[10px] text-ink-muted truncate mt-0.5">{act.reportTitle}</p>
                    </div>
                  </td>

                  {/* Description */}
                  <td className="py-4 px-3 max-w-[280px]">
                    <span className="font-extrabold text-ink-primary block text-[11px] mb-0.5">
                      {act.actionType}
                    </span>
                    <p className="text-ink-secondary text-[11px] line-clamp-2 leading-relaxed">
                      {act.description}
                    </p>
                  </td>

                  {/* Assignee */}
                  <td className="py-4 px-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-[#FAF7F2] border border-surface-border flex items-center justify-center text-[10px] font-bold text-ink-secondary shadow-spatial-xs">
                        <User className="w-3.5 h-3.5 text-emerald-800" />
                      </div>
                      <div>
                        <span className="font-extrabold text-ink-primary block text-xs">{act.assigneeName}</span>
                        <span className="text-[10px] text-ink-muted">{act.assigneeRole}</span>
                      </div>
                    </div>
                  </td>

                  {/* Facility */}
                  <td className="py-4 px-3 text-ink-secondary whitespace-nowrap font-medium text-[11px]">
                    {act.facilityName}
                  </td>

                  {/* Priority */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <span className={`inline-flex px-3 py-0.5 rounded-full text-[10px] uppercase border ${getPriorityBadge(act.priority)}`}>
                      {act.priority}
                    </span>
                  </td>

                  {/* Due Date */}
                  <td className="py-4 px-3 whitespace-nowrap font-mono text-[11px]">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-ink-muted" />
                      <span className={isOverdue ? 'font-extrabold text-red-700' : 'text-ink-secondary'}>
                        {formatDate(act.dueDate)}
                      </span>
                    </div>
                  </td>

                  {/* Status Dropdown / Action */}
                  <td className="py-4 px-5 text-center whitespace-nowrap">
                    <select
                      value={act.status}
                      onChange={(e) => onStatusChange(act.actionId, e.target.value)}
                      className={`text-xs font-extrabold py-1.2 px-3 rounded-full border cursor-pointer focus:outline-none transition-all shadow-spatial-xs ${getStatusBadge(act.status)}`}
                    >
                      <option value="Open">Open</option>
                      <option value="In Progress">In Progress</option>
                      <option value="Completed">Completed</option>
                      <option value="Overdue">Overdue</option>
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
