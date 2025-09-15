from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import JSONResponse

from models.common import ErrorResponse, ModelSummary
from models.graph import GraphModel, GraphModelCreate
from services import storage

router = APIRouter(tags=["Models"])


# PUBLIC_INTERFACE
@router.get(
    "/models",
    summary="List saved models",
    description="Lists saved models (file-based JSON persistence).",
    response_model=dict,
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {"items": [{"id": "model-123", "name": "Call 001 flow", "updated_at": "…", "view": "flow"}]}
                }
            },
        }
    },
)
def list_models() -> dict:
    """List saved models as summaries.

    Returns:
        dict: Object with 'items' containing a list of ModelSummary objects.
    """
    items = storage.list_models()
    return {"items": [i.model_dump() for i in items]}


# PUBLIC_INTERFACE
@router.get(
    "/models/{model_id}",
    summary="Get a saved model by id",
    description="Returns a saved graph model by its id.",
    response_model=GraphModel,
    responses={
        404: {
            "description": "Not found",
            "model": ErrorResponse,
            "content": {"application/json": {"example": {"error": "not_found"}}},
        }
    },
)
def get_model(
    model_id: str = Path(..., description="The unique identifier of the model to retrieve."),
) -> GraphModel:
    """Get a saved graph model.

    Args:
        model_id (str): Identifier of the model.

    Returns:
        GraphModel: The saved graph model.

    Raises:
        HTTPException: 404 if the model does not exist.
    """
    try:
        return storage.load_model(model_id)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "id": model_id})


# PUBLIC_INTERFACE
@router.post(
    "/models",
    summary="Save or upsert a model",
    description=(
        "Saves a model. If id is omitted, the server will generate one. "
        "If a model with the same id exists, it will be updated (upsert)."
    ),
    responses={
        201: {
            "description": "Saved",
            "content": {"application/json": {"example": {"id": "model-123", "status": "saved"}}},
        },
        200: {
            "description": "Updated (upsert)",
            "content": {"application/json": {"example": {"id": "model-123", "status": "updated"}}},
        },
    },
)
def create_or_update_model(payload: GraphModelCreate):
    """Create or update a graph model.

    Args:
        payload (GraphModelCreate): The model payload; id may be omitted.

    Returns:
        dict: Object with 'id' and 'status' in {'saved','updated'}.
    """
    new_id, status_text = storage.upsert_model(payload)
    status_code = status.HTTP_201_CREATED if status_text == "saved" else status.HTTP_200_OK
    return JSONResponse(content={"id": new_id, "status": status_text}, status_code=status_code)


# PUBLIC_INTERFACE
@router.put(
    "/models/{model_id}",
    summary="Update a model by id",
    description="Updates an existing model by id. Returns status 'updated' if successful.",
    responses={
        200: {"description": "Updated", "content": {"application/json": {"example": {"id": "model-123", "status": "updated"}}}},
        404: {"description": "Not found", "content": {"application/json": {"example": {"error": "not_found"}}}},
    },
)
def update_model(
    payload: GraphModel,
    model_id: str = Path(..., description="The unique identifier of the model to update."),
):
    """Update an existing model identified by path parameter.

    Args:
        payload (GraphModel): The updated model body (its id will be overridden with path id).
        model_id (str): Path parameter identifying which model to update.

    Returns:
        dict: Object with 'id' and 'status'='updated'.

    Raises:
        HTTPException: 404 if the model id is not found.
    """
    if not storage.model_exists(model_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "id": model_id})
    storage.update_model(model_id, payload)
    return {"id": model_id, "status": "updated"}


# PUBLIC_INTERFACE
@router.delete(
    "/models/{model_id}",
    summary="Delete a model by id (optional MVP)",
    description="Deletes a saved model by its id.",
    responses={
        200: {"description": "Deleted", "content": {"application/json": {"example": {"id": "model-123", "status": "deleted"}}}},
        404: {"description": "Not found", "content": {"application/json": {"example": {"error": "not_found"}}}},
    },
)
def delete_model(
    model_id: str = Path(..., description="The unique identifier of the model to delete."),
):
    """Delete a saved model file.

    Args:
        model_id (str): Identifier to delete.

    Returns:
        dict: Object with 'id' and 'status'='deleted'.

    Raises:
        HTTPException: 404 if not found.
    """
    if not storage.model_exists(model_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "id": model_id})
    storage.delete_model(model_id)
    return {"id": model_id, "status": "deleted"}


# PUBLIC_INTERFACE
@router.get(
    "/models/{model_id}/export",
    summary="Export a model (server-side; optional; returns 501 for MVP)",
    description="Export model to an artifact. For MVP, returns 501 since export is handled client-side (Cytoscape).",
    responses={
        501: {
            "description": "Not implemented",
            "content": {"application/json": {"example": {"status": "not_implemented"}}},
        }
    },
)
def export_model(
    model_id: str = Path(..., description="The unique identifier of the model to export."),
    format: Literal["png"] = "png",
):
    """Export a model to the requested format. Not implemented for MVP.

    Args:
        model_id (str): The model identifier.
        format (Literal['png']): Export format. Defaults to 'png'.

    Returns:
        JSONResponse: Always returns 501 Not Implemented in the MVP.
    """
    return JSONResponse(content={"status": "not_implemented"}, status_code=status.HTTP_501_NOT_IMPLEMENTED)
