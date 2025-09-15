# Vision Modelling MVP – Backend Requirements (Week 2 Plan Extraction)

Source: attachments/20250915_042042_Vision_Modelling_2_Week_Plan.pptx

This document extracts and translates the Week 2 plan into concrete backend requirements, constraints, and action items for implementation in the Python backend container.

1) Extracted plan highlights (verbatim from deck)
- MVP Scope (2 Weeks)
  - Call Dashboard (mocked list, Start Modelling button)
  - Visual Workspace (graph rendering from mock AI output)
  - Drag/drop nodes, annotations, color coding
  - Multi-view toggle: Flow vs Architecture
  - Export to PNG, Save/Load JSON (Knowledge Base)
- Tools & Stack
  - Frontend: React (scaffold via Kavia)
  - Visualization: Cytoscape.js
  - Backend (mock only): Node.js/Express (optional)
  - Storage: LocalStorage for Knowledge Base
  - Codegen + LLM: Kavia for scaffolding, LLMs for refinement
- Week 2 Plan – Export, Storage & Demo Polish
  - Day 6: Export graph to PNG
  - Day 7: Save graph JSON to LocalStorage (Knowledge Base)
  - Day 8: Load saved models into Workspace
  - Day 9: Polish UI with Tailwind, add color legend
  - Day 10: Preload mock AI outputs for demo
  - Day 11: Write documentation (setup, Kavia prompts, roadmap)
  - Day 12: Final demo run & packaging
- Deliverables After 2 Weeks
  - Working MVP Web App (React + Cytoscape.js)
  - Call Dashboard + Visual Workspace
  - Flow vs Architecture toggle
  - Export PNG + JSON save/load (Knowledge Base)
  - Mock Data Pack (AI outputs for calls)
  - Documentation (setup, Kavia prompts, roadmap)
  - Demo Script for client showcase


2) Context and adaptation to our backend container
- The deck positions the backend as “mock only” and “optional,” with LocalStorage as the primary Knowledge Base for the MVP timeline.
- Our project includes a Python backend container (Vision_Modelling-4995). We will implement a minimal mock API to support:
  - Mock data supply for Call Dashboard
  - Model start/generation endpoint that returns mock graph JSON
  - Optional persistence of models (file-based JSON) mirroring LocalStorage schema
  - Optional server-side export (deferred; front-end PNG export through Cytoscape is sufficient per plan)
- Non-goals for the MVP (explicitly out of scope)
  - Real AI inference or model training
  - Authentication/authorization and multi-user features
  - Database setup or migrations (use LocalStorage and optional file-based storage)
  - Real-time collaboration or websockets
  - Production-grade export pipelines (front-end export is acceptable for demo)


3) Backend responsibilities derived from the plan
- Provide endpoints to decouple front-end from hardcoded mocks:
  - Call list for the dashboard (mocked)
  - Start Modelling to retrieve a mock graph JSON (AI output simulation)
  - Save/Load models using JSON (to mirror LocalStorage schema; file-based optional)
  - Health check and basic metadata endpoints
- Provide a canonical Graph JSON schema so front-end and backend agree on shapes
- Preload a “Mock Data Pack” for demo (static JSON shipped with the backend)
- Support CORS for local frontend development


4) Proposed API contract (mock-first)
All endpoints return JSON unless otherwise specified.

- GET /health
  - Returns service status.
  - Response: {"status":"ok","service":"vision-modelling-backend","version":"0.1.0"}

- GET /calls
  - Returns a mocked list of available calls for the dashboard.
  - Query params: none
  - Response example:
    {
      "items": [
        {"id":"call-001","title":"Onboarding call","timestamp":"2024-05-01T10:00:00Z"},
        {"id":"call-002","title":"Design review","timestamp":"2024-05-02T14:00:00Z"}
      ]
    }

- POST /model/start
  - Starts “modelling” for a call and returns a mock graph JSON (AI output simulation).
  - Body: {"call_id":"call-001","view":"flow"}  // view optional: "flow" | "architecture"
  - Response: Graph model JSON (see Graph JSON schema)

- GET /models
  - Lists saved models (file-based if backend persistence is used).
  - Response: {"items":[{"id":"model-123","name":"Call 001 flow","updated_at":"..."}, ...]}

- GET /models/{model_id}
  - Returns a saved model graph JSON.

- POST /models
  - Saves a model graph JSON (upsert by id).
  - Body: Graph model JSON; if id missing, server generates one.
  - Response: {"id":"model-123","status":"saved"}

- PUT /models/{model_id}
  - Updates an existing model graph JSON.
  - Body: Graph model JSON
  - Response: {"id":"model-123","status":"updated"}

- DELETE /models/{model_id} (optional for MVP)
  - Deletes a saved model.

- GET /models/{model_id}/export?format=png (optional for MVP)
  - Returns a PNG export. Note: per plan, client-side Cytoscape export suffices. This server endpoint is optional and can be a no-op or return 501 Not Implemented for MVP.


5) Graph JSON schema (contract)
Minimal shape to align with Cytoscape.js usage. Fields beyond the minimum are optional.

- Graph object
  - id: string
  - name: string
  - view: "flow" | "architecture"
  - nodes: array<Node>
  - edges: array<Edge>
  - meta: object
    - source: "mock" | "ai"
    - created_at: ISO datetime string
    - tags: array<string>

- Node
  - id: string
  - label: string
  - type: string  // e.g., "actor", "service", "db", etc.
  - annotations: object  // arbitrary key/value annotations
  - color: string  // hex or semantic key for color coding

- Edge
  - id: string
  - source: string (node id)
  - target: string (node id)
  - label: string
  - type: string  // e.g., "call", "data", "dependency"

Example:
{
  "id": "model-123",
  "name": "Call 001 flow",
  "view": "flow",
  "nodes": [
    {"id":"n1","label":"Client","type":"actor","annotations":{},"color":"#4F46E5"},
    {"id":"n2","label":"API Gateway","type":"service","annotations":{},"color":"#22C55E"}
  ],
  "edges": [
    {"id":"e1","source":"n1","target":"n2","label":"requests","type":"call"}
  ],
  "meta": {"source":"mock","created_at":"2024-05-01T10:00:00Z","tags":["demo","week2"]}
}


6) Development constraints from the plan
- Strict 2-week scope; include only essential demo features
- Backend is mock-only and optional; do not introduce databases or network-heavy dependencies
- Storage: Prefer LocalStorage in the front-end; backend persistence should be lightweight (file-based JSON) and optional
- PNG export can be performed on the client via Cytoscape; server export is not required for MVP
- Provide a preloaded mock data pack to enable an offline demo
- Keep cold start and footprint small; avoid GPU or heavy ML libraries
- Documentation is a deliverable: setup, prompts, and roadmap

Assumptions
- The front-end will consume the Graph JSON schema and perform rendering and client-side export to PNG.
- For a clean demo flow, the backend will serve mock calls and graphs and optionally persist JSON to disk for convenience during development.
- CORS will be needed for local development with the React front-end.


7) Build and run instructions (backend)
- Language/runtime: Python 3.10+ recommended
- Dependencies: see requirements.txt (FastAPI + Uvicorn + Pydantic + Dotenv)
- Suggested project entrypoint: App.py with `app = FastAPI()` (to be implemented in subsequent tasks)
- Local run (after implementation):
  - python3 -m pip install -r requirements.txt
  - uvicorn App:app --host 0.0.0.0 --port 8000 --reload
- Directory suggestions (for future implementation):
  - Vision_Modelling-4995/
    - App.py  // FastAPI app instance
    - routers/  // API route modules: health.py, calls.py, models.py
    - models/   // Pydantic schemas for Graph, Node, Edge
    - data/
      - mocks/  // preloaded mock graphs and calls
      - models/ // saved models (file-based)
    - docs/backend/  // this file and other backend docs
    - requirements.txt


8) Action items for backend implementation (Week 2 alignment)
- Day 6
  - Define Pydantic models for Graph, Node, Edge
  - Add GET /health
- Day 7
  - Implement GET /calls returning mocked calls
  - Implement POST /model/start returning a mock Graph JSON (accept view param)
- Day 8
  - Implement optional file-based persistence for models:
    - GET /models, GET /models/{id}, POST /models, PUT /models/{id}
- Day 9
  - Add CORS config and logging; ensure responses align with front-end needs
  - Finalize color legend keys in node metadata where applicable
- Day 10
  - Add preloaded mock datasets in data/mocks (flow and architecture variants)
- Day 11
  - Flesh out API docs via OpenAPI (auto from FastAPI)
  - Write README updates and usage examples
- Day 12
  - Tag a release build, verify demo script flows, and package the data/mocks

Risks and mitigations
- Risk: Over-building the backend given the optional nature. Mitigation: Keep endpoints mock-only; client retains storage/export responsibilities.
- Risk: Divergent graph schemas across views. Mitigation: Align on a single Graph schema with a “view” field; front-end handles layout and visual mapping.
- Risk: Heavy export features creep into backend. Mitigation: Defer server-side PNG export; mark as explicitly optional/not required for MVP.

Status
- This doc captures backend requirements from the Week 2 plan and translates them into a concrete API contract and action items tailored for the Python backend container.
