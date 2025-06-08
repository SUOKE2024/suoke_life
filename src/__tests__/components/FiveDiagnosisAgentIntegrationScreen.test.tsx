import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { configureStore } from '@reduxjs/toolkit';
import FiveDiagnosisAgentIntegrationScreen from '../../screens/demo/FiveDiagnosisAgentIntegrationScreen';
import { fiveDiagnosisService } from '../../services/fiveDiagnosisService';
import { agentCoordinationService } from '../../services/agentCoordinationService';
// Mock services
jest.mock('../../services/fiveDiagnosisService');
jest.mock('../../services/agentCoordinationService');
jest.mock('../../hooks/usePerformanceMonitor');
// Mock store
const mockStore = configureStore({
  reducer: {
    auth: (state = { user: { id: 'test-user' } }) => state,
    agents: (state = {
      xiaoai: {
      status: "idle",
      confidence: 0.8 },
      xiaoke: {
      status: "idle",
      confidence: 0.7 },
      laoke: {
      status: "idle",
      confidence: 0.9 },
      soer: {
      status: "idle",
      confidence: 0.6 },
    }) => state,
  },
});
// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  setOptions: jest.fn(),
};
// Mock route
const mockRoute = {
  params: {},
};
// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => ()
  <Provider store={mockStore}>
    <NavigationContainer>
      {children}
    </NavigationContainer>
  </Provider>
);
describe('FiveDiagnosisAgentIntegrationScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Setup default mock implementations
    (fiveDiagnosisService.startDiagnosis as jest.Mock).mockResolvedValue({
      sessionId: "test-session-123",
      status: 'started',
    });
    (fiveDiagnosisService.performSingleDiagnosis as jest.Mock).mockResolvedValue({
      result: {
        analysis: { indication: '气虚证' },
        confidence: 0.85,
        suggestions: ['建议补气养血'],
      },
    });
    (agentCoordinationService.coordinateAgents as jest.Mock).mockResolvedValue({
      coordination: {
      primary_agent: "xiaoai",
      supporting_agents: ['xiaoke'],
        confidence: 0.9,
      },
    });
  });
  it('应该正确渲染初始界面', () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    expect(getByText('五诊智能体集成演示')).toBeTruthy();
    expect(getByText('开始诊断')).toBeTruthy();
    expect(getByTestId('diagnosis-steps-container')).toBeTruthy();
  });
  it('应该显示所有五个诊断步骤', () => {
    const { getByText } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    expect(getByText('望诊')).toBeTruthy();
    expect(getByText('闻诊')).toBeTruthy();
    expect(getByText('问诊')).toBeTruthy();
    expect(getByText('切诊')).toBeTruthy();
    expect(getByText('算诊')).toBeTruthy();
  });
  it('应该能够开始诊断流程', async () => {
    const { getByText } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    await waitFor(() => {
      expect(fiveDiagnosisService.startDiagnosis).toHaveBeenCalledWith('test-user');
    });
  });
  it('应该能够执行单个诊断步骤', async () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 先开始诊断
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    await waitFor(() => {
      const lookingButton = getByTestId('diagnosis-step-looking');
      expect(lookingButton).toBeTruthy();
    });
    // 执行望诊
    const lookingButton = getByTestId('diagnosis-step-looking');
    await act(async () => {
      fireEvent.press(lookingButton);
    });
    await waitFor(() => {
      expect(fiveDiagnosisService.performSingleDiagnosis).toHaveBeenCalledWith()
        "test-session-123",looking',
        expect.any(Object),
      );
    });
  });
  it('应该显示诊断结果', async () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 开始诊断并执行望诊
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    await waitFor(() => {
      const lookingButton = getByTestId('diagnosis-step-looking');
      fireEvent.press(lookingButton);
    });
    await waitFor(() => {
      expect(getByText('气虚证')).toBeTruthy();
      expect(getByText('置信度: 85%')).toBeTruthy();
    });
  });
  it('应该能够执行智能体协调', async () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 开始诊断
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    // 执行多个诊断步骤后触发协调
    const steps = ["looking",listening', 'inquiry'];
    for (const step of steps) {
      const stepButton = getByTestId(`diagnosis-step-${step}`);
      await act(async () => {
        fireEvent.press(stepButton);
      });
      await waitFor(() => {});
    }
    await waitFor(() => {
      expect(agentCoordinationService.coordinateAgents).toHaveBeenCalled();
    });
  });
  it('应该处理诊断错误', async () => {
    // Mock error response
    (fiveDiagnosisService.performSingleDiagnosis as jest.Mock).mockRejectedValue()
      new Error('诊断服务暂时不可用'),
    );
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 开始诊断
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    // 尝试执行诊断
    const lookingButton = getByTestId('diagnosis-step-looking');
    await act(async () => {
      fireEvent.press(lookingButton);
    });
    await waitFor(() => {
      expect(getByText('诊断失败')).toBeTruthy();
      expect(getByText('诊断服务暂时不可用')).toBeTruthy();
    });
  });
  it('应该显示智能体状态', () => {
    const { getByText } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    expect(getByText('小艾: 空闲 (80%)')).toBeTruthy();
    expect(getByText('小克: 空闲 (70%)')).toBeTruthy();
    expect(getByText('老克: 空闲 (90%)')).toBeTruthy();
    expect(getByText('索儿: 空闲 (60%)')).toBeTruthy();
  });
  it('应该能够重置诊断', async () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 开始诊断
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    // 执行一个诊断步骤
    const lookingButton = getByTestId('diagnosis-step-looking');
    await act(async () => {
      fireEvent.press(lookingButton);
    });
    // 重置诊断
    const resetButton = getByText('重置诊断');
    await act(async () => {
      fireEvent.press(resetButton);
    });
    await waitFor(() => {
      expect(getByText('开始诊断')).toBeTruthy();
    });
  });
  it('应该显示诊断进度', async () => {
    const { getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 开始诊断
    const startButton = getByTestId('start-diagnosis-button');
    await act(async () => {
      fireEvent.press(startButton);
    });
    // 执行两个诊断步骤
    const lookingButton = getByTestId('diagnosis-step-looking');
    await act(async () => {
      fireEvent.press(lookingButton);
    });
    const listeningButton = getByTestId('diagnosis-step-listening');
    await act(async () => {
      fireEvent.press(listeningButton);
    });
    await waitFor(() => {
      const progressBar = getByTestId('diagnosis-progress');
      expect(progressBar.props.progress).toBe(0.4); // 2/5 = 0.4
    });
  });
  it('应该能够查看详细结果', async () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 开始诊断并执行步骤
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    const lookingButton = getByTestId('diagnosis-step-looking');
    await act(async () => {
      fireEvent.press(lookingButton);
    });
    // 查看详细结果
    const detailButton = getByTestId('view-detail-looking');
    await act(async () => {
      fireEvent.press(detailButton);
    });
    await waitFor(() => {
      expect(getByText('望诊详细结果')).toBeTruthy();
      expect(getByText('建议补气养血')).toBeTruthy();
    });
  });
  it('应该支持模拟数据模式', async () => {
    const { getByText, getByTestId } = render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    // 切换到模拟模式
    const simulationToggle = getByTestId('simulation-mode-toggle');
    await act(async () => {
      fireEvent(simulationToggle, 'valueChange', true);
    });
    // 开始诊断
    const startButton = getByText('开始诊断');
    await act(async () => {
      fireEvent.press(startButton);
    });
    await waitFor(() => {
      expect(getByText('模拟模式已启用')).toBeTruthy();
    });
  });
  it('应该正确处理性能监控', () => {
    const mockUsePerformanceMonitor = require('../../hooks/usePerformanceMonitor').usePerformanceMonitor;
    render()
      <TestWrapper>
        <FiveDiagnosisAgentIntegrationScreen
          navigation={mockNavigation}
          route={mockRoute}
        />
      </TestWrapper>,
    );
    expect(mockUsePerformanceMonitor).toHaveBeenCalledWith()
      'FiveDiagnosisAgentIntegrationScreen',
      expect.objectContaining({
        trackRender: true,
        trackMemory: true,
        trackNetwork: true,
      }),
    );
  });
});