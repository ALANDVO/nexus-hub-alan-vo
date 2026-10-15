import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { SwarmsPage } from '@/pages/SwarmsPage'
import { api } from '@/api/client'

vi.mock('@/api/client', () => ({
  api: {
    health: vi.fn(),
    listSwarms: vi.fn(),
    createSwarm: vi.fn(),
    deleteSwarm: vi.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
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
        { id: '1', name: 'swarm-1', description: 'First', topology: 'hierarchical', max_agents: 10, min_agents: 1, auto_scale: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        { id: '2', name: 'swarm-2', description: 'Second', topology: 'mesh', max_agents: 5, min_agents: 1, auto_scale: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ],
      total: 2,
      skip: 0,
      limit: 50,
    })

    render(<SwarmsPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('swarm-1')).toBeInTheDocument()
      expect(screen.getByText('swarm-2')).toBeInTheDocument()
    })
  })

  it('shows empty state when no swarms', async () => {
    api.listSwarms.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 50 })

    render(<SwarmsPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('No swarms yet')).toBeInTheDocument()
    })
  })

  it('creates a new swarm', async () => {
    api.listSwarms.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 50 })
    api.createSwarm.mockResolvedValue({
      id: 'new-id',
      name: 'new-swarm',
      description: '',
      topology: 'hierarchical',
      max_agents: 10,
      min_agents: 1,
      auto_scale: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })

    render(<SwarmsPage />, { wrapper: createWrapper() })

    const createButton = screen.getByText('New Swarm')
    fireEvent.click(createButton)

    const nameInput = screen.getByLabelText('Name')
    fireEvent.change(nameInput, { target: { value: 'new-swarm' } })

    const submitButton = screen.getByText('Create Swarm')
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(api.createSwarm).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'new-swarm' })
      )
    })
  })
})