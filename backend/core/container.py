"""
Lightweight service container for managing application dependencies and their lifecycles.
"""
from typing import Optional
import threading
from utils.logger import get_logger

from providers.base import BaseLLMProvider
from providers.provider_factory import ProviderFactory
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from crew.orchestrator import StartupValidatorOrchestrator

logger = get_logger(__name__)

class Container:
    """
    Service container responsible for constructing and sharing application services.
    It ensures that expensive clients (like LLM clients) can be reused across requests.
    Thread-safe lazy initialization ensures singletons under concurrent access.
    """
    
    def __init__(self):
        self._llm_provider: Optional[BaseLLMProvider] = None
        self._search_service: Optional[TavilySearchService] = None
        self._result_processor: Optional[ResultProcessor] = None
        self._orchestrator: Optional[StartupValidatorOrchestrator] = None
        self._lock = threading.RLock()

    def get_llm_provider(self) -> BaseLLMProvider:
        """Provides a shared instance of the configured LLM provider."""
        if self._llm_provider is None:
            with self._lock:
                if self._llm_provider is None:
                    try:
                        self._llm_provider = ProviderFactory.create()
                        logger.info("Successfully initialized LLM provider singleton.")
                    except Exception as e:
                        logger.error(f"Failed to initialize LLM provider: {type(e).__name__}")
                        raise
        return self._llm_provider

    def get_search_service(self) -> TavilySearchService:
        """Provides a shared instance of TavilySearchService."""
        if self._search_service is None:
            with self._lock:
                if self._search_service is None:
                    try:
                        self._search_service = TavilySearchService()
                        logger.info("Successfully initialized Search Service singleton.")
                    except Exception as e:
                        logger.error(f"Failed to initialize Search Service: {type(e).__name__}")
                        raise
        return self._search_service

    def get_result_processor(self) -> ResultProcessor:
        """Provides a shared instance of ResultProcessor."""
        if self._result_processor is None:
            with self._lock:
                if self._result_processor is None:
                    try:
                        self._result_processor = ResultProcessor()
                        logger.info("Successfully initialized Result Processor singleton.")
                    except Exception as e:
                        logger.error(f"Failed to initialize Result Processor: {type(e).__name__}")
                        raise
        return self._result_processor

    def get_orchestrator(self) -> StartupValidatorOrchestrator:
        """
        Provides a shared instance of the StartupValidatorOrchestrator, constructing it 
        if it does not exist by injecting its required dependencies.
        """
        if self._orchestrator is None:
            with self._lock:
                if self._orchestrator is None:
                    try:
                        self._orchestrator = StartupValidatorOrchestrator(
                            llm_client=self.get_llm_provider(),
                            search_service=self.get_search_service(),
                            result_processor=self.get_result_processor()
                        )
                        logger.info("Successfully constructed Orchestrator and wired dependencies.")
                    except Exception as e:
                        logger.error(f"Failed to construct Orchestrator: {type(e).__name__}")
                        raise
        return self._orchestrator

    async def validate_dependencies(self) -> None:
        """
        Optional dependency warmup/validation. Detects provider misconfiguration early
        and fails fast when critical dependencies are unavailable.
        """
        logger.info("Starting startup dependency validation...")
        try:
            llm = self.get_llm_provider()
            self.get_search_service()
            self.get_result_processor()
            self.get_orchestrator()
            
            if hasattr(llm, "health_check"):
                is_healthy = await llm.health_check()
                if not is_healthy:
                    raise RuntimeError("LLM provider health check failed.")
            logger.info("All dependencies validated successfully.")
        except Exception as e:
            logger.error(f"Critical dependency validation failed: {type(e).__name__}")
            raise
        
    async def shutdown(self) -> None:
        """Gracefully close and cleanup all initialized services."""
        logger.info("Initiating graceful shutdown of managed services.")
        
        if self._orchestrator is not None:
            if hasattr(self._orchestrator, "close"):
                await self._orchestrator.close()
            self._orchestrator = None

        if self._result_processor is not None:
            if hasattr(self._result_processor, "close"):
                await self._result_processor.close()
            self._result_processor = None
            
        if self._search_service is not None:
            if hasattr(self._search_service, "close"):
                await self._search_service.close()
            self._search_service = None

        if self._llm_provider is not None:
            try:
                await self._llm_provider.close()
                logger.info("Successfully closed LLM provider connections.")
            except Exception as e:
                logger.error(f"Error closing LLM provider: {type(e).__name__}")
            finally:
                self._llm_provider = None
                
        logger.info("Service container shutdown complete.")

# Global singleton container instance for the application
container = Container()
