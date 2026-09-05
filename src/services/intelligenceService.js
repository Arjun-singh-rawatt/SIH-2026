import { apiClient } from './api/apiClient';
import { mapPatternFromApi } from './api/mappers';
import { mockPatterns } from '../data/mockPatterns';

export const intelligenceService = {
  /**
   * Fetch recurring SIF precursor patterns calculated from database observations
   */
  async getPatterns(filters = {}) {
    const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
    if (isDemo) {
      return mockPatterns.filter((p) => {
        if (filters.category && filters.category !== 'ALL' && p.category !== filters.category) return false;
        if (filters.riskLevel && filters.riskLevel !== 'ALL' && p.riskLevel !== filters.riskLevel) return false;
        return true;
      });
    }

    try {
      const queryParams = {
        category: filters.category,
        risk_level: filters.riskLevel,
        facility: filters.facility,
        search: filters.search,
      };

      const response = await apiClient.get('/intelligence/patterns', queryParams);
      return (response || []).map(mapPatternFromApi);
    } catch (error) {
      console.warn('Backend API failed. Using demo patterns.');
      return mockPatterns;
    }
  },

  /**
   * Fetch specific pattern details and recommended intervention
   */
  async getPatternById(patternId) {
    if (!patternId) return null;
    const response = await apiClient.get(`/intelligence/patterns/${patternId}`);
    return mapPatternFromApi(response);
  },

  /**
   * Fetch pattern overview summary KPIs
   */
  async getPatternOverview() {
    const response = await apiClient.get('/intelligence/overview');
    return {
      totalPatterns: response.total_patterns,
      criticalPatterns: response.critical_patterns,
      affectedFacilitiesCount: response.affected_facilities_count,
      dominantPrecursor: response.dominant_precursor,
    };
  },

  /**
   * Find semantically similar historical reports by report ID
   */
  async getSimilarReports(reportId, topK = 4) {
    if (!reportId) return [];
    const response = await apiClient.get(`/intelligence/similar-reports/${reportId}`, { top_k: topK });
    return (response?.matches || []).map((m) => ({
      reportId: m.report_id,
      similarity: m.similarity,
      precursorCategory: m.precursor_category,
      facilityName: m.facility_name,
      primaryHazard: m.primary_hazard,
      lifeSavingRule: m.life_saving_rule,
      sifPotential: m.sif_potential,
      rawSnippet: m.raw_snippet,
    }));
  },

  /**
   * Find semantically similar historical reports from raw text query
   */
  async querySimilarReports(queryText, topK = 4) {
    if (!queryText) return [];
    const response = await apiClient.post('/intelligence/similar-reports', {
      query_text: queryText,
      top_k: topK,
    });
    return (response?.matches || []).map((m) => ({
      reportId: m.report_id,
      similarity: m.similarity,
      precursorCategory: m.precursor_category,
      facilityName: m.facility_name,
      primaryHazard: m.primary_hazard,
      lifeSavingRule: m.life_saving_rule,
      sifPotential: m.sif_potential,
      rawSnippet: m.raw_snippet,
    }));
  },
};
