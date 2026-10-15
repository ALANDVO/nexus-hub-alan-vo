import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { SwarmsPage } from '@/pages/SwarmsPage';
import { SwarmDetailPage } from '@/pages/SwarmDetailPage';
import { HealthPage } from '@/pages/HealthPage';

export function App() {
  return (
    <Routes>
      <Route path="/health" element={<HealthPage />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/swarms" replace />} />
        <Route path="/swarms" element={<SwarmsPage />} />
        <Route path="/swarms/:swarmId" element={<SwarmDetailPage />} />
      </Route>
    </Routes>
  );
}