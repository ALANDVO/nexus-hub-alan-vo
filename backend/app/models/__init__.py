import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, DateTime, Enum, ForeignKey, Integer, Float, Index, JSON, Boolean
)
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def gen_uuid() -> str:
    return str(uuid.uuid4())


class SwarmTopology(str, enum.Enum):
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    RING = "ring"
    STAR = "star"


class AgentRole(str, enum.Enum):
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


class AgentStatus(str, enum.Enum):
    SPAWNING = "spawning"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    ERROR = "error"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Swarm(Base):
    __tablename__ = "swarms"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    topology = Column(Enum(SwarmTopology), nullable=False, default=SwarmTopology.HIERARCHICAL)
    max_agents = Column(Integer, nullable=False, default=10)
    min_agents = Column(Integer, nullable=False, default=1)
    auto_scale = Column(Boolean, nullable=False, default=False)
    scale_up_threshold = Column(Float, nullable=False, default=0.8)
    scale_down_threshold = Column(Float, nullable=False, default=0.3)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    agents = relationship("Agent", back_populates="swarm", lazy="dynamic")
    tasks = relationship("Task", back_populates="swarm", lazy="dynamic")
    memories = relationship("Memory", back_populates="swarm", lazy="dynamic")

    __table_args__ = (
        Index("ix_swarms_created_at", "created_at"),
        Index("ix_swarms_deleted_at", "deleted_at"),
    )


class Agent(Base):
    __tablename__ = "agents"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    swarm_id = Column(PG_UUID(as_uuid=False), ForeignKey("swarms.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(Enum(AgentRole), nullable=False, default=AgentRole.DEVELOPER)
    status = Column(Enum(AgentStatus), nullable=False, default=AgentStatus.SPAWNING)
    config = Column(JSON, nullable=True)
    current_task_id = Column(PG_UUID(as_uuid=False), ForeignKey("tasks.id"), nullable=True)
    spawn_order = Column(Integer, nullable=False, default=0)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    terminated_at = Column(DateTime(timezone=True), nullable=True)

    swarm = relationship("Swarm", back_populates="agents")
    current_task = relationship("Task", foreign_keys=[current_task_id])
    memories = relationship("Memory", back_populates="agent", lazy="dynamic")

    __table_args__ = (
        Index("ix_agents_swarm_status", "swarm_id", "status"),
        Index("ix_agents_swarm_role", "swarm_id", "role"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    swarm_id = Column(PG_UUID(as_uuid=False), ForeignKey("swarms.id"), nullable=False, index=True)
    agent_id = Column(PG_UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    payload = Column(JSON, nullable=True)
    priority = Column(Integer, nullable=False, default=0)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    swarm = relationship("Swarm", back_populates="tasks")
    agent = relationship("Agent", foreign_keys=[agent_id], backref="assigned_tasks")

    __table_args__ = (
        Index("ix_tasks_swarm_status", "swarm_id", "status"),
        Index("ix_tasks_swarm_priority_created", "swarm_id", "priority", "created_at"),
    )


class Memory(Base):
    __tablename__ = "memories"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    swarm_id = Column(PG_UUID(as_uuid=False), ForeignKey("swarms.id"), nullable=False, index=True)
    agent_id = Column(PG_UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True, index=True)
    task_id = Column(PG_UUID(as_uuid=False), ForeignKey("tasks.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Stored as list[float]
    metadata = Column(JSON, nullable=True)
    memory_type = Column(String(64), nullable=False, default="general")  # general, task_output, research, etc.
    importance = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    swarm = relationship("Swarm", back_populates="memories")
    agent = relationship("Agent", back_populates="memories")
    task = relationship("Task", backref="memories")

    __table_args__ = (
        Index("ix_memories_swarm_type_created", "swarm_id", "memory_type", "created_at"),
        Index("ix_memories_agent_created", "agent_id", "created_at"),
    )