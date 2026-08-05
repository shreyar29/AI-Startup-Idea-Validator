class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""
    pass

class AuthenticationError(LLMProviderError):
    pass

class RateLimitError(LLMProviderError):
    pass

class TimeoutError(LLMProviderError):
    pass

class NetworkError(LLMProviderError):
    pass

class InvalidResponseError(LLMProviderError):
    pass

class ProviderConfigurationError(LLMProviderError):
    pass
