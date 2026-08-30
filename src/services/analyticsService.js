import { apiClient } from './api/apiClient';
import { mapDashboardFromApi } from './api/mappers';

let cachedDashboard = null;
let lastFetchTime = 0;
const CACHE_TTL = 3000; // 3 seconds cache for rapid multi-component renders

async function fetchDashboardData(force = false) {
  const now = Date.now();
  if (!force && cachedDashboard && (now - lastFetchTime) < CACHE_TTL) {
    return cachedDashboard;
  }
  const rawData = await apiClient.get('/dashboard/overview');
  cachedDashboard = mapDashboardFromApi(rawData);
  lastFetchTime = now;
  return cachedDashboard;
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
