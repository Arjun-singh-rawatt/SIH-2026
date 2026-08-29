import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertOctagon, ArrowUpRight, Flame, ShieldAlert, ChevronRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { analyticsService } from '../../services/analyticsService';

export function PriorityAttention() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await analyticsService.getPriorityAlerts();
        setAlerts(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <Card className="h-full flex flex-col justify-between border-amber-200/70 bg-gradient-to-b from-white via-white to-[#FFFDF9] rounded-3.5xl shadow-spatial">
      <CardHeader
        action={
          <span className="text-[11px] font-extrabold px-3 py-1 rounded-full bg-red-50 text-red-900 border border-red-200/80 flex items-center gap-1.5 shadow-spatial-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-pulse" />
            Active Focus
          </span>
        }
      >
        <CardTitle subtitle="High-urgency operational precursors requiring targeted HSE intervention">
          Priority Attention
        </CardTitle>
      </CardHeader>

      <CardContent className="p-5 sm:p-6 space-y-3.5 flex-1">
        {loading ? (
          <div className="text-xs text-ink-muted py-6 text-center">Loading priority alerts...</div>
        ) : (
          alerts.map((alert) => {
            const isCritical = alert.level === 'CRITICAL';
            return (
              <div
                key={alert.id}
                onClick={() => navigate(alert.actionUrl)}
                className={`p-4 sm:p-5 rounded-2.5xl border transition-all duration-200 cursor-pointer group shadow-spatial-xs hover:shadow-spatial hover:-translate-y-0.5 ${
                  isCritical
                    ? 'bg-gradient-to-r from-[#FFF5F5] to-[#FFF9F9] border-red-200/80 hover:border-red-300'
                    : 'bg-gradient-to-r from-[#FFFBF0] to-[#FFFCF5] border-amber-200/80 hover:border-amber-300'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border shadow-spatial-xs ${
                        isCritical
                          ? 'bg-red-100/90 text-red-950 border-red-300/80'
                          : 'bg-amber-100/90 text-amber-950 border-amber-300/80'
                      }`}
                    >
                      {alert.level}
                    </span>
                    <span className="text-xs font-bold text-ink-secondary">
                      {alert.precursor}
                    </span>
                  </div>

                  <div className="flex items-center gap-1 text-xs font-bold text-emerald-800 group-hover:text-emerald-900 group-hover:translate-x-0.5 transition-all">
                    <span>Investigate</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </div>
                </div>

                <h4 className="text-xs sm:text-sm font-extrabold text-ink-primary mt-2.5 group-hover:text-emerald-950 transition-colors">
                  {alert.title}
                </h4>

                <p className="text-xs text-ink-secondary/90 mt-1 line-clamp-2 leading-relaxed">
                  {alert.subtitle}
                </p>

                <div className="mt-3 pt-2.5 border-t border-surface-border/60 flex items-center justify-between text-[11px] text-ink-secondary flex-wrap gap-2">
                  <span className="font-bold text-ink-primary">{alert.facilityName}</span>
                  <span className="font-mono bg-white px-2.5 py-0.5 rounded-full border border-surface-border/80 text-[10px] shadow-spatial-xs">
                    Barrier: <span className="font-bold text-red-800">{alert.failedBarrier}</span>
                  </span>
                </div>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}
