import { apiClient } from './api/apiClient';
import { mapLifeSavingRuleFromApi } from './api/mappers';

export const lifeSavingRuleService = {
  /**
   * Fetch all IOGP Life-Saving Rules with calculated failure statistics
   */
  async getLifeSavingRules() {
    const response = await apiClient.get('/life-saving-rules');
    return (response || []).map(mapLifeSavingRuleFromApi);
  },

  /**
   * Fetch specific Life-Saving Rule details with associated reports
   */
  async getRuleById(id) {
    if (!id) return null;
    const response = await apiClient.get(`/life-saving-rules/${id}`);
    return mapLifeSavingRuleFromApi(response);
  },
};
