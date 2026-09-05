import { apiClient } from './api/apiClient';
import { mapReportFromApi, mapReportToApi } from './api/mappers';

export const reportService = {
  /**
   * Fetch paginated list of safety reports with filtering, searching, and sorting
   */
  async getReports(filters = {}, page = 1, pageSize = 100) {
    const queryParams = {
      page,
      page_size: pageSize,
      search: filters.search,
      facility_id: filters.facilityId,
      region: filters.region,
      report_type: filters.reportType,
      sif_potential: filters.sifPotential,
      urgency_level: filters.urgencyLevel,
      life_saving_rule: filters.lifeSavingRule,
      review_status: filters.reviewStatus,
      activity: filters.activity,
      sort_by: filters.sortBy === 'createdAt' ? 'created_at' : (filters.sortBy === 'urgencyScore' ? 'ai_urgency_score' : filters.sortBy),
      sort_order: filters.sortOrder || 'desc',
    };

    const response = await apiClient.get('/reports', queryParams);
    
    // Both worker and manager views read only the persisted API records.
    return response && response.items
      ? response.items.map(mapReportFromApi)
      : Array.isArray(response)
        ? response.map(mapReportFromApi)
        : [];
  },

  /**
   * Fetch single report details with facility, barriers, and actions
   */
  async getReportById(id) {
    if (!id) return null;
    const response = await apiClient.get(`/reports/${id}`);
    return mapReportFromApi(response);
  },

  /**
   * Fetch aggregate statistics across all reports
   */
  async getReportStats() {
    const response = await apiClient.get('/reports/stats');
    return {
      total: response.total_count,
      sifCount: response.sif_count,
      sifPercentage: response.sif_density,
      criticalCount: response.high_urgency_count,
      pendingReviewCount: response.pending_review_count,
      avgConfidence: 94,
    };
  },

  /**
   * Ingest and create a new safety observation with automated AI classification
   */
  async createReport(reportData) {
    const payload = mapReportToApi(reportData);
    const response = await apiClient.post('/reports', payload);
    return mapReportFromApi(response);
  },

  /**
   * Update report fields
   */
  async updateReport(reportId, updateData) {
    const response = await apiClient.patch(`/reports/${reportId}`, updateData);
    return mapReportFromApi(response);
  },

  /**
   * Delete report
   */
  async deleteReport(reportId) {
    return apiClient.delete(`/reports/${reportId}`);
  },

  /**
   * Fetch human-in-the-loop review queue items
   */
  async getReviewQueue(tab = 'PENDING', page = 1, pageSize = 50) {
    const response = await apiClient.get('/reviews/queue', {
      tab,
      page,
      page_size: pageSize,
    });
    if (response && response.items) {
      return response.items.map(mapReportFromApi);
    }
    return [];
  },

  /**
   * Fetch review queue summary counters
   */
  async getReviewSummary() {
    const response = await apiClient.get('/reviews/summary');
    return {
      pendingCount: response.pending_count,
      criticalCount: response.critical_count,
      lowConfidenceCount: response.low_confidence_count,
      totalCount: response.total_count,
    };
  },

  /**
   * Submit Human-in-the-Loop review sign-off or reclassification
   */
  async updateReportReview(reportId, reviewUpdate) {
    const payload = {
      action: reviewUpdate.action || 'APPROVE',
      reviewer_id: reviewUpdate.reviewerId || 'USR-001',
      reviewer_name: reviewUpdate.reviewerName || 'Alok Sharma',
      reviewer_notes: reviewUpdate.reviewerNotes || reviewUpdate.notes,
      final_sif_potential: reviewUpdate.finalSifPotential || reviewUpdate.sifPotential,
      final_sif_precursor: reviewUpdate.finalSifPrecursor || reviewUpdate.sifPrecursor,
      final_life_saving_rule: reviewUpdate.finalLifeSavingRule || reviewUpdate.lifeSavingRule,
      final_failed_barrier: reviewUpdate.finalFailedBarrier || reviewUpdate.failedBarrier,
      final_barrier_status: reviewUpdate.finalBarrierStatus || reviewUpdate.barrierStatus,
    };

    const response = await apiClient.post(`/reports/${reportId}/review`, payload);
    return mapReportFromApi(response);
  },

  /**
   * Client-side calculation helper for filtered arrays
   */
  getReportStatsFromList(reports = []) {
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
  },
};
