# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this format.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-15

### Added
- Initial release of Nexus Hub
- FastAPI backend with modular architecture (api, services, models, core)
- React + TypeScript + Vite frontend with TanStack Query, Zustand, Tailwind CSS
- PostgreSQL persistence with SQLAlchemy 2.0 and Alembic migrations
- Redis caching layer
- Keycloak OIDC authentication with PKCE, HttpOnly cookies, CSRF protection
- Swarm management: create, list, get, update, delete with pagination/filtering
- Agent lifecycle: spawn, status updates, termination with role-based assignment
- Task orchestration: submit, claim, start, complete, fail, cancel with priority queue
- Vector memory system: store embeddings, semantic search via cosine similarity
- Docker Compose orchestration: backend, frontend, PostgreSQL, Redis, Keycloak
- Health checks for all services
- GitHub Actions CI pipeline (backend tests, frontend typecheck/build/test, Docker builds)
- Comprehensive README with architecture diagram, API reference, deployment guide

### Security
- OIDC tokens validated for signature, issuer, audience
- Demo mode binds to localhost only; refuses startup in production
- No hardcoded secrets; all credentials via environment variables
- HttpOnly SameSite cookies with CSRF protection

### Domain Engine
- Deterministic swarm coordination engine (no LLM required for core operations)
- Topologies: hierarchical, mesh, ring, star
- Agent roles: orchestrator, analyst, developer, researcher, validator, specialist, optimizer, tester, documenter, monitor, reviewer
- Auto-scaling policies with configurable thresholds

---

## [Unreleased]

### Planned
- HNSW index for production-scale vector search
- WebSocket/SSE for real-time task updates
- LLM adapter abstraction (OpenAI-compatible, Anthropic, Gemini, Ollama)
- RAG endpoint with grounded responses
- Keycloak realm import file
- Comprehensive test suite (12+ backend, 3+ frontend)
- Performance benchmarks
- Backup/restore tooling