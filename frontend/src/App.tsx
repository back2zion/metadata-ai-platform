import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import koKR from 'antd/locale/ko_KR';
import MainLayout from './components/Layout/MainLayout.tsx';
import { Dashboard } from './pages/Dashboard.tsx';
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
            colorPrimary: '#006241', // ASAN GREEN
            colorSuccess: '#52A67D', // ASAN Light Green
            colorWarning: '#FF6F00', // ASAN Orange
            colorError: '#dc3545',
            colorInfo: '#006241',
            borderRadius: 6,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            fontSize: 14,
          },
          components: {
            Layout: {
              headerBg: '#ffffff',
              siderBg: '#ffffff', 
              bodyBg: '#F5F0E8', // BEIGE
            },
            Card: {
              borderRadius: 8,
              boxShadow: '0 2px 8px rgba(0, 98, 65, 0.06)',
            },
            Button: {
              borderRadius: 6,
              primaryShadow: '0 2px 4px rgba(0, 98, 65, 0.2)',
            },
            Menu: {
              itemSelectedBg: 'rgba(0, 98, 65, 0.08)',
              itemHoverBg: 'rgba(0, 98, 65, 0.05)',
            },
          },
        }}
      >
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
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