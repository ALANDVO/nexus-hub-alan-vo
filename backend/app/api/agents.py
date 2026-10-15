from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db_session
from app.services import AgentService, SwarmService
from app.api.schemas import (
    AgentCreate, AgentResponse, AgentStatusUpdate,
    AgentRole, AgentStatus, PaginatedResponse
)

router = APIRouter()


def get_agent_service(db: Session = Depends(get_db_session)) -> AgentService:
    return AgentService(db)


def get_swarm_service(db: Session = Depends(get_db_session)) -> SwarmService:
    return SwarmService(db)


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def spawn_agent(
    swarm_id: str,
    payload: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    agent = agent_service.spawn_agent(swarm_id=swarm_id, **payload.model_dump())
    if not agent:
        raise HTTPException(status_code=400, detail="Cannot spawn agent: swarm at max capacity or not found")
    return agent


@router.get("", response_model=PaginatedResponse)
def list_agents(
    swarm_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    role: Optional[AgentRole] = None,
    status: Optional[AgentStatus] = None,
    agent_service: AgentService = Depends(get_agent_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    agents = agent_service.list_agents(swarm_id, skip=skip, limit=limit, role=role, status=status)
    total = agent_service.count_agents(swarm_id, role=role, status=status)
    return PaginatedResponse(items=agents, total=total, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(swarm_id: str, agent_id: str, agent_service: AgentService = Depends(get_agent_service)):
    agent = agent_service.get_agent(agent_id)
    if not agent or agent.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}/status", response_model=AgentResponse)
def update_agent_status(
    swarm_id: str,
    agent_id: str,
    payload: AgentStatusUpdate,
    agent_service: AgentService = Depends(get_agent_service),
):
    agent = agent_service.get_agent(agent_id)
    if not agent or agent.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_service.update_agent_status(agent_id, payload.status, payload.error_message)
    return agent


@router.post("/{agent_id}/terminate", status_code=status.HTTP_204_NO_CONTENT)
def terminate_agent(swarm_id: str, agent_id: str, agent_service: AgentService = Depends(get_agent_service)):
    agent = agent_service.get_agent(agent_id)
    if not agent or agent.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Agent not found")
    success = agent_service.terminate_agent(agent_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to terminate agent")
    return None