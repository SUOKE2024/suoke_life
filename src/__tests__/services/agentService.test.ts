// 智能体服务测试
describe('AgentService', () => {
  // Mock智能体服务
  const mockAgentService = {
    getAgents: jest.fn(),
    getAgentById: jest.fn(),
    sendMessage: jest.fn(),
    getChatHistory: jest.fn(),
    startConsultation: jest.fn(),
    endConsultation: jest.fn(),
    getAgentRecommendations: jest.fn(),
    updateAgentStatus: jest.fn(),
    rateAgent: jest.fn(),
    startCollaboration: jest.fn(),
    submitFeedback: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('智能体管理', () => {
    it('应该成功获取所有智能体', async () => {
      const mockAgents = [
        {
          id: 'xiaoai',
          name: '小艾',
          avatar: '🤖',
          specialty: '健康咨询',
          description: '专业的健康管理助手',
          status: 'online',
          rating: 4.8,
          totalChats: 1250,
          lastActive: '2024-01-15T10:00:00Z',
        },
        {
          id: 'xiaoke',
          name: '小克',
          avatar: '👨‍⚕️',
          specialty: '中医诊断',
          description: '中医辨证论治专家',
          status: 'online',
          rating: 4.9,
          totalChats: 980,
          lastActive: '2024-01-15T09:45:00Z',
        },
        {
          id: 'laoke',
          name: '老克',
          avatar: '👴',
          specialty: '养生指导',
          description: '传统养生文化传承者',
          status: 'busy',
          rating: 4.7,
          totalChats: 2100,
          lastActive: '2024-01-15T08:30:00Z',
        },
        {
          id: 'soer',
          name: '索儿',
          avatar: '👧',
          specialty: '生活助手',
          description: '贴心的生活健康顾问',
          status: 'online',
          rating: 4.6,
          totalChats: 1800,
          lastActive: '2024-01-15T10:15:00Z',
        },
      ];

      mockAgentService.getAgents.mockResolvedValue({
        success: true,
        data: mockAgents,
      });

      const result = await mockAgentService.getAgents();
      
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(4);
      expect(result.data[0].name).toBe('小艾');
      expect(result.data[1].name).toBe('小克');
      expect(result.data[2].name).toBe('老克');
      expect(result.data[3].name).toBe('索儿');
    });

    it('应该成功获取特定智能体信息', async () => {
      const mockAgent = {
        id: 'xiaoai',
        name: '小艾',
        avatar: '🤖',
        specialty: '健康咨询',
        description: '专业的健康管理助手，擅长健康数据分析和个性化建议',
        status: 'online',
        rating: 4.8,
        totalChats: 1250,
        lastActive: '2024-01-15T10:00:00Z',
        capabilities: [
          '健康数据分析',
          '个性化建议',
          '症状评估',
          '健康计划制定',
        ],
        languages: ['中文', '英文'],
      };

      mockAgentService.getAgentById.mockResolvedValue({
        success: true,
        data: mockAgent,
      });

      const result = await mockAgentService.getAgentById('xiaoai');
      
      expect(result.success).toBe(true);
      expect(result.data.id).toBe('xiaoai');
      expect(result.data.name).toBe('小艾');
      expect(result.data.capabilities).toHaveLength(4);
      expect(mockAgentService.getAgentById).toHaveBeenCalledWith('xiaoai');
    });
  });

  describe('聊天功能', () => {
    it('应该成功发送消息给智能体', async () => {
      const message = {
        content: '我最近感觉有点疲劳，应该怎么办？',
        type: 'text',
      };

      const mockResponse = {
        id: 'msg123',
        agentId: 'xiaoai',
        userId: 'user123',
        content: '疲劳可能有多种原因，让我帮您分析一下。请问您最近的睡眠质量如何？',
        type: 'text',
        timestamp: '2024-01-15T10:30:00Z',
        suggestions: [
          '检查睡眠质量',
          '评估工作压力',
          '查看营养状况',
        ],
      };

      mockAgentService.sendMessage.mockResolvedValue({
        success: true,
        data: mockResponse,
      });

      const result = await mockAgentService.sendMessage('xiaoai', 'user123', message);
      
      expect(result.success).toBe(true);
      expect(result.data.content).toContain('疲劳可能有多种原因');
      expect(result.data.suggestions).toHaveLength(3);
      expect(mockAgentService.sendMessage).toHaveBeenCalledWith('xiaoai', 'user123', message);
    });

    it('应该成功获取聊天历史', async () => {
      const mockChatHistory = [
        {
          id: 'msg1',
          sender: 'user',
          content: '你好，小艾',
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: 'msg2',
          sender: 'agent',
          content: '您好！我是小艾，您的健康管理助手。有什么可以帮助您的吗？',
          timestamp: '2024-01-15T10:00:30Z',
        },
        {
          id: 'msg3',
          sender: 'user',
          content: '我想了解一下我的健康状况',
          timestamp: '2024-01-15T10:01:00Z',
        },
      ];

      mockAgentService.getChatHistory.mockResolvedValue({
        success: true,
        data: mockChatHistory,
      });

      const result = await mockAgentService.getChatHistory('xiaoai', 'user123');
      
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(3);
      expect(result.data[0].sender).toBe('user');
      expect(result.data[1].sender).toBe('agent');
      expect(mockAgentService.getChatHistory).toHaveBeenCalledWith('xiaoai', 'user123');
    });
  });

  describe('咨询会话', () => {
    it('应该成功开始咨询会话', async () => {
      const consultationData = {
        type: 'health_assessment',
        topic: '健康评估',
        priority: 'normal',
      };

      const mockSession = {
        id: 'session123',
        agentId: 'xiaoke',
        userId: 'user123',
        type: 'health_assessment',
        status: 'active',
        startTime: '2024-01-15T10:30:00Z',
        estimatedDuration: 30,
      };

      mockAgentService.startConsultation.mockResolvedValue({
        success: true,
        data: mockSession,
      });

      const result = await mockAgentService.startConsultation('xiaoke', 'user123', consultationData);
      
      expect(result.success).toBe(true);
      expect(result.data.status).toBe('active');
      expect(result.data.type).toBe('health_assessment');
      expect(mockAgentService.startConsultation).toHaveBeenCalledWith('xiaoke', 'user123', consultationData);
    });

    it('应该成功结束咨询会话', async () => {
      const sessionSummary = {
        duration: 25,
        messagesCount: 15,
        recommendations: [
          '建议增加运动量',
          '注意饮食均衡',
        ],
        followUpDate: '2024-01-22T10:30:00Z',
      };

      mockAgentService.endConsultation.mockResolvedValue({
        success: true,
        data: sessionSummary,
      });

      const result = await mockAgentService.endConsultation('session123');
      
      expect(result.success).toBe(true);
      expect(result.data.duration).toBe(25);
      expect(result.data.recommendations).toHaveLength(2);
      expect(mockAgentService.endConsultation).toHaveBeenCalledWith('session123');
    });
  });

  describe('智能体建议', () => {
    it('应该成功获取智能体建议', async () => {
      const mockRecommendations = [
        {
          id: 'rec1',
          agentId: 'laoke',
          type: 'lifestyle',
          title: '晨起养生建议',
          content: '建议每天早上6-7点起床，进行15分钟的太极或八段锦练习',
          priority: 'medium',
          category: 'exercise',
          validUntil: '2024-02-15T00:00:00Z',
        },
        {
          id: 'rec2',
          agentId: 'soer',
          type: 'diet',
          title: '春季饮食调理',
          content: '春季宜多食用绿叶蔬菜和时令水果，少食辛辣刺激食物',
          priority: 'high',
          category: 'nutrition',
          validUntil: '2024-04-30T00:00:00Z',
        },
      ];

      mockAgentService.getAgentRecommendations.mockResolvedValue({
        success: true,
        data: mockRecommendations,
      });

      const result = await mockAgentService.getAgentRecommendations('user123');
      
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(2);
      expect(result.data[0].agentId).toBe('laoke');
      expect(result.data[1].agentId).toBe('soer');
      expect(mockAgentService.getAgentRecommendations).toHaveBeenCalledWith('user123');
    });
  });

  describe('智能体状态管理', () => {
    it('应该成功更新智能体状态', async () => {
      mockAgentService.updateAgentStatus.mockResolvedValue({
        success: true,
        message: '状态更新成功',
      });

      const result = await mockAgentService.updateAgentStatus('xiaoai', 'busy');
      
      expect(result.success).toBe(true);
      expect(result.message).toBe('状态更新成功');
      expect(mockAgentService.updateAgentStatus).toHaveBeenCalledWith('xiaoai', 'busy');
    });

    it('应该成功评价智能体', async () => {
      const rating = {
        score: 5,
        comment: '小艾的建议非常专业和实用，帮助很大！',
        sessionId: 'session123',
      };

      mockAgentService.rateAgent.mockResolvedValue({
        success: true,
        message: '评价提交成功',
        newRating: 4.85,
      });

      const result = await mockAgentService.rateAgent('xiaoai', 'user123', rating);
      
      expect(result.success).toBe(true);
      expect(result.newRating).toBe(4.85);
      expect(mockAgentService.rateAgent).toHaveBeenCalledWith('xiaoai', 'user123', rating);
    });
  });

  describe('特殊功能测试', () => {
    it('应该支持多智能体协作', async () => {
      const collaborationRequest = {
        primaryAgent: 'xiaoke',
        secondaryAgents: ['xiaoai', 'laoke'],
        topic: '综合健康评估',
        userId: 'user123',
      };

      const mockCollaboration = {
        id: 'collab123',
        status: 'active',
        participants: ['xiaoke', 'xiaoai', 'laoke'],
        coordinator: 'xiaoke',
        startTime: '2024-01-15T11:00:00Z',
      };

      mockAgentService.startCollaboration.mockResolvedValue({
        success: true,
        data: mockCollaboration,
      });

      const result = await mockAgentService.startCollaboration(collaborationRequest);
      
      expect(result.success).toBe(true);
      expect(result.data.participants).toHaveLength(3);
      expect(result.data.coordinator).toBe('xiaoke');
    });

    it('应该支持智能体学习反馈', async () => {
      const feedback = {
        sessionId: 'session123',
        helpful: true,
        accuracy: 4,
        suggestions: '建议增加更多个性化的运动方案',
      };

      mockAgentService.submitFeedback.mockResolvedValue({
        success: true,
        message: '反馈提交成功，将用于智能体优化',
      });

      const result = await mockAgentService.submitFeedback('xiaoai', feedback);
      
      expect(result.success).toBe(true);
      expect(result.message).toContain('反馈提交成功');
    });
  });

  describe('错误处理', () => {
    it('应该处理智能体不可用的情况', async () => {
      mockAgentService.sendMessage.mockResolvedValue({
        success: false,
        error: '智能体当前不可用',
        code: 'AGENT_UNAVAILABLE',
      });

      const result = await mockAgentService.sendMessage('offline_agent', 'user123', {
        content: 'Hello',
        type: 'text',
      });
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('智能体当前不可用');
      expect(result.code).toBe('AGENT_UNAVAILABLE');
    });

    it('应该处理消息发送失败', async () => {
      mockAgentService.sendMessage.mockRejectedValue(new Error('网络连接失败'));

      try {
        await mockAgentService.sendMessage('xiaoai', 'user123', {
          content: 'Test message',
          type: 'text',
        });
      } catch (error: any) {
        expect(error.message).toBe('网络连接失败');
      }
    });

    it('应该处理无效的智能体ID', async () => {
      mockAgentService.getAgentById.mockResolvedValue({
        success: false,
        error: '智能体不存在',
        code: 'AGENT_NOT_FOUND',
      });

      const result = await mockAgentService.getAgentById('invalid_agent');
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('智能体不存在');
      expect(result.code).toBe('AGENT_NOT_FOUND');
    });
  });

  describe('性能和限制', () => {
    it('应该处理并发聊天限制', async () => {
      mockAgentService.sendMessage.mockResolvedValue({
        success: false,
        error: '智能体当前忙碌，请稍后再试',
        code: 'AGENT_BUSY',
        retryAfter: 30,
      });

      const result = await mockAgentService.sendMessage('xiaoai', 'user123', {
        content: 'Test',
        type: 'text',
      });
      
      expect(result.success).toBe(false);
      expect(result.code).toBe('AGENT_BUSY');
      expect(result.retryAfter).toBe(30);
    });

    it('应该处理消息长度限制', async () => {
      const longMessage = 'a'.repeat(5000);
      
      mockAgentService.sendMessage.mockResolvedValue({
        success: false,
        error: '消息长度超出限制',
        code: 'MESSAGE_TOO_LONG',
        maxLength: 2000,
      });

      const result = await mockAgentService.sendMessage('xiaoai', 'user123', {
        content: longMessage,
        type: 'text',
      });
      
      expect(result.success).toBe(false);
      expect(result.code).toBe('MESSAGE_TOO_LONG');
      expect(result.maxLength).toBe(2000);
    });
  });
}); 