import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db_session
from app.models import Swarm, Agent, Task, Memory, SwarmTopology, AgentRole, AgentStatus, TaskStatus


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoints:
    def test_healthz(self):
        response = client.get("/api/v1/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data


class TestSwarmEndpoints:
    def test_create_swarm(self):
        response = client.post(
            "/api/v1/swarms",
            json={
                "name": "test-swarm",
                "description": "Test swarm",
                "topology": "hierarchical",
                "max_agents": 10,
                "min_agents": 1,
                "auto_scale": False,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-swarm"
        assert data["topology"] == "hierarchical"
        assert "id" in data

    def test_list_swarms(self):
        client.post("/api/v1/swarms", json={"name": "swarm-1"})
        client.post("/api/v1/swarms", json={"name": "swarm-2"})
        response = client.get("/api/v1/swarms")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_swarm(self):
        create_resp = client.post("/api/v1/swarms", json={"name": "get-test"})
        swarm_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/swarms/{swarm_id}")
        assert response.status_code == 200
        assert response.json()["id"] == swarm_id

    def test_get_swarm_not_found(self):
        response = client.get("/api/v1/swarms/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_update_swarm(self):
        create_resp = client.post("/api/v1/swarms", json={"name": "update-test"})
        swarm_id = create_resp.json()["id"]
        response = client.patch(f"/api/v1/swarms/{swarm_id}", json={"name": "updated-name"})
        assert response.status_code == 200
        assert response.json()["name"] == "updated-name"

    def test_delete_swarm(self):
        create_resp = client.post("/api/v1/swarms", json={"name": "delete-test"})
        swarm_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/swarms/{swarm_id}")
        assert response.status_code == 204
        get_resp = client.get(f"/api/v1/swarms/{swarm_id}")
        assert get_resp.status_code == 404

    def test_swarm_stats(self):
        create_resp = client.post("/api/v1/swarms", json={"name": "stats-test", "max_agents": 5})
        swarm_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/swarms/{swarm_id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["swarm_id"] == swarm_id
        assert data["max_agents"] == 5
        assert "agents" in data
        assert "tasks" in data
        assert "memories" in data


class TestAgentEndpoints:
    def test_spawn_agent(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "agent-swarm", "max_agents": 5})
        swarm_id = swarm_resp.json()["id"]
        response = client.post(
            f"/api/v1/swarms/{swarm_id}/agents",
            json={"name": "agent-1", "role": "developer"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "agent-1"
        assert data["role"] == "developer"
        assert data["status"] == "spawning"

    def test_list_agents(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "list-agent-swarm", "max_agents": 10})
        swarm_id = swarm_resp.json()["id"]
        client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "a1", "role": "developer"})
        client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "a2", "role": "researcher"})
        response = client.get(f"/api/v1/swarms/{swarm_id}/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_get_agent(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "get-agent-swarm", "max_agents": 5})
        swarm_id = swarm_resp.json()["id"]
        agent_resp = client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "get-agent"})
        agent_id = agent_resp.json()["id"]
        response = client.get(f"/api/v1/swarms/{swarm_id}/agents/{agent_id}")
        assert response.status_code == 200
        assert response.json()["id"] == agent_id

    def test_update_agent_status(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "status-swarm", "max_agents": 5})
        swarm_id = swarm_resp.json()["id"]
        agent_resp = client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "status-agent"})
        agent_id = agent_resp.json()["id"]
        response = client.patch(
            f"/api/v1/swarms/{swarm_id}/agents/{agent_id}/status",
            json={"status": "active"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_terminate_agent(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "term-swarm", "max_agents": 5})
        swarm_id = swarm_resp.json()["id"]
        agent_resp = client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "term-agent"})
        agent_id = agent_resp.json()["id"]
        response = client.post(f"/api/v1/swarms/{swarm_id}/agents/{agent_id}/terminate")
        assert response.status_code == 204
        get_resp = client.get(f"/api/v1/swarms/{swarm_id}/agents/{agent_id}")
        assert get_resp.json()["status"] == "terminated"

    def test_max_agents_limit(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "limit-swarm", "max_agents": 2})
        swarm_id = swarm_resp.json()["id"]
        client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "a1"})
        client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "a2"})
        response = client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "a3"})
        assert response.status_code == 400


class TestTaskEndpoints:
    def test_create_task(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "task-swarm"})
        swarm_id = swarm_resp.json()["id"]
        response = client.post(
            f"/api/v1/swarms/{swarm_id}/tasks",
            json={"name": "task-1", "description": "Test task", "priority": 5},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "task-1"
        assert data["status"] == "pending"
        assert data["priority"] == 5

    def test_list_tasks(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "list-task-swarm"})
        swarm_id = swarm_resp.json()["id"]
        client.post(f"/api/v1/swarms/{swarm_id}/tasks", json={"name": "t1"})
        client.post(f"/api/v1/swarms/{swarm_id}/tasks", json={"name": "t2"})
        response = client.get(f"/api/v1/swarms/{swarm_id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_task_lifecycle(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "lifecycle-swarm", "max_agents": 5})
        swarm_id = swarm_resp.json()["id"]
        agent_resp = client.post(f"/api/v1/swarms/{swarm_id}/agents", json={"name": "worker"})
        agent_id = agent_resp.json()["id"]
        task_resp = client.post(f"/api/v1/swarms/{swarm_id}/tasks", json={"name": "lifecycle-task"})
        task_id = task_resp.json()["id"]

        claim = client.post(f"/api/v1/swarms/{swarm_id}/tasks/{task_id}/claim", json={"agent_id": agent_id})
        assert claim.status_code == 200
        assert claim.json()["status"] == "claimed"

        start = client.post(f"/api/v1/swarms/{swarm_id}/tasks/{task_id}/start")
        assert start.status_code == 200
        assert start.json()["status"] == "running"

        complete = client.post(
            f"/api/v1/swarms/{swarm_id}/tasks/{task_id}/complete",
            json={"result": "done"},
        )
        assert complete.status_code == 200
        assert complete.json()["status"] == "completed"
        assert complete.json()["result"]["result"] == "done"


class TestMemoryEndpoints:
    def test_store_memory(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "memory-swarm"})
        swarm_id = swarm_resp.json()["id"]
        response = client.post(
            f"/api/v1/swarms/{swarm_id}/memories",
            json={"content": "Test memory", "memory_type": "general", "importance": 1.0},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test memory"
        assert data["memory_type"] == "general"

    def test_list_memories(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "list-mem-swarm"})
        swarm_id = swarm_resp.json()["id"]
        client.post(f"/api/v1/swarms/{swarm_id}/memories", json={"content": "mem1"})
        client.post(f"/api/v1/swarms/{swarm_id}/memories", json={"content": "mem2"})
        response = client.get(f"/api/v1/swarms/{swarm_id}/memories")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_semantic_search(self):
        swarm_resp = client.post("/api/v1/swarms", json={"name": "search-swarm"})
        swarm_id = swarm_resp.json()["id"]
        client.post(
            f"/api/v1/swarms/{swarm_id}/memories",
            json={"content": "The cat sat on the mat", "embedding": [0.1, 0.2, 0.3]},
        )
        client.post(
            f"/api/v1/swarms/{swarm_id}/memories",
            json={"content": "The dog ran in the park", "embedding": [0.9, 0.8, 0.7]},
        )
        response = client.post(
            f"/api/v1/swarms/{swarm_id}/memories/search",
            json={"query_embedding": [0.15, 0.25, 0.35], "limit": 1, "min_similarity": 0.5},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "cat" in data[0]["content"]