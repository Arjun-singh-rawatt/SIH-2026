import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ArrowUpDown, Building2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { SIFPotentialBadge } from '../ui/RiskBadge';
import { ProgressBar } from '../ui/ProgressBar';
import { analyticsService } from '../../services/analyticsService';
import { formatNumber, formatPercent } from '../../utils/formatters';

export function FacilityRiskTable() {
  const navigate = useNavigate();
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const ranking = await analyticsService.getFacilityRiskRanking();
        setFacilities(ranking.slice(0, 6));
      } catch (e) {
        console.error(e);
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
            onClick={() => navigate('/facilities')}
            className="text-xs font-extrabold text-emerald-800 hover:text-emerald-900 hover:underline cursor-pointer"
          >
            All Facilities ({facilities.length}+) →
          </button>
        }
      >
        <CardTitle subtitle="Ranked by SIF Precursor Density (SIF reports ÷ total volume)">
          SIF Density by Facility
        </CardTitle>
      </CardHeader>

      <CardContent className="p-0 flex-1 overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-surface-border/60 bg-[#FAF7F2]/70 text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
              <th className="py-4 px-5">Facility / Location</th>
              <th className="py-4 px-3">Region</th>
              <th className="py-4 px-3 text-right">Total Reports</th>
              <th className="py-4 px-3 text-right">SIF Potential</th>
              <th className="py-4 px-3 min-w-[130px]">SIF Density</th>
              <th className="py-4 px-3">Top Precursor</th>
              <th className="py-4 px-5 text-center">Risk Level</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/40">
            {loading ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-ink-muted">
                  Calculating facility density metrics...
                </td>
              </tr>
            ) : (
              facilities.map((fac, idx) => (
                <tr
                  key={fac.facilityId}
                  onClick={() => navigate(`/facilities/${fac.facilityId}`)}
                  className="hover:bg-[#FAF7F2] cursor-pointer transition-colors group"
                >
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-[#FAF7F2] border border-surface-border flex items-center justify-center text-[10px] font-mono font-extrabold text-ink-muted group-hover:text-emerald-900 group-hover:bg-emerald-50 transition-colors shadow-spatial-xs">
                        {idx + 1}
                      </span>
                      <div>
                        <span className="font-extrabold text-ink-primary group-hover:text-emerald-900 transition-colors block text-xs">
                          {fac.shortName}
                        </span>
                        <span className="block text-[10px] text-ink-muted leading-none mt-0.5 font-mono">
                          {fac.facilityId}
                        </span>
                      </div>
                    </div>
                  </td>

                  <td className="py-4 px-3 text-ink-secondary text-[11px] font-medium">{fac.region}</td>

                  <td className="py-4 px-3 text-right font-mono font-bold text-ink-primary">
                    {formatNumber(fac.totalReports)}
                  </td>

                  <td className="py-4 px-3 text-right font-mono font-black text-amber-950">
                    {formatNumber(fac.sifReports)}
                  </td>

                  <td className="py-4 px-3">
                    <div className="space-y-1">
                      <span className="font-extrabold font-mono text-ink-primary text-xs">{fac.sifDensity}%</span>
                      <ProgressBar
                        value={fac.sifDensity}
                        max={35}
                        variant={fac.sifDensity > 24 ? 'crimson' : fac.sifDensity > 18 ? 'amber' : 'emerald'}
                        size="sm"
                      />
                    </div>
                  </td>

                  <td className="py-4 px-3">
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#FAF7F2] text-ink-secondary border border-surface-border">
                      {fac.topPrecursor}
                    </span>
                  </td>

                  <td className="py-4 px-5 text-center">
                    <SIFPotentialBadge potential={fac.riskLevel} size="xs" showIcon={false} />
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
