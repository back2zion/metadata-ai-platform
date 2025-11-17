import React, { useState } from 'react';
import { Card, Table, Button, Space, Tag, Timeline, Progress, Row, Col, Statistic, Badge, Alert } from 'antd';
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  SyncOutlined,
  WarningOutlined 
} from '@ant-design/icons';
import { useQuery, useMutation } from 'react-query';
import axios from 'axios';

const ETL: React.FC = () => {
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null);

  // Fetch pipelines
  const { data: pipelines, refetch: refetchPipelines } = useQuery('etl-pipelines', async () => {
    const response = await axios.get('/api/v1/etl/pipelines');
    return response.data.pipelines;
  });

  // Fetch jobs
  const { data: jobs, refetch: refetchJobs } = useQuery('etl-jobs', async () => {
    const response = await axios.get('/api/v1/etl/jobs');
    return response.data.jobs;
  });

  // Fetch ETL health
  const { data: health } = useQuery('etl-health', async () => {
    const response = await axios.get('/api/v1/etl/monitoring/health');
    return response.data;
  });

  // Run pipeline
  const runPipeline = useMutation(
    async (pipelineId: string) => {
      const response = await axios.post(`/api/v1/etl/pipelines/${pipelineId}/run`);
      return response.data;
    },
    {
      onSuccess: () => {
        refetchJobs();
      }
    }
  );

  const pipelineColumns = [
    {
      title: '파이프라인',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>,
    },
    {
      title: '소스',
      dataIndex: 'source',
      key: 'source',
    },
    {
      title: '대상',
      dataIndex: 'destination',
      key: 'destination',
    },
    {
      title: '스케줄',
      dataIndex: 'schedule',
      key: 'schedule',
      render: (schedule: string) => <Tag>{schedule}</Tag>,
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'active' ? 'green' : status === 'paused' ? 'orange' : 'red';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: '작업',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button 
            icon={<PlayCircleOutlined />} 
            size="small" 
            type="primary"
            onClick={() => runPipeline.mutate(record.id)}
          >
            실행
          </Button>
          <Button icon={<PauseCircleOutlined />} size="small">
            일시정지
          </Button>
        </Space>
      ),
    },
  ];

  const jobColumns = [
    {
      title: '작업 ID',
      dataIndex: 'job_id',
      key: 'job_id',
    },
    {
      title: '파이프라인',
      dataIndex: 'pipeline_name',
      key: 'pipeline_name',
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        let color = 'default';
        let icon = null;
        
        switch(status) {
          case 'completed':
            color = 'green';
            icon = <CheckCircleOutlined />;
            break;
          case 'running':
            color = 'blue';
            icon = <SyncOutlined spin />;
            break;
          case 'failed':
            color = 'red';
            icon = <WarningOutlined />;
            break;
          default:
            icon = <ClockCircleOutlined />;
        }
        
        return <Tag color={color} icon={icon}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: '처리 레코드',
      dataIndex: 'records_processed',
      key: 'records_processed',
      render: (value: number) => value?.toLocaleString() || '-',
    },
    {
      title: '시작 시간',
      dataIndex: 'started_at',
      key: 'started_at',
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="활성 파이프라인"
              value={health?.active_pipelines || 0}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="실행 중인 작업"
              value={health?.running_jobs || 0}
              prefix={<SyncOutlined spin />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="24시간 내 실패"
              value={health?.failed_jobs_24h || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: health?.failed_jobs_24h > 0 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="24시간 처리량"
              value={health?.data_processed_24h || '0 GB'}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="ETL 파이프라인" extra={<Badge status="processing" text="실시간 모니터링" />}>
            <Table 
              columns={pipelineColumns} 
              dataSource={pipelines}
              pagination={false}
              onRow={(record) => ({
                onClick: () => setSelectedPipeline(record.id),
                style: { cursor: 'pointer' }
              })}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={16}>
          <Card title="최근 실행 작업">
            <Table 
              columns={jobColumns} 
              dataSource={jobs}
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="ETL 스테이지 상태">
            <Timeline>
              <Timeline.Item color="green" dot={<CheckCircleOutlined />}>
                Extract: 데이터 추출 완료 (180초)
              </Timeline.Item>
              <Timeline.Item color="green" dot={<CheckCircleOutlined />}>
                Transform: 데이터 변환 완료 (420초)
              </Timeline.Item>
              <Timeline.Item color="blue" dot={<SyncOutlined spin />}>
                Load: 데이터 적재 중... (진행률: 65%)
              </Timeline.Item>
            </Timeline>
            <Progress percent={65} status="active" />
          </Card>
          
          <Card title="시스템 상태" style={{ marginTop: 16 }}>
            <Alert
              message="모든 시스템 정상"
              description="ETL 파이프라인이 정상적으로 작동 중입니다."
              type="success"
              showIcon
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ETL;