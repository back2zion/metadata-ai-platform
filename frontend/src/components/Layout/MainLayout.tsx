import React from 'react';
import { Layout, Menu, Space, Typography } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  FundOutlined,
  ApiOutlined,
  RobotOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <HomeOutlined />,
      label: '홈 대시보드 (SFR-001)',
    },
    {
      key: 'group-data',
      label: '데이터 관리',
      type: 'group',
    },
    {
      key: '/datamart',
      icon: <DatabaseOutlined />,
      label: 'SFR-002: 데이터마트',
    },
    {
      key: '/etl',
      icon: <ApiOutlined />,
      label: 'SFR-005: ETL',
    },
    {
      key: 'group-analysis',
      label: '분석 & 시각화',
      type: 'group',
    },
    {
      key: '/bi',
      icon: <BarChartOutlined />,
      label: 'SFR-003: BI',
    },
    {
      key: '/olap',
      icon: <FundOutlined />,
      label: 'SFR-004: OLAP',
    },
    {
      key: 'group-ai',
      label: 'AI & 연구',
      type: 'group',
    },
    {
      key: '/ai-environment',
      icon: <RobotOutlined />,
      label: 'SFR-006: AI 분석환경',
    },
    {
      key: '/cdw',
      icon: <ExperimentOutlined />,
      label: 'SFR-007: CDW 연구',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };
  
  const getPageTitle = () => {
    for (const item of menuItems) {
      if (item && 'key' in item && item.key === location.pathname) {
        return item.label;
      }
    }
    return '아산병원 IDP';
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={280} theme="light" style={{ borderRight: '1px solid #e9ecef' }}>
        <div style={{ 
          padding: '16px', 
          textAlign: 'center',
          borderBottom: '1px solid #e9ecef'
        }}>
          <img 
            src="/asan_logo.png" 
            alt="Asan Medical Center Logo" 
            style={{ 
              height: '40px'
            }} 
          />
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px' }}>
          <Title level={4} style={{ margin: 0, lineHeight: '64px' }}>
            {getPageTitle()}
          </Title>
        </Header>
        <Content style={{ margin: '24px', padding: '24px', minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;