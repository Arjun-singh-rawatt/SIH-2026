"""SIFT Vector Store Package."""

from app.core.config import settings
from app.vector.base import VectorStore, EmbeddingProvider
from app.vector.mock_store import MockVectorStore, MockEmbeddingProvider
from app.vector.pinecone_client import PineconeVectorStore

# Singleton in-memory store for fallback
_mock_vector_store = MockVectorStore()
_mock_embedding_provider = MockEmbeddingProvider()


def get_vector_store() -> VectorStore:
    if settings.VECTOR_STORE_PROVIDER.lower() == "pinecone" and settings.PINECONE_API_KEY:
        return PineconeVectorStore()
    return _mock_vector_store


def get_embedding_provider() -> EmbeddingProvider:
    return _mock_embedding_provider


__all__ = [
    "VectorStore",
    "EmbeddingProvider",
    "MockVectorStore",
    "MockEmbeddingProvider",
    "PineconeVectorStore",
    "get_vector_store",
    "get_embedding_provider",
]
