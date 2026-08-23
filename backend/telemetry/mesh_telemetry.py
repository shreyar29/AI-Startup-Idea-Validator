import time
import logging
from functools import wraps
from typing import Callable, Any
from .metrics_service import MetricsService

logger = logging.getLogger("telemetry")

def track_agent_metrics(agent_name: str):
    """
    Decorator to track execution time, success rate, and failures for any agent.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.perf_counter()
            status = "success"
            failure_reason = None
            
            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                status = "failed"
                failure_reason = str(e)
                raise
            finally:
                latency = time.perf_counter() - start_time
                MetricsService.record_agent_execution(
                    agent_name=agent_name,
                    latency_seconds=latency,
                    status=status,
                    failure_reason=failure_reason
                )
                logger.info(f"[{agent_name}] Telemetry recorded: {status} in {latency:.2f}s")
        return wrapper
    return decorator
