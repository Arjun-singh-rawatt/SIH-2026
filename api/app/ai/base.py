"""AI Provider Abstract Protocol."""

from typing import Protocol
from app.schemas.analysis import AnalyzeRequest, ReportAnalysisResult


class AIProvider(Protocol):
    """Abstract interface for AI NLP safety report analysis providers.
    
    Implementations (Mock, Gemini, HuggingFace, OpenAI, Custom ML) must adhere
    to this protocol, ensuring loose coupling with FastAPI routing logic.
    """

    async def analyze_report(self, request: AnalyzeRequest) -> ReportAnalysisResult:
        """Process free-text report narrative and return structured validated SIF assessment."""
        ...
