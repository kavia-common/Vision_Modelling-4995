from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class NodeModel(BaseModel):
    """Represents a node in the graph."""

    id: str = Field(..., description="Unique identifier of the node.")
    label: str = Field(..., description="Human-readable label.")
    type: str = Field(..., description="Semantic type e.g., 'actor', 'service', 'db'.")
    annotations: Dict[str, str] = Field(default_factory=dict, description="Free-form key/value annotations.")
    color: Optional[str] = Field(default=None, description="Hex color or semantic color token.")


class EdgeModel(BaseModel):
    """Represents a directed edge in the graph."""

    id: str = Field(..., description="Unique identifier of the edge.")
    source: str = Field(..., description="Source node id.")
    target: str = Field(..., description="Target node id.")
    label: str = Field(..., description="Human-readable edge label.")
    type: str = Field(..., description="Semantic type e.g., 'call', 'data', 'dependency'.")


class GraphMeta(BaseModel):
    """Metadata describing the graph origin and tags."""

    source: Literal["mock", "ai"] = Field("mock", description="Origin of the graph data.")
    created_at: datetime = Field(..., description="ISO timestamp when the graph was created.")
    tags: List[str] = Field(default_factory=list, description="Arbitrary tags for the graph.")


class GraphModel(BaseModel):
    """Canonical graph schema used by the application."""

    id: str = Field(..., description="Unique identifier of the graph model.")
    name: str = Field(..., description="Human-readable graph name.")
    view: Literal["flow", "architecture"] = Field(
        "flow", description="View type of the graph; either 'flow' or 'architecture'."
    )
    nodes: List[NodeModel] = Field(default_factory=list, description="List of nodes.")
    edges: List[EdgeModel] = Field(default_factory=list, description="List of edges.")
    meta: GraphMeta = Field(..., description="Metadata for the graph.")


class GraphModelCreate(BaseModel):
    """Input payload for creating or upserting a graph model.

    This mirrors GraphModel but allows 'id' to be omitted so the server can generate one.
    """

    id: Optional[str] = Field(None, description="Optional id; if omitted, server will generate one.")
    name: str = Field(..., description="Human-readable graph name.")
    view: Literal["flow", "architecture"] = Field(
        "flow", description="View type of the graph; either 'flow' or 'architecture'."
    )
    nodes: List[NodeModel] = Field(default_factory=list, description="List of nodes.")
    edges: List[EdgeModel] = Field(default_factory=list, description="List of edges.")
    meta: GraphMeta = Field(..., description="Metadata for the graph.")
