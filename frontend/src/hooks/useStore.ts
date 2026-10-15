import { create } from 'zustand';
import type { SwarmResponse, AgentResponse, TaskResponse } from '@/types/api';

interface SwarmState {
  selectedSwarm: SwarmResponse | null;
  setSelectedSwarm: (swarm: SwarmResponse | null) => void;
}

interface AgentState {
  selectedAgent: AgentResponse | null;
  setSelectedAgent: (agent: AgentResponse | null) => void;
}

interface TaskState {
  selectedTask: TaskResponse | null;
  setSelectedTask: (task: TaskResponse | null) => void;
}

export const useSwarmStore = create<SwarmState>((set) => ({
  selectedSwarm: null,
  setSelectedSwarm: (swarm) => set({ selectedSwarm: swarm }),
}));

export const useAgentStore = create<AgentState>((set) => ({
  selectedAgent: null,
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
}));

export const useTaskStore = create<TaskState>((set) => ({
  selectedTask: null,
  setSelectedTask: (task) => set({ selectedTask: task }),
}));