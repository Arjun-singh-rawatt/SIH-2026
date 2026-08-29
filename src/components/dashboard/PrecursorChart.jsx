import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { analyticsService } from '../../services/analyticsService';
import { useNavigate } from 'react-router-dom';

export function PrecursorChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const res = await analyticsService.getPrecursorBreakdown();
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white/95 backdrop-blur-md p-4 rounded-3xl border border-surface-border/80 shadow-spatial-lg text-xs">
          <div className="font-extrabold text-ink-primary mb-1.5 pb-1 border-b border-surface-border/50">
            {item.category}
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between gap-5 text-ink-secondary">
              <span>Total Reports:</span>
              <span className="font-mono font-bold text-ink-primary">{item.count}</span>
            </div>
            <div className="flex justify-between gap-5 text-red-950 font-bold">
              <span>High / Critical SIF:</span>
              <span className="font-mono">{item.critical}</span>
            </div>
            <div className="flex justify-between gap-5 text-amber-950 font-black">
              <span>SIF Density:</span>
              <span className="font-mono">{item.density}%</span>
            </div>
          </div>
          <div className="mt-2.5 pt-1.5 border-t border-surface-border/50 text-[10px] text-emerald-800 font-extrabold">
            Click to view associated reports →
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
          <button
            onClick={() => navigate('/intelligence')}
            className="text-xs font-extrabold text-emerald-800 hover:text-emerald-900 hover:underline cursor-pointer"
          >
            Pattern Intelligence →
          </button>
        }
      >
        <CardTitle subtitle="Precursor categories ranked by frequency and fatality-potential volume">
          SIF Precursors by Category
        </CardTitle>
      </CardHeader>

      <CardContent className="pt-3 flex-1">
        <div className="h-72 w-full">
          {loading ? (
            <div className="h-full flex items-center justify-center text-xs text-ink-muted">
              Loading precursor analysis...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                onClick={(e) => {
                  if (e && e.activePayload && e.activePayload.length) {
                    const cat = e.activePayload[0].payload.category;
                    navigate(`/reports?precursorCategory=${encodeURIComponent(cat)}`);
                  }
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#ECE5D8" horizontal={false} />
                <XAxis type="number" stroke="#857E74" fontSize={11} tickLine={false} axisLine={{ stroke: '#E8E1D5' }} />
                <YAxis
                  type="category"
                  dataKey="category"
                  stroke="#524D46"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#E8E1D5' }}
                  width={110}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[0, 10, 10, 0]} cursor="pointer">
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || '#D97706'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
