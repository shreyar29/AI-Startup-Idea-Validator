import os
from crewai import Agent
from utils.logger import get_logger

logger = get_logger(__name__)

class OrchestrationAgents:
    """
    Defines CrewAI agents for the orchestration layer.
    Maintains modularity so future agents can be added cleanly.
    """
    def __init__(self):
        # Configure LLM for CrewAI to use OpenRouter, falling back to basic if needed.
        self.model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
        if "openrouter" not in self.model_name.lower():
            self.model_name = f"openrouter/{self.model_name}"
            
        # We also need to map OPENROUTER_API_KEY if not already using LiteLLM envs
        if not os.getenv("OPENAI_API_KEY") and os.getenv("OPENROUTER_API_KEY"):
            # CrewAI via LiteLLM often checks OPENAI_API_KEY depending on exact version/adapter. 
            # LiteLLM native openrouter format uses OPENROUTER_API_KEY directly.
            pass

    def orchestrator_agent(self, tools) -> Agent:
        logger.info("Initializing Orchestrator Agent.")
        return Agent(
            role='Chief Orchestrator',
            goal='Execute the Web Search validation tool for the given startup idea.',
            backstory=(
                'You are an expert startup validation orchestrator. Your only job is to delegate '
                'the validation workload to your specialized web search tool and report completion.'
            ),
            tools=tools,
            verbose=True,
            allow_delegation=False,
            # Let CrewAI use its defaults or configured LiteLLM environment. 
            # This is sufficient for simply calling a tool.
        )
