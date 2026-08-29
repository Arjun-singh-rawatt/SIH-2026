import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  MapPin,
  ShieldAlert,
  ArrowUpRight,
  TrendingUp,
  Search,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { SIFPotentialBadge } from '../components/ui/RiskBadge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { mockFacilities } from '../data/mockFacilities';
import { formatNumber } from '../utils/formatters';

export function Facilities() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [regionFilter, setRegionFilter] = useState('ALL');

  const regions = ['ALL', 'Upper Assam Basin', 'Assam Shelf', 'Central Assam', 'Tinsukia District', 'Arunachal Foothills', 'Krishna Godavari Offshore', 'Bikaner-Nagaur Basin'];

  const filtered = mockFacilities.filter((f) => {
    if (regionFilter !== 'ALL' && f.region !== regionFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      return (
        f.facilityName.toLowerCase().includes(q) ||
        f.region.toLowerCase().includes(q) ||
        f.topPrecursor.toLowerCase().includes(q) ||
        f.type.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="OIL Operational Facilities Directory"
        subtitle="Facility-level safety performance, SIF precursor density rankings, and localized hazard exposure."
      />

      {/* Filter and Search Bar */}
      <div className="bg-white border border-surface-border/80 rounded-3.5xl p-5 sm:p-6 shadow-spatial flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:max-w-md">
          <Search className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search facility name, region, or precursor..."
            className="sift-input pl-10 text-xs py-2.5 rounded-full"
          />
        </div>

        <div className="w-full sm:w-auto">
          <select
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
            className="sift-select w-full sm:w-auto text-xs font-bold py-2 px-3.5 rounded-2xl"
          >
            <option value="ALL">All Operational Regions</option>
            {regions.filter(r => r !== 'ALL').map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Facilities Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
        {filtered.map((facility) => (
          <Card
            key={facility.facilityId}
            variant="interactive"
            onClick={() => navigate(`/facilities/${facility.facilityId}`)}
            className="p-6 sm:p-7 flex flex-col justify-between group rounded-3.5xl"
          >
            <div>
              {/* Header */}
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className="w-12 h-12 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 flex items-center justify-center text-emerald-900 shadow-spatial-xs group-hover:bg-emerald-50 transition-colors">
                  <Building2 className="w-6 h-6 text-emerald-800" />
                </div>
                <div className="flex items-center gap-2">
                  <SIFPotentialBadge potential={facility.riskLevel} size="xs" showIcon={false} />
                  <span className="font-mono text-[10px] text-ink-muted font-bold">{facility.facilityId}</span>
                </div>
              </div>

              {/* Facility Title & Type */}
              <h3 className="text-base sm:text-lg font-black text-ink-primary group-hover:text-emerald-950 transition-colors font-sans">
                {facility.shortName}
              </h3>
              <p className="text-xs text-ink-secondary mt-1 font-medium">{facility.region}</p>
              <p className="text-[11px] text-ink-muted mt-1 line-clamp-1">{facility.type}</p>

              {/* Statistics Strip */}
              <div className="mt-5 p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 space-y-2.5 text-xs shadow-spatial-xs">
                <div className="flex justify-between items-center text-ink-muted text-[11px]">
                  <span>Total Safety Reports</span>
                  <span className="font-mono font-black text-ink-primary">
                    {formatNumber(facility.totalReports)}
                  </span>
                </div>

                <div className="flex justify-between items-center text-amber-950 text-[11px] font-black">
                  <span>SIF Precursor Density</span>
                  <span className="font-mono">{facility.sifDensity}% ({facility.sifReports})</span>
                </div>

                <ProgressBar
                  value={facility.sifDensity}
                  max={35}
                  variant={facility.sifDensity > 24 ? 'crimson' : facility.sifDensity > 18 ? 'amber' : 'emerald'}
                  size="sm"
                />

                <div className="pt-2 border-t border-surface-border/50 flex justify-between items-center text-[10px] text-ink-muted">
                  <span>High Urgency: <strong className="text-red-700 font-extrabold">{facility.highUrgencyCount}</strong></span>
                  <span>Open Actions: <strong className="text-ink-primary font-extrabold">{facility.openActions}</strong></span>
                </div>
              </div>

              {/* Top Precursor Callout */}
              <div className="mt-4 text-[11px] text-ink-secondary">
                <span className="text-ink-muted">Dominant Precursor: </span>
                <span className="font-extrabold text-ink-primary">{facility.topPrecursor}</span>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-5 pt-3.5 border-t border-surface-border/60 flex items-center justify-between text-xs">
              <span className="text-[10px] text-ink-muted font-bold">
                {facility.activePersonnel} active personnel
              </span>
              <span className="flex items-center gap-1 font-extrabold text-emerald-800 group-hover:translate-x-0.5 transition-transform text-[11px]">
                <span>Safety Profile</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
