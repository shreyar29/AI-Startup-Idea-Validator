import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("feature_flags")

class FeatureFlags:
    """
    Lightweight Feature Flag management system.
    Can be backed by Redis or LaunchDarkly. Uses an in-memory dictionary for this stub.
    """
    _flags: Dict[str, bool] = {
        "enable_rag_augmentation": True,
        "enable_sse_streaming": True,
        "enable_celery_jobs": False,
        "experimental_scoring_algorithm": False
    }

    @classmethod
    def is_enabled(cls, flag_name: str, default: bool = False) -> bool:
        # Check environment variable first for rapid overrides (e.g. FF_ENABLE_RAG=true)
        env_override = os.environ.get(f"FF_{flag_name.upper()}")
        if env_override is not None:
            return env_override.lower() == "true"
            
        # Fallback to internal flag mapping
        return cls._flags.get(flag_name, default)

    @classmethod
    def set_flag(cls, flag_name: str, value: bool):
        """
        Dynamically update a flag (e.g. from an admin endpoint).
        """
        cls._flags[flag_name] = value
        logger.info(f"Feature Flag '{flag_name}' set to {value}")
