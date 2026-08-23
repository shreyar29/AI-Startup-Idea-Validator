from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class EvidenceReference(BaseModel):
    source: str
    section: Optional[str] = None
    chunk_id: str
    confidence_score: float
    retrieval_score: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChunkMetadata(BaseModel):
    source: str
    title: str
    category: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    score: Optional[float] = None
    freshness_score: float = 1.0

class RAGResponse(BaseModel):
    answer: str
    evidence_references: List[EvidenceReference] = Field(default_factory=list)
    confidence: str = Field(default="low", pattern="^(high|medium|low)$")
    
class SecurityRiskClassification(BaseModel):
    risk_level: str = Field(pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    reason: str
    action: str = Field(pattern="^(allow|warn|block)$")
