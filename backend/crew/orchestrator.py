from crewai import Crew, Process
from utils.logger import get_logger
from .tools import WebSearchTool, MarketAnalysisTool
from .agents import OrchestrationAgents
from .tasks import OrchestrationTasks

logger = get_logger(__name__)

class CrewOrchestrator:
    """
    CrewAI Orchestrator for the validation pipeline.
    It encapsulates the CrewAI logic, tools, agents, and tasks,
    providing a clean interface that guarantees exact backward compatibility.
    """
    def __init__(self):
        # We initialize factories here. 
        # The tools and crew are instantiated per-request in `run()` to ensure thread-safety.
        self.agents = OrchestrationAgents()
        self.tasks = OrchestrationTasks()
        
    def _create_crew(self, startup_idea: str, shared_state: dict) -> Crew:
        web_search_tool = WebSearchTool(shared_state=shared_state)
        market_analysis_tool = MarketAnalysisTool(shared_state=shared_state)
        
        orchestrator_agent = self.agents.orchestrator_agent(
            tools=[web_search_tool, market_analysis_tool]
        )
        
        web_search_task = self.tasks.web_search_task(
            agent=orchestrator_agent, 
            startup_idea=startup_idea
        )
        
        market_analysis_task = self.tasks.market_analysis_task(
            agent=orchestrator_agent,
            startup_idea=startup_idea
        )
        
        return Crew(
            agents=[orchestrator_agent],
            tasks=[web_search_task, market_analysis_task],
            process=Process.sequential,
            verbose=True
        )

    def run(self, startup_idea: str) -> dict:
        """
        Executes the CrewAI orchestration and returns the EXACT structured JSON
        from the primary Web Search Agent AND the Market Opportunity Agent.
        """
        logger.info(f"Starting CrewAI orchestration for idea: {startup_idea}")
        
        # Thread-safe state for this specific execution
        shared_state = {}
        crew = self._create_crew(startup_idea, shared_state)
        
        # Kickoff the CrewAI process
        try:
            crew.kickoff()
        except Exception as e:
            logger.exception("CrewAI orchestration failed during kickoff.")
            raise e
            
        # Extract the exact JSON results directly from the shared state
        web_search_result = shared_state.get("web_search_result")
        market_analysis_result = shared_state.get("market_analysis_result")
        
        if not web_search_result:
            raise RuntimeError("The Web Search Tool did not produce any result.")
        if not market_analysis_result:
            raise RuntimeError("The Market Analysis Tool did not produce any result.")
            
        logger.info("CrewAI orchestration completed successfully, returning combined JSON output.")
        
        return {
            "web_search": web_search_result,
            "market_analysis": market_analysis_result
        }
