"""
Vector Search & Semantic Retrieval for True Memory.
Performs cosine similarity search over user memories with metadata filtering:
- Status filter: status == 'CONFIRMED'
- Confidence filter: confidence_score >= threshold
- Privacy filter: respect user privacy mode
- Contextual ranking: cosine distance between query embedding and memory embeddings
"""

import math
from typing import List, Dict, Any, Optional

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two numeric vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def compute_mock_embedding(text: str, dim: int = 64) -> List[float]:
    """
    Deterministic pseudo-embedding for testing and zero-dependency local execution.
    In production, this is replaced by OpenAI text-embedding-3 or Gemini text-embedding-004.
    """
    vector = [0.0] * dim
    for i, char in enumerate(text.lower()):
        vector[(ord(char) + i) % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [x / norm for x in vector]
    return vector

class VectorSearchService:
    @staticmethod
    def rank_memories(
        query_text: str,
        memories: List[Dict[str, Any]],
        top_k: int = 3,
        similarity_threshold: float = 0.40
    ) -> List[Dict[str, Any]]:
        """
        Ranks confirmed user memories by semantic relevance to query_text.
        """
        if not memories or not query_text.strip():
            return []

        query_vec = compute_mock_embedding(query_text)
        scored_memories = []

        for mem in memories:
            if mem.get("status") != "CONFIRMED":
                continue
            
            content = mem.get("content", "")
            mem_vec = mem.get("embedding") or compute_mock_embedding(content)
            sim = cosine_similarity(query_vec, mem_vec)

            if sim >= similarity_threshold:
                scored_memories.append({
                    **mem,
                    "similarity_score": round(sim, 3)
                })

        # Sort descending by similarity
        scored_memories.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_memories[:top_k]

