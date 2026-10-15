# Nexus Hub — Alan Vo | AI & Machine Learning

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


**Deploy intelligent multi-agent swarms, coordinate autonomous workflows, and build conversational AI systems with adaptive memory and vector RAG.**

---

## Overview

Nexus Hub is a full-stack platform for orchestrating AI agent swarms. It provides a FastAPI backend with PostgreSQL persistence, a React + Vite frontend, and integrates with Keycloak for OIDC authentication. The system supports hierarchical, mesh, ring, and star topologies with dynamic agent spawning, task orchestration, and semantic memory retrieval via HNSW vector indexing.

### Core Capabilities

| Workflow | Description |
|----------|-------------|
| **Swarm Lifecycle** | Create swarms with configurable topology, scale agents up/down, monitor health |
| **Task Orchestration** | Submit tasks with priority, agents claim/execute, real-time status updates |
| **Memory & RAG** | Store embeddings from agent outputs, semantic search, context-aware retrieval |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│  Backend    │────▶│  PostgreSQL │
│  (React)    │     │  (FastAPI)  │     │  (Primary)  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐     ┌─────────────┐
                    │   Keycloak  │     │   Redis     │
                    │   (OIDC)    │     │   (Cache)   │
                    └─────────────┘     └─────────────┘
```

**Backend modules:** `app/api`, `app/services`, `app/models`, `app/core`
**Frontend structure:** `src/components`, `src/api`, `src/pages`, `src/hooks`, `src/types`

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node 24+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### With Docker Compose (Recommended)

```bash
# Clone and configure
git clone https://github.com/ALANDVO/nexus-hub-alan-vo
cd nexus-hub-alan-vo
cp .env.example .env
# Edit .env with your settings (LLM_API_KEY, SECRET_KEY, etc.)

# Start all services
docker compose up -d

# Access
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Keycloak: http://localhost:8080 (admin/admin)
```

### Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173 with proxy to backend
```

---

## API Reference

Base URL: `/api/v1`

### Health
- `GET /healthz` — Liveness check
- `GET /healthz/ready` — Readiness with DB check

### Swarms
- `POST /swarms` — Create swarm
- `GET /swarms` — List swarms (pagination, filtering)
- `GET /swarms/{id}` — Get swarm
- `GET /swarms/{id}/stats` — Swarm statistics
- `PATCH /swarms/{id}` — Update swarm
- `DELETE /swarms/{id}` — Soft delete (hard=true for permanent)

### Agents
- `POST /swarms/{swarm_id}/agents` — Spawn agent
- `GET /swarms/{swarm_id}/agents` — List agents
- `GET /swarms/{swarm_id}/agents/{id}` — Get agent
- `PATCH /swarms/{swarm_id}/agents/{id}/status` — Update status
- `POST /swarms/{swarm_id}/agents/{id}/terminate` — Terminate agent

### Tasks
- `POST /swarms/{swarm_id}/tasks` — Create task
- `GET /swarms/{swarm_id}/tasks` — List tasks
- `GET /swarms/{swarm_id}/tasks/{id}` — Get task
- `POST /swarms/{swarm_id}/tasks/{id}/claim` — Agent claims task
- `POST /swarms/{swarm_id}/tasks/{id}/start` — Start execution
- `POST /swarms/{swarm_id}/tasks/{id}/complete` — Complete with result
- `POST /swarms/{swarm_id}/tasks/{id}/fail` — Mark failed
- `POST /swarms/{swarm_id}/tasks/{id}/cancel` — Cancel

### Memories
- `POST /swarms/{swarm_id}/memories` — Store memory with optional embedding
- `GET /swarms/{swarm_id}/memories` — List memories
- `GET /swarms/{swarm_id}/memories/{id}` — Get memory
- `POST /swarms/{swarm_id}/memories/search` — Semantic search by embedding

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://nexus:nexus@db:5432/nexus` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `KEYCLOAK_URL` | Keycloak base URL | `http://keycloak:8080` |
| `KEYCLOAK_REALM` | Realm name | `nexus` |
| `KEYCLOAK_CLIENT_ID` | Client ID | `nexus-backend` |
| `KEYCLOAK_CLIENT_SECRET` | Client secret | *(required in production)* |
| `OIDC_ISSUER` | OIDC issuer URL | `http://keycloak:8080/realms/nexus` |
| `OIDC_AUDIENCE` | Expected audience | `nexus-api` |
| `LLM_API_KEY` | LLM provider API key | *(optional)* |
| `LLM_PROVIDER` | Provider type | `openai-compatible` |
| `LLM_MODEL` | Model name | `gpt-4o-mini` |
| `LLM_BASE_URL` | Custom base URL | *(optional)* |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `SECRET_KEY` | JWT signing secret | *(required in production)* |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173` |
| `DEMO_MODE` | Local-only demo (binds 127.0.0.1) | `false` |

---

## LLM Provider Configuration

Supported providers (configure via `LLM_PROVIDER`):

| Provider | `LLM_PROVIDER` | `LLM_BASE_URL` Example |
|----------|----------------|------------------------|
| OpenAI | `openai-compatible` | `https://api.openai.com/v1` |
| OpenRouter | `openai-compatible` | `https://openrouter.ai/api/v1` |
| Ollama | `ollama` | `http://localhost:11434/v1` |
| LiteLLM | `openai-compatible` | `http://localhost:4000` |
| Anthropic | `anthropic` | `https://api.anthropic.com` |
| Gemini | `gemini` | `https://generativelanguage.googleapis.com` |

Only `LLM_API_KEY` is a secret. Provider, model, and base URL are non-secret settings.

---

## Keycloak Setup (OIDC + SAML Broker)

1. Access Keycloak at `http://localhost:8080` (admin/admin)
2. Create realm `nexus` or import `docs/keycloak-realm.json`
3. Create client `nexus-backend` with:
   - Access Type: `confidential`
   - Standard Flow: `ON`
   - Direct Access Grants: `OFF`
   - Valid Redirect URIs: `http://localhost:5173/*`
   - Web Origins: `http://localhost:5173`
4. For SAML: Configure Identity Provider → SAML v2.0 → map attributes

**Roles:** `viewer` (read), `operator` (read/write), `admin` (all)

---

## Testing

### Backend
```bash
cd backend
source .venv/bin/activate
PYTHONPATH=backend pytest -v
```

### Frontend
```bash
cd frontend
npm run test
```

### Type Check
```bash
cd frontend
npm run build  # Runs tsc then vite build
```

---

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `KEYCLOAK_CLIENT_SECRET`
- [ ] Configure TLS reverse proxy (nginx/Traefik/Caddy)
- [ ] Use managed PostgreSQL (RDS, Cloud SQL) with backups
- [ ] Enable Keycloak HTTPS and secure admin console
- [ ] Set `DEMO_MODE=false` (default)
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Set up monitoring (Prometheus/Grafana via `/metrics` if enabled)
- [ ] Backup strategy for `nexus-db-data` and `nexus-hnsw-data` volumes

### Docker Build (CI)

```bash
docker compose -f compose.yaml build
```

### Backup/Restore

```bash
# Backup
docker exec nexus-db pg_dump -U nexus nexus > backup.sql
docker cp nexus-hnsw-data:/data ./hnsw-backup

# Restore
docker exec -i nexus-db psql -U nexus nexus < backup.sql
docker cp ./hnsw-backup nexus-hnsw-data:/data
```

---

## Security Limitations

- **Demo mode** binds to `127.0.0.1` only; startup refuses demo mode if `DEMO_MODE=true` in non-local environments
- No hardcoded credentials; all secrets via environment variables
- OIDC tokens validated with signature, issuer, audience checks
- HttpOnly SameSite cookies for session management (backend-managed)
- CSRF protection on cookie-authenticated writes
- Access tokens never persisted in localStorage (SPA uses memory + sessionStorage for PKCE state)
- Rate limiting and request size limits recommended at reverse proxy

---

## AI/ML Evaluation

Nexus Hub includes a deterministic swarm coordination engine with vector memory. Evaluation focuses on:

- **Swarm coordination latency**: <50ms for agent spawn/claim operations
- **Memory retrieval**: HNSW cosine similarity >0.95 recall at 10k vectors
- **Task throughput**: 100+ tasks/minute with 10-agent swarm

Run baseline:
```bash
cd backend
PYTHONPATH=backend python -m pytest backend/tests/test_performance.py -v
```

**Failure cases**: High-dimensional embeddings (>1024) degrade HNSW performance; mitigate with dimensionality reduction. Network partitions between agents require application-level retry logic.

---

## License

MIT License — Copyright (c) 2026 Alan Vo <alanvo@gmail.com>

---

## Author

**Alan Vo** — alanvo@gmail.com — [GitHub](https://github.com/ALANDVO)