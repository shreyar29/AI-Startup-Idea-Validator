from typing import Dict, Type
from .base import BaseLLMProvider
from .exceptions import ProviderConfigurationError
from core.config import settings

class ProviderFactory:
    """
    Factory for instantiating LLM providers based on configuration.
    Uses a registry pattern for easy extensibility without modifying core logic.
    """
    
    _registry: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a new provider class."""
        cls._registry[name.lower()] = provider_class

    @classmethod
    def create(cls, provider_name: str = None, **kwargs) -> BaseLLMProvider:
        """
        Create and return an instance of the configured BaseLLMProvider.
        """
        # Default to checking config if not explicitly passed
        name = provider_name or settings.llm.LLM_PROVIDER
        name = name.lower()

        provider_class = cls._registry.get(name)
        if not provider_class:
            raise ProviderConfigurationError(
                f"Unknown LLM provider: '{name}'. "
                f"Available providers: {list(cls._registry.keys())}"
            )

        return provider_class(**kwargs)

# Pre-register built-in providers
from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider

ProviderFactory.register_provider("gemini", GeminiProvider)
ProviderFactory.register_provider("google", GeminiProvider)
ProviderFactory.register_provider("openrouter", OpenRouterProvider)
