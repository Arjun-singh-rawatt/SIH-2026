import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ZapOff,
  Box,
  Target,
  Flame,
  ArrowUpCircle,
  Anchor,
  Truck,
  AlertTriangle,
  Activity,
  ArrowUpRight,
  TrendingUp,
  TrendingDown,
  Building2,
  Search,
  Loader2,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { SIFPotentialBadge } from '../components/ui/RiskBadge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { lifeSavingRuleService } from '../services/lifeSavingRuleService';
import { formatNumber } from '../utils/formatters';

const ICON_MAP = {
  ZapOff,
  Box,
  Target,
  Flame,
  ArrowUpCircle,
  Anchor,
  Truck,
  ShieldAlert,
  AlertTriangle,
  Activity,
};

export function LifeSavingRules() {
  const navigate = useNavigate();
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let isMounted = true;
    async function loadRules() {
      setLoading(true);
      try {
        const data = await lifeSavingRuleService.getLifeSavingRules();
        if (isMounted) {
          setRules(data);
        }
      } catch (err) {
        console.error('Error fetching life saving rules:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRules();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredRules = rules.filter((rule) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      rule.name.toLowerCase().includes(q) ||
      rule.category.toLowerCase().includes(q) ||
      rule.shortDescription.toLowerCase().includes(q) ||
      (rule.topActivity && rule.topActivity.toLowerCase().includes(q)) ||
      (rule.topFacility && rule.topFacility.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="IOGP Life-Saving Rules Dashboard"
        subtitle="Standardized safety rules mapped to fatal precursor reports, failure frequencies, and site exposures."
      />

      {/* Search Bar */}
      <div className="max-w-md relative">
        <Search className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter Life-Saving Rules by name or activity..."
          className="sift-input pl-11 text-xs py-2.5 rounded-full"
        />
      </div>

      {/* Rules Grid */}
      {loading ? (
        <div className="bg-white border border-surface-border/80 rounded-3.5xl p-16 text-center shadow-spatial flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-800 animate-spin" />
          <p className="text-xs font-bold text-ink-muted">Loading IOGP Life-Saving Rules metrics from SIFT API...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
          {filteredRules.map((rule) => {
            const Icon = ICON_MAP[rule.iconName] || ShieldAlert;
            const isUp = rule.trendDirection === 'up';

            return (
              <Card
                key={rule.id}
                variant="interactive"
                onClick={() => navigate(`/life-saving-rules/${rule.id}`)}
                className="p-6 sm:p-7 flex flex-col justify-between group rounded-3.5xl"
              >
                <div>
                  {/* Header with Icon and Risk Badge */}
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <div
                      className="w-12 h-12 rounded-2.5xl flex items-center justify-center border shadow-spatial-xs group-hover:scale-105 transition-transform"
                      style={{ backgroundColor: rule.bgColor || '#FAF7F2', borderColor: `${rule.color || '#044E3B'}40`, color: rule.color || '#044E3B' }}
                    >
                      <Icon className="w-6 h-6" />
                    </div>

                    <div className="flex items-center gap-2">
                      <SIFPotentialBadge potential={rule.riskLevel} size="xs" showIcon={false} />
                      <span className="font-mono text-[10px] text-ink-muted font-bold">{rule.id}</span>
                    </div>
                  </div>

                  {/* Rule Title & Short Description */}
                  <h3 className="text-base sm:text-lg font-black text-ink-primary group-hover:text-emerald-950 transition-colors font-sans">
                    {rule.name}
                  </h3>
                  <p className="text-xs text-ink-secondary mt-1.5 line-clamp-2 leading-relaxed font-normal">
                    {rule.shortDescription}
                  </p>

                  {/* Statistics Box */}
                  <div className="mt-5 p-4 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 space-y-2.5 text-xs shadow-spatial-xs">
                    <div className="flex justify-between items-center text-ink-muted text-[11px]">
                      <span>Total Flagged Reports</span>
                      <span className="font-mono font-black text-ink-primary">{formatNumber(rule.totalReports)}</span>
                    </div>

                    <div className="flex justify-between items-center text-amber-950 text-[11px] font-black">
                      <span>SIF-Potential Reports</span>
                      <span className="font-mono">{formatNumber(rule.sifReports)} ({rule.sifPercentage}%)</span>
                    </div>

                    <ProgressBar value={rule.sifPercentage} max={50} variant={rule.sifPercentage > 30 ? 'crimson' : 'amber'} size="sm" />
                  </div>

                  {/* Top Activity & Facility */}
                  <div className="mt-4 space-y-2 text-[11px] text-ink-secondary">
                    <div className="flex items-center justify-between">
                      <span className="text-ink-muted">Top Activity:</span>
                      <span className="font-extrabold text-ink-primary truncate max-w-[170px]">{rule.topActivity}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-ink-muted">Top Facility:</span>
                      <span className="font-extrabold text-ink-primary truncate max-w-[170px]">{rule.topFacility}</span>
                    </div>
                  </div>
                </div>

                {/* Card Footer */}
                <div className="mt-5 pt-3.5 border-t border-surface-border/60 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1 font-black text-[11px]">
                    {isUp ? (
                      <span className="text-amber-800 flex items-center gap-1">
                        <TrendingUp className="w-3.5 h-3.5" />
                        {rule.trend || '+4.2%'} vs last mo
                      </span>
                    ) : (
                      <span className="text-emerald-700 flex items-center gap-1">
                        <TrendingDown className="w-3.5 h-3.5" />
                        {rule.trend || '-2.1%'} vs last mo
                      </span>
                    )}
                  </div>

                  <span className="flex items-center gap-1 font-extrabold text-emerald-800 group-hover:translate-x-0.5 transition-transform text-[11px]">
                    <span>Rule Details</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
