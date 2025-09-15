from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.common import CallItem, ErrorResponse, StartModelRequest
from models.graph import GraphModel
from services import mocks

router = APIRouter(tags=["Calls"])


# PUBLIC_INTERFACE
@router.get(
    "/calls",
    summary="List available calls (mocked)",
    description="Returns a mocked list of available calls for the dashboard.",
    response_model=dict,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {"id": "call-001", "title": "Onboarding call", "timestamp": "2024-05-01T10:00:00Z"}
                        ]
                    }
                }
            },
        }
    },
)
def list_calls() -> dict:
    """List available calls using the shipped mock data pack.

    Returns:
        dict: Object with 'items' containing a list of CallItem objects.
    """
    items = mocks.get_calls()
    # Pydantic models auto-serialize; ensure plain dict
    return {"items": [i.model_dump() for i in items]}


# PUBLIC_INTERFACE
@router.post(
    "/model/start",
    summary="Start modelling for a call and view (returns mock graph)",
    description=(
        "Starts modelling by returning a mock graph JSON for the given call and view.\n"
        "Views supported: 'flow' | 'architecture'."
    ),
    response_model=GraphModel,
    responses={
        400: {
            "description": "Invalid request",
            "model": ErrorResponse,
            "content": {"application/json": {"example": {"error": "invalid_call_id"}}},
        },
        200: {"description": "Graph for the call and view (mock)"},
    },
)
def start_model(payload: StartModelRequest) -> GraphModel | JSONResponse:
    """Return a mock graph for the specified call and view.

    Args:
        payload (StartModelRequest): Request containing call_id and view.

    Returns:
        GraphModel: The mock graph model for the call and view.

    Raises:
        HTTPException: 400 if the call_id is invalid or graph mock not found.
    """
    call_id = payload.call_id
    view = payload.view or "flow"

    # Validate call existence
    if not mocks.call_exists(call_id):
        # 400 per architecture outline for invalid call
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_call_id", "details": {"call_id": call_id}},
        )

    graph = mocks.get_graph_for_call(call_id=call_id, view=view)
    if graph is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "graph_not_found_for_call_and_view", "details": {"call_id": call_id, "view": view}},
        )
    return graph
