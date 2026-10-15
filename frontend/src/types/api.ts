export type SwarmTopology = 'hierarchical' | 'mesh' | 'ring' | 'star';
export type AgentRole = 'orchestrator' | 'analyst' | 'developer' | 'researcher' | 'validator' | 'specialist' | 'optimizer' | 'tester' | 'documenter' | 'monitor' | 'reviewer';
export type AgentStatus = 'spawning' | 'active' | 'idle' | 'busy' | 'terminating' | 'terminated' | 'error';
export type TaskStatus = 'pending' | 'queued' | 'claimed' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface SwarmBase {
  name: string;
  description?: string;
  topology: SwarmTopology;
  max_agents: number;
  min_agents: number;
  auto_scale: boolean;
  scale_up_threshold: number;
  scale_down_threshold: number;
  config?: Record<string, unknown>;
}

export interface SwarmCreate extends SwarmBase {}
export interface SwarmUpdate extends Partial<SwarmBase> {}

export interface SwarmResponse extends SwarmBase {
  id: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface SwarmStats {
  swarm_id: string;
  name: string;
  topology: string;
  max_agents: number;
  min_agents: number;
  auto_scale: boolean;
  agents: Record<string, number>;
  tasks: Record<string, number>;
  memories: number;
  created_at: string;
}

export interface AgentBase {
  name: string;
  role: AgentRole;
  config?: Record<string, unknown>;
}

export interface AgentCreate extends AgentBase {}
export interface AgentResponse extends AgentBase {
  id: string;
  swarm_id: string;
  status: AgentStatus;
  current_task_id?: string;
  spawn_order: number;
  last_heartbeat?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
  terminated_at?: string;
}

export interface AgentStatusUpdate {
  status: AgentStatus;
  error_message?: string;
}

export interface TaskBase {
  name: string;
  description?: string;
  payload?: Record<string, unknown>;
  priority: number;
}

export interface TaskCreate extends TaskBase {}
export interface TaskResponse extends TaskBase {
  id: string;
  swarm_id: string;
  agent_id?: string;
  status: TaskStatus;
  result?: Record<string, unknown>;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface MemoryBase {
  content: string;
  embedding?: number[];
  metadata?: Record<string, unknown>;
  memory_type: string;
  importance: number;
}

export interface MemoryCreate extends MemoryBase {
  agent_id?: string;
  task_id?: string;
}
export interface MemoryResponse extends MemoryBase {
  id: string;
  swarm_id: string;
  agent_id?: string;
  task_id?: string;
  created_at: string;
}

export interface MemorySearchRequest {
  query_embedding: number[];
  limit?: number;
  min_similarity?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}