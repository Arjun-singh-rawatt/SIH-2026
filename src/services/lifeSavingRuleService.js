import { mockLifeSavingRules } from '../data/mockLifeSavingRules';
import { mockReports } from '../data/mockReports';

export const lifeSavingRuleService = {
  async getLifeSavingRules() {
    await new Promise((resolve) => setTimeout(resolve, 30));
    return [...mockLifeSavingRules];
  },

  async getRuleById(id) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    const rule = mockLifeSavingRules.find(
      (r) => r.id.toLowerCase() === id.toLowerCase() || r.category.toLowerCase() === id.toLowerCase()
    );
    if (!rule) return null;

    // Associated reports
    const associatedReports = mockReports.filter(
      (r) =>
        r.lifeSavingRule.toLowerCase() === rule.name.toLowerCase() ||
        r.precursorCategory.toLowerCase() === rule.category.toLowerCase()
    );

    return {
      ...rule,
      associatedReports,
    };
  },
};
