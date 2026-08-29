import { analyzeSafetyReport } from '../utils/mockAnalysis';

export const analysisService = {
  /**
   * Run multi-stage AI safety intelligence analysis on raw narrative text
   */
  async analyzeReportText(rawText, metadata = {}, onProgress) {
    const stages = [
      { step: 1, name: 'Normalizing and sanitizing field safety narrative...' },
      { step: 2, name: 'Extracting hazards, activities, and operational entities...' },
      { step: 3, name: 'Classifying Serious Injury & Fatality (SIF) potential...' },
      { step: 4, name: 'Evaluating safety barrier integrity and failure modes...' },
      { step: 5, name: 'Mapping IOGP Life-Saving Rules and calculating urgency score...' },
    ];

    if (onProgress) {
      for (const stage of stages) {
        onProgress(stage);
        await new Promise((resolve) => setTimeout(resolve, 260));
      }
    } else {
      await new Promise((resolve) => setTimeout(resolve, 400));
    }

    const result = analyzeSafetyReport(rawText, metadata);
    return result;
  },
};
