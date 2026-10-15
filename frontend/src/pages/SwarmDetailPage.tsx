import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSwarm, useSwarmStats, useAgents, useSpawnAgent, useUpdateAgentStatus, useTerminateAgent, useTasks, useCreateTask, useClaimTask, useStartTask, useCompleteTask, useFailTask, useCancelTask, useMemories, useStoreMemory } from '@/hooks/useApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Textarea } from '@/components/ui/Textarea';
import { Plus, Trash2, Loader2, Play, CheckCircle, XCircle, Brain, Activity, Database, Users, ChevronRight } from 'lucide-react';
import { cn, formatDate, formatRelativeTime, getStatusColor } from '@/lib/utils';
import type { AgentResponse, TaskResponse, AgentRole, AgentStatus, TaskStatus, SwarmTopology } from '@/types/api';

export function SwarmDetailPage() {
  const { swarmId } = useParams<{ swarmId: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('agents');
  const [showSpawnAgent, setShowSpawnAgent] = useState(false);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [agentForm, setAgentForm] = useState({ name: '', role: 'developer' as AgentRole });
  const [taskForm, setTaskForm] = useState({ name: '', description: '', payload: '', priority: 0 });

  const { data: swarm, isLoading: swarmLoading } = useSwarm(swarmId!);
  const { data: stats } = useSwarmStats(swarmId!);
  const { data: agentsData, refetch: refetchAgents } = useAgents(swarmId!, { limit: 100 });
  const { data: tasksData, refetch: refetchTasks } = useTasks(swarmId!, { limit: 100 });
  const { data: memoriesData } = useMemories(swarmId!, { limit: 50 });

  const spawnMutation = useSpawnAgent(swarmId!);
  const updateAgentMutation = useUpdateAgentStatus(swarmId!);
  const terminateMutation = useTerminateAgent(swarmId!);
  const createTaskMutation = useCreateTask(swarmId!);
  const claimMutation = useClaimTask(swarmId!);
  const startMutation = useStartTask(swarmId!);
  const completeMutation = useCompleteTask(swarmId!);
  const failMutation = useFailTask(swarmId!);
  const cancelMutation = useCancelTask(swarmId!);
  const storeMemoryMutation = useStoreMemory(swarmId!);

  const agents = agentsData?.items || [];
  const tasks = tasksData?.items || [];
  const memories = memoriesData?.items || [];

  if (swarmLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/4" />
          <div className="h-4 bg-muted rounded w-1/2" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[1,2,3,4].map(i => <Card key={i}><CardContent className="space-y-2"><div className="h-4 bg-muted rounded"/><div className="h-8 bg-muted rounded w-1/2"/></CardContent></Card>)}
        </div>
      </div>
    );
  }

  if (!swarm) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold">Swarm not found</h2>
        <Button onClick={() => navigate('/swarms')} variant="outline" className="mt-4">Back to Swarms</Button>
      </div>
    );
  }

  const handleSpawnAgent = (e: React.FormEvent) => {
    e.preventDefault();
    spawnMutation.mutate(agentForm, {
      onSuccess: () => {
        setShowSpawnAgent(false);
        setAgentForm({ name: '', role: 'developer' });
        refetchAgents();
      },
    });
  };

  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault();
    let parsedPayload: Record<string, unknown> = {};
    try {
      parsedPayload = taskForm.payload ? JSON.parse(taskForm.payload) : {};
    } catch {
      alert('Invalid JSON in payload');
      return;
    }
    createTaskMutation.mutate({
      name: taskForm.name,
      description: taskForm.description,
      payload: parsedPayload,
      priority: taskForm.priority,
    }, {
      onSuccess: () => {
        setShowCreateTask(false);
        setTaskForm({ name: '', description: '', payload: '', priority: 0 });
        refetchTasks();
      },
    });
  };

  const handleAgentAction = (agentId: string, status: AgentStatus) => {
    updateAgentMutation.mutate({ agentId, payload: { status } }, { onSuccess: () => refetchAgents() });
  };

  const handleTerminateAgent = (agentId: string) => {
    if (confirm('Terminate this agent?')) {
      terminateMutation.mutate(agentId, { onSuccess: () => refetchAgents() });
    }
  };

  const handleTaskAction = (taskId: string, action: 'claim' | 'start' | 'complete' | 'fail' | 'cancel', agentId?: string) => {
    switch (action) {
      case 'claim':
        if (agentId) claimMutation.mutate({ taskId, agentId }, { onSuccess: () => refetchTasks() });
        break;
      case 'start':
        startMutation.mutate(taskId, { onSuccess: () => refetchTasks() });
        break;
      case 'complete':
        completeMutation.mutate({ taskId, result: { completed: true, timestamp: new Date().toISOString() } }, { onSuccess: () => refetchTasks() });
        break;
      case 'fail':
        failMutation.mutate({ taskId, errorMessage: 'Manual failure' }, { onSuccess: () => refetchTasks() });
        break;
      case 'cancel':
        cancelMutation.mutate(taskId, { onSuccess: () => refetchTasks() });
        break;
    }
  };

  const roleOptions = [
    { value: 'orchestrator', label: 'Orchestrator' },
    { value: 'analyst', label: 'Analyst' },
    { value: 'developer', label: 'Developer' },
    { value: 'researcher', label: 'Researcher' },
    { value: 'validator', label: 'Validator' },
    { value: 'specialist', label: 'Specialist' },
    { value: 'optimizer', label: 'Optimizer' },
    { value: 'tester', label: 'Tester' },
    { value: 'documenter', label: 'Documenter' },
    { value: 'monitor', label: 'Monitor' },
    { value: 'reviewer', label: 'Reviewer' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{swarm.name}</h1>
            <Badge variant={getStatusColor(swarm.topology) as any}>{swarm.topology}</Badge>
          </div>
          <p className="text-muted-foreground mt-1">{swarm.description || 'No description'}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/swarms')}>Back</Button>
          <Button onClick={() => setShowSpawnAgent(true)}><Plus className="mr-2 h-4 w-4" />Spawn Agent</Button>
          <Button onClick={() => setShowCreateTask(true)} variant="secondary"><Plus className="mr-2 h-4 w-4" />New Task</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4">
            <Users className="h-10 w-10 text-primary" />
            <div>
              <p className="text-2xl font-bold">{stats?.agents?.active || 0}</p>
              <p className="text-sm text-muted-foreground">Active Agents</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4">
            <Activity className="h-10 w-10 text-blue-500" />
            <div>
              <p className="text-2xl font-bold">{stats?.tasks?.running || 0}</p>
              <p className="text-sm text-muted-foreground">Running Tasks</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4">
            <CheckCircle className="h-10 w-10 text-green-500" />
            <div>
              <p className="text-2xl font-bold">{stats?.tasks?.completed || 0}</p>
              <p className="text-sm text-muted-foreground">Completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4">
            <Database className="h-10 w-10 text-purple-500" />
            <div>
              <p className="text-2xl font-bold">{stats?.memories || 0}</p>
              <p className="text-sm text-muted-foreground">Memories</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {showSpawnAgent && (
        <Card className="border-primary mb-6">
          <CardHeader><CardTitle>Spawn New Agent</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleSpawnAgent} className="space-y-4 max-w-md">
              <Input label="Name" value={agentForm.name} onChange={e => setAgentForm({...agentForm, name: e.target.value})} required placeholder="agent-1" />
              <Select label="Role" value={agentForm.role} onChange={e => setAgentForm({...agentForm, role: e.target.value as AgentRole})} options={roleOptions} />
              <div className="flex gap-2">
                <Button type="submit" disabled={spawnMutation.isPending}>{spawnMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}Spawn Agent</Button>
                <Button type="button" variant="outline" onClick={() => setShowSpawnAgent(false)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {showCreateTask && (
        <Card className="border-primary mb-6">
          <CardHeader><CardTitle>Create New Task</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleCreateTask} className="space-y-4 max-w-2xl">
              <Input label="Name" value={taskForm.name} onChange={e => setTaskForm({...taskForm, name: e.target.value})} required placeholder="process-data" />
              <Textarea label="Description" value={taskForm.description} onChange={e => setTaskForm({...taskForm, description: e.target.value})} placeholder="Optional description" rows={2} />
              <Textarea label="Payload (JSON)" value={taskForm.payload} onChange={e => setTaskForm({...taskForm, payload: e.target.value})} placeholder='{"key": "value"}' rows={3} />
              <Input label="Priority" type="number" value={taskForm.priority} onChange={e => setTaskForm({...taskForm, priority: parseInt(e.target.value) || 0})} />
              <div className="flex gap-2">
                <Button type="submit" disabled={createTaskMutation.isPending}>{createTaskMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}Create Task</Button>
                <Button type="button" variant="outline" onClick={() => setShowCreateTask(false)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="agents"><Users className="mr-2 h-4 w-4" />Agents ({agents.length})</TabsTrigger>
          <TabsTrigger value="tasks"><Activity className="mr-2 h-4 w-4" />Tasks ({tasks.length})</TabsTrigger>
          <TabsTrigger value="memory"><Database className="mr-2 h-4 w-4" />Memory ({memories.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="agents">
          <AgentList
            agents={agents}
            onAction={handleAgentAction}
            onTerminate={handleTerminateAgent}
            onClaimTask={handleTaskAction}
            tasks={tasks.filter(t => t.status === 'pending')}
          />
        </TabsContent>

        <TabsContent value="tasks">
          <TaskList
            tasks={tasks}
            onAction={handleTaskAction}
            agents={agents.filter(a => a.status === 'active' || a.status === 'idle')}
          />
        </TabsContent>

        <TabsContent value="memory">
          <MemoryList memories={memories} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function AgentList({ agents, onAction, onTerminate, onClaimTask, tasks }: {
  agents: AgentResponse[];
  onAction: (agentId: string, status: AgentStatus) => void;
  onTerminate: (agentId: string) => void;
  onClaimTask: (taskId: string, action: 'claim', agentId: string) => void;
  tasks: TaskResponse[];
}) {
  if (agents.length === 0) {
    return (
      <Card><CardContent className="py-12 text-center">
        <Brain className="mx-auto h-12 w-12 text-muted-foreground/50" />
        <h3 className="mt-4 text-lg font-medium">No agents yet</h3>
        <p className="mt-2 text-muted-foreground">Spawn agents to start processing tasks</p>
      </CardContent></Card>
    );
  }

  return (
    <div className="space-y-3">
      {agents.map(agent => (
        <Card key={agent.id}>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn('h-3 w-3 rounded-full', getStatusColor(agent.status) === 'success' && 'bg-green-500', getStatusColor(agent.status) === 'warning' && 'bg-yellow-500', getStatusColor(agent.status) === 'info' && 'bg-blue-500', getStatusColor(agent.status) === 'destructive' && 'bg-red-500', getStatusColor(agent.status) === 'default' && 'bg-gray-500')} />
                <div>
                  <h4 className="font-medium">{agent.name}</h4>
                  <p className="text-sm text-muted-foreground">{agent.role}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={getStatusColor(agent.status) as any}>{agent.status}</Badge>
                {agent.current_task_id && (
                  <Badge variant="info">Task: {agent.current_task_id.slice(0,8)}</Badge>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {agent.status === 'idle' && <Button size="sm" onClick={() => onAction(agent.id, 'active')}>Activate</Button>}
              {agent.status === 'active' && <Button size="sm" variant="secondary" onClick={() => onAction(agent.id, 'idle')}>Idle</Button>}
              {agent.status === 'busy' && <Button size="sm" variant="secondary" onClick={() => onAction(agent.id, 'idle')}>Release</Button>}
              {(agent.status === 'active' || agent.status === 'idle' || agent.status === 'busy') && tasks.length > 0 && (
                <Select
                  placeholder="Assign task..."
                  value=""
                  onChange={e => e.target.value && onClaimTask(e.target.value, 'claim', agent.id)}
                  options={tasks.map(t => ({ value: t.id, label: `${t.name} (${t.id.slice(0,8)})` }))}
                />
              )}
              <Button size="sm" variant="destructive" onClick={() => onTerminate(agent.id)}>Terminate</Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function TaskList({ tasks, onAction, agents }: { tasks: TaskResponse[]; onAction: (taskId: string, action: 'claim' | 'start' | 'complete' | 'fail' | 'cancel', agentId?: string) => void; agents: AgentResponse[] }) {
  if (tasks.length === 0) {
    return (
      <Card><CardContent className="py-12 text-center">
        <Activity className="mx-auto h-12 w-12 text-muted-foreground/50" />
        <h3 className="mt-4 text-lg font-medium">No tasks yet</h3>
        <p className="mt-2 text-muted-foreground">Create tasks for agents to process</p>
      </CardContent></Card>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map(task => (
        <Card key={task.id}>
          <CardContent className="space-y-3">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">{task.name}</h4>
                  <Badge variant={getStatusColor(task.status) as any}>{task.status}</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">{task.description || 'No description'}</p>
                {task.payload && Object.keys(task.payload).length > 0 && (
                  <pre className="mt-2 text-xs bg-muted p-2 rounded overflow-auto max-h-32">{JSON.stringify(task.payload, null, 2)}</pre>
                )}
              </div>
              <div className="flex flex-col gap-1 ml-4">
                {task.status === 'pending' && agents.length > 0 && (
                  <Select
                    placeholder="Assign to agent..."
                    value=""
                    onChange={e => e.target.value && onAction(task.id, 'claim', e.target.value)}
                    options={agents.map(a => ({ value: a.id, label: `${a.name} (${a.role})` }))}
                  />
                )}
                {task.status === 'claimed' && <Button size="sm" onClick={() => onAction(task.id, 'start')}>Start</Button>}
                {task.status === 'running' && (
                  <>
                    <Button size="sm" onClick={() => onAction(task.id, 'complete')}>Complete</Button>
                    <Button size="sm" variant="destructive" onClick={() => onAction(task.id, 'fail')}>Fail</Button>
                  </>
                )}
                {(task.status === 'pending' || task.status === 'claimed' || task.status === 'running') && (
                  <Button size="sm" variant="outline" onClick={() => onAction(task.id, 'cancel')}>Cancel</Button>
                )}
                {task.agent_id && (
                  <span className="text-xs text-muted-foreground">Agent: {task.agent_id.slice(0,8)}</span>
                )}
              </div>
            </div>
            {task.result && (
              <div className="pt-2 border-t">
                <p className="text-xs text-muted-foreground">Result:</p>
                <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-32">{JSON.stringify(task.result, null, 2)}</pre>
              </div>
            )}
            {task.error_message && (
              <div className="pt-2 border-t text-destructive text-sm">Error: {task.error_message}</div>
            )}
            <div className="flex items-center justify-between text-xs text-muted-foreground pt-2">
              <span>Created {formatRelativeTime(task.created_at)}</span>
              {task.started_at && <span>Started {formatRelativeTime(task.started_at)}</span>}
              {task.completed_at && <span>Completed {formatRelativeTime(task.completed_at)}</span>}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function MemoryList({ memories }: { memories: MemoryResponse[] }) {
  if (memories.length === 0) {
    return (
      <Card><CardContent className="py-12 text-center">
        <Database className="mx-auto h-12 w-12 text-muted-foreground/50" />
        <h3 className="mt-4 text-lg font-medium">No memories yet</h3>
        <p className="mt-2 text-muted-foreground">Memories are stored automatically from task outputs and agent activities</p>
      </CardContent></Card>
    );
  }

  return (
    <div className="space-y-3">
      {memories.map(memory => (
        <Card key={memory.id}>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <Badge variant="outline">{memory.memory_type}</Badge>
              <span className="text-xs text-muted-foreground">Importance: {memory.importance}</span>
            </div>
            <p className="text-sm">{memory.content.slice(0, 200)}{memory.content.length > 200 ? '...' : ''}</p>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              {memory.agent_id && <span>Agent: {memory.agent_id.slice(0,8)}</span>}
              {memory.task_id && <span>Task: {memory.task_id.slice(0,8)}</span>}
              <span>{formatDate(memory.created_at)}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}