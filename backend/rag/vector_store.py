import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from rag.models import DocumentChunk, ChunkMetadata
import math
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = "venturelens_kb"):
        self.collection_name = collection_name
        qdrant_url = os.environ.get("QDRANT_URL", ":memory:")
        self.client = QdrantClient(location=qdrant_url)
        
        # Default vector size for text embeddings
        self.vector_size = int(os.environ.get("EMBEDDING_DIMENSIONS", "768"))
        
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_size, 
                    distance=qmodels.Distance.COSINE
                )
            )
        
    def _calculate_freshness_score(self, created_at: datetime, category: str) -> float:
        """Knowledge Freshness Engine"""
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        age_days = (now - created_at).days
        decay_rate = 0.0019 
        
        if category in ["market_reports", "competitor_research", "startup_trends"]:
            decay_rate = 0.0077
            
        score = math.exp(-decay_rate * age_days)
        return max(0.1, score)

    async def upsert(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        if not chunks:
            return
            
        points = [
            qmodels.PointStruct(
                id=chunk.id,
                vector=emb,
                payload={
                    "text": chunk.text,
                    "metadata": chunk.metadata.model_dump()
                }
            )
            for chunk, emb in zip(chunks, embeddings)
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Upserted {len(chunks)} chunks into {self.collection_name} in Qdrant")

    async def search(self, query_vector: List[float], limit: int = 5, category_filter: Optional[str] = None) -> List[DocumentChunk]:
        query_filter = None
        if category_filter:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="metadata.category",
                        match=qmodels.MatchValue(value=category_filter)
                    )
                ]
            )
            
        # Fetch more candidates to re-rank with freshness
        search_limit = limit * 3
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=search_limit
        )
        
        reranked_results = []
        for scored_point in results:
            payload = scored_point.payload
            meta_dict = payload.get("metadata", {})
            if "created_at" in meta_dict and isinstance(meta_dict["created_at"], str):
                meta_dict["created_at"] = datetime.fromisoformat(meta_dict["created_at"])
                
            metadata = ChunkMetadata(**meta_dict)
            chunk = DocumentChunk(
                id=str(scored_point.id),
                text=payload.get("text", ""),
                metadata=metadata
            )
            
            freshness = self._calculate_freshness_score(metadata.created_at, metadata.category)
            cosine_sim = scored_point.score
            final_score = (cosine_sim * 0.7) + (freshness * 0.3)
            
            chunk.score = float(cosine_sim)
            chunk.freshness_score = float(freshness)
            
            reranked_results.append((final_score, chunk))
            
        reranked_results.sort(key=lambda x: x[0], reverse=True)
        return [c for score, c in reranked_results[:limit]]
