import { Request, Response, NextFunction } from 'express';
import { authenticate, authenticateAgent } from '../../../src/middlewares/auth';
import { loadConfig } from '../../../src/utils/config-loader';
import { AppError, ErrorCode } from '../../../src/utils/error-handler';

// 模拟配置加载器
jest.mock('../../../src/utils/config-loader');
const mockLoadConfig = loadConfig as jest.MockedFunction<typeof loadConfig>;

// 模拟logger避免测试输出过多日志
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

describe('认证中间件', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: jest.Mock;
  let originalEnv: NodeJS.ProcessEnv;
  
  beforeEach(() => {
    // 保存原始环境变量
    originalEnv = { ...process.env };
    
    // 重置环境
    jest.clearAllMocks();
    
    // 创建模拟请求和响应对象
    mockRequest = {
      headers: {},
      ip: '127.0.0.1',
      path: '/test',
      method: 'GET'
    };
    
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis()
    };
    
    nextFunction = jest.fn();
    
    // 默认禁用认证
    mockLoadConfig.mockReturnValue({
      security: {
        enableApiAuthentication: false,
        enableAgentAuthentication: false
      }
    });
  });
  
  afterEach(() => {
    // 恢复原始环境变量
    process.env = originalEnv;
  });
  
  describe('API认证中间件', () => {
    it('如果认证被禁用，应直接通过', () => {
      authenticate(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith();
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(Error));
    });
    
    it('如果认证启用但缺少API密钥，应抛出未授权错误', () => {
      // 启用API认证
      mockLoadConfig.mockReturnValue({
        security: {
          enableApiAuthentication: true
        }
      });
      
      // 设置环境变量
      process.env.API_KEY = 'test-api-key';
      
      authenticate(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith(expect.any(AppError));
      const error = nextFunction.mock.calls[0][0] as AppError;
      expect(error.errorCode).toBe(ErrorCode.UNAUTHORIZED);
      expect(error.statusCode).toBe(401);
    });
    
    it('如果认证启用且提供了有效的API密钥，应通过', () => {
      // 启用API认证
      mockLoadConfig.mockReturnValue({
        security: {
          enableApiAuthentication: true
        }
      });
      
      // 设置API密钥
      process.env.API_KEY = 'test-api-key';
      mockRequest.headers = { 'x-api-key': 'test-api-key' };
      
      authenticate(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith();
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(Error));
    });
    
    it('如果认证启用但提供了无效的API密钥，应抛出未授权错误', () => {
      // 启用API认证
      mockLoadConfig.mockReturnValue({
        security: {
          enableApiAuthentication: true
        }
      });
      
      // 设置不同的API密钥
      process.env.API_KEY = 'correct-api-key';
      mockRequest.headers = { 'x-api-key': 'wrong-api-key' };
      
      authenticate(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith(expect.any(AppError));
      const error = nextFunction.mock.calls[0][0] as AppError;
      expect(error.errorCode).toBe(ErrorCode.UNAUTHORIZED);
      expect(error.statusCode).toBe(401);
    });
  });
  
  describe('代理认证中间件', () => {
    it('如果代理认证被禁用，应直接通过', () => {
      authenticateAgent(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith();
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(Error));
    });
    
    it('如果代理认证启用但缺少代理ID，应抛出未授权错误', () => {
      // 启用代理认证
      mockLoadConfig.mockReturnValue({
        security: {
          enableAgentAuthentication: true
        }
      });
      
      authenticateAgent(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith(expect.any(AppError));
      const error = nextFunction.mock.calls[0][0] as AppError;
      expect(error.errorCode).toBe(ErrorCode.UNAUTHORIZED);
      expect(error.statusCode).toBe(401);
      expect(error.message).toContain('缺少代理ID');
    });
    
    it('如果代理认证启用但提供了无效的代理密钥，应抛出未授权错误', () => {
      // 启用代理认证
      mockLoadConfig.mockReturnValue({
        security: {
          enableAgentAuthentication: true
        }
      });
      
      // 设置代理ID但密钥错误
      mockRequest.headers = { 
        'x-agent-id': 'test-agent',
        'x-agent-key': 'wrong-key'
      };
      
      // 设置环境变量 (代理ID会被转为大写)
      process.env.TEST_AGENT_KEY = 'correct-key';
      
      authenticateAgent(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalledWith(expect.any(AppError));
      const error = nextFunction.mock.calls[0][0] as AppError;
      expect(error.errorCode).toBe(ErrorCode.UNAUTHORIZED);
      expect(error.statusCode).toBe(401);
      expect(error.message).toContain('代理密钥无效');
    });
    
    it('如果代理认证启用且提供了有效的代理ID和密钥，应通过', () => {
      // 启用代理认证
      mockLoadConfig.mockReturnValue({
        security: {
          enableAgentAuthentication: true
        }
      });
      
      // 注意这里：我们需要使用一致的命名格式
      const agentId = 'test-agent';
      const agentKey = 'valid-key';
      const envVarName = `${agentId.toUpperCase()}_KEY`;
      
      // 设置代理ID和密钥
      mockRequest.headers = { 
        'x-agent-id': agentId,
        'x-agent-key': agentKey
      };
      
      // 设置环境变量，确保与代码中的格式完全匹配
      process.env[envVarName] = agentKey;
      
      authenticateAgent(mockRequest as Request, mockResponse as Response, nextFunction);
      
      // 验证next被调用，且没有传递错误
      expect(nextFunction).toHaveBeenCalled();
      expect(nextFunction.mock.calls[0].length).toBe(0); // 确保没有传递参数
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(Error));
    });
  });
}); 