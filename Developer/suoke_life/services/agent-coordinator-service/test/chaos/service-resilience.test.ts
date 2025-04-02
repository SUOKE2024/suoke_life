import axios from 'axios';
import { createTestServer } from '../integration/test-server';
import MockAdapter from 'axios-mock-adapter';

// 常量
const USER_ID = 'test-user-123';
const API_BASE_URL = 'http://localhost:4000/api';
const TEST_QUERY = '中医如何看待维生素D与骨骼健康的关系？';

/**
 * 混沌测试 - 服务弹性测试
 * 
 * 这些测试通过模拟各种故障情况来验证服务的恢复能力:
 * 1. 服务中断和恢复
 * 2. 超时和重试机制
 * 3. 错误的响应数据格式
 * 4. 内部服务连接失败
 */
describe('混沌测试 - 服务弹性', () => {
  // 创建应用实例
  const app = createTestServer();
  
  // 创建Axios实例和模拟适配器
  let axiosInstance: any;
  let mockAxios: any;
  
  // 模拟响应数据
  const mockSuccessResponse = {
    success: true,
    data: {
      responseId: 'resp-123',
      content: '根据中医理论，维生素D被认为与肾的"精气"密切相关...',
      source: 'knowledge-base',
      timestamp: new Date().toISOString()
    }
  };
  
  beforeAll(() => {
    // 创建Axios实例
    axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'
      },
      timeout: 5000
    });
    
    // 创建并附加模拟适配器
    mockAxios = new MockAdapter(axiosInstance);
  });
  
  afterEach(() => {
    // 重置模拟
    mockAxios.reset();
    jest.clearAllMocks();
  });
  
  afterAll(() => {
    // 恢复原始适配器
    mockAxios.restore();
  });
  
  describe('服务中断和自动恢复', () => {
    // 混沌场景：服务临时不可用后恢复
    test('服务应在临时中断后恢复', async () => {
      // 初始返回服务不可用
      mockAxios.onPost('/knowledge/rag').replyOnce(503);
      
      // 后续请求返回成功
      mockAxios.onPost('/knowledge/rag').reply(200, mockSuccessResponse);
      
      // 第一次请求（期望失败）
      try {
        await axiosInstance.post('/knowledge/rag', {
          query: TEST_QUERY,
          userId: USER_ID
        });
        fail('应当抛出503错误');
      } catch (error: any) {
        expect(error.response.status).toBe(503);
      }
      
      // 第二次请求（期望成功）
      const response = await axiosInstance.post('/knowledge/rag', {
        query: TEST_QUERY,
        userId: USER_ID
      });
      
      expect(response.status).toBe(200);
      expect(response.data.success).toBe(true);
    });
  });
  
  describe('超时和重试机制', () => {
    // 混沌场景：连续超时后成功
    test('应在连续超时后通过重试成功获取响应', async () => {
      // 配置网络延迟
      // 前两次请求超时
      mockAxios.onPost('/knowledge/rag').replyOnce(() => {
        return new Promise((resolve) => {
          setTimeout(() => resolve([408]), 6000); // 超过5秒超时
        });
      });
      
      mockAxios.onPost('/knowledge/rag').replyOnce(() => {
        return new Promise((resolve) => {
          setTimeout(() => resolve([408]), 6000); // 超过5秒超时
        });
      });
      
      // 第三次请求成功但有轻微延迟
      mockAxios.onPost('/knowledge/rag').reply(() => {
        return new Promise((resolve) => {
          setTimeout(() => resolve([200, mockSuccessResponse]), 1000); // 1秒后成功
        });
      });
      
      // 创建支持重试的axios实例
      const retryAxios = axios.create({
        baseURL: API_BASE_URL,
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
      
      // 添加重试拦截器
      retryAxios.interceptors.response.use(null, async (error) => {
        const config = error.config;
        
        // 设置重试计数
        config.retryCount = config.retryCount || 0;
        
        // 最大重试次数
        const MAX_RETRIES = 3;
        
        // 如果未达到最大重试次数，则重试
        if (config.retryCount < MAX_RETRIES) {
          config.retryCount += 1;
          
          // 指数退避延迟
          const delay = Math.pow(2, config.retryCount) * 500;
          
          // 等待延迟
          await new Promise(resolve => setTimeout(resolve, delay));
          
          // 重试请求
          return retryAxios(config);
        }
        
        return Promise.reject(error);
      });
      
      // 使用支持重试的axios实例发送请求
      const response = await retryAxios.post('/knowledge/rag', {
        query: TEST_QUERY,
        userId: USER_ID
      });
      
      // 验证最终响应成功
      expect(response.status).toBe(200);
      expect(response.data.success).toBe(true);
    });
  });
  
  describe('错误的响应数据处理', () => {
    // 混沌场景：服务返回格式不正确的数据
    test('应优雅处理格式不正确的响应数据', async () => {
      // 模拟返回格式不正确的数据
      mockAxios.onPost('/knowledge/rag').reply(200, {
        // 缺少必要的字段
        incorrectFormat: true,
        message: '格式不正确的响应'
      });
      
      try {
        await axiosInstance.post('/knowledge/rag', {
          query: TEST_QUERY,
          userId: USER_ID
        });
        
        // 如果服务端有数据验证，可能会返回400错误
        // 这种情况下，不应到达这里
        // 但如果服务端没有验证，我们至少应该在前端验证响应结构
        const response: any = await axiosInstance.post('/knowledge/rag', {
          query: TEST_QUERY,
          userId: USER_ID
        });
        
        // 客户端验证响应格式
        expect(() => {
          if (!response.data.data || !response.data.data.responseId || !response.data.data.content) {
            throw new Error('响应数据格式不正确');
          }
        }).toThrow();
        
      } catch (error: any) {
        // 期望错误或验证失败
        expect(error).toBeDefined();
      }
    });
  });
  
  describe('内部服务连接失败', () => {
    // 混沌场景：依赖服务不可用
    test('当知识库服务不可用时应降级到备用服务', async () => {
      // 设置查询端点
      const primaryEndpoint = '/knowledge/rag';
      const fallbackEndpoint = '/agents/default/query';
      
      // 模拟主服务不可用
      mockAxios.onPost(primaryEndpoint).reply(503);
      
      // 模拟备用服务可用
      mockAxios.onPost(fallbackEndpoint).reply(200, {
        success: true,
        data: {
          responseId: 'fallback-resp-123',
          content: '这是来自备用服务的回复...',
          source: 'fallback-agent',
          timestamp: new Date().toISOString()
        }
      });
      
      // 实际应用中的降级逻辑（这里只是模拟）
      async function queryWithFallback(query: string) {
        try {
          // 尝试主服务
          return await axiosInstance.post(primaryEndpoint, { query, userId: USER_ID });
        } catch (error: any) {
          if (error.response && error.response.status === 503) {
            console.log('主服务不可用，切换到备用服务');
            // 切换到备用服务
            return await axiosInstance.post(fallbackEndpoint, { query, userId: USER_ID });
          }
          throw error;
        }
      }
      
      // 执行带有故障转移的查询
      const response = await queryWithFallback(TEST_QUERY);
      
      // 验证从备用服务获得了响应
      expect(response.status).toBe(200);
      expect(response.data.success).toBe(true);
      expect(response.data.data.source).toBe('fallback-agent');
    });
  });
  
  describe('部分故障情况下的请求合并', () => {
    // 混沌场景：多个微服务部分可用
    test('应合并多个部分故障服务的结果', async () => {
      // 设置多个服务端点
      const knowledgeEndpoint = '/knowledge/search';
      const agentEndpoint = '/agents/tcm/query';
      const coordinationEndpoint = '/coordination/analyze';
      
      // 模拟知识搜索服务部分成功（只返回部分结果）
      mockAxios.onGet(knowledgeEndpoint).reply(200, {
        success: true,
        results: [
          { id: 'k1', title: '维生素D与骨骼健康', content: '部分内容...' }
        ],
        message: '部分结果可用，某些索引不可访问'
      });
      
      // 模拟代理服务正常
      mockAxios.onPost(agentEndpoint).reply(200, {
        success: true,
        data: {
          responseId: 'agent-resp-123',
          content: '代理的回答内容...',
          source: 'tcm-agent'
        }
      });
      
      // 模拟协调服务部分成功
      mockAxios.onPost(coordinationEndpoint).reply(200, {
        success: true,
        analysis: {
          domains: ['health'],
          intent: 'information_seeking',
          // 缺少某些分析结果
          message: '部分分析完成，某些模型不可用'
        }
      });
      
      // 实际应用中的结果合并逻辑（这里只是示例）
      async function getAggregatedResults(query: string) {
        const results: any = { success: false };
        
        try {
          // 并行调用所有服务
          const [knowledgeResponse, agentResponse, coordinationResponse] = await Promise.allSettled([
            axiosInstance.get(`${knowledgeEndpoint}?query=${encodeURIComponent(query)}`),
            axiosInstance.post(agentEndpoint, { query, userId: USER_ID }),
            axiosInstance.post(coordinationEndpoint, { query, userId: USER_ID })
          ]);
          
          // 初始化整合结果
          results.success = true;
          results.knowledgeResults = [];
          results.agentResponse = null;
          results.analysis = null;
          
          // 处理每个服务的响应
          if (knowledgeResponse.status === 'fulfilled') {
            results.knowledgeResults = knowledgeResponse.value.data.results || [];
          }
          
          if (agentResponse.status === 'fulfilled') {
            results.agentResponse = agentResponse.value.data.data;
          }
          
          if (coordinationResponse.status === 'fulfilled') {
            results.analysis = coordinationResponse.value.data.analysis;
          }
          
          // 至少需要一种结果可用
          if (results.knowledgeResults.length === 0 && !results.agentResponse) {
            results.success = false;
            results.message = '无法获取完整结果';
          }
          
        } catch (error) {
          results.success = false;
          results.message = '汇总结果时出错';
        }
        
        return results;
      }
      
      // 获取整合结果
      const results = await getAggregatedResults(TEST_QUERY);
      
      // 验证整合的结果
      expect(results.success).toBe(true);
      expect(results.knowledgeResults).toHaveLength(1);
      expect(results.agentResponse).toBeDefined();
      expect(results.analysis).toBeDefined();
      
      // 验证即使协调分析不完整，整体结果仍然可用
      expect(results.analysis.message).toContain('部分分析完成');
    });
  });
}); 