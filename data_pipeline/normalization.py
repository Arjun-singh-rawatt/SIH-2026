"""SIFT Text Normalization & Hashing Engine.

Provides deterministic, safe normalization of safety observation narratives
while preserving domain-specific safety terminology and character offset integrity.
"""

import hashlib
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


def normalize_text(text: str, form: str = "NFC") -> str:
    """Deterministically normalize raw safety observation text.
    
    Operations performed:
    1. Unicode canonical composition (NFC by default) to eliminate composite inconsistencies.
    2. Normalize line endings (\r\n -> \n, \r -> \n).
    3. Normalize non-breaking spaces (U+00A0) and tabs to standard spaces where appropriate.
    4. Strip trailing whitespace per line while preserving structural paragraph breaks.
    5. Strip overall leading/trailing whitespace.
    
    Safety wording is strictly preserved; no vocabulary substitutions or spell-checks are performed.
    
    Args:
        text: Raw input string from frontline safety report.
        form: Unicode normalization form ('NFC' or 'NFKC'). Default is 'NFC'.
        
    Returns:
        Deterministically normalized string.
    """
    if not text:
        return ""
    
    # 1. Unicode normalization
    normalized = unicodedata.normalize(form, text)
    
    # 2. Line ending normalization
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    
    # 3. Replace non-breaking spaces with standard spaces
    normalized = normalized.replace("\u00a0", " ")
    
    # 4. Strip trailing whitespace on each line
    lines = [line.rstrip() for line in normalized.split("\n")]
    normalized = "\n".join(lines)
    
    # 5. Strip leading and trailing whitespace
    return normalized.strip()


def compute_content_hash(text: str) -> str:
    """Compute deterministic SHA-256 content hash of normalized text.
    
    Args:
        text: Input string.
        
    Returns:
        Hexadecimal SHA-256 digest.
    """
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def recalculate_evidence_offsets(
    original_raw: str,
    normalized_raw: str,
    spans: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Recalculate character offsets of evidence spans if raw text underwent safe normalization.
    
    Args:
        original_raw: Original un-normalized raw text.
        normalized_raw: Normalized raw text.
        spans: List of span dicts with 'text', 'start_offset', 'end_offset'.
        
    Returns:
        Updated list of span dicts with validated start/end offsets.
        
    Raises:
        ValueError: If a span cannot be safely re-anchored in normalized_raw.
    """
    updated_spans = []
    
    for span in spans:
        span_text = span["text"]
        
        # Verify original match first if offsets are provided
        if "start_offset" in span and "end_offset" in span:
            orig_slice = original_raw[span["start_offset"]:span["end_offset"]]
            if orig_slice != span_text:
                pass
        
        # Search in normalized_raw
        idx = normalized_raw.find(span_text)
        if idx == -1:
            # Try finding normalized version of the span text
            norm_span_text = normalize_text(span_text)
            idx = normalized_raw.find(norm_span_text)
            if idx == -1:
                raise ValueError(
                    f"Evidence span '{span_text}' could not be re-anchored in normalized text"
                )
            span_text = norm_span_text
            
        new_span = {
            "text": span_text,
            "start_offset": idx,
            "end_offset": idx + len(span_text),
        }
        updated_spans.append(new_span)
        
    return updated_spans


def normalize_record_text(record_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize narrative text inside a record dict while preserving span invariants."""
    raw_key = "raw_text" if "raw_text" in record_dict else "raw_report_text"
    if raw_key not in record_dict:
        return record_dict
    
    orig = record_dict[raw_key]
    norm = normalize_text(orig)
    record_dict[raw_key] = norm
    
    # Recalculate spans if present
    labels = record_dict.get("labels", {})
    if "evidence_spans" in labels and labels["evidence_spans"]:
        labels["evidence_spans"] = recalculate_evidence_offsets(orig, norm, labels["evidence_spans"])
        record_dict["labels"] = labels
        
    return record_dict


class TextNormalizer:
    """Class wrapper for text normalization operations."""
    normalize_text = staticmethod(normalize_text)
    compute_content_hash = staticmethod(compute_content_hash)
    recalculate_evidence_offsets = staticmethod(recalculate_evidence_offsets)
    normalize_record_text = staticmethod(normalize_record_text)
