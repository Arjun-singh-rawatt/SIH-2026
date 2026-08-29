import React, { useState, useEffect } from 'react';
import { ShieldX, AlertTriangle, ChevronRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { ProgressBar } from '../ui/ProgressBar';
import { analyticsService } from '../../services/analyticsService';
import { useNavigate } from 'react-router-dom';

export function BarrierFailures() {
  const [barriers, setBarriers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const res = await analyticsService.getBarrierFailureBreakdown();
        setBarriers(res);
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
            Barrier Intelligence →
          </button>
        }
      >
        <CardTitle subtitle="Critical safety barriers identified as failed or degraded in field reports">
          Weakened / Failed Barriers
        </CardTitle>
      </CardHeader>

      <CardContent className="p-5 sm:p-6 space-y-4 flex-1">
        {loading ? (
          <div className="text-xs text-ink-muted py-6 text-center">Loading barrier failure analysis...</div>
        ) : (
          barriers.map((bar) => (
            <div
              key={bar.barrier}
              onClick={() => navigate(`/reports?barrier=${encodeURIComponent(bar.barrier)}`)}
              className="p-3.5 sm:p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 hover:border-surface-border transition-all cursor-pointer group shadow-spatial-xs hover:shadow-spatial-sm"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-extrabold text-ink-primary group-hover:text-emerald-900 transition-colors">
                  {bar.barrier}
                </span>
                <span className="text-xs font-mono font-black text-red-950 bg-red-50 px-2 py-0.2 rounded-full border border-red-200">
                  {bar.failedCount} failures ({bar.percentage}%)
                </span>
              </div>

              <div className="text-[11px] text-ink-muted flex items-center justify-between mb-2">
                <span>Category: <strong className="text-ink-secondary">{bar.category}</strong></span>
                <span>Type: <strong className="text-ink-secondary">{bar.barrierType}</strong></span>
              </div>

              <ProgressBar
                value={bar.percentage}
                max={30}
                variant={bar.percentage > 18 ? 'crimson' : 'amber'}
                size="sm"
              />
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
