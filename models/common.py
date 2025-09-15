from __future__ import annotations

from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field


class CallItem(BaseModel):
    """Call item for dashboard list."""

    id: str = Field(..., description="Call identifier e.g., 'call-001'.")
    title: str = Field(..., description="Call title.")
    timestamp: datetime = Field(..., description="ISO timestamp when the call occurred.")


class ModelSummary(BaseModel):
    """Summary info for a saved model."""

    id: str = Field(..., description="Model identifier.")
    name: str = Field(..., description="Model name.")
    updated_at: datetime = Field(..., description="ISO timestamp when the model file was last updated.")
    view: Literal["flow", "architecture"] = Field(..., description="View type of the graph.")


class StartModelRequest(BaseModel):
    """Request payload to start modelling from a given call and view."""

    call_id: str = Field(..., description="Call identifier to model.")
    view: Optional[Literal["flow", "architecture"]] = Field(
        "flow", description="Desired view; defaults to 'flow' if omitted."
    )


class ErrorResponse(BaseModel):
    """Standard error structure returned by the API."""

    error: str = Field(..., description="Short machine-readable error code.")
    details: Optional[Dict] = Field(None, description="Optional error details payload.")
