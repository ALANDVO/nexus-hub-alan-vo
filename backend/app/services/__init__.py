from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from app.models import (
    Swarm, Agent, Task, Memory,
    SwarmTopology, AgentRole, AgentStatus, TaskStatus
)
from app.core.database import get_db_session


class SwarmService:
    def __init__(self, db: Session):
        self.db = db

    def create_swarm(
        self,
        name: str,
        description: Optional[str] = None,
        topology: SwarmTopology = SwarmTopology.HIERARCHICAL,
        max_agents: int = 10,
        min_agents: int = 1,
        auto_scale: bool = False,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.3,
        config: Optional[Dict[str, Any]] = None,
    ) -> Swarm:
        swarm = Swarm(
            name=name,
            description=description,
            topology=topology,
            max_agents=max_agents,
            min_agents=min_agents,
            auto_scale=auto_scale,
            scale_up_threshold=scale_up_threshold,
            scale_down_threshold=scale_down_threshold,
            config=config or {},
        )
        self.db.add(swarm)
        self.db.commit()
        self.db.refresh(swarm)
        return swarm

    def get_swarm(self, swarm_id: str) -> Optional[Swarm]:
        return self.db.query(Swarm).filter(Swarm.id == swarm_id, Swarm.deleted_at.is_(None)).first()

    def list_swarms(
        self,
        skip: int = 0,
        limit: int = 50,
        topology: Optional[SwarmTopology] = None,
        include_deleted: bool = False,
    ) -> List[Swarm]:
        query = self.db.query(Swarm)
        if not include_deleted:
            query = query.filter(Swarm.deleted_at.is_(None))
        if topology:
            query = query.filter(Swarm.topology == topology)
        return query.order_by(desc(Swarm.created_at)).offset(skip).limit(limit).all()

    def count_swarms(self, topology: Optional[SwarmTopology] = None, include_deleted: bool = False) -> int:
        query = self.db.query(func.count(Swarm.id))
        if not include_deleted:
            query = query.filter(Swarm.deleted_at.is_(None))
        if topology:
            query = query.filter(Swarm.topology == topology)
        return query.scalar() or 0

    def update_swarm(self, swarm_id: str, **kwargs) -> Optional[Swarm]:
        swarm = self.get_swarm(swarm_id)
        if not swarm:
            return None
        for key, value in kwargs.items():
            if hasattr(swarm, key) and value is not None:
                setattr(swarm, key, value)
        swarm.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(swarm)
        return swarm

    def delete_swarm(self, swarm_id: str, hard: bool = False) -> bool:
        swarm = self.get_swarm(swarm_id)
        if not swarm:
            return False
        if hard:
            self.db.delete(swarm)
        else:
            swarm.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def get_swarm_stats(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        swarm = self.get_swarm(swarm_id)
        if not swarm:
            return None

        agent_counts = (
            self.db.query(Agent.status, func.count(Agent.id))
            .filter(Agent.swarm_id == swarm_id)
            .group_by(Agent.status)
            .all()
        )
        task_counts = (
            self.db.query(Task.status, func.count(Task.id))
            .filter(Task.swarm_id == swarm_id)
            .group_by(Task.status)
            .all()
        )
        memory_count = (
            self.db.query(func.count(Memory.id))
            .filter(Memory.swarm_id == swarm_id)
            .scalar()
        )

        return {
            "swarm_id": swarm_id,
            "name": swarm.name,
            "topology": swarm.topology.value,
            "max_agents": swarm.max_agents,
            "min_agents": swarm.min_agents,
            "auto_scale": swarm.auto_scale,
            "agents": {status.value: count for status, count in agent_counts},
            "tasks": {status.value: count for status, count in task_counts},
            "memories": memory_count or 0,
            "created_at": swarm.created_at.isoformat(),
        }


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def spawn_agent(
        self,
        swarm_id: str,
        name: str,
        role: AgentRole = AgentRole.DEVELOPER,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Agent]:
        swarm = self.db.query(Swarm).filter(Swarm.id == swarm_id, Swarm.deleted_at.is_(None)).first()
        if not swarm:
            return None

        active_count = (
            self.db.query(func.count(Agent.id))
            .filter(Agent.swarm_id == swarm_id, Agent.status.in_([AgentStatus.ACTIVE, AgentStatus.IDLE, AgentStatus.BUSY, AgentStatus.SPAWNING]))
            .scalar()
        )
        if active_count >= swarm.max_agents:
            return None

        max_order = (
            self.db.query(func.max(Agent.spawn_order))
            .filter(Agent.swarm_id == swarm_id)
            .scalar()
        ) or 0

        agent = Agent(
            swarm_id=swarm_id,
            name=name,
            role=role,
            status=AgentStatus.SPAWNING,
            config=config or {},
            spawn_order=max_order + 1,
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def list_agents(
        self,
        swarm_id: str,
        skip: int = 0,
        limit: int = 50,
        role: Optional[AgentRole] = None,
        status: Optional[AgentStatus] = None,
    ) -> List[Agent]:
        query = self.db.query(Agent).filter(Agent.swarm_id == swarm_id)
        if role:
            query = query.filter(Agent.role == role)
        if status:
            query = query.filter(Agent.status == status)
        return query.order_by(asc(Agent.spawn_order)).offset(skip).limit(limit).all()

    def count_agents(self, swarm_id: str, role: Optional[AgentRole] = None, status: Optional[AgentStatus] = None) -> int:
        query = self.db.query(func.count(Agent.id)).filter(Agent.swarm_id == swarm_id)
        if role:
            query = query.filter(Agent.role == role)
        if status:
            query = query.filter(Agent.status == status)
        return query.scalar() or 0

    def update_agent_status(self, agent_id: str, status: AgentStatus, error_message: Optional[str] = None) -> Optional[Agent]:
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        agent.status = status
        agent.last_heartbeat = datetime.now(timezone.utc)
        if error_message:
            agent.error_message = error_message
        if status == AgentStatus.TERMINATED:
            agent.terminated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def assign_task(self, agent_id: str, task_id: str) -> Optional[Agent]:
        agent = self.get_agent(agent_id)
        if not agent or agent.status not in [AgentStatus.ACTIVE, AgentStatus.IDLE]:
            return None
        agent.current_task_id = task_id
        agent.status = AgentStatus.BUSY
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def release_agent(self, agent_id: str) -> Optional[Agent]:
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        agent.current_task_id = None
        agent.status = AgentStatus.IDLE
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def terminate_agent(self, agent_id: str) -> bool:
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        agent.status = AgentStatus.TERMINATING
        self.db.commit()
        # Actual termination would be async; mark terminated
        agent.status = AgentStatus.TERMINATED
        agent.terminated_at = datetime.now(timezone.utc)
        self.db.commit()
        return True


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        swarm_id: str,
        name: str,
        description: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        priority: int = 0,
    ) -> Optional[Task]:
        swarm = self.db.query(Swarm).filter(Swarm.id == swarm_id, Swarm.deleted_at.is_(None)).first()
        if not swarm:
            return None

        task = Task(
            swarm_id=swarm_id,
            name=name,
            description=description,
            payload=payload or {},
            priority=priority,
            status=TaskStatus.PENDING,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list_tasks(
        self,
        swarm_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[TaskStatus] = None,
        agent_id: Optional[str] = None,
    ) -> List[Task]:
        query = self.db.query(Task).filter(Task.swarm_id == swarm_id)
        if status:
            query = query.filter(Task.status == status)
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
        return query.order_by(desc(Task.priority), asc(Task.created_at)).offset(skip).limit(limit).all()

    def count_tasks(self, swarm_id: str, status: Optional[TaskStatus] = None) -> int:
        query = self.db.query(func.count(Task.id)).filter(Task.swarm_id == swarm_id)
        if status:
            query = query.filter(Task.status == status)
        return query.scalar() or 0

    def claim_task(self, task_id: str, agent_id: str) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return None
        agent = self.db.query(Agent).filter(Agent.id == agent_id, Agent.swarm_id == task.swarm_id).first()
        if not agent or agent.status not in [AgentStatus.ACTIVE, AgentStatus.IDLE]:
            return None
        task.status = TaskStatus.CLAIMED
        task.agent_id = agent_id
        agent.status = AgentStatus.BUSY
        agent.current_task_id = task_id
        self.db.commit()
        self.db.refresh(task)
        return task

    def start_task(self, task_id: str) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task or task.status != TaskStatus.CLAIMED:
            return None
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
        return task

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return None
        task.status = TaskStatus.COMPLETED
        task.result = result
        task.completed_at = datetime.now(timezone.utc)
        if task.agent_id:
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task_id = None
        self.db.commit()
        self.db.refresh(task)
        return task

    def fail_task(self, task_id: str, error_message: str) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task or task.status not in [TaskStatus.CLAIMED, TaskStatus.RUNNING]:
            return None
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.now(timezone.utc)
        if task.agent_id:
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task_id = None
        self.db.commit()
        self.db.refresh(task)
        return task

    def cancel_task(self, task_id: str) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task or task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return None
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc)
        if task.agent_id:
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task_id = None
        self.db.commit()
        self.db.refresh(task)
        return task


class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def store_memory(
        self,
        swarm_id: str,
        content: str,
        embedding: Optional[List[float]] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        memory_type: str = "general",
        importance: float = 1.0,
    ) -> Memory:
        memory = Memory(
            swarm_id=swarm_id,
            agent_id=agent_id,
            task_id=task_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            memory_type=memory_type,
            importance=importance,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        return self.db.query(Memory).filter(Memory.id == memory_id).first()

    def list_memories(
        self,
        swarm_id: str,
        skip: int = 0,
        limit: int = 50,
        memory_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> List[Memory]:
        query = self.db.query(Memory).filter(Memory.swarm_id == swarm_id)
        if memory_type:
            query = query.filter(Memory.memory_type == memory_type)
        if agent_id:
            query = query.filter(Memory.agent_id == agent_id)
        if task_id:
            query = query.filter(Memory.task_id == task_id)
        return query.order_by(desc(Memory.importance), desc(Memory.created_at)).offset(skip).limit(limit).all()

    def count_memories(self, swarm_id: str, memory_type: Optional[str] = None) -> int:
        query = self.db.query(func.count(Memory.id)).filter(Memory.swarm_id == swarm_id)
        if memory_type:
            query = query.filter(Memory.memory_type == memory_type)
        return query.scalar() or 0

    def semantic_search(
        self,
        swarm_id: str,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7,
    ) -> List[Memory]:
        """Simple cosine similarity search. In production, use HNSW index."""
        from math import sqrt

        def cosine_sim(a: List[float], b: List[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = sqrt(sum(x * x for x in a))
            norm_b = sqrt(sum(y * y for y in b))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot / (norm_a * norm_b)

        memories = self.db.query(Memory).filter(
            Memory.swarm_id == swarm_id,
            Memory.embedding.isnot(None),
        ).all()

        scored = []
        for m in memories:
            if m.embedding:
                sim = cosine_sim(query_embedding, m.embedding)
                if sim >= min_similarity:
                    scored.append((sim, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:limit]]