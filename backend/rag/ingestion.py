import logging
import uuid
from typing import List, Dict, Any
from .vector_store import get_vector_store
from .embeddings import get_embedding_service

logger = logging.getLogger("rag_ingestion")

class IngestionPipeline:
    @staticmethod
    async def ingest_document(content: str, metadata: Dict[str, Any], collection_name: str = "startup_playbooks"):
        """
        Chunks and ingests a document into Qdrant using the embedding service.
        """
        store = get_vector_store()
        embedder = get_embedding_service()
        
        # Simple chunking for demonstration (should use a proper chunker like RecursiveCharacterTextSplitter)
        chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
        
        points = []
        for i, chunk in enumerate(chunks):
            embedding = await embedder.get_embedding(chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["content"] = chunk
            
            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": chunk_metadata
            })
            
        await store.upsert_points(collection_name, points)
        logger.info(f"Ingested {len(chunks)} chunks into {collection_name}")
