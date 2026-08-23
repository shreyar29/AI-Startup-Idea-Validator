import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RAGAnalyticsService:
    _metrics = {
        "query_count": 0,
        "retrieval_count": 0,
        "retrieved_chunks": 0,
        "total_embedding_latency": 0.0,
        "total_retrieval_latency": 0.0,
        "token_usage": 0,
        "cost_estimation": 0.0,
        "confidence_distribution": {"high": 0, "medium": 0, "low": 0}
    }

    @classmethod
    def track_query(cls):
        cls._metrics["query_count"] += 1

    @classmethod
    def track_retrieval(cls, chunk_count: int, latency: float):
        cls._metrics["retrieval_count"] += 1
        cls._metrics["retrieved_chunks"] += chunk_count
        cls._metrics["total_retrieval_latency"] += latency

    @classmethod
    def track_embedding(cls, latency: float, tokens: int, cost: float):
        cls._metrics["total_embedding_latency"] += latency
        cls._metrics["token_usage"] += tokens
        cls._metrics["cost_estimation"] += cost

    @classmethod
    def track_confidence(cls, confidence: str):
        c = confidence.lower()
        if c in cls._metrics["confidence_distribution"]:
            cls._metrics["confidence_distribution"][c] += 1

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        return cls._metrics.copy()
