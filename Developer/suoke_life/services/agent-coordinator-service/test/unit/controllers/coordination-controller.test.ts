/**
 * 协调控制器单元测试
 */
import { Request, Response } from 'express';
import { CoordinationController } from '../../../src/controllers/coordination-controller';
import { CoordinationService } from '../../../src/services/coordination-service';
import logger from '../../../src/utils/logger';

// 模拟依赖
jest.mock('../../../src/services/coordination-service');
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

describe('协调控制器', () => {
  let coordinationController: CoordinationController;
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockJson: jest.Mock;
  let mockStatus: jest.Mock;
  let mockCoordinationService: jest.Mocked<CoordinationService>;

  // 模拟响应数据
  const mockRouteResponse = {
    agentId: 'agent1',
    sessionId: 'session1',
    content: '这是代理的回复内容',
    metadata: { processingTime: 120 }
  };

  const mockHandoffResponse = {
    success: true,
    message: '成功将会话从 agent1 交接给 agent2',
    handoffId: 'handoff-uuid-1'
  };

  const mockAnalysisResponse = {
    recommendedAgent: 'agent1',
    confidence: 0.85,
    matchedKeywords: ['健康', '饮食'],
    domainClassifications: [
      { domain: '健康', confidence: 0.9, subdomains: ['饮食', '运动'] }
    ],
    alternativeAgents: [
      { agentId: 'agent2', confidence: 0.6 }
    ]
  };

  const mockCapabilitiesResponse = {
    capabilities: ['健康咨询', '饮食建议', '运动指导'],
    agentCapabilities: {
      'agent1': ['健康咨询', '饮食建议'],
      'agent2': ['运动指导']
    }
  };

  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();

    // 模拟请求和响应对象
    mockJson = jest.fn();
    mockStatus = jest.fn().mockReturnValue({ json: mockJson });
    mockRequest = {
      body: {},
      query: {}
    };
    mockResponse = {
      json: mockJson,
      status: mockStatus
    };

    // 模拟协调服务的所有方法
    mockCoordinationService = {
      routeRequest: jest.fn().mockResolvedValue(mockRouteResponse),
      handoffSession: jest.fn().mockResolvedValue(mockHandoffResponse),
      analyzeQuery: jest.fn().mockResolvedValue(mockAnalysisResponse),
      getSystemCapabilities: jest.fn().mockResolvedValue(mockCapabilitiesResponse)
    } as unknown as jest.Mocked<CoordinationService>;

    // 替换CoordinationService的构造函数，返回我们的模拟对象
    (CoordinationService as jest.Mock).mockImplementation(() => mockCoordinationService);

    // 初始化控制器
    coordinationController = new CoordinationController();
  });

  describe('routeRequest', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.body = {
        sessionId: 'session1',
        query: '我需要一些健康饮食的建议',
        context: { userId: 'user1' }
      };
    });

    it('应正确路由请求并返回结果', async () => {
      await coordinationController.routeRequest(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockCoordinationService.routeRequest).toHaveBeenCalledWith(
        'session1',
        '我需要一些健康饮食的建议',
        { userId: 'user1' }
      );

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('智能路由请求', { sessionId: 'session1' });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockRouteResponse
      });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('路由请求错误');
      mockCoordinationService.routeRequest.mockRejectedValue(error);
      
      await coordinationController.routeRequest(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('智能路由请求失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '路由请求时发生错误',
        error: '路由请求错误'
      });
    });
  });

  describe('handoffSession', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.body = {
        sessionId: 'session1',
        fromAgentId: 'agent1',
        toAgentId: 'agent2',
        reason: '用户需要运动指导',
        context: { userId: 'user1' }
      };
    });

    it('应正确交接会话并返回结果', async () => {
      await coordinationController.handoffSession(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockCoordinationService.handoffSession).toHaveBeenCalledWith(
        'session1',
        'agent1',
        'agent2',
        '用户需要运动指导',
        { userId: 'user1' }
      );

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('代理交接会话', {
        sessionId: 'session1',
        fromAgentId: 'agent1',
        toAgentId: 'agent2',
        reason: '用户需要运动指导'
      });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockHandoffResponse
      });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('交接会话错误');
      mockCoordinationService.handoffSession.mockRejectedValue(error);
      
      await coordinationController.handoffSession(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('代理交接会话失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '交接会话时发生错误',
        error: '交接会话错误'
      });
    });
  });

  describe('analyzeQuery', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.body = {
        query: '我需要一些健康饮食的建议',
        context: { userId: 'user1' }
      };
    });

    it('应正确分析查询并返回结果', async () => {
      await coordinationController.analyzeQuery(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockCoordinationService.analyzeQuery).toHaveBeenCalledWith(
        '我需要一些健康饮食的建议',
        { userId: 'user1' }
      );

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('分析用户查询', {
        queryLength: '我需要一些健康饮食的建议'.length
      });

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockAnalysisResponse
      });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('分析查询错误');
      mockCoordinationService.analyzeQuery.mockRejectedValue(error);
      
      await coordinationController.analyzeQuery(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('分析用户查询失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '分析查询时发生错误',
        error: '分析查询错误'
      });
    });
  });

  describe('getSystemCapabilities', () => {
    it('应正确获取系统能力并返回结果', async () => {
      await coordinationController.getSystemCapabilities(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockCoordinationService.getSystemCapabilities).toHaveBeenCalled();

      // 验证日志
      expect(logger.info).toHaveBeenCalledWith('获取系统总体能力');

      // 验证响应
      expect(mockStatus).toHaveBeenCalledWith(200);
      expect(mockJson).toHaveBeenCalledWith({
        success: true,
        data: mockCapabilitiesResponse
      });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('获取系统能力错误');
      mockCoordinationService.getSystemCapabilities.mockRejectedValue(error);
      
      await coordinationController.getSystemCapabilities(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('获取系统总体能力失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
        message: '获取系统能力时发生错误',
        error: '获取系统能力错误'
      });
    });
  });
});