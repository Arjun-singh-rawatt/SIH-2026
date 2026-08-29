import { mockReports } from '../data/mockReports';

// In-memory reports store initialized from deterministic mock data
let inMemoryReports = [...mockReports];

export const reportService = {
  /**
   * Fetch all reports with optional filtering, search, sorting and pagination
   */
  async getReports(filters = {}) {
    // Simulated network delay for realism
    await new Promise((resolve) => setTimeout(resolve, 50));

    let result = [...inMemoryReports];

    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(
        (r) =>
          r.reportId.toLowerCase().includes(q) ||
          r.facilityName.toLowerCase().includes(q) ||
          r.rawReportText.toLowerCase().includes(q) ||
          r.activity.toLowerCase().includes(q) ||
          r.primaryHazard.toLowerCase().includes(q) ||
          r.precursorCategory.toLowerCase().includes(q)
      );
    }

    if (filters.facilityId && filters.facilityId !== 'ALL') {
      result = result.filter((r) => r.facilityId === filters.facilityId);
    }

    if (filters.region && filters.region !== 'ALL') {
      result = result.filter((r) => r.region === filters.region);
    }

    if (filters.reportType && filters.reportType !== 'ALL') {
      result = result.filter((r) => r.reportType === filters.reportType);
    }

    if (filters.sifPotential && filters.sifPotential !== 'ALL') {
      result = result.filter((r) => r.sifPotential === filters.sifPotential);
    }

    if (filters.urgencyLevel && filters.urgencyLevel !== 'ALL') {
      if (filters.urgencyLevel === 'CRITICAL') {
        result = result.filter((r) => r.urgencyScore >= 90);
      } else if (filters.urgencyLevel === 'HIGH') {
        result = result.filter((r) => r.urgencyScore >= 75 && r.urgencyScore < 90);
      } else if (filters.urgencyLevel === 'MEDIUM') {
        result = result.filter((r) => r.urgencyScore >= 50 && r.urgencyScore < 75);
      } else if (filters.urgencyLevel === 'LOW') {
        result = result.filter((r) => r.urgencyScore < 50);
      }
    }

    if (filters.lifeSavingRule && filters.lifeSavingRule !== 'ALL') {
      result = result.filter((r) => r.lifeSavingRule === filters.lifeSavingRule);
    }

    if (filters.activity && filters.activity !== 'ALL') {
      result = result.filter((r) => r.activity.toLowerCase().includes(filters.activity.toLowerCase()));
    }

    if (filters.reviewStatus && filters.reviewStatus !== 'ALL') {
      result = result.filter((r) => r.reviewStatus === filters.reviewStatus);
    }

    // Sorting
    if (filters.sortBy) {
      const order = filters.sortOrder === 'asc' ? 1 : -1;
      result.sort((a, b) => {
        if (filters.sortBy === 'urgencyScore') {
          return (a.urgencyScore - b.urgencyScore) * order;
        }
        if (filters.sortBy === 'createdAt') {
          return (new Date(a.createdAt) - new Date(b.createdAt)) * order;
        }
        if (filters.sortBy === 'confidence') {
          return (a.confidence - b.confidence) * order;
        }
        if (filters.sortBy === 'reportId') {
          return a.reportId.localeCompare(b.reportId) * order;
        }
        return 0;
      });
    } else {
      // Default sort by most recent
      result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    return result;
  },

  /**
   * Get single report by ID or reportId
   */
  async getReportById(id) {
    await new Promise((resolve) => setTimeout(resolve, 30));
    const report = inMemoryReports.find(
      (r) => r.id === id || r.reportId.toUpperCase() === id.toUpperCase()
    );
    return report || null;
  },

  /**
   * Update Human-in-the-Loop review status
   */
  async updateReportReview(reportId, reviewUpdate) {
    await new Promise((resolve) => setTimeout(resolve, 50));
    const index = inMemoryReports.findIndex(
      (r) => r.id === reportId || r.reportId.toUpperCase() === reportId.toUpperCase()
    );

    if (index !== -1) {
      inMemoryReports[index] = {
        ...inMemoryReports[index],
        ...reviewUpdate,
        reviewedAt: new Date().toISOString(),
      };
      return inMemoryReports[index];
    }
    throw new Error('Report not found');
  },

  /**
   * Add a new safety report (e.g. from live analyze page)
   */
  async createReport(reportData) {
    await new Promise((resolve) => setTimeout(resolve, 50));
    const newId = `rep-${String(inMemoryReports.length + 1).padStart(3, '0')}`;
    const nextSeq = 124 + inMemoryReports.length;
    const newReport = {
      id: newId,
      reportId: `SIF-2026-00${nextSeq}`,
      createdAt: new Date().toISOString(),
      reviewStatus: 'PENDING',
      ...reportData,
    };
    inMemoryReports.unshift(newReport);
    return newReport;
  },

  /**
   * Fetch prioritized items for Review Queue
   */
  async getReviewQueue(filterType = 'ALL') {
    await new Promise((resolve) => setTimeout(resolve, 40));
    let items = [...inMemoryReports];

    if (filterType === 'UNREVIEWED') {
      items = items.filter((r) => r.reviewStatus === 'PENDING');
    } else if (filterType === 'CRITICAL_HIGH') {
      items = items.filter((r) => r.sifPotential === 'CRITICAL' || r.sifPotential === 'HIGH');
    } else if (filterType === 'LOW_CONFIDENCE') {
      items = items.filter((r) => r.confidence < 90);
    }

    // Order by urgency and pending status first
    items.sort((a, b) => {
      if (a.reviewStatus === 'PENDING' && b.reviewStatus !== 'PENDING') return -1;
      if (a.reviewStatus !== 'PENDING' && b.reviewStatus === 'PENDING') return 1;
      return b.urgencyScore - a.urgencyScore;
    });

    return items;
  },

  /**
   * Calculate summary statistics across reports
   */
  getReportStats(reports = inMemoryReports) {
    const total = reports.length;
    const sifCount = reports.filter((r) => r.sifPotential === 'HIGH' || r.sifPotential === 'CRITICAL').length;
    const criticalCount = reports.filter((r) => r.sifPotential === 'CRITICAL').length;
    const pendingReviewCount = reports.filter((r) => r.reviewStatus === 'PENDING').length;
    const avgConfidence = total > 0 ? Math.round(reports.reduce((sum, r) => sum + (r.confidence || 0), 0) / total) : 0;

    return {
      total,
      sifCount,
      sifPercentage: total > 0 ? Number(((sifCount / total) * 100).toFixed(1)) : 0,
      criticalCount,
      pendingReviewCount,
      avgConfidence,
    };
  }
};
