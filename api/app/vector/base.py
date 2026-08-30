"""Vector Storage and Embedding Provider Protocols."""

from typing import Protocol, List, Dict, Any, Optional
from app.schemas.vector import VectorMatch, VectorRecord


class EmbeddingProvider(Protocol):
    """Abstract interface for text embedding models."""

    async def embed_text(self, text: str) -> List[float]:
        """Generate a dense vector representation of input text."""
        ...

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vectors for a batch of input texts."""
        ...


class VectorStore(Protocol):
    """Abstract interface for vector database storage & similarity search."""

    async def upsert(self, record: VectorRecord) -> bool:
        """Insert or update a vector record with metadata."""
        ...

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorMatch]:
        """Query top-K similar vector embeddings matching optional metadata filter."""
        ...

    async def delete(self, vector_id: str) -> bool:
        """Remove a vector record by ID."""
        ...

    async def health_check(self) -> bool:
        """Verify vector index connectivity."""
        ...
