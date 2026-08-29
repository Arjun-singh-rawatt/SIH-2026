import React from 'react';
import { Search, Filter, RotateCcw, X } from 'lucide-react';
import { mockFacilities } from '../../data/mockFacilities';
import { mockLifeSavingRules } from '../../data/mockLifeSavingRules';
import { Button } from '../ui/Button';

export function ReportFilters({ filters, onFilterChange, onReset }) {
  const regions = ['ALL', 'Upper Assam Basin', 'Assam Shelf', 'Central Assam', 'Tinsukia District', 'Arunachal Foothills', 'Krishna Godavari Offshore', 'Bikaner-Nagaur Basin'];
  const reportTypes = ['ALL', 'Near Miss', 'Unsafe Act', 'Unsafe Condition', 'Incident'];
  const sifPotentials = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NON-SIF'];
  const urgencyLevels = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const reviewStatuses = ['ALL', 'PENDING', 'APPROVED', 'NEEDS CORRECTION'];

  const hasActiveFilters =
    filters.search ||
    (filters.facilityId && filters.facilityId !== 'ALL') ||
    (filters.region && filters.region !== 'ALL') ||
    (filters.reportType && filters.reportType !== 'ALL') ||
    (filters.sifPotential && filters.sifPotential !== 'ALL') ||
    (filters.urgencyLevel && filters.urgencyLevel !== 'ALL') ||
    (filters.lifeSavingRule && filters.lifeSavingRule !== 'ALL') ||
    (filters.reviewStatus && filters.reviewStatus !== 'ALL');

  return (
    <div className="bg-white border border-surface-border/80 rounded-3.5xl p-5 sm:p-6 shadow-spatial mb-6 space-y-4">
      {/* Top Search and Reset Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:max-w-md">
          <Search className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            placeholder="Search report text, hazard, activity, or ID..."
            className="w-full bg-[#FAF7F2] border border-surface-border/80 text-xs sm:text-sm text-ink-primary placeholder:text-ink-muted/80 pl-10 pr-9 py-2.5 rounded-full focus:outline-none focus:ring-2 focus:ring-brand-700/20 focus:border-brand-700 focus:bg-white transition-all shadow-spatial-xs"
          />
          {filters.search && (
            <button
              onClick={() => onFilterChange({ search: '' })}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted hover:text-ink-primary p-0.5 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          {hasActiveFilters && (
            <Button
              variant="outline"
              size="sm"
              onClick={onReset}
              icon={RotateCcw}
              className="text-xs text-ink-secondary hover:text-ink-primary shadow-spatial-xs"
            >
              Reset Filters
            </Button>
          )}
        </div>
      </div>

      {/* Dropdown Filters Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-3 border-t border-surface-border/60">
        {/* SIF Potential Filter */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
            SIF Potential
          </label>
          <select
            value={filters.sifPotential || 'ALL'}
            onChange={(e) => onFilterChange({ sifPotential: e.target.value })}
            className="sift-select w-full text-xs font-bold py-1.8 px-3 rounded-2xl"
          >
            <option value="ALL">All Potentials</option>
            {sifPotentials.filter(p => p !== 'ALL').map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        {/* Urgency Score Level */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
            Urgency Score
          </label>
          <select
            value={filters.urgencyLevel || 'ALL'}
            onChange={(e) => onFilterChange({ urgencyLevel: e.target.value })}
            className="sift-select w-full text-xs font-bold py-1.8 px-3 rounded-2xl"
          >
            <option value="ALL">All Urgencies</option>
            <option value="CRITICAL">Critical (≥ 90)</option>
            <option value="HIGH">High (75 - 89)</option>
            <option value="MEDIUM">Medium (50 - 74)</option>
            <option value="LOW">Low (&lt; 50)</option>
          </select>
        </div>

        {/* Facility Filter */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
            OIL Facility
          </label>
          <select
            value={filters.facilityId || 'ALL'}
            onChange={(e) => onFilterChange({ facilityId: e.target.value })}
            className="sift-select w-full text-xs font-medium py-1.8 px-3 rounded-2xl truncate"
          >
            <option value="ALL">All Facilities</option>
            {mockFacilities.map((f) => (
              <option key={f.facilityId} value={f.facilityId}>{f.shortName}</option>
            ))}
          </select>
        </div>

        {/* Life-Saving Rule */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
            Life-Saving Rule
          </label>
          <select
            value={filters.lifeSavingRule || 'ALL'}
            onChange={(e) => onFilterChange({ lifeSavingRule: e.target.value })}
            className="sift-select w-full text-xs font-medium py-1.8 px-3 rounded-2xl truncate"
          >
            <option value="ALL">All LSR Rules</option>
            {mockLifeSavingRules.map((lsr) => (
              <option key={lsr.id} value={lsr.name}>{lsr.name}</option>
            ))}
          </select>
        </div>

        {/* Report Type */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
            Report Type
          </label>
          <select
            value={filters.reportType || 'ALL'}
            onChange={(e) => onFilterChange({ reportType: e.target.value })}
            className="sift-select w-full text-xs font-medium py-1.8 px-3 rounded-2xl"
          >
            <option value="ALL">All Types</option>
            {reportTypes.filter(t => t !== 'ALL').map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        {/* Review Status */}
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
            Review Status
          </label>
          <select
            value={filters.reviewStatus || 'ALL'}
            onChange={(e) => onFilterChange({ reviewStatus: e.target.value })}
            className="sift-select w-full text-xs font-bold py-1.8 px-3 rounded-2xl"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="APPROVED">Approved</option>
            <option value="NEEDS CORRECTION">Needs Correction</option>
          </select>
        </div>
      </div>
    </div>
  );
}
