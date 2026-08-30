"""AI Analysis Orchestration Service."""

from app.ai.base import AIProvider
from app.core.logging import logger
from app.core.errors import InvalidReportException, AIProviderException
from app.schemas.analysis import AnalyzeRequest, ReportAnalysisResult
from app.utils.enums import SIFPotential, SIFPrecursor, BarrierStatus


class AnalysisService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def analyze_report(self, request: AnalyzeRequest) -> ReportAnalysisResult:
        if not request.report_text or len(request.report_text.strip()) < 5:
            raise InvalidReportException("Safety observation narrative must contain at least 5 characters.")

        try:
            # 1. Run AI analysis
            raw_result = await self.ai_provider.analyze_report(request)

            # 2. Business rule vocabulary validation & normalization
            normalized_sif_potential = raw_result.sif_potential.upper()
            if normalized_sif_potential not in [p.value for p in SIFPotential]:
                normalized_sif_potential = SIFPotential.HIGH.value

            normalized_barrier_status = raw_result.barrier_status.upper()
            if normalized_barrier_status not in [b.value for b in BarrierStatus]:
                normalized_barrier_status = BarrierStatus.FAILED.value

            # 3. Return validated result
            return ReportAnalysisResult(
                sif_potential=normalized_sif_potential,
                sif_precursor=raw_result.sif_precursor,
                confidence=round(raw_result.confidence, 1),
                urgency_score=min(100, max(0, raw_result.urgency_score)),
                precursor_category=raw_result.precursor_category,
                activity=raw_result.activity,
                primary_hazard=raw_result.primary_hazard,
                life_saving_rule=raw_result.life_saving_rule,
                failed_barrier=raw_result.failed_barrier,
                barrier_status=normalized_barrier_status,
                potential_consequence=raw_result.potential_consequence,
                evidence_phrase=raw_result.evidence_phrase,
                evidence_phrases=raw_result.evidence_phrases or [raw_result.evidence_phrase],
                ai_explanation=raw_result.ai_explanation,
            )
        except InvalidReportException:
            raise
        except Exception as e:
            logger.error(f"Error during AI analysis pipeline: {e}")
            raise AIProviderException(f"Failed to complete AI safety analysis: {str(e)}")
