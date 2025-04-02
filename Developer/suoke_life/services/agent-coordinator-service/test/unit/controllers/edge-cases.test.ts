import { Request, Response } from 'express';
import { AgentController } from '../../../src/controllers/agent-controller';
import { AgentService } from '../../../src/services/agent-service';
import { KnowledgeController } from '../../../src/controllers/knowledge-controller';
import { KnowledgeService } from '../../../src/services/knowledge-service';
import { createMockResponse, mockResponseAsResponse } from '../../utils/mock-response';
import axios from 'axios';

// 模拟logger避免测试输出过多日志
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

// 模拟axios来模拟网络请求
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('边缘情况测试', () => {
  
  describe('网络错误处理', () => {
    it('处理网络超时', async () => {
      // 设置模拟实现
      const timeoutError = new Error('网络请求超时');
      timeoutError.name = 'TimeoutError';
      (timeoutError as any).code = 'ECONNABORTED';
      mockedAxios.get.mockRejectedValueOnce(timeoutError);
      
      // 创建AgentService实例并手动注入模拟的axios
      const agentService = new AgentService();
      const agentController = new AgentController(agentService);
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        params: { agentId: 'agent1' }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用会触发网络请求的方法
      await agentController.checkAgentHealth(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: expect.stringContaining('检查代理健康状态时发生错误')
      }));
    });
    
    it('处理网络连接失败', async () => {
      // 设置模拟实现
      const connectionError = new Error('无法连接到服务器');
      (connectionError as any).code = 'ECONNREFUSED';
      mockedAxios.post.mockRejectedValueOnce(connectionError);
      
      // 创建AgentService实例并手动注入模拟的axios
      const agentService = new AgentService();
      const agentController = new AgentController(agentService);
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        params: { agentId: 'agent1' },
        body: {
          sessionId: 'session123',
          query: '测试查询'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用会触发网络请求的方法
      await agentController.queryAgent(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: expect.stringContaining('向代理发送请求时发生错误')
      }));
    });
  });
  
  describe('服务器响应错误处理', () => {
    it('处理服务器500错误', async () => {
      // 设置模拟实现
      const serverError = new Error('内部服务器错误');
      (serverError as any).response = {
        status: 500,
        data: { error: '服务器内部错误' }
      };
      mockedAxios.get.mockRejectedValueOnce(serverError);
      
      // 创建KnowledgeService实例
      const knowledgeService = new KnowledgeService();
      const knowledgeController = new KnowledgeController();
      // 手动替换服务
      (knowledgeController as any).knowledgeService = knowledgeService;
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        query: {
          query: '健康知识搜索'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用会触发网络请求的方法
      await knowledgeController.searchKnowledge(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        error: expect.stringContaining('知识搜索失败')
      }));
    });
    
    it('处理服务器404错误', async () => {
      // 设置模拟实现
      const notFoundError = new Error('资源未找到');
      (notFoundError as any).response = {
        status: 404,
        data: { error: '请求的资源不存在' }
      };
      mockedAxios.get.mockRejectedValueOnce(notFoundError);
      
      // 创建KnowledgeService实例
      const knowledgeService = new KnowledgeService();
      const knowledgeController = new KnowledgeController();
      // 手动替换服务
      (knowledgeController as any).knowledgeService = knowledgeService;
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        query: {
          query: '罕见疾病知识'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用会触发网络请求的方法
      await knowledgeController.searchKnowledge(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        error: expect.stringContaining('知识搜索失败')
      }));
    });
  });
  
  describe('认证和权限错误处理', () => {
    it('处理未授权错误', async () => {
      // 设置模拟实现
      const unauthorizedError = new Error('未授权');
      (unauthorizedError as any).response = {
        status: 401,
        data: { error: '未提供有效的认证凭据' }
      };
      mockedAxios.post.mockRejectedValueOnce(unauthorizedError);
      
      // 创建AgentService实例并手动注入模拟的axios
      const agentService = new AgentService();
      const agentController = new AgentController(agentService);
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        params: { agentId: 'agent1' },
        body: {
          sessionId: 'session123',
          query: '测试查询'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用会触发网络请求的方法
      await agentController.queryAgent(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: expect.stringContaining('向代理发送请求时发生错误')
      }));
    });
    
    it('处理禁止访问错误', async () => {
      // 设置模拟实现
      const forbiddenError = new Error('禁止访问');
      (forbiddenError as any).response = {
        status: 403,
        data: { error: '没有权限访问该资源' }
      };
      mockedAxios.get.mockRejectedValueOnce(forbiddenError);
      
      // 创建KnowledgeService实例
      const knowledgeService = new KnowledgeService();
      const knowledgeController = new KnowledgeController();
      // 手动替换服务
      (knowledgeController as any).knowledgeService = knowledgeService;
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        query: {
          query: '敏感健康数据'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用会触发网络请求的方法
      await knowledgeController.searchKnowledge(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        error: expect.stringContaining('知识搜索失败')
      }));
    });
  });
  
  describe('异常数据处理', () => {
    it('处理格式错误的响应数据', async () => {
      // 设置模拟实现返回无效的JSON
      mockedAxios.get.mockResolvedValueOnce({
        data: 'Invalid JSON response',
        status: 200
      });
      
      // 创建KnowledgeService实例
      const knowledgeService = new KnowledgeService();
      // 修改searchKnowledge方法使其在解析响应时出错
      knowledgeService.searchKnowledge = jest.fn().mockImplementation(() => {
        throw new Error('无法解析响应数据');
      });
      
      const knowledgeController = new KnowledgeController();
      // 手动替换服务
      (knowledgeController as any).knowledgeService = knowledgeService;
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        query: {
          query: '健康数据'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用控制器方法
      await knowledgeController.searchKnowledge(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        error: expect.stringContaining('知识搜索失败')
      }));
    });
    
    it('处理空响应数据', async () => {
      // 设置模拟实现返回空响应
      mockedAxios.get.mockResolvedValueOnce({
        data: null,
        status: 200
      });
      
      // 创建KnowledgeService实例
      const knowledgeService = new KnowledgeService();
      // 修改searchKnowledge方法使其在处理空响应时出错
      knowledgeService.searchKnowledge = jest.fn().mockImplementation(() => {
        throw new Error('响应数据为空');
      });
      
      const knowledgeController = new KnowledgeController();
      // 手动替换服务
      (knowledgeController as any).knowledgeService = knowledgeService;
      
      // 创建模拟请求和响应对象
      const mockRequest = {
        query: {
          query: '健康数据'
        }
      } as unknown as Request;
      const mockResponse = createMockResponse();
      const res = mockResponseAsResponse(mockResponse);
      
      // 调用控制器方法
      await knowledgeController.searchKnowledge(mockRequest, res);
      
      // 验证错误处理
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
        error: expect.stringContaining('知识搜索失败')
      }));
    });
  });
}); 