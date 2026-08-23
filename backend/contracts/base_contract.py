import logging
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger("contracts")

class BaseAgentContract(BaseModel):
    status: str = "success"
    failure_reason: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def validate_and_log(cls, data: Dict[str, Any], agent_name: str) -> "BaseAgentContract":
        """
        Validates the output of an agent against the Pydantic schema.
        Logs any schema drift, missing fields, or validation errors.
        Returns a fallback if validation completely fails.
        """
        try:
            instance = cls(**data)
            logger.info(f"[{agent_name}] Output strictly validated against {cls.__name__}.")
            return instance
        except ValidationError as e:
            logger.error(f"[{agent_name}] SCHEMA DRIFT DETECTED: Output failed validation against {cls.__name__}.")
            logger.error(f"Validation Errors: {e.errors()}")
            
            # Fail gracefully with detailed diagnostics
            fallback_data = {
                "status": "degraded",
                "failure_reason": f"Schema Validation Failed: {str(e)}",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            # Attempt to rescue any valid fields
            for field in cls.model_fields.keys():
                if field in data and field not in ["status", "failure_reason", "generated_at"]:
                    fallback_data[field] = data[field]
                    
            return cls.model_construct(**fallback_data)
