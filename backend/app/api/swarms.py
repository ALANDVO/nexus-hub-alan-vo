from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db_session
from app.services import SwarmService
from app.api.schemas import (
    SwarmCreate, SwarmUpdate, SwarmResponse, SwarmStats,
    SwarmTopology, PaginatedResponse
)

router = APIRouter()


def get_swarm_service(db: Session = Depends(get_db_session)) -> SwarmService:
    return SwarmService(db)


@router.post("", response_model=SwarmResponse, status_code=status.HTTP_201_CREATED)
def create_swarm(payload: SwarmCreate, service: SwarmService = Depends(get_swarm_service)):
    swarm = service.create_swarm(**payload.model_dump())
    return swarm


@router.get("", response_model=PaginatedResponse)
def list_swarms(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    topology: Optional[SwarmTopology] = None,
    include_deleted: bool = False,
    service: SwarmService = Depends(get_swarm_service),
):
    swarms = service.list_swarms(skip=skip, limit=limit, topology=topology, include_deleted=include_deleted)
    total = service.count_swarms(topology=topology, include_deleted=include_deleted)
    return PaginatedResponse(items=swarms, total=total, skip=skip, limit=limit)


@router.get("/{swarm_id}", response_model=SwarmResponse)
def get_swarm(swarm_id: str, service: SwarmService = Depends(get_swarm_service)):
    swarm = service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")
    return swarm


@router.get("/{swarm_id}/stats", response_model=SwarmStats)
def get_swarm_stats(swarm_id: str, service: SwarmService = Depends(get_swarm_service)):
    stats = service.get_swarm_stats(swarm_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Swarm not found")
    return stats


@router.patch("/{swarm_id}", response_model=SwarmResponse)
def update_swarm(swarm_id: str, payload: SwarmUpdate, service: SwarmService = Depends(get_swarm_service)):
    swarm = service.update_swarm(swarm_id, **payload.model_dump(exclude_unset=True))
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")
    return swarm


@router.delete("/{swarm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_swarm(swarm_id: str, hard: bool = Query(False), service: SwarmService = Depends(get_swarm_service)):
    success = service.delete_swarm(swarm_id, hard=hard)
    if not success:
        raise HTTPException(status_code=404, detail="Swarm not found")
    return None