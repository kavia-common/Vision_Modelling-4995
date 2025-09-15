from __future__ import annotations

from fastapi import APIRouter
from utils.version import SERVICE_NAME, SERVICE_VERSION

router = APIRouter(tags=["Health"])


# PUBLIC_INTERFACE
@router.get(
    "/health",
    summary="Health check",
    description="Returns service status, name, and version for monitoring and readiness checks.",
    response_description="Service status.",
)
def get_health() -> dict:
    """Return service health status.

    Returns:
        dict: A JSON object with status, service name, and semantic version.
    """
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}
