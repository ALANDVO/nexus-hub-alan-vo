import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  SwarmCreate, SwarmUpdate, SwarmResponse, SwarmStats,
  AgentCreate, AgentResponse, AgentStatusUpdate,
  TaskCreate, TaskResponse,
  MemoryCreate, MemoryResponse, MemorySearchRequest,
  PaginatedResponse,
  SwarmTopology, AgentRole, AgentStatus, TaskStatus,
} from '@/types/api';

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = error.response?.data?.detail || error.message;
        return Promise.reject(new Error(message));
      }
    );
  }

  // Health
  async health(): Promise<{ status: string; service: string; version: string }> {
    const { data } = await this.client.get('/healthz');
    return data;
  }

  async ready(): Promise<{ status: string; database: string }> {
    const { data } = await this.client.get('/healthz/ready');
    return data;
  }

  // Swarms
  async listSwarms(params?: {
    skip?: number; limit?: number; topology?: SwarmTopology; include_deleted?: boolean;
  }): Promise<PaginatedResponse<SwarmResponse>> {
    const { data } = await this.client.get('/swarms', { params });
    return data;
  }

  async getSwarm(id: string): Promise<SwarmResponse> {
    const { data } = await this.client.get(`/swarms/${id}`);
    return data;
  }

  async createSwarm(payload: SwarmCreate): Promise<SwarmResponse> {
    const { data } = await this.client.post('/swarms', payload);
    return data;
  }

  async updateSwarm(id: string, payload: SwarmUpdate): Promise<SwarmResponse> {
    const { data } = await this.client.patch(`/swarms/${id}`, payload);
    return data;
  }

  async deleteSwarm(id: string, hard = false): Promise<void> {
    await this.client.delete(`/swarms/${id}`, { params: { hard } });
  }

  async getSwarmStats(id: string): Promise<SwarmStats> {
    const { data } = await this.client.get(`/swarms/${id}/stats`);
    return data;
  }

  // Agents
  async listAgents(swarmId: string, params?: {
    skip?: number; limit?: number; role?: AgentRole; status?: AgentStatus;
  }): Promise<PaginatedResponse<AgentResponse>> {
    const { data } = await this.client.get(`/swarms/${swarmId}/agents`, { params });
    return data;
  }

  async getAgent(swarmId: string, agentId: string): Promise<AgentResponse> {
    const { data } = await this.client.get(`/swarms/${swarmId}/agents/${agentId}`);
    return data;
  }

  async spawnAgent(swarmId: string, payload: AgentCreate): Promise<AgentResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/agents`, payload);
    return data;
  }

  async updateAgentStatus(swarmId: string, agentId: string, payload: AgentStatusUpdate): Promise<AgentResponse> {
    const { data } = await this.client.patch(`/swarms/${swarmId}/agents/${agentId}/status`, payload);
    return data;
  }

  async terminateAgent(swarmId: string, agentId: string): Promise<void> {
    await this.client.post(`/swarms/${swarmId}/agents/${agentId}/terminate`);
  }

  // Tasks
  async listTasks(swarmId: string, params?: {
    skip?: number; limit?: number; status?: TaskStatus; agent_id?: string;
  }): Promise<PaginatedResponse<TaskResponse>> {
    const { data } = await this.client.get(`/swarms/${swarmId}/tasks`, { params });
    return data;
  }

  async getTask(swarmId: string, taskId: string): Promise<TaskResponse> {
    const { data } = await this.client.get(`/swarms/${swarmId}/tasks/${taskId}`);
    return data;
  }

  async createTask(swarmId: string, payload: TaskCreate): Promise<TaskResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/tasks`, payload);
    return data;
  }

  async claimTask(swarmId: string, taskId: string, agentId: string): Promise<TaskResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/tasks/${taskId}/claim`, { agent_id: agentId });
    return data;
  }

  async startTask(swarmId: string, taskId: string): Promise<TaskResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/tasks/${taskId}/start`);
    return data;
  }

  async completeTask(swarmId: string, taskId: string, result: Record<string, unknown>): Promise<TaskResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/tasks/${taskId}/complete`, result);
    return data;
  }

  async failTask(swarmId: string, taskId: string, errorMessage: string): Promise<TaskResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/tasks/${taskId}/fail`, { error_message: errorMessage });
    return data;
  }

  async cancelTask(swarmId: string, taskId: string): Promise<TaskResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/tasks/${taskId}/cancel`);
    return data;
  }

  // Memories
  async listMemories(swarmId: string, params?: {
    skip?: number; limit?: number; memory_type?: string; agent_id?: string; task_id?: string;
  }): Promise<PaginatedResponse<MemoryResponse>> {
    const { data } = await this.client.get(`/swarms/${swarmId}/memories`, { params });
    return data;
  }

  async getMemory(swarmId: string, memoryId: string): Promise<MemoryResponse> {
    const { data } = await this.client.get(`/swarms/${swarmId}/memories/${memoryId}`);
    return data;
  }

  async storeMemory(swarmId: string, payload: MemoryCreate): Promise<MemoryResponse> {
    const { data } = await this.client.post(`/swarms/${swarmId}/memories`, payload);
    return data;
  }

  async searchMemories(swarmId: string, payload: MemorySearchRequest): Promise<MemoryResponse[]> {
    const { data } = await this.client.post(`/swarms/${swarmId}/memories/search`, payload);
    return data;
  }
}

export const api = new ApiClient();