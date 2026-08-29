"""
FastAPI dependency providers. These functions integrate the lightweight service container
with FastAPI's dependency injection system (Depends).
"""
from core.container import container
from crew.orchestrator import StartupValidatorOrchestrator

def get_orchestrator() -> StartupValidatorOrchestrator:
    """
    FastAPI dependency to retrieve a fully constructed StartupValidatorOrchestrator 
    from the service container.
    """
    return container.get_orchestrator()
