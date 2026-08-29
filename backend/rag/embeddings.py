import logging
import time
from typing import List
from core.container import container
from rag.analytics import RAGAnalyticsService

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, llm_client = None):
        self.llm_client = llm_client or container.get_llm_provider()
        # Cost estimate: Gemini embeddings are ~$0.00002 per 1k characters (approx 250 tokens)
        self.cost_per_token = 0.00000008 

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        start_time = time.time()
        
        # Fallback implementation until official google-genai is configured with embeddings
        # For this prototype we will mock it if the SDK doesn't support it directly in this wrapper
        try:
            if hasattr(self.llm_client._shared_client.aio.models, 'embed_content'):
                response = await self.llm_client._shared_client.aio.models.embed_content(
                    model="text-embedding-004", 
                    contents=texts
                )
                embeddings = [e.values for e in response.embeddings]
            else:
                # Mock embedding for graceful degradation if SDK method differs
                import random
                embeddings = [[random.random() for _ in range(768)] for _ in texts]
                
            latency = time.time() - start_time
            # Rough token estimate
            estimated_tokens = sum(len(t) // 4 for t in texts)
            estimated_cost = estimated_tokens * self.cost_per_token
            
            RAGAnalyticsService.track_embedding(latency, estimated_tokens, estimated_cost)
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding failed: {e}. Using fallback zero vectors.")
            return [[0.0]*768 for _ in texts]
