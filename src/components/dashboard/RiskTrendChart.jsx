import React, { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { analyticsService } from '../../services/analyticsService';

export function RiskTrendChart() {
  const [timeRange, setTimeRange] = useState('30D');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const trend = await analyticsService.getTrendData(timeRange);
        if (isMounted) {
          setData(trend);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [timeRange]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-md p-4 rounded-3xl border border-surface-border/80 shadow-spatial-lg text-xs">
          <div className="font-extrabold text-ink-primary mb-2 pb-1.5 border-b border-surface-border/50">
            {payload[0]?.payload?.date ? `${label} (${payload[0]?.payload?.date})` : label}
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center justify-between gap-5 text-ink-secondary">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#A8A29E]" />
                Total Volume:
              </span>
              <span className="font-mono font-bold text-ink-primary">{payload[0]?.payload?.total}</span>
            </div>
            <div className="flex items-center justify-between gap-5 text-amber-950 font-bold">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                SIF Potential:
              </span>
              <span className="font-mono">{payload[0]?.payload?.sifPotential}</span>
            </div>
            <div className="flex items-center justify-between gap-5 text-red-950 font-bold">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-red-600" />
                Critical PSIF:
              </span>
              <span className="font-mono">{payload[0]?.payload?.critical}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="h-full flex flex-col justify-between rounded-3.5xl shadow-spatial">
      <CardHeader
        action={
          <div className="flex items-center p-1 bg-[#EFEAE1]/90 rounded-full border border-surface-border/80 shadow-spatial-xs">
            {['7D', '30D', '90D', '1Y'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3.5 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
                  timeRange === range
                    ? 'bg-white text-ink-primary shadow-spatial-xs border border-surface-border/50'
                    : 'text-ink-muted hover:text-ink-primary'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        }
      >
        <CardTitle subtitle="Observed SIF-potential precursors vs baseline reporting volume">
          SIF Potential Exposure Trend
        </CardTitle>
      </CardHeader>

      <CardContent className="pt-3 flex-1">
        <div className="h-72 w-full">
          {loading ? (
            <div className="h-full flex items-center justify-center text-xs text-ink-muted">
              Loading trend timeline...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#A8A29E" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#A8A29E" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="sifGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="critGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#DC2626" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="#DC2626" stopOpacity={0.03} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ECE5D8" vertical={false} />
                <XAxis
                  dataKey="label"
                  stroke="#857E74"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#E8E1D5' }}
                />
                <YAxis
                  stroke="#857E74"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#E8E1D5' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#A8A29E"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#totalGrad)"
                  name="Total Reports"
                />
                <Area
                  type="monotone"
                  dataKey="sifPotential"
                  stroke="#D97706"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#sifGrad)"
                  name="SIF Potential"
                />
                <Area
                  type="monotone"
                  dataKey="critical"
                  stroke="#DC2626"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#critGrad)"
                  name="Critical SIF"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Chart Legend Summary */}
        <div className="mt-4 pt-3.5 border-t border-surface-border/50 flex items-center justify-center gap-6 text-xs text-ink-secondary flex-wrap">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#A8A29E]" />
            <span className="font-medium">Total Volume</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span className="font-bold text-amber-950">SIF Potential (Precursor Flagged)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600" />
            <span className="font-bold text-red-950">Critical SIF (Immediate Urgency)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
