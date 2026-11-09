from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Set, Any
from datetime import datetime, timezone
import json
import asyncio

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


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, swarm_id: str, websocket: WebSocket):
        await websocket.accept()
        if swarm_id not in self.active_connections:
            self.active_connections[swarm_id] = set()
        self.active_connections[swarm_id].add(websocket)

    def disconnect(self, swarm_id: str, websocket: WebSocket):
        if swarm_id in self.active_connections:
            self.active_connections[swarm_id].discard(websocket)
            if not self.active_connections[swarm_id]:
                del self.active_connections[swarm_id]

    async def broadcast(self, swarm_id: str, message: dict):
        if swarm_id in self.active_connections:
            dead = set()
            for ws in self.active_connections[swarm_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.add(ws)
            for ws in dead:
                self.disconnect(swarm_id, ws)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, swarm_id: str):
    await manager.connect(swarm_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for keepalive/ping-pong
            await websocket.send_json({"type": "ping", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(swarm_id, websocket)


async def broadcast_task_update(swarm_id: str, task_id: str, event: str, data: dict):
    await manager.broadcast(swarm_id, {
        "type": "task_update",
        "task_id": task_id,
        "event": event,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


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
        raise HTTPException(status_code=400, detail="Cannot create task: swarm not found")
    return task


@router.get("", response_model=PaginatedResponse[TaskResponse])
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
    payload: TaskAction,
    task_service: TaskService = Depends(get_task_service),
    agent_service: AgentService = Depends(get_agent_service),
    swarm_service: SwarmService = Depends(get_swarm_service),
):
    swarm = swarm_service.get_swarm(swarm_id)
    if not swarm:
        raise HTTPException(status_code=404, detail="Swarm not found")

    agent = agent_service.get_agent(payload.agent_id)
    if not agent or agent.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Agent not found in this swarm")

    task = task_service.claim_task(task_id, payload.agent_id)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot claim task: not pending or agent not available")
    
    # Broadcast task update via WebSocket
    import asyncio
    asyncio.create_task(broadcast_task_update(swarm_id, task_id, "claimed", {"agent_id": payload.agent_id, "status": task.status.value}))
    
    return task


@router.post("/{task_id}/start", response_model=TaskResponse)
def start_task(swarm_id: str, task_id: str, task_service: TaskService = Depends(get_task_service)):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.start_task(task_id)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot start task: not claimed")
    
    # Broadcast task update via WebSocket
    import asyncio
    asyncio.create_task(broadcast_task_update(swarm_id, task_id, "started", {"status": task.status.value, "started_at": task.started_at.isoformat() if task.started_at else None}))
    
    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    swarm_id: str,
    task_id: str,
    result: Dict[str, Any],
    task_service: TaskService = Depends(get_task_service),
):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.complete_task(task_id, result)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot complete task: not running")
    
    # Broadcast task update via WebSocket
    import asyncio
    asyncio.create_task(broadcast_task_update(swarm_id, task_id, "completed", {"result": task.result, "status": task.status.value, "completed_at": task.completed_at.isoformat() if task.completed_at else None}))
    
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
    
    # Broadcast task update via WebSocket
    import asyncio
    asyncio.create_task(broadcast_task_update(swarm_id, task_id, "failed", {"error_message": task.error_message, "status": task.status.value, "completed_at": task.completed_at.isoformat() if task.completed_at else None}))
    
    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(swarm_id: str, task_id: str, task_service: TaskService = Depends(get_task_service)):
    task = task_service.get_task(task_id)
    if not task or task.swarm_id != swarm_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=400, detail="Cannot cancel task: already terminal")
    
    # Broadcast task update via WebSocket
    import asyncio
    asyncio.create_task(broadcast_task_update(swarm_id, task_id, "cancelled", {"status": task.status.value, "completed_at": task.completed_at.isoformat() if task.completed_at else None}))
    
    return task
