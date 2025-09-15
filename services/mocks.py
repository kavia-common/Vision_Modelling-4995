from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from models.common import CallItem
from models.graph import GraphModel
from utils.io import get_data_dir

logger = logging.getLogger(__name__)

# In-memory caches (loaded on first access)
_calls_cache: Optional[List[CallItem]] = None
_graphs_cache: Dict[str, GraphModel] = {}


def _mocks_dir() -> Path:
    """Return the path to the mocks directory."""
    return get_data_dir() / "mocks"


def _calls_file() -> Path:
    """Path to the calls.json file."""
    return _mocks_dir() / "calls.json"


def _graph_file_for(call_id: str, view: str) -> Path:
    """Resolve the appropriate graph JSON file path for a call/view."""
    return _mocks_dir() / "graphs" / f"{call_id}-{view}.json"


# PUBLIC_INTERFACE
def load_calls() -> List[CallItem]:
    """Load calls from the mock data file.

    Returns:
        List[CallItem]: Parsed list of CallItem objects.
    """
    global _calls_cache
    calls_fp = _calls_file()
    if not calls_fp.exists():
        logger.warning("Calls mock file not found: %s", calls_fp)
        _calls_cache = []
        return _calls_cache

    try:
        data = json.loads(calls_fp.read_text(encoding="utf-8"))
        items = data.get("items", [])
        _calls_cache = [CallItem.model_validate(i) for i in items]
    except Exception as exc:
        logger.exception("Failed to load calls from %s: %s", calls_fp, exc)
        _calls_cache = []

    return _calls_cache


# PUBLIC_INTERFACE
def get_calls() -> List[CallItem]:
    """Get calls list, loading from disk if not already cached.

    Returns:
        List[CallItem]: Call items.
    """
    global _calls_cache
    if _calls_cache is None:
        return load_calls()
    return _calls_cache


# PUBLIC_INTERFACE
def call_exists(call_id: str) -> bool:
    """Check whether a given call_id exists in the mock calls list.

    Args:
        call_id (str): The call identifier to check.

    Returns:
        bool: True if exists, False otherwise.
    """
    return any(c.id == call_id for c in get_calls())


# PUBLIC_INTERFACE
def get_graph_for_call(call_id: str, view: str) -> Optional[GraphModel]:
    """Load a mock graph for the given call and view.

    Args:
        call_id (str): Call identifier such as 'call-001'.
        view (str): One of 'flow' or 'architecture'.

    Returns:
        Optional[GraphModel]: The graph model if found, otherwise None.
    """
    cache_key = f"{call_id}:{view}"
    if cache_key in _graphs_cache:
        return _graphs_cache[cache_key]

    fp = _graph_file_for(call_id, view)
    if not fp.exists():
        logger.warning("Graph mock not found for call_id=%s view=%s at %s", call_id, view, fp)
        return None

    try:
        graph_data = json.loads(fp.read_text(encoding="utf-8"))
        graph = GraphModel.model_validate(graph_data)
        _graphs_cache[cache_key] = graph
        return graph
    except Exception as exc:
        logger.exception("Failed to parse graph at %s: %s", fp, exc)
        return None
