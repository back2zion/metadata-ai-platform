import React, { useState } from 'react';
import { Card, Input, Button, Typography, Space, Row, Col, Alert, Divider, Tag, Spin } from 'antd';
import { SendOutlined, ClearOutlined, CopyOutlined, ExperimentOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

interface EnhancementResult {
  original_question: string;
  enhanced_question: string;
  enhancements_applied: string[];
  enhancement_confidence: number;
  sql: string;
  sql_explanation: string;
  sql_confidence: number;
  execution_result?: {
    results: any[];
    row_count: number;
    columns: string[];
    execution_time_ms: number;
    natural_language_explanation: string;
    error?: string;
  };
}

const PromptEnhancement: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<EnhancementResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEnhance = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/text2sql/enhanced-generate', {
        question: question.trim(),
        enhancement_type: 'medical',
        include_explanation: true,
        auto_execute: true
      });

      setResult(response.data);
    } catch (err) {
      console.error('Enhancement error:', err);
      setError('프롬프트 강화 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    setResult(null);
    setError(null);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const exampleQuestions = [
    "내 진료내역 중 홍길동 환자에 대한 내분비내과와 연계된 당뇨 경과기록 정보 전체와 TG 및 콜레스테롤 검사 결과, 그리고 혈압, 맥박 정보를 정리해서 보여줘",
    "김철수 환자의 최근 1년간 심장내과 진료 기록과 혈액검사 결과 보여줘",
    "응급실에 내원한 고혈압 환자들의 약물 처방 현황 알려줘",
    "당뇨병 환자의 평균 입원 일수와 진료비 분석해줘",
    "이번 달 외래 환자 수는 얼마나 되나",
    "50대 남성 중 고혈압 진단받은 사람 몇 명인지"
  ];

  return (
    <div style={{ padding: '0 16px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Title level={3}>
            <ExperimentOutlined style={{ color: '#1890ff' }} /> Text2SQL
          </Title>
          <Paragraph type="secondary">
            자연어 질의를 SQL로 변환하여 의료 데이터를 조회합니다.
            프롬프트 강화 → SQL 생성 → 실행이 자동으로 이루어져 정확한 결과를 제공합니다.
          </Paragraph>
        </Card>

        <Row gutter={24}>
          <Col span={24}>
            <Card title="질의 입력" extra={
              <Space>
                <Button icon={<ClearOutlined />} onClick={handleClear}>
                  초기화
                </Button>
                <Button 
                  type="primary" 
                  icon={<SendOutlined />} 
                  onClick={handleEnhance}
                  loading={loading}
                  disabled={!question.trim()}
                >
                  프롬프트 강화
                </Button>
              </Space>
            }>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <TextArea
                  placeholder="의료 질의를 입력하세요..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  rows={4}
                  showCount
                  maxLength={1000}
                />
                
                <div>
                  <Text strong>예시 질의:</Text>
                  <div style={{ marginTop: 8 }}>
                    {exampleQuestions.map((example, index) => (
                      <Tag
                        key={index}
                        style={{ margin: 4, cursor: 'pointer' }}
                        onClick={() => setQuestion(example)}
                      >
                        예시 {index + 1}
                      </Tag>
                    ))}
                  </div>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>

        {error && (
          <Alert
            message="오류 발생"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
          />
        )}

        {loading && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Spin size="large" />
              <div style={{ marginTop: 16 }}>
                <Text>프롬프트를 강화하고 있습니다...</Text>
              </div>
            </div>
          </Card>
        )}

        {result && !loading && (
          <Card title="강화 결과" extra={
            <Space>
              <Tag color={getConfidenceColor(result.enhancement_confidence)}>
                강화 신뢰도: {(result.enhancement_confidence * 100).toFixed(1)}%
              </Tag>
              <Tag color={getConfidenceColor(result.sql_confidence)}>
                SQL 신뢰도: {(result.sql_confidence * 100).toFixed(1)}%
              </Tag>
            </Space>
          }>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Title level={5}>원본 질의:</Title>
                <Card type="inner" style={{ background: '#fafafa' }}>
                  <Text>{result.original_question}</Text>
                </Card>
              </div>

              <div>
                <Title level={5}>
                  강화된 질의:
                  <Button 
                    type="text" 
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(result.enhanced_question)}
                    style={{ marginLeft: 8 }}
                  >
                    복사
                  </Button>
                </Title>
                <Card type="inner" style={{ background: '#f6ffed', border: '1px solid #b7eb8f' }}>
                  <Text strong style={{ color: '#52c41a' }}>{result.enhanced_question}</Text>
                </Card>
              </div>

              {result.enhancements_applied && result.enhancements_applied.length > 0 && (
                <div>
                  <Title level={5}>적용된 강화 사항:</Title>
                  <Space wrap>
                    {result.enhancements_applied.map((enhancement, index) => (
                      <Tag key={index} color="blue">
                        {enhancement}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}

              <Divider />

              <div>
                <Title level={5}>
                  생성된 SQL:
                  <Button 
                    type="text" 
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(result.sql)}
                    style={{ marginLeft: 8 }}
                  >
                    복사
                  </Button>
                </Title>
                <Card type="inner" style={{ background: '#f0f8ff', border: '1px solid #91d5ff' }}>
                  <Text code style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>{result.sql}</Text>
                </Card>
                {result.sql_explanation && (
                  <div style={{ marginTop: 8 }}>
                    <Text type="secondary">{result.sql_explanation}</Text>
                  </div>
                )}
              </div>

              {result.execution_result && (
                <div>
                  <Title level={5}>실행 결과:</Title>
                  {result.execution_result.error ? (
                    <Alert
                      message="SQL 실행 오류"
                      description={result.execution_result.error}
                      type="error"
                      showIcon
                    />
                  ) : (
                    <Card type="inner">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div>
                          <Text strong>조회 결과: </Text>
                          <Text>{result.execution_result.row_count}건</Text>
                          <Text type="secondary" style={{ marginLeft: 16 }}>
                            실행시간: {result.execution_result.execution_time_ms?.toFixed(1)}ms
                          </Text>
                        </div>
                        {result.execution_result.natural_language_explanation && (
                          <Alert
                            message={result.execution_result.natural_language_explanation}
                            type="success"
                            showIcon
                          />
                        )}
                        {result.execution_result.results && result.execution_result.results.length > 0 && (
                          <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                              <thead>
                                <tr style={{ background: '#fafafa', borderBottom: '1px solid #d9d9d9' }}>
                                  {result.execution_result.columns?.map((col, idx) => (
                                    <th key={idx} style={{ padding: '8px', textAlign: 'left', border: '1px solid #d9d9d9' }}>
                                      {col}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {result.execution_result.results.slice(0, 10).map((row, idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid #f0f0f0' }}>
                                    {result.execution_result!.columns?.map((col, colIdx) => (
                                      <td key={colIdx} style={{ padding: '8px', border: '1px solid #d9d9d9' }}>
                                        {String(row[col] || '')}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                            {result.execution_result.results.length > 10 && (
                              <div style={{ textAlign: 'center', marginTop: 8 }}>
                                <Text type="secondary">... 더 많은 결과가 있습니다 (총 {result.execution_result.row_count}건)</Text>
                              </div>
                            )}
                          </div>
                        )}
                      </Space>
                    </Card>
                  )}
                </div>
              )}

              <Alert
                message="통합 프로세스 완료"
                description="프롬프트 강화 → SQL 생성 → 실행이 완료되었습니다. 이제 정확한 의료 데이터 조회가 가능합니다."
                type="success"
                showIcon
              />
            </Space>
          </Card>
        )}

        <Card title="프롬프트 강화 규칙" style={{ marginTop: 24 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Title level={5}>구조화 규칙:</Title>
              <ul>
                <li>환자명 → "환자이름이 [이름]인"</li>
                <li>진료과 → "진료과가 [과명]인"</li>
                <li>질병명을 의학 용어로 구체화</li>
                <li>검사명을 정확한 의학 용어로 변환</li>
              </ul>
            </Col>
            <Col span={8}>
              <Title level={5}>의학 용어 변환:</Title>
              <ul>
                <li>TG → 중성지방</li>
                <li>혈압, 맥박 → vital sign 혈압, 맥박</li>
                <li>경과기록 → 입원경과기록</li>
                <li>검사 → 검사명이 [검사명]인 검사</li>
              </ul>
            </Col>
            <Col span={8}>
              <Title level={5}>질문 형태 변환:</Title>
              <ul>
                <li>보여줘 → 보여주세요</li>
                <li>알려줘 → 알려주세요</li>
                <li>분석해줘 → 분석해주세요</li>
                <li>명령형 → 을/를 조회해주세요</li>
              </ul>
            </Col>
          </Row>
        </Card>
      </Space>
    </div>
  );
};

export default PromptEnhancement;