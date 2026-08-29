from typing import Dict, Type
from .base import BaseLLMProvider
from .exceptions import ProviderConfigurationError
from core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class ProviderFactory:
    """
    Factory for instantiating LLM providers based on configuration.
    Uses a registry pattern for easy extensibility without modifying core logic.
    """
    
    _registry: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a new provider class."""
        if not issubclass(provider_class, BaseLLMProvider):
            error_msg = f"Cannot register '{name}': {provider_class.__name__} does not inherit from BaseLLMProvider."
            logger.error(error_msg)
            raise ProviderConfigurationError(error_msg)
            
        name_lower = name.lower()
        if name_lower in cls._registry:
            logger.warning(f"Overwriting existing provider registration for '{name_lower}'.")
            
        cls._registry[name_lower] = provider_class
        logger.info(f"Successfully registered LLM provider: '{name_lower}'")

    @classmethod
    def validate_provider_config(cls, provider_name: str = None) -> None:
        """
        Optional startup hook to verify the provider configuration early.
        Fails fast if critical dependencies (like API keys) are missing.
        """
        name = provider_name or settings.llm.LLM_PROVIDER
        name = name.lower()
        logger.info(f"Validating configuration for provider: '{name}'")
        try:
            # Attempt instantiation to catch API key / init errors safely
            cls.create(name)
            logger.info(f"Provider '{name}' configuration validated successfully.")
        except Exception as e:
            logger.error(f"Provider validation failed for '{name}': {type(e).__name__}")
            raise ProviderConfigurationError(f"Validation failed for provider '{name}': {e}") from e

    @classmethod
    def create(cls, provider_name: str = None, **kwargs) -> BaseLLMProvider:
        """
        Create and return an instance of the configured BaseLLMProvider.
        """
        # Default to checking config if not explicitly passed
        name = provider_name or settings.llm.LLM_PROVIDER
        name = name.lower()

        logger.debug(f"Attempting to select provider: '{name}'")

        provider_class = cls._registry.get(name)
        if not provider_class:
            error_msg = f"Unknown LLM provider: '{name}'. Available providers: {list(cls._registry.keys())}"
            logger.error(error_msg)
            raise ProviderConfigurationError(error_msg)

        logger.info(f"Creating instance of provider '{name}' ({provider_class.__name__})")
        try:
            return provider_class(**kwargs)
        except Exception as e:
            logger.error(f"Failed to initialize provider '{name}': {type(e).__name__}")
            raise ProviderConfigurationError(f"Failed to initialize provider '{name}': {e}") from e

# Pre-register built-in providers
from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider

ProviderFactory.register_provider("gemini", GeminiProvider)
ProviderFactory.register_provider("google", GeminiProvider)
ProviderFactory.register_provider("openrouter", OpenRouterProvider)
