from typing import Any
from .base import BaseLLMProvider
from .exceptions import (
    LLMProviderError, ProviderConfigurationError, TimeoutError as ProviderTimeoutError
)
from llm.openrouter_client import OpenRouterClient, OpenRouterConfigError

class OpenRouterProvider(BaseLLMProvider):
    """Adapter for the OpenRouterClient to conform to BaseLLMProvider."""
    
    def __init__(self, **kwargs):
        try:
            self._client = OpenRouterClient(**kwargs)
        except OpenRouterConfigError as e:
            raise ProviderConfigurationError(str(e)) from e
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize OpenRouterClient: {e}") from e

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        try:
            return await self._client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format=response_format
            )
        except OpenRouterConfigError as e:
            if "Timeout" in str(e):
                raise ProviderTimeoutError(str(e)) from e
            raise ProviderConfigurationError(str(e)) from e
        except Exception as e:
            raise LLMProviderError(str(e)) from e

    async def close(self) -> None:
        await self._client.close()

    async def health_check(self) -> bool:
        # Lightweight readiness verification
        return self._client._api_key is not None
