# Vision Modelling Backend Architecture Outline (Wireframes Extraction)

Source references:
- Wireframes (sketched): attachments/20250915_042042_Vision_Modelling_Wireframes_Sketched.pptx (and 20250915_042005_Vision_Modelling_Wireframes_Sketched.pptx)
- Week 2 Plan extraction: docs/backend/requirements-week2.md

This document translates the wireframes into a concrete backend architecture, API endpoints, data models, and data flows, ready for a FastAPI implementation. It complements the Week 2 requirements and sets a clear plan for code scaffolding.

-----------------------------------------------------------------------

1) Wireframes interpretation → backend responsibilities
- Call Dashboard (list + “Start Modelling” button)
  - Backend: provide a mocked call list; accept a “start modelling” request to return a graph model JSON.
- Visual Workspace (graph)
  - Backend: supply graph JSON per view (“flow” | “architecture”).
  - Save/Load: mirror front-end LocalStorage schema with optional server-side file-based storage.
  - Export PNG: front-end with Cytoscape; backend can return 501 for server-side export (optional).
- Multi-view toggle (Flow vs Architecture)
  - Backend: Models indicate view in JSON; same schema, front-end handles layout.
- Annotations/colors/legend
  - Backend: Node metadata includes annotations and color fields; legend keys may be added to meta.tags.

Non-goals for MVP (as per plan and wireframes):
- Real AI inference/training, auth, DB, websockets, real-time collaboration.

-----------------------------------------------------------------------

2) High-level architecture (modules and responsibilities)

- App.py
  - Create FastAPI app instance, mount routers, configure CORS, logging, and lifespan events.
- routers/
  - health.py: GET /health
  - calls.py: GET /calls, POST /model/start
  - models.py: CRUD for models (GET /models, GET/PUT/DELETE /models/{id}, POST /models), optional export endpoint returning 501
- models/ (Pydantic schemas)
  - graph.py: GraphModel, NodeModel, EdgeModel
  - common.py: CallItem, ModelSummary, ErrorResponse, StartModelRequest
- services/
  - storage.py: file-based persistence (save/load/list/delete models)
  - mocks.py: loading mock calls and graphs
- data/
  - mocks/: preloaded mock JSONs (calls.json; graphs per call and per view)
  - models/: saved models from API (server-side persistence; optional)
- utils/
  - ids.py (uuid generation), time.py (timestamps), io.py (safe read/write), validation.py (schema checks)
- docs/backend/
  - requirements-week2.md (given)
  - architecture-outline.md (this document)
  - openapi-skeleton.yaml (OpenAPI definition for quick reference)

-----------------------------------------------------------------------

3) API surface (mock-first contract)

All responses are JSON unless specified. CORS enabled for local dev. Versioning is implicit for MVP (no /v1 prefix); can be added later.

- GET /health
  - 200: {"status":"ok","service":"vision-modelling-backend","version":"0.1.0"}
- GET /calls
  - 200: {"items":[CallItem, ...]}
- POST /model/start
  - Body: {"call_id":"call-001","view":"flow"} // view optional: "flow" | "architecture"
  - 200: GraphModel (mock “AI output”)
  - 400: ErrorResponse (invalid call)
- GET /models
  - 200: {"items":[ModelSummary, ...]}
- GET /models/{model_id}
  - 200: GraphModel
  - 404: ErrorResponse
- POST /models
  - Body: GraphModel (id optional; server generates if missing)
  - 201: {"id":"model-123","status":"saved"}
  - 200: {"id":"model-123","status":"updated"} (if upsert semantics used)
- PUT /models/{model_id}
  - Body: GraphModel
  - 200: {"id":"model-123","status":"updated"}
  - 404: ErrorResponse
- DELETE /models/{model_id} (optional MVP)
  - 200: {"id":"model-123","status":"deleted"}
  - 404: ErrorResponse
- GET /models/{model_id}/export?format=png (optional MVP)
  - 501 Not Implemented with JSON: {"status":"not_implemented"} (since front-end does export)

HTTP status semantics:
- 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 409 Conflict (if needed), 501 Not Implemented, 500 Internal Error.

-----------------------------------------------------------------------

4) Data models (Pydantic schemas)

Graph JSON schema (canonical):
- GraphModel
  - id: string
  - name: string
  - view: "flow" | "architecture"
  - nodes: array<NodeModel>
  - edges: array<EdgeModel>
  - meta: object { source: "mock"|"ai", created_at: ISO datetime, tags: array<string> }
- NodeModel
  - id: string
  - label: string
  - type: string (e.g., "actor","service","db")
  - annotations: object (free-form key/values)
  - color: string (hex or semantic)
- EdgeModel
  - id: string
  - source: string (node id)
  - target: string (node id)
  - label: string
  - type: string (e.g., "call","data","dependency")
- CallItem
  - id: string
  - title: string
  - timestamp: ISO datetime
- ModelSummary
  - id: string
  - name: string
  - updated_at: ISO datetime
  - view: "flow" | "architecture"
- StartModelRequest
  - call_id: string
  - view: Optional["flow"|"architecture"] (default "flow")
- ErrorResponse
  - error: string
  - details: Optional[object]

Pydantic skeleton (for reference):
```python
# models/graph.py
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime

class NodeModel(BaseModel):
    id: str
    label: str
    type: str
    annotations: Dict[str, str] = {}
    color: str | None = None

class EdgeModel(BaseModel):
    id: str
    source: str
    target: str
    label: str
    type: str

class GraphMeta(BaseModel):
    source: Literal["mock", "ai"] = "mock"
    created_at: datetime
    tags: List[str] = []

class GraphModel(BaseModel):
    id: str
    name: str
    view: Literal["flow", "architecture"] = "flow"
    nodes: List[NodeModel] = []
    edges: List[EdgeModel] = []
    meta: GraphMeta

# models/common.py
class CallItem(BaseModel):
    id: str
    title: str
    timestamp: datetime

class ModelSummary(BaseModel):
    id: str
    name: str
    updated_at: datetime
    view: Literal["flow", "architecture"]

class StartModelRequest(BaseModel):
    call_id: str
    view: Literal["flow", "architecture"] | None = "flow"

class ErrorResponse(BaseModel):
    error: str
    details: dict | None = None
```

-----------------------------------------------------------------------

5) Data flows (from wireframes → API)

A) Dashboard load
- FE → GET /calls
- BE → returns {"items":[CallItem,...]} from data/mocks/calls.json

B) Start modelling
- FE → POST /model/start {"call_id":"call-001","view":"flow"}
- BE → loads mock graph for call+view (e.g., data/mocks/graphs/call-001-flow.json), returns GraphModel
- FE → renders graph with Cytoscape

C) Save model (optional server persistence)
- FE → POST /models GraphModel (id optional)
- BE → if no id: generate UUID; write JSON to data/models/<id>.json
- BE → return {"id":"...", "status":"saved" | "updated"}

D) Load model
- FE → GET /models (to list)
- FE → GET /models/{id} for details
- BE → read data/models/<id>.json and return GraphModel

E) Export PNG (client-side)
- Initiated by FE using Cytoscape export; backend endpoint returns 501 for now (optional).

-----------------------------------------------------------------------

6) File system layout (proposed)

Vision_Modelling-4995/
- App.py
- routers/
  - health.py
  - calls.py
  - models.py
- models/
  - graph.py
  - common.py
- services/
  - storage.py
  - mocks.py
- data/
  - mocks/
    - calls.json
    - graphs/
      - call-001-flow.json
      - call-001-architecture.json
  - models/  # server-saved models (gitignored in future)
- docs/backend/
  - requirements-week2.md
  - architecture-outline.md
  - openapi-skeleton.yaml
- requirements.txt

-----------------------------------------------------------------------

7) Mock data pack (for demo)

- calls.json: a few Calls (onboarding, design review, sprint planning).
- graphs/: at least one flow and one architecture variant for call-001 (sample included in this repo).
- BE start endpoint picks correct mock based on {"call_id","view"}.

-----------------------------------------------------------------------

8) Validation and error handling

- Request validation via Pydantic; respond 400 with ErrorResponse on invalid data.
- 404 when a requested model_id or call_id is not found.
- 501 for server-side export endpoint for MVP.
- Include standard error structure to keep FE predictable.

-----------------------------------------------------------------------

9) Non-functional requirements

- CORS enabled (localhost:*)
- Logging: INFO by default; log requests and storage operations
- Small footprint; no DB or heavy ML dependencies
- OpenAPI auto-docs enabled (/docs, /redoc)

-----------------------------------------------------------------------

10) OpenAPI skeleton

See docs/backend/openapi-skeleton.yaml for detailed path and schema summaries.

-----------------------------------------------------------------------

11) Next steps for implementation

- Scaffold directories and Pydantic models (models/graph.py, models/common.py).
- Implement routers with FastAPI and wire them into App.py.
- Add services/storage.py to persist models under data/models/.
- Load mocks from data/mocks at startup (services/mocks.py).
- Add CORS middleware and basic logging in App.py.
- Write basic unit tests (if test harness added).
- Run:
  - python -m pip install -r requirements.txt
  - uvicorn App:app --host 0.0.0.0 --port 8000 --reload

This plan is intentionally minimal to align with the 2-week MVP scope.
