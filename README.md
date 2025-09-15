Vision Modelling Backend (MVP)

Overview
- FastAPI backend exposing a mock-first API for the Vision Modelling MVP.
- Serves mocked calls and graphs, with optional file-based persistence for saved models.
- Aligns with docs/backend/requirements-week2.md and docs/backend/architecture-outline.md.

Endpoints (high-level)
- GET /health — Service status
- GET /calls — Mocked call list
- POST /model/start — Returns a mock Graph JSON for a given call_id and view
- GET /models — List saved models (file-based)
- GET /models/{model_id} — Load a saved model
- POST /models — Save/upsert a model (id optional; server generates)
- PUT /models/{model_id} — Update model by id
- DELETE /models/{model_id} — Delete model by id
- GET /models/{model_id}/export — Returns 501 (client handles PNG export)

Run locally
1) Install Python deps
   python3 -m pip install -r requirements.txt

2) Start dev server (default port 3001)
   # Option A (recommended):
   python App.py
   # Option B:
   uvicorn App:app --host 0.0.0.0 --port 3001 --reload

3) Open docs
   - Swagger UI: http://localhost:3001/docs
   - ReDoc: http://localhost:3001/redoc

Configuration (optional)
- PORT: listening port (default: 3001)
- SERVER_HOST: host to bind (default: 0.0.0.0)
- DATA_DIR: override path to data directory (default: ./data)
- CORS_ALLOW_ORIGINS: comma-separated list of allowed origins (default: '*')
- LOG_LEVEL: Python logging level (default: INFO)

Project structure
- App.py — FastAPI app setup (CORS, logging, routers, startup, runtime entrypoint)
- routers/ — API route modules
- models/ — Pydantic schemas
- services/ — mock data loader and file-based storage
- utils/ — helpers for ids, time, IO, version
- data/ — mock datasets and persisted models

Notes
- No websockets or server-side export for MVP (handled by front-end via Cytoscape).
- This backend ships a mock data pack under data/mocks/ for demo flows.
