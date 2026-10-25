from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum


class SwarmTopology(str, Enum):
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    RING = "ring"
    STAR = "star"


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    VALIDATOR = "validator"
    SPECIALIST = "specialist"
    OPTIMIZER = "optimizer"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    MONITOR = "monitor"
    REVIEWER = "reviewer"


class AgentStatus(str, Enum):
    SPAWNING = "spawning"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    ERROR = "error"


class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SwarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    topology: SwarmTopology = SwarmTopology.HIERARCHICAL
    max_agents: int = Field(default=10, ge=1, le=1000)
    min_agents: int = Field(default=1, ge=1)
    auto_scale: bool = False
    scale_up_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    scale_down_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    config: Optional[Dict[str, Any]] = None


class SwarmCreate(SwarmBase):
    pass


class SwarmUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    topology: Optional[SwarmTopology] = None
    max_agents: Optional[int] = Field(None, ge=1, le=1000)
    min_agents: Optional[int] = Field(None, ge=1)
    auto_scale: Optional[bool] = None
    scale_up_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    scale_down_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    config: Optional[Dict[str, Any]] = None


class SwarmResponse(SwarmBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class SwarmStats(BaseModel):
    swarm_id: str
    name: str
    topology: str
    max_agents: int
    min_agents: int
    auto_scale: bool
    agents: Dict[str, int]
    tasks: Dict[str, int]
    memories: int
    created_at: str


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: AgentRole = AgentRole.DEVELOPER
    config: Optional[Dict[str, Any]] = None


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    swarm_id: str
    status: AgentStatus
    current_task_id: Optional[str] = None
    spawn_order: int
    last_heartbeat: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    terminated_at: Optional[datetime] = None


class AgentStatusUpdate(BaseModel):
    status: AgentStatus
    error_message: Optional[str] = None


class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    priority: int = Field(default=0, ge=-100, le=100)


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    swarm_id: str
    agent_id: Optional[str] = None
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TaskAction(BaseModel):
    agent_id: str


class MemoryBase(BaseModel):
    content: str = Field(..., min_length=1)
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="memory_metadata")
    memory_type: str = Field(default="general", max_length=64)
    importance: float = Field(default=1.0, ge=0.0, le=10.0)


class MemoryCreate(MemoryBase):
    agent_id: Optional[str] = None
    task_id: Optional[str] = None


class MemoryResponse(MemoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    swarm_id: str
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    created_at: datetime


class MemorySearchRequest(BaseModel):
    query_embedding: List[float] = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int