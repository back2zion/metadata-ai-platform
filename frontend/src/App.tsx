import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import koKR from 'antd/locale/ko_KR';
import MainLayout from './components/Layout/MainLayout.tsx';
import Dashboard from './pages/Dashboard.tsx';
import DataMart from './pages/DataMart.tsx';
import BI from './pages/BI.tsx';
import OLAP from './pages/OLAP.tsx';
import ETL from './pages/ETL.tsx';
import AIEnvironment from './pages/AIEnvironment.tsx';
import CDWResearch from './pages/CDWResearch.tsx';

import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={koKR}
        theme={{
          token: {
            colorPrimary: '#1a5d3a', // Asan Hospital Green
            colorSuccess: '#52c41a',
            colorWarning: '#ff6600', // Asan Hospital Orange
            colorError: '#ff4d4f',
            colorInfo: '#1890ff',
            borderRadius: 8,
          },
        }}
      >
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<MainLayout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="datamart" element={<DataMart />} />
                <Route path="bi" element={<BI />} />
                <Route path="olap" element={<OLAP />} />
                <Route path="etl" element={<ETL />} />
                <Route path="ai-environment" element={<AIEnvironment />} />
                <Route path="cdw" element={<CDWResearch />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;