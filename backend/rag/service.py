import logging
import time
from typing import List, Optional, Tuple
from rag.models import DocumentChunk, RAGResponse, EvidenceReference
from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore
from rag.cache import CacheService
from rag.analytics import RAGAnalyticsService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embeddings = EmbeddingService()
        self.store = VectorStore()
        self.cache = CacheService()

    async def retrieve(self, query: str, limit: int = 5, category_filter: Optional[str] = None, confidence_threshold: float = 0.6) -> List[DocumentChunk]:
        """Smart Retrieval Policy"""
        RAGAnalyticsService.track_query()
        
        # Check cache
        cache_key = f"rag:{query}:{category_filter}:{limit}"
        cached_results = await self.cache.get(cache_key)
        if cached_results:
            logger.info("RAG Cache Hit")
            # Reconstruct Pydantic models
            return [DocumentChunk(**c) for c in cached_results]
            
        start_time = time.time()
        
        # 1. Embed Query
        query_vec = (await self.embeddings.get_embeddings([query]))[0]
        
        # 2. Search
        chunks = await self.store.search(query_vec, limit=limit, category_filter=category_filter)
        
        latency = time.time() - start_time
        RAGAnalyticsService.track_retrieval(len(chunks), latency)
        
        # Smart Retrieval Policy: Filter low confidence
        filtered_chunks = [c for c in chunks if c.score and c.score >= confidence_threshold]
        
        # Cache results
        if filtered_chunks:
            await self.cache.set(cache_key, [c.model_dump() for c in filtered_chunks], ttl=3600)
            
        return filtered_chunks

    async def retrieve_for_agent(self, query: str, agent_type: str) -> List[DocumentChunk]:
        """Agent Integration (Phase 6) - Selective RAG with budgeting."""
        category_map = {
            "market": "market_reports",
            "competitor": "competitor_research",
            "gtm": "gtm_frameworks",
            "mvp": "startup_playbooks"
        }
        category = category_map.get(agent_type.lower())
        # Budgeting: Max 3 chunks for agents to save tokens
        return await self.retrieve(query, limit=3, category_filter=category)

    async def get_vera_context(self, question: str, active_section: str, report_context: dict) -> Tuple[List[DocumentChunk], str]:
        """Vera Context Engine"""
        section_mapping = {
            "market": "market_analysis",
            "competitors": "competitor_analysis",
            "risks": "risk_analysis",
            "score": "startup_score_analysis"
        }
        
        target_context_key = section_mapping.get(active_section.lower(), "executive_summary")
        existing_context = report_context.get(target_context_key)
        
        # Smart Retrieval Policy: Retrieve only when context is missing or insufficient
        if existing_context and isinstance(existing_context, dict) and len(str(existing_context)) > 500:
            logger.info(f"Using existing report context for active section: {active_section}")
            return [], target_context_key
            
        logger.info(f"Report context insufficient for {active_section}. Falling back to RAG retrieval.")
        chunks = await self.retrieve(question, limit=3)
        return chunks, target_context_key

    def validate_and_build_response(self, answer: str, chunks_used: List[DocumentChunk], confidence: str) -> RAGResponse:
        """RAG Output Validation & Evidence Traceability System"""
        if not chunks_used and confidence == "high":
            logger.warning("High confidence without evidence. Downgrading to low.")
            confidence = "low"
            
        references = []
        for c in chunks_used:
            ref = EvidenceReference(
                source=c.metadata.source,
                section=c.metadata.category,
                chunk_id=c.chunk_id,
                confidence_score=c.freshness_score, # Using freshness as confidence proxy here
                retrieval_score=c.score or 0.0
            )
            references.append(ref)
            
        response = RAGResponse(
            answer=answer,
            evidence_references=references,
            confidence=confidence
        )
        RAGAnalyticsService.track_confidence(response.confidence)
        return response
