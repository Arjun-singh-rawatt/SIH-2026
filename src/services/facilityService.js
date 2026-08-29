import { mockFacilities } from '../data/mockFacilities';
import { mockReports } from '../data/mockReports';

export const facilityService = {
  async getFacilities(filters = {}) {
    await new Promise((resolve) => setTimeout(resolve, 30));
    let result = [...mockFacilities];

    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(
        (f) =>
          f.facilityName.toLowerCase().includes(q) ||
          f.region.toLowerCase().includes(q) ||
          f.topPrecursor.toLowerCase().includes(q) ||
          f.type.toLowerCase().includes(q)
      );
    }

    if (filters.region && filters.region !== 'ALL') {
      result = result.filter((f) => f.region === filters.region);
    }

    if (filters.riskLevel && filters.riskLevel !== 'ALL') {
      result = result.filter((f) => f.riskLevel === filters.riskLevel);
    }

    if (filters.sortBy === 'sifDensity') {
      result.sort((a, b) => b.sifDensity - a.sifDensity);
    } else if (filters.sortBy === 'totalReports') {
      result.sort((a, b) => b.totalReports - a.totalReports);
    }

    return result;
  },

  async getFacilityById(facilityId) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    const facility = mockFacilities.find((f) => f.facilityId === facilityId);
    if (!facility) return null;

    // Get associated reports for this facility
    const facilityReports = mockReports.filter((r) => r.facilityId === facilityId);

    return {
      ...facility,
      recentReports: facilityReports,
    };
  },
};
