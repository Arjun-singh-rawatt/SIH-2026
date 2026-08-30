import { apiClient } from './api/apiClient';
import { mapFacilityFromApi, mapReportFromApi } from './api/mappers';

export const facilityService = {
  /**
   * Fetch all operational facilities
   */
  async getFacilities(filters = {}) {
    const response = await apiClient.get('/facilities');
    let facilities = (response || []).map(mapFacilityFromApi);

    if (filters.search) {
      const q = filters.search.toLowerCase();
      facilities = facilities.filter(
        (f) =>
          f.facilityName.toLowerCase().includes(q) ||
          f.region.toLowerCase().includes(q) ||
          f.topPrecursor.toLowerCase().includes(q) ||
          f.type.toLowerCase().includes(q)
      );
    }

    if (filters.region && filters.region !== 'ALL') {
      facilities = facilities.filter((f) => f.region === filters.region);
    }

    if (filters.riskLevel && filters.riskLevel !== 'ALL') {
      facilities = facilities.filter((f) => f.riskLevel === filters.riskLevel);
    }

    if (filters.sortBy === 'sifDensity') {
      facilities.sort((a, b) => b.sifDensity - a.sifDensity);
    } else if (filters.sortBy === 'totalReports') {
      facilities.sort((a, b) => b.totalReports - a.totalReports);
    }

    return facilities;
  },

  /**
   * Fetch specific facility details with live KPI stats and recent reports
   */
  async getFacilityById(facilityId) {
    if (!facilityId) return null;

    const [facDetails, facStats, recentReportsRes] = await Promise.all([
      apiClient.get(`/facilities/${facilityId}`),
      apiClient.get(`/facilities/${facilityId}/stats`).catch(() => ({})),
      apiClient.get('/reports', { facility_id: facilityId, page_size: 10 }).catch(() => ({ items: [] })),
    ]);

    const mapped = mapFacilityFromApi({
      ...facDetails,
      ...facStats,
    });

    const recentReports = (recentReportsRes.items || []).map(mapReportFromApi);

    return {
      ...mapped,
      recentReports,
    };
  },
};
