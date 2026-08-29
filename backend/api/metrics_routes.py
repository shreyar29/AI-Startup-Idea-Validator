from fastapi import APIRouter
from typing import Dict, Any
from telemetry.metrics_service import MetricsService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("", response_model=Dict[str, Any])
async def get_metrics():
    """
    Returns the real-time health and telemetry metrics of the Mesh Network.
    """
    return MetricsService.get_mesh_health()
