from __future__ import annotations

# PUBLIC_INTERFACE
def get_service_name() -> str:
    """Return the canonical service name."""
    return "vision-modelling-backend"


# PUBLIC_INTERFACE
def get_service_version() -> str:
    """Return the service semantic version."""
    return "0.1.0"


# Public constants for convenience
SERVICE_NAME = get_service_name()
SERVICE_VERSION = get_service_version()
