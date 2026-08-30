import { apiClient } from './api/apiClient';

export const analysisService = {
  /**
   * Run multi-stage AI safety intelligence analysis on raw narrative text via FastAPI
   */
  async analyzeReportText(rawText, metadata = {}, onProgress) {
    const stages = [
      { step: 1, name: 'Normalizing and sanitizing field safety narrative...' },
      { step: 2, name: 'Extracting hazards, activities, and operational entities...' },
      { step: 3, name: 'Classifying Serious Injury & Fatality (SIF) potential...' },
      { step: 4, name: 'Evaluating safety barrier integrity and failure modes...' },
      { step: 5, name: 'Mapping IOGP Life-Saving Rules and calculating urgency score...' },
    ];

    // Trigger visual progress stepper
    if (onProgress) {
      for (const stage of stages) {
        onProgress(stage);
        await new Promise((resolve) => setTimeout(resolve, 180));
      }
    }

    const payload = {
      report_text: rawText,
      report_type: metadata.reportType || 'Near Miss',
      facility_id: metadata.facilityId || 'FAC-DIG-02',
      location: metadata.location || 'Processing Area',
      activity: metadata.activity || 'Maintenance',
    };

    const response = await apiClient.post('/reports/analyze', payload);

    return {
      sifPotential: response.sif_potential,
      sifPrecursor: response.sif_precursor,
      confidence: response.confidence,
      urgencyScore: response.urgency_score,
      precursorCategory: response.precursor_category,
      activity: response.activity,
      primaryHazard: response.primary_hazard,
      lifeSavingRule: response.life_saving_rule,
      failedBarrier: response.failed_barrier,
      barrierStatus: response.barrier_status,
      potentialConsequence: response.potential_consequence,
      evidencePhrase: response.evidence_phrase,
      evidencePhrases: response.evidence_phrases || [response.evidence_phrase],
      aiExplanation: response.ai_explanation,
    };
  },
};
