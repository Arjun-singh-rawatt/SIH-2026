import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, AlertTriangle, ArrowRight, ChevronRight, BellRing } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function Login() {
  const navigate = useNavigate();
  const { login, availableUsers } = useAuth();
  const safetyOfficerUser = availableUsers.find((user) => user.role === 'Safety Officer') || availableUsers[0];
  const managerUser = availableUsers.find((user) => user.role === 'HSE Manager') || availableUsers[0];
  const demoUserIds = ['USR-002', 'USR-008', 'USR-001'];
  const demoUsers = demoUserIds
    .map((userId) => availableUsers.find((user) => user.userId === userId))
    .filter(Boolean);
  const [selectedUserId, setSelectedUserId] = useState(safetyOfficerUser.userId);

  const handleAccessSystem = () => {
    login(managerUser);
    navigate('/dashboard');
  };

  const handleReportConcern = () => {
    login(safetyOfficerUser);
    navigate('/report');
  };

  const handleDemoAccess = () => {
    const selectedUser = demoUsers.find((user) => user.userId === selectedUserId) || safetyOfficerUser;
    login(selectedUser);
    navigate(selectedUser.role === 'HSE Manager' ? '/dashboard' : '/report');
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f4f1eb] text-ink-primary lg:h-screen lg:min-h-0">
      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: 'linear-gradient(180deg, rgba(249, 246, 239, 0.88) 0%, rgba(248, 244, 237, 0.74) 42%, rgba(244, 239, 230, 0.86) 100%), url(/assets/oil-refinery-bg.png)',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
          }}
        />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,253,248,0.86)_0%,rgba(255,252,247,0.38)_34%,rgba(244,241,235,0.12)_62%,rgba(244,241,235,0.42)_100%)]" />
        <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-white/55 via-white/15 to-transparent" />
      </div>
      <div className="absolute -left-16 bottom-12 h-64 w-64 rounded-full bg-[#0b6b55]/[0.045] blur-3xl" />
      <div className="absolute -right-20 top-20 h-72 w-72 rounded-full bg-[#dd934c]/[0.06] blur-3xl" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-[1366px] flex-col px-5 py-4 sm:px-8 sm:py-5 lg:h-screen lg:min-h-0 lg:px-10 lg:py-4">
        <header className="shrink-0 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-b from-[#058867] to-[#046B4F] shadow-btn-emerald ring-1 ring-[#045D44]">
              <Shield className="h-[18px] w-[18px] text-emerald-50" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-[1.7rem] font-black leading-none tracking-tight">SIFT</span>
                <span className="rounded-full border border-amber-200 bg-amber-100 px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-[0.16em] text-amber-900">
                  OIL
                </span>
              </div>
              <p className="text-[10px] text-ink-muted">Safety Intelligence & Fatality-risk</p>
            </div>
          </div>

          <div className="hidden items-center gap-2 text-[9px] font-extrabold uppercase tracking-[0.3em] text-ink-muted md:flex">
            <span className="h-px w-7 bg-[#0a5e46]/30" />
            <span>Safer operations. Stronger tomorrow.</span>
          </div>
        </header>

        <main className="flex min-h-0 flex-1 items-center justify-center py-3 lg:py-2">
          <div className="w-full max-w-[980px]">
            <div className="mb-5 text-center lg:mb-6">
              <h1 className="text-[2.5rem] font-black leading-[1.04] tracking-[-0.05em] text-ink-primary sm:text-[3rem] md:text-[3.35rem] lg:text-[3.5rem]">
                <span className="text-[#0f4f43]">OIL</span> <span className="text-[#0d3f38]">SIF</span>{' '}
                <span className="text-[#0d3f38]">Precursor Intelligence</span>
              </h1>
              <p className="mx-auto mt-2.5 max-w-[640px] text-[0.9rem] leading-5 text-ink-secondary md:text-[1rem]">
                Turn safety observations into actionable SIF-risk intelligence.
              </p>
            </div>

            <div className="mx-auto mb-5 flex max-w-[860px] flex-col items-stretch gap-3 rounded-2xl border border-[#e4d7bd] bg-white/80 p-3 shadow-[0_10px_25px_rgba(15,79,67,0.05)] sm:flex-row sm:items-center sm:justify-between sm:p-3.5">
              <div className="text-left">
                <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-[#0f5e4b]">Demo access</p>
                <p className="mt-1 text-xs text-ink-secondary">Choose a demo ID to show role-based access.</p>
              </div>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <select
                  value={selectedUserId}
                  onChange={(event) => setSelectedUserId(event.target.value)}
                  aria-label="Select demo user ID"
                  className="rounded-xl border border-[#d8cdbb] bg-[#faf7f2] px-3 py-2 text-xs font-bold text-ink-primary outline-none focus:border-[#0a5e46]"
                >
                  {demoUsers.map((user) => (
                    <option key={user.userId} value={user.userId}>
                      {user.userId} - {user.name} ({user.role})
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={handleDemoAccess}
                  className="rounded-xl bg-[#0a5e46] px-4 py-2 text-xs font-extrabold tracking-[0.08em] text-white shadow-btn-emerald transition hover:bg-[#084b39]"
                >
                  CONTINUE AS SELECTED ID
                </button>
              </div>
            </div>

            <div className="mx-auto grid max-w-[860px] gap-5 md:grid-cols-2 lg:gap-6">
              <button
                type="button"
                onClick={handleReportConcern}
                className="group mx-auto flex h-auto min-h-[310px] w-full max-w-[410px] flex-col rounded-[1.35rem] border border-[#e4d7bd] bg-[linear-gradient(180deg,rgba(255,255,255,0.94)_0%,rgba(248,244,237,0.98)_100%)] p-5 text-left shadow-[0_14px_32px_rgba(15,79,67,0.07)] transition-transform duration-200 hover:-translate-y-1 hover:shadow-[0_20px_40px_rgba(15,79,67,0.09)] lg:h-[380px] lg:min-h-0 lg:p-5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-[0.9rem] bg-[#dff4eb] text-[#0d5a49] ring-1 ring-[#8fcec0]">
                    <AlertTriangle className="h-5 w-5" />
                  </div>
                  <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[#d4d0c7] bg-[#f7f4ef] text-ink-primary transition-colors group-hover:bg-white">
                    <ChevronRight className="h-3.5 w-3.5" />
                  </div>
                </div>

                <div className="mt-4">
                  <h2 className="text-[1.5rem] font-black leading-tight tracking-[-0.04em] text-ink-primary sm:text-[1.65rem]">
                    Report a Safety Concern
                  </h2>
                  <p className="mt-1.5 text-[0.85rem] text-ink-secondary">For workers / field supervisors</p>
                </div>

                <div className="mt-4 border-t border-[#e8dfd1] pt-4" />

                <div className="flex flex-wrap gap-1.5 text-[10px] font-bold text-ink-secondary">
                  <span className="rounded-lg border border-[#cfe7df] bg-[#eef9f4] px-2 py-1.5 text-[#0f5e4b]">Quick Reporting</span>
                  <span className="rounded-lg border border-[#dfe0e4] bg-white px-2 py-1.5">Mobile Friendly</span>
                  <span className="rounded-lg border border-[#dfe0e4] bg-white px-2 py-1.5">Safer Workplaces</span>
                </div>

                <div className="mt-auto pt-4">
                  <div className="flex items-center justify-center rounded-full bg-[#0a5e46] px-5 py-2.5 text-[0.78rem] font-extrabold tracking-[0.12em] text-white shadow-btn-emerald">
                    PROCEED <ArrowRight className="ml-2 h-3.5 w-3.5" />
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={handleAccessSystem}
                className="group mx-auto flex h-auto min-h-[310px] w-full max-w-[410px] flex-col rounded-[1.35rem] border border-[#e4d7bd] bg-[linear-gradient(180deg,rgba(255,255,255,0.94)_0%,rgba(248,244,237,0.98)_100%)] p-5 text-left shadow-[0_14px_32px_rgba(15,79,67,0.07)] transition-transform duration-200 hover:-translate-y-1 hover:shadow-[0_20px_40px_rgba(15,79,67,0.09)] lg:h-[380px] lg:min-h-0 lg:p-5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-[0.9rem] bg-[#f0e1c8] text-[#b15a0f] ring-1 ring-[#e5bc78]">
                    <BellRing className="h-5 w-5" />
                  </div>
                  <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[#d4d0c7] bg-[#f7f4ef] text-ink-primary transition-colors group-hover:bg-white">
                    <ChevronRight className="h-3.5 w-3.5" />
                  </div>
                </div>

                <div className="mt-4">
                  <h2 className="text-[1.5rem] font-black leading-tight tracking-[-0.04em] text-ink-primary sm:text-[1.65rem]">
                    Safety Command Center
                  </h2>
                  <p className="mt-1.5 text-[0.85rem] text-ink-secondary">For safety managers</p>
                </div>

                <div className="mt-4 border-t border-[#e8dfd1] pt-4" />

                <div className="flex flex-wrap gap-1.5 text-[10px] font-bold text-ink-secondary">
                  <span className="rounded-lg border border-[#e7d4ae] bg-[#f9f0d7] px-2 py-1.5 text-[#7c4c15]">Real-time Insights</span>
                  <span className="rounded-lg border border-[#dfe0e4] bg-white px-2 py-1.5">Risk Prioritization</span>
                  <span className="rounded-lg border border-[#dfe0e4] bg-white px-2 py-1.5">Action Management</span>
                </div>

                <div className="mt-auto pt-4">
                  <div className="flex items-center justify-center rounded-full bg-[#ef7b30] px-5 py-2.5 text-[0.78rem] font-extrabold tracking-[0.12em] text-white shadow-[0_10px_22px_rgba(239,123,48,0.22)]">
                    ACCESS SYSTEM <ArrowRight className="ml-2 h-3.5 w-3.5" />
                  </div>
                </div>
              </button>
            </div>
          </div>
        </main>

        <div className="pointer-events-none absolute bottom-8 left-5 hidden text-[10px] font-semibold uppercase tracking-[0.3em] text-ink-muted 2xl:block">
          <div className="mb-5 h-px w-6 bg-[#0a5e46]/50" />
          <p>Detect</p>
          <p className="mt-2.5">Analyze</p>
          <p className="mt-2.5">Prevent</p>
        </div>

        <div className="pointer-events-none absolute right-6 top-[42%] hidden -translate-y-1/2 text-right text-[11px] font-semibold uppercase tracking-[0.24em] text-ink-muted 2xl:block">
          <p>Safety</p>
          <p className="mt-3">People</p>
          <p className="mt-3">Process</p>
          <p className="mt-3">Progress</p>
        </div>

        <footer className="shrink-0 flex flex-col items-center justify-between gap-2 pb-1 pt-2 text-center text-[10px] text-ink-muted md:flex-row md:text-[11px]">
          <span>Copyright 2026 SIF Intelligence Engine. Authorized personnel only.</span>
          <span>Oil India Limited | HSE Digital Initiative</span>
        </footer>
      </div>
    </div>
  );
}
