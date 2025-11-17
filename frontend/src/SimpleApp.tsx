import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, Layout, Menu, Typography, Card, Space, Alert } from 'antd';
import koKR from 'antd/locale/ko_KR';
import { ExperimentOutlined, HomeOutlined } from '@ant-design/icons';
import PromptEnhancement from './pages/PromptEnhancement.tsx';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const SimpleLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={280} theme="dark">
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <img 
            src="/asan-logo.png" 
            alt="아산병원 로고" 
            style={{ 
              height: '40px', 
              marginBottom: '8px',
              filter: 'brightness(0) invert(1)'
            }} 
          />
          <div style={{ color: '#999', fontSize: '12px', marginTop: '4px' }}>
            통합 데이터 플랫폼
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          onClick={handleMenuClick}
          items={[
            {
              key: '/dashboard',
              icon: <HomeOutlined />,
              label: '대시보드',
            },
            {
              key: '/text2sql',
              icon: <ExperimentOutlined />,
              label: 'Text2SQL',
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px' }}>
          <Title level={4} style={{ margin: 0, lineHeight: '64px' }}>
            {location.pathname === '/dashboard' && '대시보드'}
            {location.pathname === '/text2sql' && 'Text2SQL'}
          </Title>
        </Header>
        <Content style={{ margin: '24px', padding: '24px', background: '#fff', minHeight: 280 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

const DashboardPage: React.FC = () => {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Alert
        message="아산병원 IDP POC 프로젝트 현황"
        description="Text2SQL MVP가 완료되었습니다. 상용 솔루션 4개 도입으로 개발 기간이 12주 단축되었습니다."
        type="success"
        showIcon
      />
      
      <Card title="프로젝트 상태">
        <Space direction="vertical">
          <div>✅ <strong>SFR-007 Text2SQL</strong>: MVP 완료 (FastAPI + React)</div>
          <div>🔄 <strong>상용 솔루션 연동</strong>: API 스펙 확인 중</div>
          <div>⏳ <strong>자체 구현 모듈</strong>: 설계 단계</div>
        </Space>
      </Card>

      <Card title="Text2SQL 테스트">
        <p>백엔드 API가 localhost:8000에서 실행 중입니다.</p>
        <p>CDW 연구 페이지에서 자연어 질의를 SQL로 변환할 수 있습니다.</p>
      </Card>
    </Space>
  );
};

const SimpleApp: React.FC = () => {
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
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <SimpleLayout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/text2sql" element={<PromptEnhancement />} />
            </Routes>
          </SimpleLayout>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default SimpleApp;