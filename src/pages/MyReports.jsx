import React, { useMemo } from 'react';
import { ChevronRight, FileText, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useReportsContext } from '../context/ReportsContext';
import { FieldShell } from '../components/layout/FieldShell';

const dummyReports = [
  {
    reportId: 'RPT-2024-0891',
    createdAt: '2024-10-24T00:00:00Z',
    rawReportText: 'Valve leakage in Sector 4B High-Pressure Line',
    reviewStatus: 'PENDING',
    location: 'Sector 4B, high-pressure line',
    summary: 'Detected minor fluid seepage during routine visual inspection of the main isolation valve manifold.',
  },
  {
    reportId: 'RPT-2024-0875',
    createdAt: '2024-10-18T00:00:00Z',
    rawReportText: 'Slip Hazard at East Access Stairway',
    reviewStatus: 'APPROVED',
    location: 'East access stairway',
    summary: 'Accumulation of industrial lubricant was observed on the third landing of the access stairs.',
  },
  {
    reportId: 'RPT-2024-0842',
    createdAt: '2024-10-05T00:00:00Z',
    rawReportText: 'Frayed Grounding Cable on Pump Station C',
    reviewStatus: 'APPROVED',
    location: 'Pump Station C',
    summary: 'Primary grounding wire sheaths appeared damaged, exposing conductive material.',
  },
];

function formatDate(value) {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: '2-digit', year: 'numeric' }).format(new Date(value));
}

function statusLabel(status) {
  if (status === 'APPROVED' || status === 'RESOLVED') return 'RESOLVED';
  if (status === 'REJECTED' || status === 'ACTION_REQUIRED') return 'ACTION REQUIRED';
  return 'UNDER REVIEW';
}

export function MyReports() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const { reports } = useReportsContext();

  const myReports = useMemo(() => {
    const ownedReports = reports.filter((report) => report.reporterId === currentUser?.userId);
    return ownedReports.length ? ownedReports : dummyReports.map((report) => ({ ...report, reporterId: currentUser?.userId }));
  }, [currentUser?.userId, reports]);

  return (
    <FieldShell activePage="/my-reports">
      <main className="mx-auto w-full max-w-[1040px] px-5 py-6 sm:px-8 lg:py-7">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-3 text-[10px] font-bold uppercase tracking-[0.26em] text-[#73757a]">
              <span className="h-0.5 w-6 bg-[#0a705a]" /> Safer operations. Stronger tomorrow.
            </div>
            <h1 className="text-[2.35rem] font-black leading-tight tracking-[-0.04em]">My Reports</h1>
            <p className="mt-1.5 text-sm text-[#595d65] sm:text-base">View and track the status of your submitted safety reports.</p>
          </div>
          <button type="button" onClick={() => navigate('/report')} className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#00654f] px-4 py-2.5 text-sm font-extrabold text-white shadow-btn-emerald transition hover:bg-[#075b49]">
            <Plus className="h-4 w-4" /> New Report
          </button>
        </div>

        <div className="space-y-2.5">
          {myReports.map((report) => {
            const status = statusLabel(report.reviewStatus);
            const isActionRequired = status === 'ACTION REQUIRED';
            const isResolved = status === 'RESOLVED';
            return (
              <article key={report.reportId} className="flex items-start gap-4 rounded-lg border border-[#e8dfd1] bg-white/90 p-4 shadow-[0_5px_16px_rgba(61,53,41,0.05)] sm:p-5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#e2f3eb] text-[#00654f]">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-[#77808d]">
                    <span>{report.reportId}</span>
                    <span>•</span>
                    <span>{formatDate(report.createdAt)}</span>
                  </div>
                  <h2 className="mt-1 text-sm font-black text-[#121827] sm:text-base">{report.rawReportText || report.title}</h2>
                  <p className="mt-1 text-xs leading-5 text-[#66707d]">{report.summary || report.location || 'Safety observation submitted for review.'}</p>
                </div>
                <div className="hidden shrink-0 items-center gap-3 sm:flex">
                  <span className={`rounded-full px-3 py-1 text-[10px] font-extrabold ${isActionRequired ? 'bg-red-50 text-red-600' : isResolved ? 'bg-[#e2f3eb] text-[#00654f]' : 'bg-[#fff2d8] text-[#a35b08]'}`}>
                    <span className="mr-1">●</span> {status}
                  </span>
                  <ChevronRight className="h-5 w-5 text-[#7c8791]" />
                </div>
              </article>
            );
          })}
        </div>
      </main>
    </FieldShell>
  );
}
