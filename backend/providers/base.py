from abc import ABC, abstractmethod
from typing import Any

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        """Generate a response from the LLM provider."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up provider resources."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Perform a lightweight readiness verification."""
        pass
