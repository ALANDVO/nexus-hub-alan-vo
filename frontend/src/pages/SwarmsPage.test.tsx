import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { SwarmsPage } from '@/pages/SwarmsPage'
import { api } from '@/api/client'

vi.mock('@/api/client', () => ({
  api: {
    health: vi.fn(),
    listSwarms: vi.fn(),
    createSwarm: vi.fn(),
    deleteSwarm: vi.fn(),
    getSwarm: vi.fn(),
    getSwarmStats: vi.fn(),
    listAgents: vi.fn(),
    spawnAgent: vi.fn(),
    updateAgentStatus: vi.fn(),
    terminateAgent: vi.fn(),
    listTasks: vi.fn(),
    createTask: vi.fn(),
    claimTask: vi.fn(),
    startTask: vi.fn(),
    completeTask: vi.fn(),
    failTask: vi.fn(),
    cancelTask: vi.fn(),
    listMemories: vi.fn(),
    storeMemory: vi.fn(),
    searchMemories: vi.fn(),
  },
}))

function TestWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/swarms']}>
        <Routes>
          <Route path="/swarms" element={<SwarmsPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('SwarmsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders swarms list', async () => {
    api.listSwarms.mockResolvedValue({
      items: [
        { id: 'swarm-1', name: 'swarm-1', description: 'First swarm', topology: 'hierarchical', max_agents: 10, min_agents: 1, auto_scale: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        { id: 'swarm-2', name: 'swarm-2', description: 'Second swarm', topology: 'mesh', max_agents: 5, min_agents: 1, auto_scale: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ],
      total: 2,
      skip: 0,
      limit: 50,
    })
    render(<TestWrapper />)

    await waitFor(() => {
      expect(screen.getByText('swarm-1')).toBeInTheDocument()
      expect(screen.getByText('swarm-2')).toBeInTheDocument()
    })
  })

  it('shows empty state when no swarms', async () => {
    api.listSwarms.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 50 })
    render(<TestWrapper />)

    await waitFor(() => {
      expect(screen.getByText('No swarms yet')).toBeInTheDocument()
    })
  })

  it('creates a new swarm', async () => {
    api.listSwarms.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 50 })
    api.createSwarm.mockResolvedValue({ id: 'new-swarm', name: 'New Swarm', topology: 'hierarchical', max_agents: 10, min_agents: 1, auto_scale: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() })

    render(<TestWrapper />)

    const createButton = screen.getByText('New Swarm')
    fireEvent.click(createButton)

    await waitFor(() => {
      expect(screen.getByText('Create New Swarm')).toBeInTheDocument()
    })

    const nameInput = screen.getByLabelText('Name')
    fireEvent.change(nameInput, { target: { value: 'New Swarm' } })

    const submitButton = screen.getByText('Create Swarm')
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(api.createSwarm).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'New Swarm' })
      )
    })
  })
})
