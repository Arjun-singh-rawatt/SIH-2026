"""SIFT AI Layer Package."""

from app.ai.base import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    """Factory function returning active AI provider based on configuration."""
    provider_name = settings.AI_PROVIDER.lower().strip()
    if provider_name == "mock":
        return MockAIProvider()
    # Future extension hooks (e.g. Gemini, HuggingFace) can be plugged here
    return MockAIProvider()


__all__ = ["AIProvider", "MockAIProvider", "get_ai_provider"]
