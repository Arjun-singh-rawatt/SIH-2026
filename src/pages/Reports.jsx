import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { FileText, Sparkles, Download, Plus, Loader2 } from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { ReportFilters } from '../components/reports/ReportFilters';
import { ReportTable } from '../components/reports/ReportTable';
import { ReportStatsBanner } from '../components/reports/ReportStatsBanner';
import { Button } from '../components/ui/Button';
import { reportService } from '../services/reportService';
import { useReportsContext } from '../context/ReportsContext';

export function Reports() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { reports: allReports, lastUpdated } = useReportsContext();

  // Read filters from URL params or state
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    facilityId: searchParams.get('facilityId') || 'ALL',
    region: searchParams.get('region') || 'ALL',
    reportType: searchParams.get('reportType') || 'ALL',
    sifPotential: searchParams.get('sifPotential') || 'ALL',
    urgencyLevel: searchParams.get('urgencyLevel') || 'ALL',
    lifeSavingRule: searchParams.get('lifeSavingRule') || 'ALL',
    reviewStatus: searchParams.get('reviewStatus') || 'ALL',
    activity: searchParams.get('activity') || 'ALL',
    sortBy: searchParams.get('sortBy') || 'createdAt',
    sortOrder: searchParams.get('sortOrder') || 'desc',
  });

  const [filteredReports, setFilteredReports] = useState([]);
  const [loading, setLoading] = useState(true);

  // Sync state changes to searchParams
  const handleFilterChange = (newFilters) => {
    const updated = { ...filters, ...newFilters };
    setFilters(updated);

    const params = new URLSearchParams();
    Object.entries(updated).forEach(([k, v]) => {
      if (v && v !== 'ALL') {
        params.set(k, v);
      }
    });
    setSearchParams(params);
  };

  const handleResetFilters = () => {
    const reset = {
      search: '',
      facilityId: 'ALL',
      region: 'ALL',
      reportType: 'ALL',
      sifPotential: 'ALL',
      urgencyLevel: 'ALL',
      lifeSavingRule: 'ALL',
      reviewStatus: 'ALL',
      activity: 'ALL',
      sortBy: 'createdAt',
      sortOrder: 'desc',
    };
    setFilters(reset);
    setSearchParams(new URLSearchParams());
  };

  const handleSort = (field) => {
    const order = filters.sortBy === field && filters.sortOrder === 'asc' ? 'desc' : 'asc';
    handleFilterChange({ sortBy: field, sortOrder: order });
  };

  // Filter against backend API
  useEffect(() => {
    let isMounted = true;
    async function filterData() {
      setLoading(true);
      try {
        const result = await reportService.getReports(filters);
        if (isMounted) {
          setFilteredReports(result);
        }
      } catch (err) {
        console.error('Error fetching reports from backend:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    filterData();
    // A worker may submit from a different device/tab. Refresh the HSE queue
    // without requiring the manager to reload the page.
    const refreshTimer = window.setInterval(filterData, 5000);
    return () => {
      isMounted = false;
      window.clearInterval(refreshTimer);
    };
  }, [filters, lastUpdated]);

  // Summary stats calculated for active filtered reports
  const stats = useMemo(() => {
    return reportService.getReportStatsFromList(filteredReports);
  }, [filteredReports]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Field Safety Reports Explorer"
        subtitle="Search, filter, and inspect AI-classified Unsafe Acts (UA), Unsafe Conditions (UC), Near Misses, and Incidents."
        actions={
          <>
            <Button
              variant="secondary"
              size="sm"
              icon={Download}
              onClick={() => {
                alert('Exporting safety reports dataset (CSV/Excel) with AI embeddings...');
              }}
            >
              Export Data
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Sparkles}
              onClick={() => navigate('/analyze')}
            >
              Analyze New Report
            </Button>
          </>
        }
      />

      {/* Summary Statistics Strip */}
      <ReportStatsBanner
        stats={stats}
        totalCount={allReports.length || filteredReports.length}
        filteredCount={filteredReports.length}
      />

      {/* Interactive Filter Bar */}
      <ReportFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {/* Main Table */}
      {loading ? (
        <div className="bg-white border border-surface-border/80 rounded-3.5xl p-12 text-center shadow-spatial flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-800 animate-spin" />
          <p className="text-xs font-bold text-ink-muted">Querying safety observations from SIFT API...</p>
        </div>
      ) : (
        <ReportTable
          reports={filteredReports}
          sortBy={filters.sortBy}
          sortOrder={filters.sortOrder}
          onSort={handleSort}
          onResetFilters={handleResetFilters}
        />
      )}
    </div>
  );
}
