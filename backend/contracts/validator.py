import logging
from typing import Dict, Any, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("contracts.validator")

class SafeContractValidator:
    """
    Validates agent outputs against Pydantic contracts safely.
    If schema drift occurs, it logs the error and attempts to salvage data,
    rather than crashing the entire mesh network.
    """
    
    @classmethod
    def validate(cls, contract_class: Type[BaseModel], data: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """
        Validates the data against the contract_class.
        Returns the data dictionary (validated or salvaged).
        """
        try:
            instance = contract_class(**data)
            logger.debug(f"[{agent_name}] Output strictly validated against {contract_class.__name__}.")
            # Return model dump to ensure only schema fields are preserved
            return instance.model_dump()
            
        except ValidationError as e:
            logger.error(f"[{agent_name}] SCHEMA DRIFT DETECTED: Output failed validation against {contract_class.__name__}.")
            logger.error(f"Validation Errors: {e.errors()}")
            
            # Fail gracefully with detailed diagnostics
            fallback_data = {
                "status": "degraded",
                "failure_reason": f"Schema Validation Failed: {str(e)}",
                "evidence": []
            }
            
            # Attempt to rescue any valid fields that were present in the raw data
            # and that match the schema keys.
            for field in contract_class.model_fields.keys():
                if field in data and field not in ["status", "failure_reason", "generated_at", "evidence"]:
                    fallback_data[field] = data[field]
                    
            return contract_class.model_construct(**fallback_data).model_dump()
