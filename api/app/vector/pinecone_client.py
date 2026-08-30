"""Pinecone Vector Database client implementation."""

from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.schemas.vector import VectorRecord, VectorMatch


class PineconeVectorStore:
    """Production Pinecone Serverless vector storage connector."""

    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.environment = settings.PINECONE_ENVIRONMENT
        self._client = None
        self._index = None

        if self.api_key:
            try:
                # Lazy import pinecone
                from pinecone import Pinecone
                self._client = Pinecone(api_key=self.api_key)
                self._index = self._client.Index(self.index_name)
                logger.info("Initialized Pinecone VectorStore client.")
            except Exception as e:
                logger.warning(f"Could not connect to Pinecone: {e}. Vector operations will gracefully fall back.")

    async def upsert(self, record: VectorRecord) -> bool:
        if not self._index:
            return False
        try:
            self._index.upsert(
                vectors=[
                    {
                        "id": record.id,
                        "values": record.values,
                        "metadata": record.metadata,
                    }
                ]
            )
            return True
        except Exception as e:
            logger.error(f"Pinecone upsert error: {e}")
            return False

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorMatch]:
        if not self._index:
            return []
        try:
            res = self._index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True,
            )
            matches = []
            for match in res.get("matches", []):
                matches.append(
                    VectorMatch(
                        id=match["id"],
                        score=float(match["score"]),
                        metadata=match.get("metadata", {}),
                    )
                )
            return matches
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            return []

    async def delete(self, vector_id: str) -> bool:
        if not self._index:
            return False
        try:
            self._index.delete(ids=[vector_id])
            return True
        except Exception as e:
            logger.error(f"Pinecone delete error: {e}")
            return False

    async def health_check(self) -> bool:
        return self._index is not None
