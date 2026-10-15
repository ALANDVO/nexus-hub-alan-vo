from fastapi import APIRouter

from app.api import swarms, agents, tasks, memories, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(swarms.router, prefix="/swarms", tags=["swarms"])
api_router.include_router(agents.router, prefix="/swarms/{swarm_id}/agents", tags=["agents"])
api_router.include_router(tasks.router, prefix="/swarms/{swarm_id}/tasks", tags=["tasks"])
api_router.include_router(memories.router, prefix="/swarms/{swarm_id}/memories", tags=["memories"])