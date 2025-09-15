"""FastAPI application entrypoint for the Vision Modelling Backend (MVP).

This app exposes mock-first endpoints for:
- Health checks
- Call listing from static mock data
- Starting a model (returns a mock graph)
- Optional file-based JSON persistence for saved models

Run locally:
- python3 -m pip install -r requirements.txt
- Option A (recommended): python App.py                # binds to 0.0.0.0:3001 by default
- Option B:           uvicorn App:app --host 0.0.0.0 --port 3001 --reload
Environment:
- PORT: listening port (default: 3001)
- SERVER_HOST: host to bind (default: 0.0.0.0)
- LOG_LEVEL: Python logging level (default: INFO)
- CORS_ALLOW_ORIGINS: comma-separated list of allowed origins (default: '*')
- DATA_DIR: override path to data directory (default: ./data)
"""
from __future__ import annotations

import logging
import os
from typing import List, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.health import router as health_router
from routers.calls import router as calls_router
from routers.models import router as models_router
from utils.version import SERVICE_NAME, SERVICE_VERSION
from services.storage import ensure_models_dir

# Load environment variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("vision-modelling-backend")

# OpenAPI/Swagger tags metadata
openapi_tags = [
    {
        "name": "Health",
        "description": "Service health and metadata endpoints.",
    },
    {
        "name": "Calls",
        "description": "Mocked calls listing and start modelling endpoints.",
    },
    {
        "name": "Models",
        "description": "File-based persistence endpoints for saved graph models.",
    },
]

app = FastAPI(
    title="Vision Modelling Backend (MVP)",
    description=(
        "Mock-first API for Vision Modelling MVP. "
        "Provides endpoints to list calls, start modelling to get mock graphs, "
        "and file-based persistence for models. "
        "Note: No websockets or server-side PNG export in MVP; front-end handles export."
    ),
    version=SERVICE_VERSION,
    openapi_tags=openapi_tags,
)


def _get_cors_allow_origins() -> List[str]:
    """Read allowed origins from env var CORS_ALLOW_ORIGINS (comma-separated) or default to '*'. """
    env_val = os.getenv("CORS_ALLOW_ORIGINS", "*")
    if env_val.strip() == "*":
        return ["*"]
    return [o.strip() for o in env_val.split(",") if o.strip()]


def _get_bind() -> Tuple[str, int]:
    """Resolve host and port to bind from environment with sensible defaults."""
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port_val = os.getenv("PORT") or os.getenv("SERVER_PORT") or "3001"
    try:
        port = int(port_val)
    except (TypeError, ValueError):
        port = 3001
    return host, port


# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Application startup hook: prepare storage directories and log service boot."""
    logger.info("Starting %s v%s", SERVICE_NAME, SERVICE_VERSION)
    # Ensure the data/models directory exists for file-based persistence
    ensure_models_dir()
    logger.info("Storage initialized.")


# Mount routers
app.include_router(health_router)
app.include_router(calls_router)
app.include_router(models_router)


# PUBLIC_INTERFACE
def main() -> None:
    """Service runtime entrypoint.

    Starts a Uvicorn HTTP server hosting the FastAPI app.
    Reads environment variables:
    - SERVER_HOST: host interface to bind (default 0.0.0.0)
    - PORT: port to listen on (default 3001)

    Returns:
        None
    """
    import uvicorn

    host, port = _get_bind()
    logger.info("Booting Uvicorn on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("LOG_LEVEL", "info").lower())


if __name__ == "__main__":
    main()
