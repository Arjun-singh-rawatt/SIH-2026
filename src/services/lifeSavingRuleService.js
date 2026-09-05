import { apiClient } from './api/apiClient';
import { mapLifeSavingRuleFromApi } from './api/mappers';
import { mockLifeSavingRules } from '../data/mockLifeSavingRules';

export const lifeSavingRuleService = {
  /**
   * Fetch all IOGP Life-Saving Rules with calculated failure statistics
   */
  async getLifeSavingRules() {
    const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
    if (isDemo) return mockLifeSavingRules;

    try {
      const response = await apiClient.get('/life-saving-rules');
      return (response || []).map(mapLifeSavingRuleFromApi);
    } catch (error) {
      console.warn('Backend API failed. Using demo life saving rules.');
      return mockLifeSavingRules;
    }
  },

  /**
   * Fetch specific Life-Saving Rule details with associated reports
   */
  async getRuleById(id) {
    if (!id) return null;
    const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
    if (isDemo) {
      return mockLifeSavingRules.find((r) => r.id === id) || null;
    }
    
    try {
      const response = await apiClient.get(`/life-saving-rules/${id}`);
      return mapLifeSavingRuleFromApi(response);
    } catch (error) {
      console.warn('Backend API failed. Using demo life saving rules.');
      return mockLifeSavingRules.find((r) => r.id === id) || null;
    }
  },
};
