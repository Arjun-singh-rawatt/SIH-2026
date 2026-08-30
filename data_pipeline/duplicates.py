"""SIFT Duplicate & Near-Duplicate Detection Engine.

Provides deterministic SHA-256 content hashing for exact deduplication,
n-gram Jaccard token similarity for near-duplicate template matching,
and leakage-preventing cluster grouping.
"""

from enum import Enum
import re
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from data_pipeline.normalization import compute_content_hash, normalize_text


class DuplicateType(str, Enum):
    """Classification of duplication level."""
    UNIQUE = "UNIQUE"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    NEAR_DUPLICATE = "NEAR_DUPLICATE"


class NearDuplicateMatch(BaseModel):
    """Pairwise near-duplicate comparison detail."""
    record_id_a: str
    record_id_b: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    match_type: DuplicateType
    reason: str


class DuplicateResult(BaseModel):
    """Deduplication assessment for a single record within a corpus."""
    record_id: str
    content_hash: str
    duplicate_type: DuplicateType = DuplicateType.UNIQUE
    exact_duplicate_of: Optional[str] = None
    near_duplicate_matches: List[NearDuplicateMatch] = Field(default_factory=list)
    cluster_id: str = Field(..., description="Unique ID of the duplication cluster")


def _tokenize_text(text: str) -> Set[str]:
    """Extract character 3-grams and word tokens for similarity computation."""
    norm = normalize_text(text).lower()
    # Word tokens
    words = set(re.findall(r'\b\w+\b', norm))
    # 3-char n-grams
    ngrams = {norm[i:i+3] for i in range(len(norm) - 2)} if len(norm) >= 3 else set()
    return words.union(ngrams)


def compute_jaccard_similarity(tokens_a: Set[str], tokens_b: Set[str]) -> float:
    """Compute Jaccard similarity coefficient between two token sets."""
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a.intersection(tokens_b))
    union = len(tokens_a.union(tokens_b))
    return intersection / union if union > 0 else 0.0


class DuplicateDetector:
    """Deduplication and near-duplicate cluster detector."""

    def __init__(self, near_duplicate_threshold: float = 0.85):
        self.near_duplicate_threshold = near_duplicate_threshold
        self.hash_to_record: Dict[str, str] = {}
        self.record_tokens: Dict[str, Set[str]] = {}
        self.record_texts: Dict[str, str] = {}
        self.clusters: Dict[str, str] = {}  # record_id -> cluster_id
        self._next_cluster_id = 1

    def process_corpus(
        self,
        records: List[Dict[str, any]],
        id_field: str = "report_id",
        text_field: str = "raw_text",
    ) -> Tuple[Dict[str, DuplicateResult], List[NearDuplicateMatch]]:
        """Process an entire corpus of records to identify exact and near duplicates.
        
        Args:
            records: List of record dictionaries.
            id_field: Field name containing the unique ID.
            text_field: Field name containing raw narrative text.
            
        Returns:
            Tuple of (dict of record_id -> DuplicateResult, list of all NearDuplicateMatches).
        """
        results: Dict[str, DuplicateResult] = {}
        all_matches: List[NearDuplicateMatch] = []
        
        # Reset state
        self.hash_to_record.clear()
        self.record_tokens.clear()
        self.record_texts.clear()
        self.clusters.clear()
        self._next_cluster_id = 1

        # Phase 1: Exact Duplicates via SHA-256
        for rec in records:
            r_id = str(rec.get(id_field, f"REC-{len(results)}"))
            raw = str(rec.get(text_field, ""))
            c_hash = compute_content_hash(raw)
            tokens = _tokenize_text(raw)
            
            self.record_texts[r_id] = raw
            self.record_tokens[r_id] = tokens

            if c_hash in self.hash_to_record:
                # Exact duplicate found
                orig_id = self.hash_to_record[c_hash]
                cluster = self.clusters[orig_id]
                self.clusters[r_id] = cluster
                
                results[r_id] = DuplicateResult(
                    record_id=r_id,
                    content_hash=c_hash,
                    duplicate_type=DuplicateType.EXACT_DUPLICATE,
                    exact_duplicate_of=orig_id,
                    cluster_id=cluster,
                )
            else:
                self.hash_to_record[c_hash] = r_id
                cluster = f"CLUSTER-{self._next_cluster_id:04d}"
                self._next_cluster_id += 1
                self.clusters[r_id] = cluster
                
                results[r_id] = DuplicateResult(
                    record_id=r_id,
                    content_hash=c_hash,
                    duplicate_type=DuplicateType.UNIQUE,
                    cluster_id=cluster,
                )

        # Phase 2: Near-Duplicates via Pairwise Jaccard on Unique records
        unique_ids = [r_id for r_id, res in results.items() if res.duplicate_type == DuplicateType.UNIQUE]
        
        for i in range(len(unique_ids)):
            id_a = unique_ids[i]
            tokens_a = self.record_tokens[id_a]
            
            for j in range(i + 1, len(unique_ids)):
                id_b = unique_ids[j]
                tokens_b = self.record_tokens[id_b]
                
                sim = compute_jaccard_similarity(tokens_a, tokens_b)
                if sim >= self.near_duplicate_threshold:
                    match = NearDuplicateMatch(
                        record_id_a=id_a,
                        record_id_b=id_b,
                        similarity_score=round(sim, 4),
                        match_type=DuplicateType.NEAR_DUPLICATE,
                        reason=f"Token/n-gram Jaccard similarity {sim:.2%} >= threshold {self.near_duplicate_threshold:.2%}",
                    )
                    all_matches.append(match)
                    
                    # Update results
                    results[id_a].near_duplicate_matches.append(match)
                    results[id_b].near_duplicate_matches.append(match)
                    
                    if results[id_b].duplicate_type == DuplicateType.UNIQUE:
                        results[id_b].duplicate_type = DuplicateType.NEAR_DUPLICATE
                    
                    # Merge cluster IDs for near duplicates to preserve event grouping
                    cluster_a = results[id_a].cluster_id
                    cluster_b = results[id_b].cluster_id
                    if cluster_a != cluster_b:
                        # Reassign all members of cluster_b to cluster_a
                        for r_k, r_v in results.items():
                            if r_v.cluster_id == cluster_b:
                                r_v.cluster_id = cluster_a
                                self.clusters[r_k] = cluster_a

        return results, all_matches
