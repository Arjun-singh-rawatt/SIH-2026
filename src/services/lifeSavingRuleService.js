import { apiClient } from './api/apiClient';
import { mapLifeSavingRuleFromApi } from './api/mappers';
import { mockLifeSavingRules } from '../data/mockLifeSavingRules';

function findLocalRule(id) {
  return mockLifeSavingRules.find(
    (rule) => rule.id.toLowerCase() === String(id).toLowerCase() || rule.name.toLowerCase() === String(id).toLowerCase()
  );
}

export const lifeSavingRuleService = {
  /**
   * Fetch all IOGP Life-Saving Rules with calculated failure statistics
   */
  async getLifeSavingRules() {
    try {
      const response = await apiClient.get('/life-saving-rules');
      const rules = Array.isArray(response) ? response.map(mapLifeSavingRuleFromApi) : [];
      return rules.length ? rules : mockLifeSavingRules;
    } catch (error) {
      console.warn('Life-Saving Rules API unavailable; using local rules.', error);
      return mockLifeSavingRules;
    }
  },

  /**
   * Fetch specific Life-Saving Rule details with associated reports
   */
  async getRuleById(id) {
    if (!id) return null;
    try {
      const response = await apiClient.get(`/life-saving-rules/${id}`);
      return mapLifeSavingRuleFromApi(response) || findLocalRule(id) || null;
    } catch (error) {
      console.warn('Life-Saving Rule detail API unavailable; using local rule.', error);
      return findLocalRule(id) || null;
    }
  },
};
