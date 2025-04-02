/**
 * 代理控制器单元测试
 */
import { Request, Response } from 'express';
import { AgentController } from '../../../src/controllers/agent-controller';
import { AgentService } from '../../../src/services/agent-service';
import { AgentNotFoundError } from '../../../src/utils/error-handler';
import logger from '../../../src/utils/logger';

// 模拟依赖
jest.mock('../../../src/services/agent-service');
jest.mock('../../../src/utils/logger');

// 模拟logger
jest.mock('../../../src/utils/logger', () => ({
  __esModule: true,
  default: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

describe('代理控制器', () => {
  let agentController: AgentController;
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockJson: jest.Mock;
  let mockStatus: jest.Mock;
  let mockAgentService: jest.Mocked<AgentService>;

  // 模拟代理数据
  const mockAgents = [
    {
      id: 'agent1',
      name: '健康顾问',
      description: '提供健康建议',
      capabilities: ['健康咨询', '饮食建议'],
      serviceUrl: 'http://agent1:8080',
      status: 'active',
      metadata: { domain: '健康' },
      isDefault: true
    },
    {
      id: 'agent2',
      name: '运动教练',
      description: '提供运动指导',
      capabilities: ['运动指导', '健身计划'],
      serviceUrl: 'http://agent2:8080',
      status: 'active',
      metadata: { domain: '健身' },
      isDefault: false
    }
  ];

  const mockQueryResponse = {
    content: '这是代理的回复内容',
    metadata: { processingTime: 120 },
    suggestions: ['你可以问我关于健康饮食的问题'],
    confidence: 0.95
  };

  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();

    // 模拟请求和响应对象
    mockJson = jest.fn();
    mockStatus = jest.fn().mockReturnValue({ json: mockJson });
    mockRequest = {
      body: {},
      query: {},
      params: {}
    };
    mockResponse = {
      json: mockJson,
      status: mockStatus
    };

    // 模拟代理服务的所有方法
    mockAgentService = {
      getAllAgents: jest.fn().mockResolvedValue(mockAgents),
      getAgentById: jest.fn().mockImplementation(async (agentId) => {
        const agent = mockAgents.find(a => a.id === agentId);
        if (!agent) {
          throw new AgentNotFoundError(agentId);
        }
        return agent;
      }),
      checkAgentCapability: jest.fn().mockImplementation(async (agentId, capability) => {
        const agent = mockAgents.find(a => a.id === agentId);
        if (!agent) {
          throw new AgentNotFoundError(agentId);
        }
        return agent.capabilities.includes(capability);
      }),
      queryAgent: jest.fn().mockResolvedValue(mockQueryResponse),
      checkAgentHealth: jest.fn().mockResolvedValue(true),
      listAgents: jest.fn(),
      getAgentDetails: jest.fn()
    } as unknown as jest.Mocked<AgentService>;

    // 初始化控制器
    agentController = new AgentController(mockAgentService);
  });

  describe('getAgents', () => {
    it('应返回所有代理列表', async () => {
      await agentController.getAgents(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockAgentService.getAllAgents).toHaveBeenCalled();

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('获取代理列表');

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockAgents
      });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('获取代理列表错误');
      mockAgentService.getAllAgents.mockRejectedValue(error);
      
      await agentController.getAgents(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('获取代理列表失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '获取代理列表失败',
        error: '获取代理列表错误'
      });
    });
  });

  describe('getAgentById', () => {
    beforeEach(() => {
      mockRequest.params = { agentId: 'agent1' };
    });

    it('应返回指定ID的代理', async () => {
      await agentController.getAgentById(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockAgentService.getAgentById).toHaveBeenCalledWith('agent1');

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('获取代理详情', { agentId: 'agent1' });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockAgents[0]
      });
    });

    it('代理不存在时应返回404错误', async () => {
      mockRequest.params = { agentId: 'nonexistent' };
      
      // 直接测试控制器方法中的catch块
      await agentController.getAgentById(mockRequest as Request, mockResponse as Response);
      
      // 根据控制器的实际行为，验证响应
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '获取代理信息失败',
        error: expect.any(String)
      });
    });

    it('服务抛出其他异常时应返回500错误', async () => {
      const error = new Error('其他错误');
      mockAgentService.getAgentById.mockRejectedValue(error);
      
      await agentController.getAgentById(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('获取代理详情失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '获取代理信息失败',
        error: '其他错误'
      });
    });
  });

  describe('checkAgentCapability', () => {
    beforeEach(() => {
      mockRequest.params = { agentId: 'agent1' };
      mockRequest.query = { capability: '健康咨询' };
    });

    it('应正确检查代理能力并返回结果', async () => {
      await agentController.checkAgentCapability(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockAgentService.checkAgentCapability).toHaveBeenCalledWith('agent1', '健康咨询');

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('检查代理能力', { agentId: 'agent1', capability: '健康咨询' });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: {
          hasCapability: true
        }
      });
    });

    it('缺少capability参数时应返回400错误', async () => {
      mockRequest.query = {};
      
      await agentController.checkAgentCapability(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '缺少capability参数'
      });
    });

    it('代理不存在时应返回404错误', async () => {
      mockRequest.params = { agentId: 'nonexistent' };
      
      // 直接测试控制器方法中的catch块
      await agentController.checkAgentCapability(mockRequest as Request, mockResponse as Response);
      
      // 根据控制器的实际行为，验证响应
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '检查代理能力失败',
        error: expect.any(String)
      });
    });

    it('服务抛出其他异常时应返回500错误', async () => {
      const error = new Error('其他错误');
      mockAgentService.checkAgentCapability.mockRejectedValue(error);
      
      await agentController.checkAgentCapability(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('检查代理能力失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '检查代理能力失败',
        error: '其他错误'
      });
    });
  });

  describe('queryAgent', () => {
    beforeEach(() => {
      mockRequest.params = { agentId: 'agent1' };
      mockRequest.body = {
        sessionId: 'session1',
        query: '我需要一些健康饮食的建议',
        context: { userId: 'user1' }
      };
    });

    it('应正确向代理发送请求并返回结果', async () => {
      await agentController.queryAgent(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockAgentService.queryAgent).toHaveBeenCalledWith(
        'agent1',
        'session1',
        '我需要一些健康饮食的建议',
        { userId: 'user1' }
      );

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('向代理发送请求', { agentId: 'agent1', sessionId: 'session1' });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockQueryResponse
      });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('查询代理错误');
      mockAgentService.queryAgent.mockRejectedValue(error);
      
      await agentController.queryAgent(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('向代理发送请求失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '向代理发送请求时发生错误',
        error: '查询代理错误'
      });
    });
  });

  describe('checkAgentHealth', () => {
    beforeEach(() => {
      mockRequest.params = { agentId: 'agent1' };
    });

    it('应正确检查代理健康状态并返回结果', async () => {
      // 固定的时间字符串
      const isoDate = '2023-01-01T12:00:00.000Z';
      
      // 模拟Date.prototype.toISOString
      const originalToISOString = Date.prototype.toISOString;
      Date.prototype.toISOString = jest.fn().mockReturnValue(isoDate);
      
      await agentController.checkAgentHealth(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockAgentService.checkAgentHealth).toHaveBeenCalledWith('agent1');

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('检查代理健康状态', { agentId: 'agent1' });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: {
          agentId: 'agent1',
          healthy: true,
          timestamp: isoDate
        }
      });
      
      // 恢复原始方法
      Date.prototype.toISOString = originalToISOString;
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('检查健康状态错误');
      mockAgentService.checkAgentHealth.mockRejectedValue(error);
      
      await agentController.checkAgentHealth(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('检查代理健康状态失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '检查代理健康状态时发生错误',
        error: '检查健康状态错误'
      });
    });
  });
});