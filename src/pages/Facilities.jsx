import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  MapPin,
  ShieldAlert,
  ArrowUpRight,
  TrendingUp,
  Search,
  Loader2,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { SIFPotentialBadge } from '../components/ui/RiskBadge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { facilityService } from '../services/facilityService';
import { formatNumber } from '../utils/formatters';

export function Facilities() {
  const navigate = useNavigate();
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [regionFilter, setRegionFilter] = useState('ALL');

  useEffect(() => {
    let isMounted = true;
    async function loadFacilities() {
      setLoading(true);
      try {
        const data = await facilityService.getFacilities();
        if (isMounted) {
          setFacilities(data);
        }
      } catch (err) {
        console.error('Error fetching facilities:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadFacilities();
    return () => {
      isMounted = false;
    };
  }, []);

  const regions = [
    'ALL',
    'Upper Assam Basin',
    'Assam Shelf',
    'Central Assam',
    'Tinsukia District',
    'Arunachal Foothills',
    'Krishna Godavari Offshore',
    'Bikaner-Nagaur Basin',
  ];

  const filtered = facilities.filter((f) => {
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
            {regions.filter((r) => r !== 'ALL').map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Facilities Cards Grid */}
      {loading ? (
        <div className="bg-white border border-surface-border/80 rounded-3.5xl p-16 text-center shadow-spatial flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-800 animate-spin" />
          <p className="text-xs font-bold text-ink-muted">Loading facilities and safety profiles from SIFT API...</p>
        </div>
      ) : (
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

                {/* Precursor Density Meter */}
                <div className="mt-5 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted">
                      SIF Precursor Density
                    </span>
                    <span className="font-mono font-black text-ink-primary">
                      {facility.sifDensity}%
                    </span>
                  </div>
                  <ProgressBar
                    value={facility.sifDensity}
                    max={50}
                    color={
                      facility.riskLevel === 'CRITICAL'
                        ? 'red'
                        : facility.riskLevel === 'HIGH'
                        ? 'amber'
                        : 'sky'
                    }
                  />
                </div>
              </div>

              {/* Bottom Quick Info */}
              <div className="pt-5 mt-5 border-t border-surface-border/60 flex items-center justify-between text-[11px]">
                <div>
                  <span className="text-[10px] text-ink-muted uppercase font-extrabold tracking-widest block">Top Precursor</span>
                  <span className="font-bold text-ink-secondary">{facility.topPrecursor}</span>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-ink-muted uppercase font-extrabold tracking-widest block">Personnel</span>
                  <span className="font-mono font-bold text-ink-primary">{facility.activePersonnel || 450}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
