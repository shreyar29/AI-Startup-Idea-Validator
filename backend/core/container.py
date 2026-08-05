"""
Lightweight service container for managing application dependencies and their lifecycles.
"""
from typing import Optional

from providers.base import BaseLLMProvider
from providers.provider_factory import ProviderFactory
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from crew.orchestrator import StartupValidatorOrchestrator

class Container:
    """
    Service container responsible for constructing and sharing application services.
    It ensures that expensive clients (like LLM clients) can be reused across requests.
    """
    
    def __init__(self):
        self._llm_provider: Optional[BaseLLMProvider] = None
        self._search_service: Optional[TavilySearchService] = None
        self._result_processor: Optional[ResultProcessor] = None
        self._orchestrator: Optional[StartupValidatorOrchestrator] = None

    def get_llm_provider(self) -> BaseLLMProvider:
        """Provides a shared instance of the configured LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = ProviderFactory.create()
        return self._llm_provider

    def get_search_service(self) -> TavilySearchService:
        """Provides a shared instance of TavilySearchService."""
        if self._search_service is None:
            self._search_service = TavilySearchService()
        return self._search_service

    def get_result_processor(self) -> ResultProcessor:
        """Provides a shared instance of ResultProcessor."""
        if self._result_processor is None:
            self._result_processor = ResultProcessor()
        return self._result_processor

    def get_orchestrator(self) -> StartupValidatorOrchestrator:
        """
        Provides a shared instance of the StartupValidatorOrchestrator, constructing it 
        if it does not exist by injecting its required dependencies.
        """
        if self._orchestrator is None:
            self._orchestrator = StartupValidatorOrchestrator(
                llm_client=self.get_llm_provider(),
                search_service=self.get_search_service(),
                result_processor=self.get_result_processor()
            )
        return self._orchestrator
        
    async def shutdown(self) -> None:
        """Gracefully close and cleanup all initialized services."""
        if self._llm_provider is not None:
            await self._llm_provider.close()
            self._llm_provider = None
        self._orchestrator = None

# Global singleton container instance for the application
container = Container()
