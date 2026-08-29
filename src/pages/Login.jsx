import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, ShieldAlert, ArrowRight, Lock, Mail, CheckCircle2, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';

export function Login() {
  const navigate = useNavigate();
  const { login, availableUsers } = useAuth();
  const [email, setEmail] = useState('alok.sharma@oilindia.in');
  const [password, setPassword] = useState('••••••••');
  const [isLoading, setIsLoading] = useState(false);

  const handleStandardLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      const user = availableUsers.find((u) => u.email === email) || availableUsers[0];
      login(user);
      setIsLoading(false);
      navigate('/dashboard');
    }, 400);
  };

  const handlePersonaLogin = (user) => {
    login(user);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-canvas flex flex-col justify-center items-center p-4 sm:p-6 select-none relative overflow-hidden">
      {/* Background Soft Lighting Gradients */}
      <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[500px] bg-gradient-to-b from-white/90 via-amber-100/20 to-transparent pointer-events-none blur-3xl" />
      <div className="absolute top-1/3 -right-40 w-96 h-96 bg-emerald-100/25 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 -left-40 w-96 h-96 bg-orange-100/25 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10 space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-gradient-to-b from-[#058867] to-[#046B4F] text-white shadow-btn-emerald border border-[#045D44] mb-1">
            <Shield className="w-8 h-8 text-emerald-100" />
          </div>
          <div>
            <div className="flex items-center justify-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black text-ink-primary tracking-tight font-sans">
                SIFT
              </h1>
              <span className="text-[11px] uppercase font-black tracking-widest px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-950 border border-amber-300/80 shadow-spatial-xs">
                OIL Enterprise
              </span>
            </div>
            <p className="text-xs font-bold text-ink-secondary mt-1">
              Safety Intelligence & Fatality-risk Tracking
            </p>
            <p className="text-[11px] text-ink-muted mt-0.5 font-normal">
              Oil India Limited — HSSE Command & Precursor Intelligence
            </p>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-white border border-surface-border/80 rounded-4xl p-6 sm:p-8 shadow-spatial-xl">
          <form onSubmit={handleStandardLogin} className="space-y-4">
            <div>
              <label className="block text-[11px] font-extrabold uppercase tracking-wider text-ink-secondary mb-1.5">
                Corporate Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="sift-input pl-11 text-xs"
                  placeholder="name@oilindia.in"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-[11px] font-extrabold uppercase tracking-wider text-ink-secondary">
                  Password
                </label>
                <span className="text-[11px] text-emerald-800 font-bold hover:underline cursor-pointer">
                  Forgot Password?
                </span>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="sift-input pl-11 text-xs font-mono"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-3 shadow-btn-emerald"
              isLoading={isLoading}
              iconRight={ArrowRight}
            >
              Sign In to Command Center
            </Button>
          </form>

          {/* Quick Switch Demo Roles */}
          <div className="mt-6 pt-5 border-t border-surface-border/80">
            <span className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted text-center mb-3">
              Or 1-Click Sign In with Demo Persona
            </span>

            <div className="space-y-2">
              {availableUsers.slice(0, 3).map((user) => (
                <button
                  key={user.userId}
                  type="button"
                  onClick={() => handlePersonaLogin(user)}
                  className="w-full flex items-center justify-between p-3 rounded-2.5xl border border-surface-border/80 bg-[#FAF7F2] hover:bg-white hover:border-emerald-600/40 hover:shadow-spatial-xs transition-all text-left cursor-pointer group"
                >
                  <div className="flex items-center gap-3">
                    <img
                      src={user.avatar}
                      alt={user.name}
                      className="w-9 h-9 rounded-2xl object-cover border border-surface-border shrink-0"
                    />
                    <div>
                      <span className="text-xs font-extrabold text-ink-primary group-hover:text-emerald-950 transition-colors block">
                        {user.name}
                      </span>
                      <span className="text-[10px] text-ink-muted font-medium block">
                        {user.role} · {user.facilityName}
                      </span>
                    </div>
                  </div>
                  <UserCheck className="w-4 h-4 text-ink-muted group-hover:text-emerald-800 transition-colors shrink-0" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Security & Standard Notice */}
        <div className="text-center space-y-1 text-[11px] text-ink-muted">
          <p>Protected by OIL Enterprise SSO & Multi-Factor Authentication</p>
          <p>Compliant with IOGP Life-Saving Rules Standards</p>
        </div>
      </div>
    </div>
  );
}
