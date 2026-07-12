class QueryStrategistError(Exception):
    """Base exception for Query Strategist errors."""
    pass

class LLMResponseError(QueryStrategistError):
    """Exception raised when the LLM response is missing, malformed, or invalid."""
    pass

class SearchServiceError(Exception):
    """Base exception for search service errors."""
    pass

class ResultProcessingError(Exception):
    """Base exception for result processing errors."""
    pass

class WebSearchAgentError(Exception):
    """Base exception for web search agent pipeline failures."""
    pass
