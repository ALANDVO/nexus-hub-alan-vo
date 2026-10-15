import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';
import type {
  SwarmResponse, SwarmCreate, SwarmUpdate, SwarmStats,
  AgentResponse, AgentCreate, AgentStatusUpdate,
  TaskResponse, TaskCreate,
  MemoryResponse, MemoryCreate, MemorySearchRequest,
  PaginatedResponse,
  SwarmTopology, AgentRole, AgentStatus, TaskStatus,
} from '@/types/api';

// Swarms
export function useSwarms(params?: {
  skip?: number; limit?: number; topology?: SwarmTopology; include_deleted?: boolean;
}) {
  return useQuery({
    queryKey: ['swarms', params],
    queryFn: () => api.listSwarms(params),
  });
}

export function useSwarm(id: string) {
  return useQuery({
    queryKey: ['swarms', id],
    queryFn: () => api.getSwarm(id),
    enabled: !!id,
  });
}

export function useSwarmStats(id: string) {
  return useQuery({
    queryKey: ['swarms', id, 'stats'],
    queryFn: () => api.getSwarmStats(id),
    enabled: !!id,
  });
}

export function useCreateSwarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: SwarmCreate) => api.createSwarm(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['swarms'] }),
  });
}

export function useUpdateSwarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: SwarmUpdate }) => api.updateSwarm(id, payload),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: ['swarms'] });
      qc.invalidateQueries({ queryKey: ['swarms', id] });
    },
  });
}

export function useDeleteSwarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, hard }: { id: string; hard?: boolean }) => api.deleteSwarm(id, hard),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['swarms'] }),
  });
}

// Agents
export function useAgents(swarmId: string, params?: {
  skip?: number; limit?: number; role?: AgentRole; status?: AgentStatus;
}) {
  return useQuery({
    queryKey: ['agents', swarmId, params],
    queryFn: () => api.listAgents(swarmId, params),
    enabled: !!swarmId,
  });
}

export function useAgent(swarmId: string, agentId: string) {
  return useQuery({
    queryKey: ['agents', swarmId, agentId],
    queryFn: () => api.getAgent(swarmId, agentId),
    enabled: !!swarmId && !!agentId,
  });
}

export function useSpawnAgent(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: AgentCreate) => api.spawnAgent(swarmId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents', swarmId] }),
  });
}

export function useUpdateAgentStatus(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ agentId, payload }: { agentId: string; payload: AgentStatusUpdate }) =>
      api.updateAgentStatus(swarmId, agentId, payload),
    onSuccess: (_, { agentId }) => {
      qc.invalidateQueries({ queryKey: ['agents', swarmId] });
      qc.invalidateQueries({ queryKey: ['agents', swarmId, agentId] });
    },
  });
}

export function useTerminateAgent(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (agentId: string) => api.terminateAgent(swarmId, agentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents', swarmId] }),
  });
}

// Tasks
export function useTasks(swarmId: string, params?: {
  skip?: number; limit?: number; status?: TaskStatus; agent_id?: string;
}) {
  return useQuery({
    queryKey: ['tasks', swarmId, params],
    queryFn: () => api.listTasks(swarmId, params),
    enabled: !!swarmId,
  });
}

export function useTask(swarmId: string, taskId: string) {
  return useQuery({
    queryKey: ['tasks', swarmId, taskId],
    queryFn: () => api.getTask(swarmId, taskId),
    enabled: !!swarmId && !!taskId,
  });
}

export function useCreateTask(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: TaskCreate) => api.createTask(swarmId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', swarmId] }),
  });
}

export function useClaimTask(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, agentId }: { taskId: string; agentId: string }) =>
      api.claimTask(swarmId, taskId, agentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', swarmId] }),
  });
}

export function useStartTask(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => api.startTask(swarmId, taskId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', swarmId] }),
  });
}

export function useCompleteTask(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, result }: { taskId: string; result: Record<string, unknown> }) =>
      api.completeTask(swarmId, taskId, result),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', swarmId] }),
  });
}

export function useFailTask(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, errorMessage }: { taskId: string; errorMessage: string }) =>
      api.failTask(swarmId, taskId, errorMessage),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', swarmId] }),
  });
}

export function useCancelTask(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => api.cancelTask(swarmId, taskId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', swarmId] }),
  });
}

// Memories
export function useMemories(swarmId: string, params?: {
  skip?: number; limit?: number; memory_type?: string; agent_id?: string; task_id?: string;
}) {
  return useQuery({
    queryKey: ['memories', swarmId, params],
    queryFn: () => api.listMemories(swarmId, params),
    enabled: !!swarmId,
  });
}

export function useStoreMemory(swarmId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: MemoryCreate) => api.storeMemory(swarmId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['memories', swarmId] }),
  });
}

export function useSearchMemories(swarmId: string) {
  return useMutation({
    mutationFn: (payload: MemorySearchRequest) => api.searchMemories(swarmId, payload),
  });
}

// Health
export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.health(),
    refetchInterval: 30000,
  });
}