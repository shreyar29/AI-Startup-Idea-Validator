from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from enum import Enum

class ProgressStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentContext(BaseModel):
    request_id: Optional[str] = None
    idea: Dict[str, Any] = Field(default_factory=dict)
    research: Dict[str, Any] = Field(default_factory=dict)
