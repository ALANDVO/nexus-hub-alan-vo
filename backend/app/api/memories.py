from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db_session
from app.services import MemoryService, SwarmService
from app.api.schemas import (
    MemoryCreate, MemoryResponse, MemorySearchRequest,
    PaginatedResponse
)

router = APIRouter()


def get_memory_service(db: Session = Depends(get_db_session)) -> MemoryService:
    return MemoryService(db)


def get_swarm_service(db: Session = Depends(get_db_session)) -> SwarmService:
    return SwarmService(db)


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def store_memory(
    swarm_id: str,
    payload: MemoryCreate,
    memory_service: MemoryService = Depends(get_memory_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    memory = memory_service.store_memory(swarm_id=swarm_id, **payload.model_dump())
    return memory


@router.get("", response_model=PaginatedResponse[MemoryResponse])
def list_memories(
    swarm_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    memory_type: Optional[str] = None,
    agent_id: Optional[str] = None,
    task_id: Optional[str] = None,
    memory_service: MemoryService = Depends(get_memory_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    memories = memory_service.list_memories(
        swarm_id, skip=skip, limit=limit, memory_type=memory_type, agent_id=agent_id, task_id=task_id
    )
    total = memory_service.count_memories(swarm_id, memory_type=memory_type)
    return PaginatedResponse(items=memories, total=total, skip=skip, limit=limit)


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(swarm_id: str, memory_id: str, memory_service: MemoryService = Depends(get_memory_service)):
    memory = memory_service.get_memory(memory_id)
    if not memory or memory.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.post("/search", response_model=List[MemoryResponse])
def semantic_search(
    swarm_id: str,
    payload: MemorySearchRequest,
    memory_service: MemoryService = Depends(get_memory_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    memories = memory_service.semantic_search(
        swarm_id,
        payload.query_embedding,
        limit=payload.limit,
        min_similarity=payload.min_similarity,
    )
    return memories