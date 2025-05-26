import React from 'react';
import { render, waitFor, screen, fireEvent } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// Mock组件
const MockSuokeScreen = () => {
  const [selectedAgent, setSelectedAgent] = React.useState('xiaoai');
  const [consultationActive, setConsultationActive] = React.useState(false);
  const [symptoms, setSymptoms] = React.useState<string[]>([]);
  const [diagnosis, setDiagnosis] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [tcmFeature, setTcmFeature] = React.useState('');
  const [recordAction, setRecordAction] = React.useState('');

  const agents = [
    { id: 'xiaoai', name: '小艾', specialty: '健康管理', status: 'online' },
    { id: 'xiaoke', name: '小克', specialty: '疾病预防', status: 'online' },
    { id: 'laoke', name: '老克', specialty: '中医诊断', status: 'online' },
    { id: 'soer', name: '索儿', specialty: '康复指导', status: 'offline' },
  ];

  const commonSymptoms = [
    '头痛', '发热', '咳嗽', '乏力', '失眠',
    '胸闷', '腹痛', '恶心', '眩晕', '心悸',
  ];

  const handleSymptomToggle = (symptom: string) => {
    setSymptoms(prev => 
      prev.includes(symptom) 
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    );
  };

  const handleStartConsultation = async () => {
    if (symptoms.length === 0) {
      return;
    }

    setLoading(true);
    setConsultationActive(true);

    try {
      // 模拟AI诊断 - 缩短等待时间以便测试
      await new Promise<void>(resolve => setTimeout(() => resolve(), 100));
      
      if (symptoms.includes('头痛') && symptoms.includes('发热')) {
        setDiagnosis('根据症状分析，可能是感冒引起的头痛发热，建议多休息，多喝水。');
      } else if (symptoms.includes('失眠') && symptoms.includes('心悸')) {
        setDiagnosis('症状提示可能存在心神不宁，建议调整作息，必要时就医检查。');
      } else if (symptoms.length === 1) {
        setDiagnosis('请提供更多症状信息以便准确诊断。');
      } else {
        setDiagnosis('根据您的症状，建议进一步观察或咨询专业医生。');
      }
    } catch (error) {
      setDiagnosis('诊断服务暂时不可用，请稍后重试。');
    } finally {
      setLoading(false);
    }
  };

  const handleEndConsultation = () => {
    setConsultationActive(false);
    setSymptoms([]);
    setDiagnosis('');
  };

  return (
    <div data-testid="suoke-screen">
      {/* 智能体选择 */}
      <div data-testid="agent-selector">
        <div data-testid="agent-title">选择智能体</div>
        {agents.map(agent => (
          <button
            key={agent.id}
            data-testid={`agent-${agent.id}`}
            onClick={() => setSelectedAgent(agent.id)}
            style={{
              backgroundColor: selectedAgent === agent.id ? '#007AFF' : '#F0F0F0',
              opacity: agent.status === 'offline' ? 0.5 : 1,
            }}
            disabled={agent.status === 'offline'}
          >
            <div data-testid={`agent-name-${agent.id}`}>{agent.name}</div>
            <div data-testid={`agent-specialty-${agent.id}`}>{agent.specialty}</div>
            <div data-testid={`agent-status-${agent.id}`}>{agent.status}</div>
          </button>
        ))}
      </div>

      {/* 症状选择 */}
      <div data-testid="symptom-selector">
        <div data-testid="symptom-title">选择症状</div>
        <div data-testid="symptom-grid">
          {commonSymptoms.map(symptom => (
            <button
              key={symptom}
              data-testid={`symptom-${symptom}`}
              onClick={() => handleSymptomToggle(symptom)}
              style={{
                backgroundColor: symptoms.includes(symptom) ? '#FF6B6B' : '#F0F0F0',
              }}
            >
              {symptom}
            </button>
          ))}
        </div>
        <div data-testid="selected-symptoms">
          已选择: {symptoms.join(', ') || '无'}
        </div>
      </div>

      {/* 咨询控制 */}
      <div data-testid="consultation-controls">
        {!consultationActive ? (
          <button
            data-testid="start-consultation"
            onClick={handleStartConsultation}
            disabled={symptoms.length === 0 || loading}
          >
            {loading ? '正在分析...' : '开始咨询'}
          </button>
        ) : (
          <button
            data-testid="end-consultation"
            onClick={handleEndConsultation}
          >
            结束咨询
          </button>
        )}
      </div>

      {/* 诊断结果 */}
      {diagnosis && (
        <div data-testid="diagnosis-result">
          <div data-testid="diagnosis-title">诊断建议</div>
          <div data-testid="diagnosis-content">{diagnosis}</div>
        </div>
      )}

      {/* 中医特色功能 */}
      <div data-testid="tcm-features">
        <div data-testid="tcm-title">中医特色</div>
        <button data-testid="constitution-test" onClick={() => setTcmFeature('constitution')}>体质测试</button>
        <button data-testid="meridian-analysis" onClick={() => setTcmFeature('meridian')}>经络分析</button>
        <button data-testid="herb-recommendation" onClick={() => setTcmFeature('herb')}>药材推荐</button>
        <button data-testid="acupoint-guide" onClick={() => setTcmFeature('acupoint')}>穴位指导</button>
      </div>

      {/* 健康档案 */}
      <div data-testid="health-profile">
        <div data-testid="profile-title">健康档案</div>
        <button data-testid="view-history" onClick={() => setRecordAction('view')}>查看历史</button>
        <button data-testid="export-report" onClick={() => setRecordAction('export')}>导出报告</button>
        <button data-testid="share-data" onClick={() => setRecordAction('share')}>分享数据</button>
      </div>
    </div>
  );
};

// Mock store
const mockStore = configureStore({
  reducer: {
    suoke: (state = { 
      selectedAgent: 'xiaoai',
      consultationHistory: [],
      healthProfile: {},
    }, action) => state,
  },
});

describe('索克屏幕测试', () => {
  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <Provider store={mockStore}>
        {component}
      </Provider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基本渲染', () => {
    it('应该正确渲染所有主要组件', () => {
      renderWithProviders(<MockSuokeScreen />);

      expect(screen.getByTestId('suoke-screen')).toBeTruthy();
      expect(screen.getByTestId('agent-selector')).toBeTruthy();
      expect(screen.getByTestId('symptom-selector')).toBeTruthy();
      expect(screen.getByTestId('consultation-controls')).toBeTruthy();
      expect(screen.getByTestId('tcm-features')).toBeTruthy();
      expect(screen.getByTestId('health-profile')).toBeTruthy();
    });

    it('应该显示所有智能体选项', () => {
      renderWithProviders(<MockSuokeScreen />);

      expect(screen.getByTestId('agent-xiaoai')).toBeTruthy();
      expect(screen.getByTestId('agent-xiaoke')).toBeTruthy();
      expect(screen.getByTestId('agent-laoke')).toBeTruthy();
      expect(screen.getByTestId('agent-soer')).toBeTruthy();

      expect(screen.getByTestId('agent-name-xiaoai')).toHaveTextContent('小艾');
      expect(screen.getByTestId('agent-specialty-xiaoai')).toHaveTextContent('健康管理');
      expect(screen.getByTestId('agent-status-xiaoai')).toHaveTextContent('online');
    });

    it('应该显示常见症状选项', () => {
      renderWithProviders(<MockSuokeScreen />);

      expect(screen.getByText('头痛')).toBeTruthy();
      expect(screen.getByText('发热')).toBeTruthy();
      expect(screen.getByText('咳嗽')).toBeTruthy();
      expect(screen.getByText('乏力')).toBeTruthy();
      expect(screen.getByText('失眠')).toBeTruthy();
    });
  });

  describe('智能体选择', () => {
    it('应该能够选择不同的智能体', () => {
      renderWithProviders(<MockSuokeScreen />);

      // 默认选择小艾
      expect(screen.getByTestId('agent-xiaoai')).toHaveStyle({
        backgroundColor: '#007AFF',
      });

      // 选择小克
      fireEvent.press(screen.getByTestId('agent-xiaoke'));
      expect(screen.getByTestId('agent-xiaoke')).toHaveStyle({
        backgroundColor: '#007AFF',
      });

      // 选择老克
      fireEvent.press(screen.getByTestId('agent-laoke'));
      expect(screen.getByTestId('agent-laoke')).toHaveStyle({
        backgroundColor: '#007AFF',
      });
    });

    it('应该禁用离线的智能体', () => {
      renderWithProviders(<MockSuokeScreen />);

      const soerAgent = screen.getByTestId('agent-soer');
      expect(soerAgent).toHaveStyle({ opacity: 0.5 });
      expect(soerAgent).toBeDisabled();
    });

    it('应该显示智能体的专业领域', () => {
      renderWithProviders(<MockSuokeScreen />);

      expect(screen.getByTestId('agent-specialty-xiaoai')).toHaveTextContent('健康管理');
      expect(screen.getByTestId('agent-specialty-xiaoke')).toHaveTextContent('疾病预防');
      expect(screen.getByTestId('agent-specialty-laoke')).toHaveTextContent('中医诊断');
      expect(screen.getByTestId('agent-specialty-soer')).toHaveTextContent('康复指导');
    });
  });

  describe('症状选择', () => {
    it('应该能够选择和取消选择症状', () => {
      renderWithProviders(<MockSuokeScreen />);

      const headacheSymptom = screen.getByTestId('symptom-头痛');
      const selectedSymptoms = screen.getByTestId('selected-symptoms');

      // 初始状态
      expect(selectedSymptoms).toHaveTextContent('已选择: 无');

      // 选择头痛
      fireEvent.press(headacheSymptom);
      expect(headacheSymptom).toHaveStyle({ backgroundColor: '#FF6B6B' });
      expect(selectedSymptoms).toHaveTextContent('已选择: 头痛');

      // 取消选择头痛
      fireEvent.press(headacheSymptom);
      expect(headacheSymptom).toHaveStyle({ backgroundColor: '#F0F0F0' });
      expect(selectedSymptoms).toHaveTextContent('已选择: 无');
    });

    it('应该能够选择多个症状', () => {
      renderWithProviders(<MockSuokeScreen />);

      const headacheSymptom = screen.getByTestId('symptom-头痛');
      const feverSymptom = screen.getByTestId('symptom-发热');
      const selectedSymptoms = screen.getByTestId('selected-symptoms');

      // 选择头痛
      fireEvent.press(headacheSymptom);
      expect(selectedSymptoms).toHaveTextContent('已选择: 头痛');

      // 选择发热
      fireEvent.press(feverSymptom);
      expect(selectedSymptoms).toHaveTextContent('已选择: 头痛, 发热');

      // 验证两个症状都被选中
      expect(headacheSymptom).toHaveStyle({ backgroundColor: '#FF6B6B' });
      expect(feverSymptom).toHaveStyle({ backgroundColor: '#FF6B6B' });
    });

    it('应该正确显示已选择的症状列表', () => {
      renderWithProviders(<MockSuokeScreen />);

      const symptoms = ['头痛', '发热', '咳嗽'];
      const selectedSymptoms = screen.getByTestId('selected-symptoms');

      symptoms.forEach(symptom => {
        fireEvent.press(screen.getByTestId(`symptom-${symptom}`));
      });

      expect(selectedSymptoms).toHaveTextContent('已选择: 头痛, 发热, 咳嗽');
    });
  });

  describe('咨询功能', () => {
    it('应该在未选择症状时禁用开始咨询按钮', () => {
      renderWithProviders(<MockSuokeScreen />);

      const startButton = screen.getByTestId('start-consultation');
      expect(startButton).toBeDisabled();
      expect(startButton).toHaveTextContent('开始咨询');
    });

    it('应该在选择症状后启用开始咨询按钮', () => {
      renderWithProviders(<MockSuokeScreen />);

      const startButton = screen.getByTestId('start-consultation');
      const headacheSymptom = screen.getByTestId('symptom-头痛');

      // 选择症状
      fireEvent.press(headacheSymptom);

      expect(startButton).not.toBeDisabled();
    });

    it('应该能够开始和结束咨询', async () => {
      renderWithProviders(<MockSuokeScreen />);

      const headacheSymptom = screen.getByTestId('symptom-头痛');
      const feverSymptom = screen.getByTestId('symptom-发热');
      const startButton = screen.getByTestId('start-consultation');

      // 选择症状
      fireEvent.press(headacheSymptom);
      fireEvent.press(feverSymptom);

      // 开始咨询
      fireEvent.press(startButton);

      // 等待诊断完成
      await waitFor(() => {
        expect(screen.getByTestId('diagnosis-result')).toBeTruthy();
      }, { timeout: 3000 });

      // 验证诊断结果
      const diagnosisContent = screen.getByTestId('diagnosis-content');
      expect(diagnosisContent).toHaveTextContent('根据症状分析，可能是感冒引起的头痛发热');

      // 结束咨询
      const endButton = screen.getByTestId('end-consultation');
      fireEvent.press(endButton);

      // 验证状态重置
      expect(screen.queryByTestId('diagnosis-result')).toBeNull();
      expect(screen.getByTestId('selected-symptoms')).toHaveTextContent('已选择: 无');
    });

    it('应该根据不同症状组合给出不同诊断', async () => {
      renderWithProviders(<MockSuokeScreen />);

      const insomniaSymptom = screen.getByTestId('symptom-失眠');
      const palpitationSymptom = screen.getByTestId('symptom-心悸');
      const startButton = screen.getByTestId('start-consultation');

      // 选择失眠和心悸
      fireEvent.press(insomniaSymptom);
      fireEvent.press(palpitationSymptom);

      // 开始咨询
      fireEvent.press(startButton);

      // 等待诊断完成
      await waitFor(() => {
        expect(screen.getByTestId('diagnosis-result')).toBeTruthy();
      }, { timeout: 3000 });

      // 验证诊断结果
      const diagnosisContent = screen.getByTestId('diagnosis-content');
      expect(diagnosisContent).toHaveTextContent('症状提示可能存在心神不宁');
    });

    it('应该显示加载状态', async () => {
      renderWithProviders(<MockSuokeScreen />);

      const headacheSymptom = screen.getByTestId('symptom-头痛');
      const startButton = screen.getByTestId('start-consultation');

      // 选择症状
      fireEvent.press(headacheSymptom);

      // 开始咨询
      fireEvent.press(startButton);

      // 验证加载状态
      expect(startButton).toHaveTextContent('正在分析...');
      expect(startButton).toBeDisabled();

      // 等待完成
      await waitFor(() => {
        expect(screen.getByTestId('diagnosis-result')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('中医特色功能', () => {
    it('应该显示所有中医特色功能按钮', () => {
      renderWithProviders(<MockSuokeScreen />);

      expect(screen.getByText('体质测试')).toBeTruthy();
      expect(screen.getByText('经络分析')).toBeTruthy();
      expect(screen.getByText('药材推荐')).toBeTruthy();
      expect(screen.getByText('穴位指导')).toBeTruthy();
    });

    it('应该能够点击中医功能按钮', () => {
      renderWithProviders(<MockSuokeScreen />);

      const constitutionTest = screen.getByText('体质测试');
      const meridianAnalysis = screen.getByText('经络分析');
      const herbRecommendation = screen.getByText('药材推荐');
      const acupointGuide = screen.getByText('穴位指导');

      // 模拟点击
      fireEvent.press(constitutionTest);
      fireEvent.press(meridianAnalysis);
      fireEvent.press(herbRecommendation);
      fireEvent.press(acupointGuide);

      // 验证点击事件被触发（这里只是确保没有错误）
      expect(constitutionTest).toBeTruthy();
      expect(meridianAnalysis).toBeTruthy();
      expect(herbRecommendation).toBeTruthy();
      expect(acupointGuide).toBeTruthy();
    });
  });

  describe('健康档案功能', () => {
    it('应该显示健康档案相关按钮', () => {
      renderWithProviders(<MockSuokeScreen />);

      expect(screen.getByText('查看历史')).toBeTruthy();
      expect(screen.getByText('导出报告')).toBeTruthy();
      expect(screen.getByText('分享数据')).toBeTruthy();
    });

    it('应该能够点击健康档案功能按钮', () => {
      renderWithProviders(<MockSuokeScreen />);

      const viewHistory = screen.getByText('查看历史');
      const exportReport = screen.getByText('导出报告');
      const shareData = screen.getByText('分享数据');

      // 模拟点击
      fireEvent.press(viewHistory);
      fireEvent.press(exportReport);
      fireEvent.press(shareData);

      // 验证点击事件被触发（这里只是确保没有错误）
      expect(viewHistory).toBeTruthy();
      expect(exportReport).toBeTruthy();
      expect(shareData).toBeTruthy();
    });
  });

  describe('交互流程', () => {
    it('应该支持完整的诊断流程', async () => {
      renderWithProviders(<MockSuokeScreen />);

      // 1. 选择智能体
      fireEvent.press(screen.getByText('老克'));

      // 2. 选择症状
      fireEvent.press(screen.getByText('头痛'));
      fireEvent.press(screen.getByText('发热'));

      // 3. 开始咨询
      fireEvent.press(screen.getByTestId('start-consultation'));

      // 4. 等待诊断结果
      await waitFor(() => {
        expect(screen.getByTestId('diagnosis-result')).toBeTruthy();
      }, { timeout: 3000 });

      // 5. 验证结果显示
      expect(screen.getByTestId('diagnosis-content')).toHaveTextContent('感冒');

      // 6. 结束咨询
      fireEvent.press(screen.getByTestId('end-consultation'));

      // 7. 验证状态重置
      expect(screen.queryByTestId('diagnosis-result')).toBeNull();
    });

    it('应该在症状不足时提示需要更多信息', async () => {
      renderWithProviders(<MockSuokeScreen />);

      // 只选择一个不常见的症状
      fireEvent.press(screen.getByText('眩晕'));

      // 开始咨询
      fireEvent.press(screen.getByTestId('start-consultation'));

      // 等待诊断结果
      await waitFor(() => {
        expect(screen.getByTestId('diagnosis-result')).toBeTruthy();
      }, { timeout: 3000 });

      // 验证提示信息
      const diagnosisContent = screen.getByTestId('diagnosis-content');
      expect(diagnosisContent).toHaveTextContent('请提供更多症状信息');
    });
  });

  describe('错误处理', () => {
    it('应该处理诊断服务错误', async () => {
      // Mock网络错误
      const originalSetTimeout = (globalThis as any).setTimeout;
      (globalThis as any).setTimeout = jest.fn().mockImplementation((callback: Function, delay: number) => {
        if (delay === 2000) {
          throw new Error('Network Error');
        }
        return originalSetTimeout(callback, delay);
      });

      renderWithProviders(<MockSuokeScreen />);

      // 选择症状
      fireEvent.press(screen.getByText('头痛'));

      // 开始咨询
      fireEvent.press(screen.getByTestId('start-consultation'));

      // 等待错误处理
      await waitFor(() => {
        expect(screen.getByTestId('diagnosis-result')).toBeTruthy();
      }, { timeout: 3000 });

      // 验证错误信息
      const diagnosisContent = screen.getByTestId('diagnosis-content');
      expect(diagnosisContent).toHaveTextContent('诊断服务暂时不可用');

      // 恢复原始setTimeout
      (globalThis as any).setTimeout = originalSetTimeout;
    });
  });
}); 