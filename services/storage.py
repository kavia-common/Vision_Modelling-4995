from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

from models.common import ModelSummary
from models.graph import GraphModel, GraphModelCreate
from utils.ids import generate_model_id
from utils.io import get_data_dir, safe_write_text
from utils.time import isoformat_utc

logger = logging.getLogger(__name__)


def _models_dir() -> Path:
    """Directory holding persisted JSON models."""
    return get_data_dir() / "models"


def _model_file(model_id: str) -> Path:
    """Compute the full path for a model JSON file."""
    return _models_dir() / f"{model_id}.json"


# PUBLIC_INTERFACE
def ensure_models_dir() -> None:
    """Ensure that the models directory exists on disk."""
    models_dir = _models_dir()
    models_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Ensured models directory exists at %s", models_dir)


# PUBLIC_INTERFACE
def model_exists(model_id: str) -> bool:
    """Check whether a model file exists.

    Args:
        model_id (str): Identifier to check.

    Returns:
        bool: True if file exists, False otherwise.
    """
    return _model_file(model_id).exists()


# PUBLIC_INTERFACE
def list_models() -> List[ModelSummary]:
    """List saved models as ModelSummary objects.

    Returns:
        List[ModelSummary]: Summaries including id, name, updated_at, and view.
    """
    ensure_models_dir()
    summaries: List[ModelSummary] = []
    for fp in sorted(_models_dir().glob("*.json")):
        try:
            with fp.open("r", encoding="utf-8") as f:
                doc = json.load(f)
            mid = doc.get("id", fp.stem)
            name = doc.get("name", fp.stem)
            view = doc.get("view", "flow")
            # Use file mtime as updated_at
            ts = datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc)
            summaries.append(
                ModelSummary(
                    id=str(mid),
                    name=str(name),
                    view=view,
                    updated_at=ts,
                )
            )
        except Exception as exc:
            logger.exception("Failed to read model summary from %s: %s", fp, exc)
            continue
    return summaries


# PUBLIC_INTERFACE
def load_model(model_id: str) -> GraphModel:
    """Load a model by id.

    Args:
        model_id (str): Identifier.

    Returns:
        GraphModel: Parsed graph model.

    Raises:
        FileNotFoundError: When the model file does not exist.
    """
    fp = _model_file(model_id)
    if not fp.exists():
        raise FileNotFoundError(model_id)
    with fp.open("r", encoding="utf-8") as f:
        doc = json.load(f)
    return GraphModel.model_validate(doc)


# PUBLIC_INTERFACE
def upsert_model(payload: GraphModelCreate) -> Tuple[str, str]:
    """Create or update a model from a GraphModelCreate payload.

    If id is omitted, server generates one. If file exists, it's updated; otherwise saved.

    Args:
        payload (GraphModelCreate): The model payload.

    Returns:
        Tuple[str, str]: (model_id, status) where status in {'saved', 'updated'}
    """
    ensure_models_dir()
    model_id = payload.id or generate_model_id()
    model_data = payload.model_dump()
    model_data["id"] = model_id  # enforce id
    # If meta.created_at is missing (shouldn't be), ensure it's present and ISO
    try:
        # Convert datetime to ISO string
        if isinstance(model_data.get("meta", {}).get("created_at"), datetime):
            model_data["meta"]["created_at"] = isoformat_utc(model_data["meta"]["created_at"])
    except Exception:
        pass

    fp = _model_file(model_id)
    status = "updated" if fp.exists() else "saved"
    safe_write_text(fp, json.dumps(model_data, ensure_ascii=False, indent=2))
    logger.info("Model %s %s at %s", model_id, status, fp)
    return model_id, status


# PUBLIC_INTERFACE
def update_model(model_id: str, model: GraphModel) -> None:
    """Update an existing model by id.

    Args:
        model_id (str): Identifier to update.
        model (GraphModel): Model content to write (id will be enforced).

    Raises:
        FileNotFoundError: If the model file is missing.
    """
    fp = _model_file(model_id)
    if not fp.exists():
        raise FileNotFoundError(model_id)
    data = model.model_dump()
    data["id"] = model_id  # enforce id from path
    safe_write_text(fp, json.dumps(data, ensure_ascii=False, indent=2))
    logger.info("Model %s updated at %s", model_id, fp)


# PUBLIC_INTERFACE
def delete_model(model_id: str) -> None:
    """Delete a model by id.

    Args:
        model_id (str): Identifier to delete.

    Raises:
        FileNotFoundError: If the model file is missing.
    """
    fp = _model_file(model_id)
    if not fp.exists():
        raise FileNotFoundError(model_id)
    fp.unlink(missing_ok=False)
    logger.info("Model %s deleted from %s", model_id, fp)
