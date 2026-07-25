from crewai import Task
from utils.logger import get_logger

logger = get_logger(__name__)

class OrchestrationTasks:
    """
    Defines CrewAI tasks for the orchestration layer.
    """
    def web_search_task(self, agent, startup_idea: str) -> Task:
        logger.info(f"Creating Web Search Task for idea: {startup_idea}")
        return Task(
            description=(
                f'Execute the web_search_agent_tool for the startup idea: "{startup_idea}". '
                'Wait for the tool to finish and then output a confirmation that it successfully completed.'
            ),
            expected_output='A confirmation string that the web search tool ran successfully.',
            agent=agent
        )

    def market_analysis_task(self, agent, startup_idea: str) -> Task:
        logger.info(f"Creating Market Analysis Task for idea: {startup_idea}")
        return Task(
            description=(
                f'After the web search completes, execute the market_analysis_tool for the startup idea: "{startup_idea}". '
                'Wait for the tool to finish and then output a confirmation that the market analysis is complete.'
            ),
            expected_output='A confirmation string that the market analysis tool ran successfully.',
            agent=agent
        )
