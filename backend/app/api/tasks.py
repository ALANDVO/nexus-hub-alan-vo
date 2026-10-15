from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db_session
from app.services import TaskService, SwarmService, AgentService
from app.api.schemas import (
    TaskCreate, TaskResponse, TaskAction,
    TaskStatus, PaginatedResponse
)

router = APIRouter()


def get_task_service(db: Session = Depends(get_db_session)) -> TaskService:
    return TaskService(db)


def get_swarm_service(db: Session = Depends(get_db_session)) -> SwarmService:
    return SwarmService(db)


def get_agent_service(db: Session = Depends(get_db_session)) -> AgentService:
    return AgentService(db)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    swarm_id: str,
    payload: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    task = task_service.create_task(swarm_id=swarm_id, **payload.model_dump())
    if not task:
        raise HTTPException(status_code=400, detail="Failed to create task")
    return task


@router.get("", response_model=PaginatedResponse)
def list_tasks(
    swarm_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[TaskStatus] = None,
    agent_id: Optional[str] = None,
    task_service: TaskService = Depends(get_task_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    tasks = task_service.list_tasks(swarm_id, skip=skip, limit=limit, status=status, agent_id=agent_id)
    total = task_service.count_tasks(swarm_id, status=status)
    return PaginatedResponse(items=tasks, total=total, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(swarm_id: str, task_id: str, task_service: TaskService = Depends(get_task_service)):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/claim", response_model=TaskResponse)
def claim_task(
    swarm_id: str,
    task_id: str,
    agent_id: str,
    task_service: TaskService = Depends(get_task_service),
    agent_service: AgentService = Depends(get_agent_service),
):
    agent = agent_service.get_agent(agent_id)
    if not agent or agent.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Agent not found")

    task = task_service.claim_task(task_id, agent_id)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot claim task: not pending or agent unavailable")
    return task


@router.post("/{task_id}/start", response_model=TaskResponse)
def start_task(swarm_id: str, task_id: str, task_service: TaskService = Depends(get_task_service)):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.start_task(task_id)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot start task: not claimed")
    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    swarm_id: str,
    task_id: str,
    result: dict,
    task_service: TaskService = Depends(get_task_service),
):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.complete_task(task_id, result)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot complete task: not running")
    return task


@router.post("/{task_id}/fail", response_model=TaskResponse)
def fail_task(
    swarm_id: str,
    task_id: str,
    error_message: str,
    task_service: TaskService = Depends(get_task_service),
):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.fail_task(task_id, error_message)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot fail task: not running or claimed")
    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(swarm_id: str, task_id: str, task_service: TaskService = Depends(get_task_service)):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot cancel task: already terminal")
    return task