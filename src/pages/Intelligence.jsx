import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Network,
  Sparkles,
  Filter,
  Building2,
  Activity,
  ShieldAlert,
  AlertTriangle,
  RotateCcw,
  Layers,
  Loader2,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { PatternCard } from '../components/intelligence/PatternCard';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { intelligenceService } from '../services/intelligenceService';
import { facilityService } from '../services/facilityService';

export function Intelligence() {
  const navigate = useNavigate();

  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [facilityFilter, setFacilityFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const [patterns, setPatterns] = useState([]);
  const [overview, setOverview] = useState({
    totalPatterns: 0,
    criticalPatterns: 0,
    affectedFacilitiesCount: 0,
    dominantPrecursor: 'Energy Isolation',
  });
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadIntelligence() {
      setLoading(true);
      try {
        const [patternsData, overviewData, facs] = await Promise.all([
          intelligenceService.getPatterns({
            category: categoryFilter,
            riskLevel: riskFilter,
            facility: facilityFilter,
            search: searchQuery,
          }),
          intelligenceService.getPatternOverview().catch(() => ({})),
          facilityService.getFacilities().catch(() => []),
        ]);

        if (isMounted) {
          setPatterns(patternsData || []);
          if (overviewData.totalPatterns) {
            setOverview(overviewData);
          }
          setFacilities(facs || []);
        }
      } catch (err) {
        console.error('Error fetching intelligence patterns:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadIntelligence();
    return () => {
      isMounted = false;
    };
  }, [categoryFilter, facilityFilter, riskFilter, searchQuery]);

  const handleResetFilters = () => {
    setCategoryFilter('ALL');
    setFacilityFilter('ALL');
    setRiskFilter('ALL');
    setSearchQuery('');
  };

  const highPriorityCount = patterns.filter((p) => p.riskLevel === 'CRITICAL').length;
  const categoriesList = Array.from(new Set(patterns.map((p) => p.category)));

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="Safety Intelligence & Pattern Detection"
        subtitle="Surfacing recurring SIF precursor patterns across facilities, activities, and failed safety barriers."
        actions={
          <Button
            variant="amber"
            size="sm"
            icon={Sparkles}
            onClick={() => navigate('/analyze')}
          >
            Analyze Live Observation
          </Button>
        }
      />

      {/* Pattern Overview KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-5">
        <Card className="p-5 sm:p-6 bg-white rounded-3.5xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
            Recurring Precursor Patterns
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-ink-primary font-sans">{overview.totalPatterns || patterns.length}</span>
            <span className="text-[10px] text-ink-muted font-bold">Clusters</span>
          </div>
        </Card>

        <Card className="p-5 sm:p-6 bg-red-50/40 border-red-200/80 rounded-3.5xl">
          <span className="text-[10px] font-black uppercase tracking-widest text-red-950 block">
            Critical Risk Patterns
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-red-950 font-sans">{overview.criticalPatterns || highPriorityCount}</span>
            <span className="text-[10px] font-black text-red-900 bg-red-100/90 px-2 py-0.2 rounded-full shadow-spatial-xs">
              High Fatality Risk
            </span>
          </div>
        </Card>

        <Card className="p-5 sm:p-6 bg-white rounded-3.5xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
            Operational Sites Affected
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black text-ink-primary font-sans">{overview.affectedFacilitiesCount || facilities.length || 10}</span>
            <span className="text-[10px] text-ink-muted font-bold">Basins & Hubs</span>
          </div>
        </Card>

        <Card className="p-5 sm:p-6 bg-amber-50/40 border-amber-200/80 rounded-3.5xl">
          <span className="text-[10px] font-black uppercase tracking-widest text-amber-950 block">
            Dominant Precursor
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-base font-black text-amber-950 truncate font-sans">{overview.dominantPrecursor || 'Energy Isolation'}</span>
            <span className="text-[10px] text-amber-900 font-mono font-extrabold">Active</span>
          </div>
        </Card>
      </div>

      {/* Interactive Pattern Filter Controls */}
      <div className="bg-white border border-surface-border/80 rounded-3.5xl p-5 sm:p-6 shadow-spatial space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter patterns by title, barrier, or activity..."
            className="sift-input text-xs w-full sm:max-w-md py-2.5 rounded-full"
          />

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            {(categoryFilter !== 'ALL' || facilityFilter !== 'ALL' || riskFilter !== 'ALL' || searchQuery) && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetFilters}
                icon={RotateCcw}
                className="text-xs"
              >
                Reset
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-3 border-t border-surface-border/60">
          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
              Precursor Category
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="sift-select w-full text-xs font-bold py-2 px-3 rounded-2xl"
            >
              <option value="ALL">All Categories</option>
              {categoriesList.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
              Risk Level
            </label>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="sift-select w-full text-xs font-bold py-2 px-3 rounded-2xl"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical Severity</option>
              <option value="HIGH">High Severity</option>
              <option value="MEDIUM">Medium Severity</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
              Target Facility
            </label>
            <select
              value={facilityFilter}
              onChange={(e) => setFacilityFilter(e.target.value)}
              className="sift-select w-full text-xs font-bold py-2 px-3 rounded-2xl"
            >
              <option value="ALL">All Facilities</option>
              {facilities.map((f) => (
                <option key={f.facilityId} value={f.shortName || f.facilityName}>{f.shortName || f.facilityName}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Detected Patterns Cards Grid */}
      {loading ? (
        <div className="bg-white border border-surface-border/80 rounded-3.5xl p-16 text-center shadow-spatial flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-800 animate-spin" />
          <p className="text-xs font-bold text-ink-muted">Aggregating cross-site precursor patterns from SIFT database...</p>
        </div>
      ) : patterns.length === 0 ? (
        <div className="p-12 text-center text-ink-muted bg-white border border-surface-border/80 rounded-3.5xl shadow-spatial">
          <Layers className="w-10 h-10 text-ink-muted mx-auto mb-2 opacity-50" />
          <h3 className="text-base font-extrabold text-ink-primary">No Patterns Match Filters</h3>
          <p className="text-xs text-ink-muted mt-1">Try resetting the filter criteria.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {patterns.map((pattern) => (
            <PatternCard key={pattern.patternId} pattern={pattern} />
          ))}
        </div>
      )}
    </div>
  );
}
