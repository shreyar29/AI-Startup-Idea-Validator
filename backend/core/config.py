from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pydantic import Field

class AppSettings(BaseSettings):
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173")
    SECRET_KEY: str = Field(...)
    LOG_LEVEL: str = Field(default="INFO")
    REQUEST_TIMEOUT: int = Field(default=120, gt=0)
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./venturelens.db")
    
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)
    JWT_ISSUER: Optional[str] = Field(default="venturelens.ai")
    JWT_AUDIENCE: Optional[str] = Field(default="venturelens-api")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

class GuardrailSettings(BaseSettings):
    GUARDRAIL_MIN_QUERY_LENGTH: int = Field(default=5)
    GUARDRAIL_MAX_QUERY_LENGTH: int = Field(default=150)
    GUARDRAIL_MIN_CONTENT_LENGTH: int = Field(default=50)
    GUARDRAIL_MAX_CONTENT_LENGTH: int = Field(default=20000)
    GUARDRAIL_NUMERIC_TOLERANCE: float = Field(default=0.03)
    TRUSTED_DOMAINS: str = Field(default="gartner.com,mckinsey.com,statista.com,forrester.com,bloomberg.com")

    @property
    def trusted_domains_list(self) -> List[str]:
        return [d.strip().lower() for d in self.TRUSTED_DOMAINS.split(",") if d.strip()]

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

class SearchSettings(BaseSettings):
    TAVILY_API_KEY: Optional[str] = Field(default=None)
    BRAVE_API_KEY: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

class LLMSettings(BaseSettings):
    LLM_PROVIDER: str = Field(default="gemini")
    
    # Gemini
    GOOGLE_AI_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_MODEL: str = Field(default="gemini-3.5-flash")
    GEMINI_MAX_RETRIES: int = Field(default=5, ge=0)
    GEMINI_TIMEOUT: float = Field(default=120.0, gt=0)
    GEMINI_MAX_TOKENS: int = Field(default=8192, gt=0)
    GEMINI_CONCURRENCY: int = Field(default=2, gt=0)

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = Field(default=None)
    OPENROUTER_MODEL: str = Field(default="meta-llama/llama-3.1-8b-instruct:free")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1")
    OPENROUTER_MAX_RETRIES: int = Field(default=5, ge=0)
    OPENROUTER_TIMEOUT: float = Field(default=120.0, gt=0)
    OPENROUTER_MAX_TOKENS: int = Field(default=8192, gt=0)
    OPENROUTER_USE_JSON_MODE: bool = Field(default=True)
    OPENROUTER_CONCURRENCY: int = Field(default=2, gt=0)

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

class OrchestratorSettings(BaseSettings):
    WEB_SEARCH_TIMEOUT: int = Field(default=120, gt=0)
    MARKET_AGENT_TIMEOUT: int = Field(default=180, gt=0)
    CUSTOMER_AGENT_TIMEOUT: int = Field(default=180, gt=0)
    COMPETITOR_AGENT_TIMEOUT: int = Field(default=180, gt=0)
    COMPARISON_AGENT_TIMEOUT: int = Field(default=180, gt=0)

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

class AgentSettings(BaseSettings):
    # Query Strategist
    QUERY_STRATEGIST_MAX_RETRIES: int = Field(default=2, ge=0)
    
    # Market Agent
    MARKET_MAX_SNIPPETS: int = Field(default=4, gt=0)
    MARKET_MAX_SNIPPET_LENGTH: int = Field(default=500, gt=0)
    MARKET_MAX_RETRIES: int = Field(default=1, ge=0)
    MARKET_LLM_TIMEOUT: int = Field(default=90, gt=0)
    
    # Competitor Agent
    COMPETITOR_MAX_SNIPPETS: int = Field(default=4, gt=0)
    COMPETITOR_MAX_SNIPPET_LENGTH: int = Field(default=500, gt=0)
    COMPETITOR_MAX_RETRIES: int = Field(default=3, ge=0)
    COMPETITOR_LLM_TIMEOUT: int = Field(default=90, gt=0)
    
    # Comparison Agent
    COMPARISON_MAX_RETRIES: int = Field(default=3, ge=0)
    COMPARISON_LLM_TIMEOUT: int = Field(default=90, gt=0)
    
    # Customer Agent
    CUSTOMER_MAX_SNIPPETS: int = Field(default=4, gt=0)
    CUSTOMER_MAX_SNIPPET_LENGTH: int = Field(default=500, gt=0)
    CUSTOMER_LLM_TIMEOUT: int = Field(default=90, gt=0)

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

class Settings:
    """Centralized configuration singleton."""
    def __init__(self):
        self.app = AppSettings()
        self.guardrails = GuardrailSettings()
        self.search = SearchSettings()
        self.llm = LLMSettings()
        self.orchestrator = OrchestratorSettings()
        self.agent = AgentSettings()

settings = Settings()
