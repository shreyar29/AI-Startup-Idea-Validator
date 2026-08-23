from typing import Dict, List, Any
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AgentConfig:
    """Configuration definition for an individual agent in the P2P Mesh."""
    def __init__(
        self,
        name: str,
        timeout: int,
        dependencies: List[str],
        execution_order: int,
        agent_category: str,
        max_retries: int = 3,
        weight: float = 1.0,
        is_critical: bool = False
    ):
        self.name = name
        self.timeout = timeout
        self.dependencies = dependencies
        self.execution_order = execution_order
        self.agent_category = agent_category
        self.max_retries = max_retries
        self.weight = weight
        self.is_critical = is_critical

# Centralized Registry mapping peer keys to AgentConfig definitions
AGENT_REGISTRY: Dict[str, AgentConfig] = {
    "web_search": AgentConfig(
        name="Web Search Agent",
        timeout=getattr(settings.orchestrator, "WEB_SEARCH_TIMEOUT", 120),
        dependencies=[],
        execution_order=10,
        agent_category="FOUNDATION",
        is_critical=True,
    ),
    "market": AgentConfig(
        name="Market Agent",
        timeout=getattr(settings.orchestrator, "MARKET_AGENT_TIMEOUT", 180),
        dependencies=["web_search"],
        execution_order=20,
        agent_category="FOUNDATION",
        weight=0.20,
    ),
    "customer": AgentConfig(
        name="Customer Agent",
        timeout=getattr(settings.orchestrator, "CUSTOMER_AGENT_TIMEOUT", 180),
        dependencies=["web_search"],
        execution_order=30,
        agent_category="FOUNDATION",
        weight=0.20,
    ),
    "competitor": AgentConfig(
        name="Competitor Agent",
        timeout=getattr(settings.orchestrator, "COMPETITOR_AGENT_TIMEOUT", 180),
        dependencies=["web_search"],
        execution_order=40,
        agent_category="FOUNDATION",
        weight=0.15,
    ),
    "risk": AgentConfig(
        name="Risk Agent",
        timeout=getattr(settings.orchestrator, "RISK_AGENT_TIMEOUT", getattr(settings.orchestrator, "COMPARISON_AGENT_TIMEOUT", 180)),
        dependencies=["market", "customer", "competitor"],
        execution_order=50,
        agent_category="STRATEGY",
        weight=0.15,
        is_critical=True,
    ),
    "swot": AgentConfig(
        name="SWOT Agent",
        timeout=getattr(settings.orchestrator, "SWOT_AGENT_TIMEOUT", getattr(settings.orchestrator, "COMPARISON_AGENT_TIMEOUT", 180)),
        dependencies=["risk"],
        execution_order=60,
        agent_category="STRATEGY",
        weight=0.0,
    ),
    "mvp": AgentConfig(
        name="MVP Agent",
        timeout=getattr(settings.orchestrator, "MVP_AGENT_TIMEOUT", getattr(settings.orchestrator, "COMPARISON_AGENT_TIMEOUT", 180)),
        dependencies=["swot"],
        execution_order=70,
        agent_category="STRATEGY",
        weight=0.15,
    ),
    "gtm": AgentConfig(
        name="GTM Agent",
        timeout=getattr(settings.orchestrator, "GTM_AGENT_TIMEOUT", getattr(settings.orchestrator, "COMPARISON_AGENT_TIMEOUT", 180)),
        dependencies=["mvp"],
        execution_order=80,
        agent_category="STRATEGY",
        weight=0.15,
    ),
    "startup_score": AgentConfig(
        name="Startup Score Agent",
        timeout=getattr(settings.orchestrator, "STARTUP_SCORE_AGENT_TIMEOUT", getattr(settings.orchestrator, "COMPARISON_AGENT_TIMEOUT", 180)),
        dependencies=["market", "customer", "competitor", "risk", "swot", "mvp", "gtm"],
        execution_order=90,
        agent_category="SCORING",
        weight=0.0,
    ),
    "comparison": AgentConfig(
        name="Comparison Agent",
        timeout=getattr(settings.orchestrator, "COMPARISON_AGENT_TIMEOUT", 180),
        dependencies=["startup_score"],
        execution_order=100,
        agent_category="REPORTING",
        is_critical=True,
    ),
}

def validate_architecture():
    """Validate AGENT_REGISTRY at startup for consistency."""
    orders = set()
    for key, config in AGENT_REGISTRY.items():
        # Validate uniqueness of execution_order
        if config.execution_order in orders:
            raise ValueError(f"Duplicate execution_order {config.execution_order} found in {key}")
        orders.add(config.execution_order)
        # Validate weights
        if config.weight < 0:
            raise ValueError(f"Agent '{key}' has negative weight")
        
        # Validate dependencies exist
        for dep in config.dependencies:
            if dep not in AGENT_REGISTRY:
                raise ValueError(f"Agent '{key}' has missing dependency: '{dep}'")

    # Validate circular dependencies
    visited = set()
    path = set()
    
    def dfs(node):
        if node in path:
            raise ValueError(f"Circular dependency detected involving agent '{node}'")
        if node in visited:
            return
            
        path.add(node)
        for dep in AGENT_REGISTRY[node].dependencies:
            dfs(dep)
        path.remove(node)
        visited.add(node)

    for key in AGENT_REGISTRY:
        dfs(key)

validate_architecture()
