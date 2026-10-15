import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Brain, Cpu, Database, Activity } from 'lucide-react';

export function Layout() {
  const location = useLocation();

  const navItems = [
    { path: '/swarms', label: 'Swarms', icon: Cpu },
    { path: '/swarms', label: 'Agents', icon: Brain, exact: false },
    { path: '/swarms', label: 'Tasks', icon: Activity, exact: false },
    { path: '/swarms', label: 'Memory', icon: Database, exact: false },
  ];

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold text-foreground">Nexus Hub</span>
            <span className="hidden sm:inline-block px-2 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded">
              Alan Vo | AI & Machine Learning
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  )
                }
              >
                <item.icon className="inline h-4 w-4 mr-2" />
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <HealthIndicator />
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t py-4">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          Nexus Hub &copy; 2026 Alan Vo <alanvo@gmail.com> — MIT License
        </div>
      </footer>
    </div>
  );
}

function HealthIndicator() {
  return (
    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-secondary">
      <span className="h-2 w-2 rounded-full bg-green-500" />
      <span className="text-xs font-medium text-muted-foreground">API Connected</span>
    </div>
  );
}