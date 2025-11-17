import React, { useState } from 'react';
import { Card, Input, Button, Space, Tag, Alert, Table, Tabs, Typography, Row, Col, Divider, message } from 'antd';
import { SendOutlined, LoadingOutlined, DatabaseOutlined, SearchOutlined, CodeOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const { TextArea } = Input;
const { TabPane } = Tabs;
const { Text, Title, Paragraph } = Typography;

const CDWResearch: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [generatedSQL, setGeneratedSQL] = useState('');
  const [sqlResult, setSqlResult] = useState<any>(null);

  // Fetch example questions
  const { data: examples } = useQuery('text2sql-examples', async () => {
    const response = await axios.get('http://localhost:8000/api/v1/text2sql/examples');
    return response.data.examples;
  });

  // Generate SQL from text
  const generateSQL = useMutation(
    async (question: string) => {
      const response = await axios.post('http://localhost:8000/api/v1/text2sql/generate', {
        question,
        include_explanation: true
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setGeneratedSQL(data.sql);
        setSqlResult(data);
        message.success('SQL 쿼리가 생성되었습니다.');
      },
      onError: () => {
        message.error('SQL 생성 중 오류가 발생했습니다.');
      }
    }
  );

  // Execute SQL
  const executeSQL = useMutation(
    async (sql: string) => {
      const response = await axios.post('http://localhost:8000/api/v1/text2sql/execute', {
        sql,
        limit: 100
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        message.success('쿼리가 실행되었습니다.');
      },
      onError: () => {
        message.error('쿼리 실행 중 오류가 발생했습니다.');
      }
    }
  );

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
  };

  const handleGenerateSQL = () => {
    if (!question.trim()) {
      message.warning('질문을 입력해주세요.');
      return;
    }
    generateSQL.mutate(question);
  };

  return (
    <div>
      <Card title={
        <Space>
          <DatabaseOutlined />
          <span>SFR-007: CDW 데이터 추출 및 연구 지원</span>
        </Space>
      }>
        <Tabs defaultActiveKey="text2sql">
          <TabPane tab="Text2SQL 자연어 쿼리" key="text2sql">
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Alert
                  message="자연어를 SQL로 변환"
                  description="일상적인 질문을 입력하시면, AI가 적절한 SQL 쿼리를 생성합니다. 의료 데이터베이스에 최적화되어 있습니다."
                  type="info"
                  showIcon
                />
              </Col>
              
              <Col span={24}>
                <Card title="질문 입력">
                  <TextArea
                    rows={4}
                    placeholder="예: 2023년에 당뇨병 진단받은 50대 남성 환자는 몇 명인가요?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onPressEnter={(e) => {
                      if (e.shiftKey) return;
                      e.preventDefault();
                      handleGenerateSQL();
                    }}
                  />
                  
                  <Space style={{ marginTop: 16 }} wrap>
                    <Button
                      type="primary"
                      icon={generateSQL.isLoading ? <LoadingOutlined /> : <SendOutlined />}
                      onClick={handleGenerateSQL}
                      loading={generateSQL.isLoading}
                    >
                      SQL 생성
                    </Button>
                    
                    <Text type="secondary">또는 예시 질문 선택:</Text>
                  </Space>
                  
                  <div style={{ marginTop: 16 }}>
                    {examples?.map((category: any, idx: number) => (
                      <div key={idx}>
                        <Text strong>{category.category}:</Text>
                        <Space wrap style={{ marginTop: 8, marginBottom: 16 }}>
                          {category.questions.map((q: string, qIdx: number) => (
                            <Button
                              key={qIdx}
                              size="small"
                              onClick={() => handleExampleClick(q)}
                            >
                              {q}
                            </Button>
                          ))}
                        </Space>
                      </div>
                    ))}
                  </div>
                </Card>
              </Col>
              
              {sqlResult && (
                <Col span={24}>
                  <Card 
                    title="생성된 SQL"
                    extra={
                      <Tag color={sqlResult.confidence > 0.8 ? 'green' : 'orange'}>
                        신뢰도: {(sqlResult.confidence * 100).toFixed(1)}%
                      </Tag>
                    }
                  >
                    <div style={{ 
                      backgroundColor: '#f5f5f5', 
                      padding: 16, 
                      borderRadius: 8,
                      fontFamily: 'monospace'
                    }}>
                      <pre style={{ margin: 0 }}>{sqlResult.sql}</pre>
                    </div>
                    
                    <Divider />
                    
                    <Alert
                      message="SQL 설명"
                      description={sqlResult.explanation}
                      type="success"
                      showIcon
                    />
                    
                    <div style={{ marginTop: 16 }}>
                      <Button 
                        type="primary"
                        icon={<CodeOutlined />}
                        onClick={() => executeSQL.mutate(sqlResult.sql)}
                        loading={executeSQL.isLoading}
                      >
                        쿼리 실행
                      </Button>
                    </div>
                  </Card>
                </Col>
              )}
              
              {executeSQL.data && (
                <Col span={24}>
                  <Card title="실행 결과">
                    <Table
                      dataSource={executeSQL.data.results}
                      columns={executeSQL.data.columns?.map((col: string) => ({
                        title: col,
                        dataIndex: col,
                        key: col,
                      }))}
                      pagination={{ pageSize: 10 }}
                      scroll={{ x: true }}
                    />
                    
                    <div style={{ marginTop: 16 }}>
                      <Space>
                        <Text type="secondary">
                          실행 시간: {executeSQL.data.execution_time_ms?.toFixed(2)}ms
                        </Text>
                        <Text type="secondary">
                          결과 행 수: {executeSQL.data.row_count}개
                        </Text>
                      </Space>
                    </div>
                  </Card>
                </Col>
              )}
            </Row>
          </TabPane>
          
          <TabPane tab="연구 데이터셋 추출" key="research">
            <Card>
              <Alert
                message="연구 데이터셋 추출 기능"
                description="IRB 승인 후 연구용 데이터셋을 추출할 수 있습니다. 비식별화 처리된 데이터만 제공됩니다."
                type="warning"
                showIcon
              />
              
              <div style={{ marginTop: 24 }}>
                <Title level={4}>추출 가능한 데이터셋</Title>
                <ul>
                  <li>환자 코호트 데이터</li>
                  <li>진료 기록 데이터</li>
                  <li>검사 결과 데이터</li>
                  <li>처방 데이터</li>
                </ul>
              </div>
              
              <Button type="primary" style={{ marginTop: 16 }}>
                데이터 추출 요청
              </Button>
            </Card>
          </TabPane>
          
          <TabPane tab="데이터 카탈로그" key="catalog">
            <Card>
              <Title level={4}>데이터베이스 스키마</Title>
              <Table
                dataSource={[
                  {
                    table: 'dim_patient',
                    description: '환자 차원 테이블',
                    columns: 'patient_key, age_group, gender, region'
                  },
                  {
                    table: 'dim_diagnosis',
                    description: '진단 차원 테이블',
                    columns: 'diagnosis_key, kcd_code, diagnosis_name, category'
                  },
                  {
                    table: 'fact_visit',
                    description: '진료 사실 테이블',
                    columns: 'visit_key, patient_key, diagnosis_key, visit_date, visit_count'
                  },
                ]}
                columns={[
                  { title: '테이블명', dataIndex: 'table', key: 'table' },
                  { title: '설명', dataIndex: 'description', key: 'description' },
                  { title: '주요 컬럼', dataIndex: 'columns', key: 'columns' },
                ]}
                pagination={false}
              />
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default CDWResearch;