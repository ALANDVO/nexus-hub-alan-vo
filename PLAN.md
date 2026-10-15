# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — Core FastAPI/React skeleton with health check

Status: in_progress

Acceptance:
- FastAPI app starts and responds to /healthz
- React + Vite frontend builds and serves
- Docker compose brings up backend, frontend, Keycloak, PostgreSQL
- Basic project structure with all required config files

### swarm-domain — Swarm coordination domain engine

Status: planned

Acceptance:
- Create/list/get swarms with topology and agent limits
- Spawn/terminate agents within a swarm
- Persist swarm and agent state to SQLite
- REST API with validation, pagination, filtering

### task-orchestration — Task orchestration workflow

Status: planned

Acceptance:
- Submit tasks to a swarm with payload and priority
- Agents claim and execute tasks with status tracking
- Task results stored and retrievable
- WebSocket or SSE for real-time task updates

### memory-rag — Vector memory with RAG retrieval

Status: planned

Acceptance:
- Store embeddings for agent memories and task outputs
- Semantic search across swarm memory
- RAG endpoint for context-aware responses
- HNSW index for efficient similarity search

### oidc-auth — OIDC authentication with Keycloak

Status: planned

Acceptance:
- Backend validates Keycloak JWT tokens
- Frontend login/logout flow with PKCE
- Role-based access (viewer, operator, admin)
- Protected API endpoints with authorization

### frontend-workflows — Frontend dashboard with three workflows

Status: planned

Acceptance:
- Swarm dashboard: create, monitor, delete swarms
- Agent management: spawn, view, terminate agents
- Task console: submit tasks, watch execution, view results
- Loading, error, empty states for all views

### packaging-docs — Docker, CI, documentation, portfolio.json

Status: planned

Acceptance:
- Backend and frontend Dockerfiles with non-root users
- compose.yaml with Keycloak, PostgreSQL, volumes
- GitHub Actions CI: pytest, npm build/test, Docker build
- README with install/run/test, architecture diagram, API ref
- portfolio.json at root with schema_version=1

