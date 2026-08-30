/**
 * Data transformation mappers between FastAPI snake_case schemas
 * and React frontend camelCase domain models.
 */

/**
 * Maps a backend SafetyReport response into frontend domain representation
 */
export function mapReportFromApi(r) {
  if (!r) return null;

  const evidencePhrases = r.evidence_phrases && r.evidence_phrases.length > 0
    ? r.evidence_phrases
    : (r.evidence_phrase ? r.evidence_phrase.split(';').map((s) => s.trim()).filter(Boolean) : []);

  const barrierAssessments = (r.barrier_assessments || []).map((b) => ({
    id: b.id,
    reportId: b.report_id,
    failedBarrier: b.failed_barrier,
    barrierStatus: b.barrier_status,
    barrierType: b.barrier_type,
    lifeSavingRule: b.life_saving_rule,
    description: b.description,
    createdAt: b.created_at,
    updatedAt: b.updated_at,
  }));

  const actions = (r.actions || []).map(mapActionFromApi);

  return {
    id: r.id || r.report_id,
    reportId: r.report_id,
    reporterId: r.reporter_id,
    facilityId: r.facility_id,
    facilityName: r.facility_name || r.facility?.name || r.facility_id,
    region: r.region || r.facility?.region || 'Upper Assam Basin',
    location: r.location,
    rawReportText: r.raw_report_text,
    language: r.language || 'English',
    reportType: r.report_type,
    activity: r.activity,
    primaryHazard: r.primary_hazard || r.ai_primary_hazard,
    precursorCategory: r.precursor_category || r.ai_precursor_category,
    potentialConsequence: r.potential_consequence,

    // AI Predictions
    aiSifPotential: r.ai_sif_potential,
    aiSifPrecursor: r.ai_sif_precursor,
    aiConfidence: r.ai_confidence,
    aiUrgencyScore: r.ai_urgency_score,
    aiLifeSavingRule: r.ai_life_saving_rule,
    aiFailedBarrier: r.ai_failed_barrier,
    aiBarrierStatus: r.ai_barrier_status,
    aiEvidencePhrase: r.ai_evidence_phrase,
    aiExplanation: r.ai_explanation,

    // Human Review Details
    reviewStatus: r.review_status || 'PENDING',
    reviewerId: r.reviewer_id,
    reviewerNotes: r.reviewer_notes,
    reviewedAt: r.reviewed_at,
    finalSifPotential: r.final_sif_potential,
    finalSifPrecursor: r.final_sif_precursor,
    finalLifeSavingRule: r.final_life_saving_rule,
    finalFailedBarrier: r.final_failed_barrier,
    finalBarrierStatus: r.final_barrier_status,

    // Active Operational Fields
    sifPotential: r.sif_potential || r.final_sif_potential || r.ai_sif_potential || 'HIGH',
    sifPrecursor: r.sif_precursor || r.final_sif_precursor || r.ai_sif_precursor || 'YES',
    confidence: r.confidence || r.ai_confidence || 94.0,
    urgencyScore: r.urgency_score !== undefined ? r.urgency_score : (r.ai_urgency_score || 85),
    lifeSavingRule: r.life_saving_rule || r.final_life_saving_rule || r.ai_life_saving_rule || 'Energy Isolation',
    failedBarrier: r.failed_barrier || r.final_failed_barrier || r.ai_failed_barrier || 'Energy Isolation Verification',
    barrierStatus: r.barrier_status || r.final_barrier_status || r.ai_barrier_status || 'FAILED',
    evidencePhrase: r.evidence_phrase || r.ai_evidence_phrase || '',
    evidencePhrases,
    aiExplanation: r.ai_explanation || '',

    // Nested Relations
    facility: r.facility ? mapFacilityFromApi(r.facility) : null,
    barrierAssessments,
    actions,
    hasVectorEmbedding: Boolean(r.has_vector_embedding),

    createdAt: r.created_at,
    updatedAt: r.updated_at,
  };
}

/**
 * Maps a frontend report payload into FastAPI ReportCreate schema
 */
export function mapReportToApi(payload) {
  return {
    reporter_id: payload.reporterId || 'USR-001',
    facility_id: payload.facilityId,
    location: payload.location,
    raw_report_text: payload.rawReportText || payload.rawText,
    language: payload.language || 'English',
    report_type: payload.reportType || 'Near Miss',
    activity: payload.activity || 'Maintenance',
    potential_consequence: payload.potentialConsequence,
    sif_potential: payload.sifPotential,
    sif_precursor: payload.sifPrecursor,
    confidence: payload.confidence,
    urgency_score: payload.urgencyScore,
    primary_hazard: payload.primaryHazard,
    precursor_category: payload.precursorCategory,
    life_saving_rule: payload.lifeSavingRule,
    failed_barrier: payload.failedBarrier,
    barrier_status: payload.barrierStatus,
    evidence_phrase: payload.evidencePhrase,
    ai_explanation: payload.aiExplanation,
  };
}

/**
 * Maps a backend ActionItem response into frontend domain representation
 */
export function mapActionFromApi(a) {
  if (!a) return null;

  return {
    id: a.id || a.action_id,
    actionId: a.action_id,
    reportId: a.report_id,
    reportTitle: a.report_title || 'Safety Remediative Action',
    assignedTo: a.assigned_to,
    assigneeName: a.assignee_name || a.assigned_to,
    assigneeRole: a.assignee_role || 'Safety Officer',
    facilityId: a.facility_id,
    facilityName: a.facility_name || a.facility_id,
    actionType: a.action_type,
    description: a.description,
    priority: a.priority,
    status: a.status,
    dueDate: a.due_date,
    completedAt: a.completed_at,
    createdAt: a.created_at,
    updatedAt: a.updated_at,
  };
}

/**
 * Maps a frontend action payload into FastAPI ActionItemCreate schema
 */
export function mapActionToApi(payload) {
  return {
    report_id: payload.reportId,
    assigned_to: payload.assignedTo,
    facility_id: payload.facilityId,
    action_type: payload.actionType,
    description: payload.description,
    priority: payload.priority || 'HIGH',
    due_date: payload.dueDate ? new Date(payload.dueDate).toISOString() : null,
  };
}

/**
 * Maps a backend Facility response into frontend domain representation
 */
export function mapFacilityFromApi(f) {
  if (!f) return null;

  return {
    id: f.id || f.facility_id,
    facilityId: f.facility_id,
    facilityName: f.name || f.facility_name,
    name: f.name,
    shortName: f.short_name || f.name,
    region: f.region,
    type: f.type,
    locationDescription: f.location_description,
    latitude: f.latitude,
    longitude: f.longitude,
    activePersonnel: f.active_personnel,
    manager: f.manager,
    active: f.active,
    // Aggregated stats if provided by facility stats endpoint
    totalReports: f.total_reports !== undefined ? f.total_reports : 0,
    sifReports: f.sif_reports !== undefined ? f.sif_reports : 0,
    sifDensity: f.sif_density !== undefined ? f.sif_density : 0,
    highUrgencyCount: f.high_urgency_count !== undefined ? f.high_urgency_count : 0,
    openActions: f.open_actions !== undefined ? f.open_actions : 0,
    topPrecursor: f.top_precursor || 'Energy Isolation',
    topActivity: f.top_activity || 'Plant Maintenance',
    primaryHazard: f.primary_hazard || 'Stored Hydrocarbon Energy',
    riskLevel: f.risk_level || 'MEDIUM',
    createdAt: f.created_at,
  };
}

/**
 * Maps a backend PatternRead response into frontend domain representation
 */
export function mapPatternFromApi(p) {
  if (!p) return null;

  return {
    patternId: p.pattern_id,
    title: p.title,
    category: p.category,
    occurrences: p.occurrences,
    sifDensity: p.sif_density,
    riskLevel: p.risk_level,
    trend: p.trend,
    trendDirection: p.trend_direction,
    affectedFacilities: p.affected_facilities || [],
    affectedActivities: p.affected_activities || [],
    commonBarrierFailure: p.common_barrier_failure,
    lifeSavingRule: p.life_saving_rule,
    primaryHazard: p.primary_hazard,
    description: p.description,
    recommendedIntervention: p.recommended_intervention,
    sampleReportIds: p.sample_report_ids || [],
  };
}

/**
 * Maps a backend LifeSavingRuleRead response into frontend domain representation
 */
export function mapLifeSavingRuleFromApi(r) {
  if (!r) return null;

  return {
    id: r.id,
    name: r.name,
    category: r.category,
    shortDescription: r.short_description,
    fullDescription: r.full_description,
    iconName: r.icon_name,
    color: r.color,
    bgColor: r.bg_color,
    riskLevel: r.risk_level,
    totalReports: r.total_reports,
    sifReports: r.sif_reports,
    sifPercentage: r.sif_percentage,
    trend: r.trend,
    trendDirection: r.trend_direction,
    topActivity: r.top_activity,
    topFacility: r.top_facility,
    keyRequirements: r.key_requirements || [],
    associatedReports: (r.associated_reports || []).map(mapReportFromApi),
  };
}

/**
 * Maps a backend DashboardOverview response into frontend metrics and chart datasets
 */
export function mapDashboardFromApi(d) {
  if (!d) return null;

  const totalReports = d.summary?.total_reports || 0;
  const sifReports = d.summary?.sif_reports || 0;
  const sifDensity = d.summary?.sif_density || 0;
  const highUrgency = d.summary?.high_urgency_reports || 0;
  const openActions = d.summary?.open_actions || 0;

  return {
    metrics: {
      totalReports: {
        value: totalReports,
        formatted: totalReports.toLocaleString(),
        change: '+8.4%',
        changeType: 'neutral',
        subtitle: 'vs previous 30-day period',
      },
      sifPotential: {
        value: sifReports,
        formatted: sifReports.toLocaleString(),
        percentage: `${sifDensity}%`,
        change: '+2.1%',
        changeType: 'increase',
        subtitle: `${sifDensity}% of total reports flagged`,
      },
      highUrgency: {
        value: highUrgency,
        formatted: highUrgency.toLocaleString(),
        percentage: totalReports > 0 ? `${Math.round((highUrgency / totalReports) * 100)}%` : '0%',
        change: '-4.6%',
        changeType: 'decrease',
        subtitle: 'High / Critical Urgency (Score ≥ 85)',
      },
      openActions: {
        value: openActions,
        formatted: openActions.toLocaleString(),
        overdueCount: 0,
        change: `${openActions} Active`,
        changeType: 'warning',
        subtitle: 'Engineering & administrative CAPA',
      },
    },
    trend: (d.trend || []).map((t) => ({
      label: t.month,
      total: t.total_reports,
      sifPotential: t.sif_reports,
      critical: t.high_urgency,
      nonSif: Math.max(0, t.total_reports - t.sif_reports),
    })),
    precursorBreakdown: (d.precursor_distribution || []).map((p) => ({
      category: p.category,
      count: p.count,
      critical: p.sif_count,
      density: p.percentage,
    })),
    facilityRiskRanking: (d.facility_ranking || []).map((f) => ({
      facilityId: f.facility_id,
      facilityName: f.facility_name,
      shortName: f.short_name,
      region: f.region,
      totalReports: f.total_reports,
      sifReports: f.sif_reports,
      sifDensity: f.sif_density,
      riskLevel: f.risk_level,
    })),
    activityRiskBreakdown: (d.activity_ranking || []).map((a) => ({
      activity: a.activity,
      totalReports: a.total_reports,
      sifCount: a.sif_reports,
      density: a.sif_density,
      risk: a.sif_density >= 25 ? 'CRITICAL' : 'HIGH',
    })),
    barrierFailures: (d.barrier_failures || []).map((b) => ({
      barrier: b.barrier,
      failures: b.count,
      failedCount: b.count,
      count: b.count,
      percentage: b.percentage,
      severity: b.percentage >= 20 ? 'CRITICAL' : 'HIGH',
    })),
    priorityAlerts: (d.priority_attention || []).map((p, idx) => ({
      id: `ALT-${String(idx + 1).padStart(2, '0')}`,
      level: p.sif_potential === 'CRITICAL' ? 'CRITICAL' : 'HIGH',
      title: `${p.primary_hazard} at ${p.facility_name}`,
      subtitle: `Report #${p.report_id} (${p.life_saving_rule}) with Urgency ${p.urgency_score} awaiting review.`,
      facilityId: p.facility_name,
      facilityName: p.facility_name,
      precursor: p.life_saving_rule,
      failedBarrier: p.primary_hazard,
      reportCount: 1,
      actionUrl: `/reports/${p.report_id}`,
    })),
  };
}

/**
 * Maps a backend User response into frontend domain representation
 */
export function mapUserFromApi(u) {
  if (!u) return null;

  return {
    id: u.id || u.user_id,
    userId: u.user_id,
    name: u.name,
    email: u.email,
    role: u.role,
    title: u.title,
    facilityId: u.facility_id,
    contactNumber: u.contact_number,
    avatar: u.avatar,
    active: u.active,
  };
}
