import { jest } from '@jest/globals';
import axios from 'axios';
import { AgentService } from '../../../src/services/agent-service';
import { AgentNotFoundError } from '../../../src/utils/error-handler';
import { Agent, AgentStatus } from '../../../src/models/agent';

// 模拟axios
jest.mock('axios');

// 模拟config-loader
jest.mock('../../../src/utils/config-loader', () => ({
  loadConfig: jest.fn().mockReturnValue({
    agents: [
      {
        id: 'agent-123',
        name: '健康代理',
        capabilities: ['health', 'nutrition'],
        description: '健康咨询代理',
        serviceUrl: 'http://health-agent:8080',
        status: 'active',
        metadata: { specialization: '全科' },
        isDefault: true
      },
      {
        id: 'agent-456',
        name: '通用代理',
        capabilities: ['general', 'chat'],
        description: '通用对话代理',
        serviceUrl: 'http://general-agent:8080',
        status: 'active',
        metadata: { language: 'zh-CN' }
      }
    ]
  })
}));

// 模拟logger避免测试输出过多日志
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

describe('代理服务', () => {
  let agentService: AgentService;
  const mockedAxios = axios as jest.Mocked<typeof axios>;
  
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 创建代理服务实例
    agentService = new AgentService();
  });
  
  describe('listAgents', () => {
    it('应返回所有代理的列表', async () => {
      const result = await agentService.listAgents();
      
      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({
        id: 'agent-123',
        name: '健康代理',
        capabilities: ['health', 'nutrition'],
        description: '健康咨询代理',
        serviceUrl: 'http://health-agent:8080',
        status: 'active',
        metadata: { specialization: '全科' },
        isDefault: true
      });
      expect(result[1]).toEqual({
        id: 'agent-456',
        name: '通用代理',
        capabilities: ['general', 'chat'],
        description: '通用对话代理',
        serviceUrl: 'http://general-agent:8080',
        status: 'active',
        metadata: { language: 'zh-CN' }
      });
    });
  });
  
  describe('getAllAgents', () => {
    it('应通过调用listAgents返回所有代理', async () => {
      const spy = jest.spyOn(agentService, 'listAgents');
      
      const result = await agentService.getAllAgents();
      
      expect(spy).toHaveBeenCalledTimes(1);
      expect(result).toHaveLength(2);
    });
  });
  
  describe('getAgentDetails', () => {
    it('应返回指定ID的代理详情', async () => {
      const result = await agentService.getAgentDetails('agent-123');
      
      expect(result).toEqual({
        id: 'agent-123',
        name: '健康代理',
        capabilities: ['health', 'nutrition'],
        description: '健康咨询代理',
        serviceUrl: 'http://health-agent:8080',
        status: 'active',
        metadata: { specialization: '全科' },
        isDefault: true
      });
    });
    
    it('当代理不存在时应返回null', async () => {
      const result = await agentService.getAgentDetails('non-existent');
      
      expect(result).toBeNull();
    });
  });
  
  describe('getAgentById', () => {
    it('应返回指定ID的代理', async () => {
      const result = await agentService.getAgentById('agent-123');
      
      expect(result).toEqual({
        id: 'agent-123',
        name: '健康代理',
        capabilities: ['health', 'nutrition'],
        description: '健康咨询代理',
        serviceUrl: 'http://health-agent:8080',
        status: 'active',
        metadata: { specialization: '全科' },
        isDefault: true
      });
    });
    
    it('当代理不存在时应抛出错误', async () => {
      await expect(agentService.getAgentById('non-existent')).rejects.toThrow('未找到代理');
    });
  });
  
  describe('checkAgentCapability', () => {
    it('当代理具有该能力时应返回true', async () => {
      const result = await agentService.checkAgentCapability('agent-123', 'health');
      
      expect(result).toBe(true);
    });
    
    it('当代理不具有该能力时应返回false', async () => {
      const result = await agentService.checkAgentCapability('agent-123', 'unknown-capability');
      
      expect(result).toBe(false);
    });
    
    it('当代理不存在时应抛出错误', async () => {
      await expect(agentService.checkAgentCapability('non-existent', 'health')).rejects.toThrow('未找到代理');
    });
  });
  
  describe('queryAgent', () => {
    it('应成功查询代理并返回响应', async () => {
      // 模拟axios成功响应
      mockedAxios.post.mockResolvedValue({
        data: {
          data: {
            content: '这是代理的回复',
            suggestions: ['你可以问更多健康问题'],
            confidence: 0.9
          }
        }
      });
      
      const result = await agentService.queryAgent(
        'agent-123',
        'session-123',
        '我该如何保持健康？',
        { userId: 'user-123' }
      );
      
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://health-agent:8080/api/query',
        {
          sessionId: 'session-123',
          userId: 'user-123',
          message: '我该如何保持健康？',
          context: { userId: 'user-123' },
          metadata: {}
        },
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'X-Agent-Coordinator': 'true'
          }),
          timeout: 30000
        })
      );
      
      expect(result).toEqual({
        content: '这是代理的回复',
        suggestions: ['你可以问更多健康问题'],
        confidence: 0.9
      });
    });
    
    it('当代理不存在时应返回错误响应', async () => {
      const result = await agentService.queryAgent(
        'non-existent',
        'session-123',
        '我该如何保持健康？'
      );
      
      expect(result).toEqual({
        content: '很抱歉，连接non-existent代理服务时出现问题，请稍后再试。',
        metadata: {
          error: '未找到代理: non-existent'
        }
      });
    });
    
    it('当请求失败时应返回错误响应', async () => {
      // 模拟axios失败响应
      mockedAxios.post.mockRejectedValue(new Error('网络错误'));
      
      const result = await agentService.queryAgent(
        'agent-123',
        'session-123',
        '我该如何保持健康？'
      );
      
      expect(result).toEqual({
        content: '很抱歉，连接agent-123代理服务时出现问题，请稍后再试。',
        metadata: {
          error: '网络错误'
        }
      });
    });
  });
  
  describe('checkAgentHealth', () => {
    it('当代理健康时应返回true', async () => {
      // 模拟axios成功响应
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: { status: 'healthy' }
      });
      
      const result = await agentService.checkAgentHealth('agent-123');
      
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://health-agent:8080/health',
        expect.objectContaining({
          timeout: 5000
        })
      );
      
      expect(result).toBe(true);
    });
    
    it('当代理不存在时应返回false', async () => {
      const result = await agentService.checkAgentHealth('non-existent');
      
      expect(result).toBe(false);
    });
    
    it('当健康检查请求失败时应返回false', async () => {
      // 模拟axios失败响应
      mockedAxios.get.mockRejectedValue(new Error('网络错误'));
      
      const result = await agentService.checkAgentHealth('agent-123');
      
      expect(result).toBe(false);
    });
  });
}); 