/**
 * 认证中间件单元测试
 */
import { Request, Response, NextFunction } from 'express';
import { authenticateApiKey, authenticateAgent } from '../../../src/middlewares/auth-middleware';

// 模拟config-loader
jest.mock('../../../src/utils/config-loader', () => ({
  loadConfig: jest.fn().mockReturnValue({
    security: {
      enableApiAuthentication: true,
      enableAgentAuthentication: true
    }
  })
}));

// 模拟winston logger
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
  __esModule: true,
  default: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  }
}));

// 保存原始环境变量
const originalEnv = process.env;

describe('认证中间件', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  
  beforeEach(() => {
    // 重置环境变量
    process.env = { ...originalEnv };
    process.env.API_KEY = 'test-api-key';
    process.env.AGENT_SECRET_KEY = 'test-agent-key';
    
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 创建模拟请求
    mockRequest = {
      headers: {},
      query: {},
      ip: '127.0.0.1',
      path: '/api/test'
    };
    
    // 创建模拟响应
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    
    // 创建模拟next函数
    mockNext = jest.fn();
  });
  
  afterAll(() => {
    // 恢复原始环境变量
    process.env = originalEnv;
  });
  
  describe('authenticateApiKey', () => {
    it('应该在提供有效API密钥时调用next', () => {
      // 设置请求中的API密钥
      mockRequest.headers = { 'x-api-key': 'test-api-key' };
      
      // 调用中间件
      authenticateApiKey(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证next被调用
      expect(mockNext).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
    
    it('应该接受作为查询参数传递的API密钥', () => {
      // 设置请求中的API密钥
      mockRequest.query = { api_key: 'test-api-key' };
      
      // 调用中间件
      authenticateApiKey(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证next被调用
      expect(mockNext).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
    
    it('应该在API密钥无效时返回401', () => {
      // 设置请求中的无效API密钥
      mockRequest.headers = { 'x-api-key': 'invalid-key' };
      
      // 调用中间件
      authenticateApiKey(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证响应
      expect(mockNext).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '未授权访问',
      });
    });
    
    it('应该在未提供API密钥时返回401', () => {
      // 调用中间件（没有设置API密钥）
      authenticateApiKey(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证响应
      expect(mockNext).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '未授权访问',
      });
    });
    
    it('应该在禁用API认证时跳过验证', () => {
      // 覆盖配置模拟，禁用API认证
      require('../../../src/utils/config-loader').loadConfig.mockReturnValueOnce({
        security: {
          enableApiAuthentication: false
        }
      });
      
      // 调用中间件（没有设置API密钥）
      authenticateApiKey(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证next被调用
      expect(mockNext).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
  });
  
  describe('authenticateAgent', () => {
    it('应该在提供有效代理密钥时调用next', () => {
      // 设置请求中的代理密钥和ID
      mockRequest.headers = {
        'x-agent-key': 'test-agent-key',
        'x-agent-id': 'agent-123'
      };
      
      // 调用中间件
      authenticateAgent(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证next被调用
      expect(mockNext).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
    
    it('应该在代理密钥无效时返回401', () => {
      // 设置请求中的无效代理密钥
      mockRequest.headers = {
        'x-agent-key': 'invalid-key',
        'x-agent-id': 'agent-123'
      };
      
      // 调用中间件
      authenticateAgent(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证响应
      expect(mockNext).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '未授权代理访问',
      });
    });
    
    it('应该在未提供代理ID时返回401', () => {
      // 设置请求中只有代理密钥但没有ID
      mockRequest.headers = {
        'x-agent-key': 'test-agent-key'
      };
      
      // 调用中间件
      authenticateAgent(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证响应
      expect(mockNext).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '未授权代理访问',
      });
    });
    
    it('应该在未提供代理密钥时返回401', () => {
      // 设置请求中只有代理ID但没有密钥
      mockRequest.headers = {
        'x-agent-id': 'agent-123'
      };
      
      // 调用中间件
      authenticateAgent(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证响应
      expect(mockNext).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '未授权代理访问',
      });
    });
    
    it('应该在禁用代理认证时跳过验证', () => {
      // 覆盖配置模拟，禁用代理认证
      require('../../../src/utils/config-loader').loadConfig.mockReturnValueOnce({
        security: {
          enableAgentAuthentication: false
        }
      });
      
      // 调用中间件（没有设置代理密钥）
      authenticateAgent(mockRequest as Request, mockResponse as Response, mockNext);
      
      // 验证next被调用
      expect(mockNext).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
  });
});