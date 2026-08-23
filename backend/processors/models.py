from typing import Any
from pydantic import BaseModel, Field
from typing import Dict

class RawSearchResult(BaseModel):
    title: str = Field(default="No Title")
    url: str = Field(default="")
    content: str = Field(default="")

    def __init__(self, **data: Any):
        if data.get("title") is None:
            data["title"] = "No Title"
        if data.get("url") is None:
            data["url"] = ""
        if data.get("content") is None:
            data["content"] = ""
        super().__init__(**data)


class ProcessedSearchResult(BaseModel):
    title: str
    url: str
    content: str
    relevance_score: int
    domain: str


class ProcessingStats(BaseModel):
    total_raw_results: int
    total_accepted: int
    total_rejected_duplicates: int
    total_rejected_low_quality: int
    processing_time_seconds: float
    category_statistics: Dict[str, Dict[str, int]]
    search_confidence: str
