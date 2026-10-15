import { useState } from 'react';
import { useSwarms, useCreateSwarm, useDeleteSwarm } from '@/hooks/useApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Textarea } from '@/components/ui/Textarea';
import { Plus, Trash2, Loader2, ChevronRight } from 'lucide-react';
import { cn, formatDate, getStatusColor } from '@/lib/utils';
import type { SwarmResponse, SwarmTopology } from '@/types/api';

export function SwarmsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    topology: 'hierarchical' as SwarmTopology,
    max_agents: 10,
    min_agents: 1,
    auto_scale: false,
  });

  const { data: swarmsData, isLoading, error, refetch } = useSwarms({ limit: 50 });
  const createMutation = useCreateSwarm();
  const deleteMutation = useDeleteSwarm();

  const topologies: { value: SwarmTopology; label: string }[] = [
    { value: 'hierarchical', label: 'Hierarchical' },
    { value: 'mesh', label: 'Mesh' },
    { value: 'ring', label: 'Ring' },
    { value: 'star', label: 'Star' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData, {
      onSuccess: () => {
        setShowCreate(false);
        setFormData({ name: '', description: '', topology: 'hierarchical', max_agents: 10, min_agents: 1, auto_scale: false });
        refetch();
      },
    });
  };

  const handleDelete = (id: string) => {
    if (confirm('Delete this swarm? This action cannot be undone.')) {
      deleteMutation.mutate({ id, hard: false }, { onSuccess: () => refetch() });
    }
  };

  const swarms = swarmsData?.items || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Swarms</h1>
          <p className="text-muted-foreground">Manage multi-agent swarm deployments</p>
        </div>
        <Button onClick={() => setShowCreate(true)}><Plus className="mr-2 h-4 w-4" />New Swarm</Button>
      </div>

      {showCreate && (
        <Card className="border-primary">
          <CardHeader>
            <CardTitle>Create New Swarm</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
              <Input
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="my-swarm"
                required
              />
              <Textarea
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Optional description"
                rows={3}
              />
              <div className="grid gap-4 md:grid-cols-2">
                <Select
                  label="Topology"
                  value={formData.topology}
                  onChange={(e) => setFormData({ ...formData, topology: e.target.value as SwarmTopology })}
                  options={topologies}
                />
                <Input
                  label="Max Agents"
                  type="number"
                  value={formData.max_agents}
                  onChange={(e) => setFormData({ ...formData, max_agents: parseInt(e.target.value) || 10 })}
                  min={1}
                  max={1000}
                />
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  label="Min Agents"
                  type="number"
                  value={formData.min_agents}
                  onChange={(e) => setFormData({ ...formData, min_agents: parseInt(e.target.value) || 1 })}
                  min={1}
                  max={1000}
                />
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.auto_scale}
                    onChange={(e) => setFormData({ ...formData, auto_scale: e.target.checked })}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span className="text-sm">Auto-scale</span>
                </label>
              </div>
              <div className="flex gap-2 pt-4">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Create Swarm
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {error && (
        <div className="rounded-md bg-destructive/10 p-4 text-destructive" role="alert">
          Failed to load swarms: {error.message}
        </div>
      )}

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="space-y-4">
                <div className="h-6 bg-muted rounded w-3/4" />
                <div className="h-4 bg-muted rounded w-1/2" />
                <div className="h-4 bg-muted rounded w-1/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : swarms.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Plus className="mx-auto h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-medium">No swarms yet</h3>
            <p className="mt-2 text-muted-foreground">Create your first swarm to get started</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {swarms.map((swarm) => (
            <Card key={swarm.id} className="transition-shadow hover:shadow-md">
              <CardContent className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold truncate">{swarm.name}</h3>
                    <p className="text-sm text-muted-foreground truncate">{swarm.description || 'No description'}</p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(swarm.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Badge variant={getStatusColor(swarm.topology) as any}>{swarm.topology}</Badge>
                  <Badge variant="outline">Max: {swarm.max_agents}</Badge>
                  <Badge variant="outline">Min: {swarm.min_agents}</Badge>
                  {swarm.auto_scale && <Badge variant="info">Auto-scale</Badge>}
                </div>
                <div className="pt-2 border-t flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Created {formatDate(swarm.created_at)}</span>
                  <NavLink to={`/swarms/${swarm.id}`} className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
                    View <ChevronRight className="h-4 w-4" />
                  </NavLink>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {swarmsData && swarmsData.total > swarms.length && (
        <div className="text-center text-sm text-muted-foreground">
          Showing {swarms.length} of {swarmsData.total} swarms
        </div>
      )}
    </div>
  );
}