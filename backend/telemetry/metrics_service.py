import logging
from typing import Dict, Any, List

logger = logging.getLogger("metrics_service")

class MetricsService:
    _agent_stats: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def record_agent_execution(cls, agent_name: str, latency_seconds: float, status: str, failure_reason: str = None, request_id: str = None, report_id: str = None, session_id: str = None):
        if agent_name not in cls._agent_stats:
            cls._agent_stats[agent_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_latency": 0.0,
                "avg_latency": 0.0,
                "failures": []
            }
            
        stats = cls._agent_stats[agent_name]
        stats["total_calls"] += 1
        stats["total_latency"] += latency_seconds
        stats["avg_latency"] = stats["total_latency"] / stats["total_calls"]
        
        if status == "success":
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
            if failure_reason:
                stats["failures"].append(failure_reason)
                # Keep last 10 failures
                if len(stats["failures"]) > 10:
                    stats["failures"] = stats["failures"][-10:]
                    
    @classmethod
    def get_mesh_health(cls) -> Dict[str, Any]:
        total_calls = sum(stats["total_calls"] for stats in cls._agent_stats.values())
        successful_calls = sum(stats["successful_calls"] for stats in cls._agent_stats.values())
        
        health_score = 100
        if total_calls > 0:
            health_score = int((successful_calls / total_calls) * 100)
            
        return {
            "mesh_health": health_score,
            "agent_stats": cls._agent_stats,
            "token_usage": {}, # Will be integrated with CostTrackingService
            "active_nodes": len(cls._agent_stats)
        }
