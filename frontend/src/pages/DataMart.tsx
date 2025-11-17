import React, { useState } from 'react';
import { Card, Table, Button, Space, Tag, Progress, Modal, Form, Input, Select, message, Row, Col, Statistic } from 'antd';
import { DatabaseOutlined, ReloadOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from 'react-query';
import axios from 'axios';

interface DataMartInfo {
  name: string;
  description: string;
  status: string;
  last_updated: string;
  records?: number;
  quality_score?: number;
}

const DataMart: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  // Fetch data marts
  const { data: datamarts, refetch } = useQuery('datamarts', async () => {
    const response = await axios.get('/api/v1/datamart/list');
    return response.data.datamarts;
  });

  // Create data mart mutation
  const createDataMart = useMutation(
    async (values: any) => {
      const response = await axios.post('/api/v1/datamart/create', values);
      return response.data;
    },
    {
      onSuccess: () => {
        message.success('데이터마트가 생성되었습니다.');
        setIsModalOpen(false);
        form.resetFields();
        refetch();
      },
      onError: () => {
        message.error('데이터마트 생성 중 오류가 발생했습니다.');
      }
    }
  );

  // Refresh data mart
  const refreshDataMart = useMutation(
    async (martName: string) => {
      const response = await axios.post(`/api/v1/datamart/${martName}/refresh`);
      return response.data;
    },
    {
      onSuccess: () => {
        message.success('데이터마트 갱신이 시작되었습니다.');
        refetch();
      }
    }
  );

  const columns = [
    {
      title: '데이터마트명',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <DatabaseOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: '설명',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'active' ? 'green' : status === 'updating' ? 'orange' : 'red';
        const icon = status === 'active' ? <CheckCircleOutlined /> : <ClockCircleOutlined />;
        return <Tag color={color} icon={icon}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: '최종 업데이트',
      dataIndex: 'last_updated',
      key: 'last_updated',
    },
    {
      title: '작업',
      key: 'action',
      render: (_: any, record: DataMartInfo) => (
        <Space size="middle">
          <Button 
            icon={<ReloadOutlined />} 
            size="small"
            onClick={() => refreshDataMart.mutate(record.name)}
          >
            갱신
          </Button>
          <Button size="small">품질 확인</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="전체 데이터마트"
              value={datamarts?.length || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="활성 데이터마트"
              value={datamarts?.filter((d: any) => d.status === 'active').length || 0}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="평균 품질 점수"
              value={98}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="총 레코드 수"
              value={1500000}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title="SFR-002: 분석 데이터마트 관리"
        extra={
          <Button type="primary" onClick={() => setIsModalOpen(true)}>
            새 데이터마트 생성
          </Button>
        }
      >
        <Table 
          columns={columns} 
          dataSource={datamarts}
          loading={!datamarts}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="새 데이터마트 생성"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
        confirmLoading={createDataMart.isLoading}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={createDataMart.mutate}
        >
          <Form.Item
            name="name"
            label="데이터마트 이름"
            rules={[{ required: true, message: '이름을 입력해주세요' }]}
          >
            <Input placeholder="예: patient_cohort_dm" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="설명"
            rules={[{ required: true, message: '설명을 입력해주세요' }]}
          >
            <Input.TextArea rows={3} placeholder="데이터마트의 목적과 내용을 설명해주세요" />
          </Form.Item>
          
          <Form.Item
            name="fact_tables"
            label="팩트 테이블"
            rules={[{ required: true, message: '팩트 테이블을 선택해주세요' }]}
          >
            <Select
              mode="multiple"
              placeholder="팩트 테이블 선택"
              options={[
                { label: 'fact_visit', value: 'fact_visit' },
                { label: 'fact_prescription', value: 'fact_prescription' },
                { label: 'fact_lab_result', value: 'fact_lab_result' },
              ]}
            />
          </Form.Item>
          
          <Form.Item
            name="dimension_tables"
            label="차원 테이블"
            rules={[{ required: true, message: '차원 테이블을 선택해주세요' }]}
          >
            <Select
              mode="multiple"
              placeholder="차원 테이블 선택"
              options={[
                { label: 'dim_patient', value: 'dim_patient' },
                { label: 'dim_diagnosis', value: 'dim_diagnosis' },
                { label: 'dim_time', value: 'dim_time' },
                { label: 'dim_department', value: 'dim_department' },
              ]}
            />
          </Form.Item>
          
          <Form.Item
            name="refresh_schedule"
            label="갱신 주기"
            rules={[{ required: true, message: '갱신 주기를 선택해주세요' }]}
          >
            <Select
              placeholder="갱신 주기 선택"
              options={[
                { label: '매일', value: '0 2 * * *' },
                { label: '매주', value: '0 2 * * 0' },
                { label: '매월', value: '0 2 1 * *' },
                { label: '실시간', value: 'realtime' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DataMart;