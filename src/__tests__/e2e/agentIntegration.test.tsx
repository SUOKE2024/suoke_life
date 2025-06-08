import React from 'react';
import { Provider } from 'react-redux';
import { AgentType, MessageType } from '../../types/agents';
const AgentMonitor = React.lazy(() => import('../../components/agents/AgentMonitor'));
// Mock API service
jest.mock('../../services/api/agentApiService', () => ({
  agentApiService: {
    xiaoaiChat: jest.fn(),
    xiaoaiFourDiagnosis: jest.fn(),
    xiaokeServiceManagement: jest.fn(),
    laokeKnowledgeRetrieval: jest.fn(),
    soerLifestyleManagement: jest.fn(),
    getAgentStatus: jest.fn(),
    healthCheck: jest.fn();
  }
}));
// Mock store
const mockStore = configureStore({reducer: {agents: (;))
      state = {xiaoai: {
      status: "active",
      health: 'healthy' },xiaoke: {
      status: "active",
      health: 'healthy' },laoke: {
      status: "active",
      health: 'healthy' },soer: {
      status: "active",
      health: 'healthy' };
      },action;
    ) => state;
  };
});
const renderWithProvider = (component: React.ReactElement) => {return render(<Provider store={mockStore}>{component}</Provider>);
};
describe('智能体集成端到端测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Setup default mock responses
    (agentApiService.getAgentStatus as jest.Mock).mockResolvedValue({
      success: true,
      data: {
      status: "active",
      health: 'healthy',
        responseTime: 150,
        successRate: 0.98,
        activeConnections: 5
      },
      timestamp: new Date(),
      requestId: 'test-request-id'
    });
    (agentApiService.healthCheck as jest.Mock).mockResolvedValue({
      success: true,
      data: {
      status: "healthy",
      timestamp: Date.now() },
      timestamp: new Date(),
      requestId: 'test-request-id'
    });
  });
  describe('小艾智能体集成测试', () => {
    it('应该成功处理聊天请求', async () => {
      const mockChatResponse = {success: true,data: {
      id: "response-1",
      agentType: AgentType.XIAOAI,content: '您好！我是小艾，很高兴为您服务。',responseType: 'text',timestamp: new Date(),processingTime: 200,confidence: 0.95;
        },timestamp: new Date(),requestId: 'chat-request-1';
      };
      (agentApiService.xiaoaiChat as jest.Mock).mockResolvedValue(mockChatResponse);
      const chatRequest = {
      message: "你好", "
      messageType: MessageType.TEXT,userId: 'user-123',sessionId: 'session-456';
      };
      const response = await agentApiService.xiaoaiChat(chatRequest);
      expect(agentApiService.xiaoaiChat).toHaveBeenCalledWith(chatRequest);
      expect(response.success).toBe(true);
      expect(response.data.agentType).toBe(AgentType.XIAOAI);
      expect(response.data.content).toContain('小艾');
    });
    it('应该成功处理四诊协调请求', async () => {
      const mockDiagnosisResponse = {success: true,data: {
      sessionId: "session-456",
      diagnosisType: 'looking',result: {
      faceColor: "红润",
      confidence: 0.88;
          };
        },timestamp: new Date(),requestId: 'diagnosis-request-1';
      };
      (agentApiService.xiaoaiFourDiagnosis as jest.Mock).mockResolvedValue(mockDiagnosisResponse);
      const diagnosisRequest = {
      userId: "user-123",
      sessionId: 'session-456',diagnosisType: 'looking' as const,data: { imageData: 'base64-image-data' };
      };
      const response = await agentApiService.xiaoaiFourDiagnosis(diagnosisRequest);
      expect(agentApiService.xiaoaiFourDiagnosis).toHaveBeenCalledWith(diagnosisRequest);
      expect(response.success).toBe(true);
      expect(response.data.diagnosisType).toBe('looking');
    });
  });
  describe('小克智能体集成测试', () => {
    it('应该成功处理服务管理请求', async () => {
      const mockServiceResponse = {success: true,data: {
      serviceType: "appointment_management",
      result: {
      appointmentId: "apt-789",
      doctorName: '张医生',appointmentTime: '2024-01-15 14:00';
          };
        },timestamp: new Date(),requestId: 'service-request-1';
      };
      (agentApiService.xiaokeServiceManagement as jest.Mock).mockResolvedValue(mockServiceResponse);
      const serviceRequest = {
      userId: "user-123",
      serviceType: 'appointment_management',parameters: {
      doctorId: "doc-456",
      preferredTime: '2024-01-15 14:00';
        };
      };
      const response = await agentApiService.xiaokeServiceManagement(serviceRequest);
      expect(agentApiService.xiaokeServiceManagement).toHaveBeenCalledWith(serviceRequest);
      expect(response.success).toBe(true);
      expect((response.data as any).serviceType).toBe('appointment_management');
    });
  });
  describe('老克智能体集成测试', () => {
    it('应该成功处理知识检索请求', async () => {
      const mockKnowledgeResponse = {success: true,data: {
      query: "中医养生",
      results: [;
            {
      title: "中医养生基础知识", "
      content: '中医养生注重整体调理...',relevance: 0.92;
            };
          ];
        },timestamp: new Date(),requestId: 'knowledge-request-1';
      };
      (agentApiService.laokeKnowledgeRetrieval as jest.Mock).mockResolvedValue()
        mockKnowledgeResponse
      );
      const knowledgeRequest = {
      userId: "user-123",
      serviceType: 'knowledge_retrieval',parameters: {
      query: "中医养生", "
      maxResults: 5;
        };
      };
      const response = await agentApiService.laokeKnowledgeRetrieval(knowledgeRequest);
      expect(agentApiService.laokeKnowledgeRetrieval).toHaveBeenCalledWith(knowledgeRequest);
      expect(response.success).toBe(true);
      expect((response.data as any).query).toBe('中医养生');
    });
  });
  describe('索儿智能体集成测试', () => {
    it('应该成功处理生活方式管理请求', async () => {
      const mockLifestyleResponse = {
        success: true,
        data: {
      userId: "user-123",
      recommendations: [;
            {
      type: "diet",
      suggestion: '建议增加蔬菜摄入量',priority: 'high';
            },{
      type: "exercise",
      suggestion: '每日步行30分钟',priority: 'medium';
            };
          ];
        },timestamp: new Date(),requestId: 'lifestyle-request-1';
      };
      (agentApiService.soerLifestyleManagement as jest.Mock).mockResolvedValue()
        mockLifestyleResponse
      );
      const lifestyleRequest = {
      userId: "user-123",
      dataType: 'manual' as const,data: {dailySteps: 5000,sleepHours: 7,waterIntake: 1.5;
        },timestamp: Date.now();
      };
      const response = await agentApiService.soerLifestyleManagement(lifestyleRequest);
      expect(agentApiService.soerLifestyleManagement).toHaveBeenCalledWith(lifestyleRequest);
      expect(response.success).toBe(true);
      expect((response.data as any).recommendations).toHaveLength(2);
    });
  });
  describe('智能体监控组件集成测试', () => {
    it('应该正确显示所有智能体状态', async () => {
      renderWithProvider(<AgentMonitor />);
      // 等待组件加载
      await waitFor(() => {
        expect(screen.getByText('智能体监控')).toBeTruthy();
      });
      // 检查智能体状态显示
      expect(screen.getByText('小艾')).toBeTruthy();
      expect(screen.getByText('小克')).toBeTruthy();
      expect(screen.getByText('老克')).toBeTruthy();
      expect(screen.getByText('索儿')).toBeTruthy();
      // 检查状态指示器
      const statusIndicators = screen.getAllByTestId(/agent-status-/);
      expect(statusIndicators).toHaveLength(4);
    });
    it('应该支持手动刷新功能', async () => {
      renderWithProvider(<AgentMonitor />);
      await waitFor(() => {
        expect(screen.getByText('智能体监控')).toBeTruthy();
      });
      // 查找并点击刷新按钮
      const refreshButton = screen.getByTestId('refresh-button');
      fireEvent.press(refreshButton);
      // 验证API调用
      await waitFor(() => {
        expect(agentApiService.getAgentStatus).toHaveBeenCalledTimes(4); // 初始加载 + 手动刷新
      });
    });
  });
  describe('错误处理集成测试', () => {
    it('应该正确处理API错误', async () => {
      const mockErrorResponse = {success: false,error: {
      code: "NETWORK_ERROR",
      message: '网络连接失败';
        },timestamp: new Date(),requestId: 'error-request-1';
      };
      (agentApiService.xiaoaiChat as jest.Mock).mockResolvedValue(mockErrorResponse);
      const chatRequest = {
      message: "测试消息",
      messageType: MessageType.TEXT,userId: 'user-123',sessionId: 'session-456';
      };
      const response = await agentApiService.xiaoaiChat(chatRequest);
      expect(response.success).toBe(false);
      expect(response.error?.code).toBe('NETWORK_ERROR');
      expect(response.error?.message).toBe('网络连接失败');
    });
    it('应该正确处理超时错误', async () => {
      (agentApiService.getAgentStatus as jest.Mock).mockRejectedValue(new Error('Request timeout'));
      try {
        await agentApiService.getAgentStatus(AgentType.XIAOAI);
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toBe('Request timeout');
      }
    });
  });
  describe('性能测试', () => {
    it('API响应时间应该在合理范围内', async () => {
      const startTime = Date.now();
      await agentApiService.getAgentStatus(AgentType.XIAOAI);
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      // API响应时间应该小于1秒
      expect(responseTime).toBeLessThan(1000);
    });
    it('并发请求应该正常处理', async () => {
      const requests = [;
        agentApiService.getAgentStatus(AgentType.XIAOAI),agentApiService.getAgentStatus(AgentType.XIAOKE),agentApiService.getAgentStatus(AgentType.LAOKE),agentApiService.getAgentStatus(AgentType.SOER);
      ];
      const responses = await Promise.all(requests);
      responses.forEach(response => {
        expect(response.success).toBe(true);
      });
    });
  });
});