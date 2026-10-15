import { useHealth } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Server, Database, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function HealthPage() {
  const { data: health, isLoading, error, refetch } = useHealth();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">System Health</h1>
        <p className="text-muted-foreground">Monitor API and database connectivity</p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>API Status</CardTitle>
          <Badge variant={health?.status === 'ok' ? 'success' : 'destructive'}>
            {health?.status || 'Unknown'}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg">
              <Server className={cn('h-6 w-6', health?.status === 'ok' ? 'text-green-500' : 'text-red-500')} />
              <div>
                <p className="font-medium">Service</p>
                <p className="text-sm text-muted-foreground">{health?.service || 'nexus-hub'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg">
              <CheckCircle className={cn('h-6 w-6', health?.status === 'ok' ? 'text-green-500' : 'text-red-500')} />
              <div>
                <p className="font-medium">Version</p>
                <p className="text-sm text-muted-foreground">{health?.version || '1.0.0'}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Database Connection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            {isLoading ? (
              <>
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                <span>Checking...</span>
              </>
            ) : error ? (
              <>
                <AlertCircle className="h-6 w-6 text-red-500" />
                <span className="text-red-500">Failed to check readiness</span>
              </>
            ) : (
              <>
                <Database className="h-6 w-6 text-green-500" />
                <span className="text-green-500">Connected</span>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}