import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { SIFPotentialBadge } from '../ui/RiskBadge';
import { ProgressBar } from '../ui/ProgressBar';
import { analyticsService } from '../../services/analyticsService';
import { formatNumber } from '../../utils/formatters';
import { useNavigate } from 'react-router-dom';

export function ActivityRiskChart() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const res = await analyticsService.getActivityRiskBreakdown();
        setActivities(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <Card className="h-full flex flex-col justify-between rounded-3.5xl shadow-spatial">
      <CardHeader
        action={
          <button
            onClick={() => navigate('/intelligence')}
            className="text-xs font-extrabold text-emerald-800 hover:text-emerald-900 hover:underline cursor-pointer"
          >
            Activity Matrix →
          </button>
        }
      >
        <CardTitle subtitle="Operational activities generating the highest SIF precursor density">
          High-Risk Activities
        </CardTitle>
      </CardHeader>

      <CardContent className="p-0 flex-1 overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-surface-border/60 bg-[#FAF7F2]/70 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              <th className="py-4 px-5">Activity Name</th>
              <th className="py-4 px-3 text-right">Total Reports</th>
              <th className="py-4 px-3 text-right">SIF Potential</th>
              <th className="py-4 px-3 min-w-[120px]">SIF Density</th>
              <th className="py-4 px-5 text-center">Risk</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/40">
            {loading ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-ink-muted">
                  Loading activity risk metrics...
                </td>
              </tr>
            ) : (
              activities.map((act) => (
                <tr
                  key={act.activity}
                  onClick={() => navigate(`/reports?activity=${encodeURIComponent(act.activity)}`)}
                  className="hover:bg-[#FAF7F2] cursor-pointer transition-colors group"
                >
                  <td className="py-4 px-5 font-extrabold text-ink-primary group-hover:text-emerald-900 transition-colors">
                    {act.activity}
                  </td>
                  <td className="py-4 px-3 text-right font-mono font-bold text-ink-primary">
                    {formatNumber(act.totalReports)}
                  </td>
                  <td className="py-4 px-3 text-right font-mono font-black text-amber-950">
                    {formatNumber(act.sifCount)}
                  </td>
                  <td className="py-4 px-3">
                    <div className="space-y-1">
                      <span className="font-extrabold font-mono text-xs text-ink-primary">{act.density}%</span>
                      <ProgressBar
                        value={act.density}
                        max={40}
                        variant={act.density > 28 ? 'crimson' : act.density > 20 ? 'amber' : 'emerald'}
                        size="sm"
                      />
                    </div>
                  </td>
                  <td className="py-4 px-5 text-center">
                    <SIFPotentialBadge potential={act.risk} size="xs" showIcon={false} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
