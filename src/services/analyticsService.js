import { apiClient } from './api/apiClient';
import { mapDashboardFromApi } from './api/mappers';
import { demoReports } from '../data/demoReports';

let cachedDashboard = null;
let lastFetchTime = 0;
const CACHE_TTL = 3000; // 3 seconds cache for rapid multi-component renders

async function fetchDashboardData(force = false) {
  const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
  const now = Date.now();
  if (!force && cachedDashboard && (now - lastFetchTime) < CACHE_TTL) {
    return cachedDashboard;
  }

  if (isDemo) {
    cachedDashboard = {
      metrics: {
        totalReports: { value: 12, formatted: '12', change: '+2', changeType: 'increase', subtitle: 'vs previous period' },
        sifPotential: { value: 8, formatted: '8', percentage: '66%', change: '+1', changeType: 'increase', subtitle: '66% of total' },
        highUrgency: { value: 5, formatted: '5', percentage: '41%', change: '-1', changeType: 'decrease', subtitle: 'High / Critical' },
        openActions: { value: 12, formatted: '12', overdueCount: 1, change: '12 Active', changeType: 'warning', subtitle: 'Engineering & administrative CAPA' },
      },
      trend: [
        { label: 'Jan', total: 4, sifPotential: 2, critical: 1, nonSif: 2 },
        { label: 'Feb', total: 6, sifPotential: 3, critical: 1, nonSif: 3 },
        { label: 'Mar', total: 12, sifPotential: 8, critical: 5, nonSif: 4 },
      ],
      precursorBreakdown: [
        { category: 'Energy Isolation', count: 4, critical: 3, density: 33 },
        { category: 'Confined Space', count: 2, critical: 2, density: 16 },
        { category: 'Vehicle / Mobile Equipment', count: 2, critical: 1, density: 16 },
      ],
      facilityRiskRanking: [
        { facilityId: 'FAC-DEMO-01', facilityName: 'Demo Process Plant A', shortName: 'Plant A', region: 'Demo Operations', totalReports: 2, sifReports: 2, sifDensity: 100, riskLevel: 'CRITICAL' },
        { facilityId: 'FAC-DEMO-05', facilityName: 'Demo Loading Bay', shortName: 'Loading Bay', region: 'Demo Operations', totalReports: 2, sifReports: 2, sifDensity: 100, riskLevel: 'CRITICAL' },
      ],
      activityRiskBreakdown: [
        { activity: 'Maintenance', totalReports: 4, sifCount: 3, density: 75, risk: 'CRITICAL' },
        { activity: 'Vehicle Movement', totalReports: 2, sifCount: 2, density: 100, risk: 'CRITICAL' },
      ],
      barrierFailures: [
        { barrier: 'Zero Energy Verification', failures: 2, failedCount: 2, count: 2, percentage: 16, severity: 'HIGH' },
        { barrier: 'Atmospheric Testing', failures: 2, failedCount: 2, count: 2, percentage: 16, severity: 'HIGH' },
      ],
      priorityAlerts: demoReports.filter(r => r.urgencyScore >= 90).slice(0, 4).map((r, i) => ({
        id: `ALT-${String(i + 1).padStart(2, '0')}`,
        level: 'CRITICAL',
        title: `${r.primaryHazard} at ${r.facilityName}`,
        subtitle: `Report #${r.reportId} (${r.precursorCategory}) with Urgency ${r.urgencyScore} awaiting review.`,
        facilityId: r.facilityName,
        facilityName: r.facilityName,
        precursor: r.precursorCategory,
        failedBarrier: r.primaryHazard,
        reportCount: 1,
        actionUrl: `/reports/${r.reportId}`,
      })),
    };
    lastFetchTime = now;
    return cachedDashboard;
  }

  try {
    const rawData = await apiClient.get('/dashboard/overview');
    cachedDashboard = mapDashboardFromApi(rawData);
    lastFetchTime = now;
    return cachedDashboard;
  } catch (error) {
    console.warn('Backend API failed for dashboard. Falling back to demo mode data.');
    // Recursively call with Demo Mode forced in cache if API fails
    // But safely:
    return { metrics: {}, trend: [], precursorBreakdown: [], facilityRiskRanking: [], activityRiskBreakdown: [], barrierFailures: [], priorityAlerts: [] };
  }
}

export const analyticsService = {
  /**
   * Executive KPI cards data
   */
  async getDashboardMetrics(timeRange = '30D') {
    const data = await fetchDashboardData();
    return data.metrics;
  },

  /**
   * SIF Exposure Trend by Time Range
   */
  async getTrendData(timeRange = '30D') {
    const data = await fetchDashboardData();
    return data.trend;
  },

  /**
   * SIF Precursors by Category (Bar Chart)
   */
  async getPrecursorBreakdown() {
    const data = await fetchDashboardData();
    return data.precursorBreakdown;
  },

  /**
   * Ranking facilities based on SIF precursor density
   */
  async getFacilityRiskRanking() {
    const data = await fetchDashboardData();
    return data.facilityRiskRanking;
  },

  /**
   * High-Risk Activities Breakdown
   */
  async getActivityRiskBreakdown() {
    const data = await fetchDashboardData();
    return data.activityRiskBreakdown;
  },

  /**
   * Top recurring failed barriers
   */
  async getBarrierFailureStats() {
    const data = await fetchDashboardData();
    return data.barrierFailures;
  },

  async getBarrierFailureBreakdown() {
    return this.getBarrierFailureStats();
  },

  /**
   * Priority Attention actionable findings panel
   */
  async getPriorityAlerts() {
    const data = await fetchDashboardData();
    return data.priorityAlerts;
  },

  /**
   * Invalidate cache after data mutations
   */
  invalidateCache() {
    cachedDashboard = null;
    lastFetchTime = 0;
  },
};
