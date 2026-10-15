import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { SwarmDetailPage } from '@/pages/SwarmDetailPage'
import { api } from '@/api/client'

vi.mock('@/api/client', () => ({
  api: {
    health: vi.fn(),
    getSwarm: vi.fn(),
    getSwarmStats: vi.fn(),
    listAgents: vi.fn(),
    listTasks: vi.fn(),
    listMemories: vi.fn(),
    spawnAgent: vi.fn(),
    createTask: vi.fn(),
    claimTask: vi.fn(),
    startTask: vi.fn(),
    completeTask: vi.fn(),
    failTask: vi.fn(),
    cancelTask: vi.fn(),
    updateAgentStatus: vi.fn(),
    terminateAgent: vi.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/swarms/:swarmId" element={<SwarmDetailPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('SwarmDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders swarm details', async () => {
    api.getSwarm.mockResolvedValue({
      id: 'swarm-1',
      name: 'Test Swarm',
      description: 'A test swarm',
      topology: 'hierarchical',
      max_agents: 10,
      min_agents: 1,
      auto_scale: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
    api.getSwarmStats.mockResolvedValue({
      swarm_id: 'swarm-1',
      name: 'Test Swarm',
      topology: 'hierarchical',
      max_agents: 10,
      min_agents: 1,
      auto_scale: false,
      agents: { active: 2, idle: 1 },
      tasks: { running: 1, completed: 5 },
      memories: 10,
      created_at: new Date().toISOString(),
    })
    api.listAgents.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 100 })
    api.listTasks.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 100 })
    api.listMemories.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 50 })

    render(<SwarmDetailPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Test Swarm')).toBeInTheDocument()
      expect(screen.getByText('A test swarm')).toBeInTheDocument()
    })
  })

  it('shows agent count in stats', async () => {
    api.getSwarm.mockResolvedValue({ id: 's1', name: 'S', topology: 'hierarchical', max_agents: 5, min_agents: 1, auto_scale: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() })
    api.getSwarmStats.mockResolvedValue({ swarm_id: 's1', name: 'S', topology: 'hierarchical', max_agents: 5, min_agents: 1, auto_scale: false, agents: { active: 3 }, tasks: {}, memories: 0, created_at: new Date().toISOString() })
    api.listAgents.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 100 })
    api.listTasks.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 100 })
    api.listMemories.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 50 })

    render(<SwarmDetailPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })
})