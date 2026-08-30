"""In-memory Mock Vector Store and Deterministic Embedding Provider."""

import math
import hashlib
from typing import List, Dict, Any, Optional
from app.schemas.vector import VectorRecord, VectorMatch


class MockEmbeddingProvider:
    """Generates deterministic pseudo-dense vector embeddings based on text hash and tokens."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    async def embed_text(self, text: str) -> List[float]:
        tokens = text.lower().split()
        vector = [0.0] * self.dimension

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            val = (h % 100) / 100.0
            vector[idx] += val

        # Normalize to unit vector
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(t) for t in texts]


class MockVectorStore:
    """In-memory vector store implementing cosine similarity search."""

    def __init__(self):
        self._store: Dict[str, VectorRecord] = {}

    async def upsert(self, record: VectorRecord) -> bool:
        self._store[record.id] = record
        return True

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorMatch]:
        matches: List[VectorMatch] = []

        def cosine_similarity(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

        for rec in self._store.values():
            # Apply metadata filter if provided
            if filter:
                match_filter = True
                for k, v in filter.items():
                    if rec.metadata.get(k) != v:
                        match_filter = False
                        break
                if not match_filter:
                    continue

            score = cosine_similarity(vector, rec.values)
            # Map into positive range 0.70 - 0.99 for display
            display_score = round(0.70 + (max(0.0, score) * 0.28), 3)
            matches.append(VectorMatch(id=rec.id, score=display_score, metadata=rec.metadata))

        # Sort by similarity score descending
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:top_k]

    async def delete(self, vector_id: str) -> bool:
        if vector_id in self._store:
            del self._store[vector_id]
            return True
        return False

    async def health_check(self) -> bool:
        return True
