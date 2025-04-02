import axios from 'axios';
import { agentServiceProvider, setupPactInteraction } from './pact-setup';
import { Matchers } from '@pact-foundation/pact';
const { like, eachLike, term, regex } = Matchers;

// 基础URL配置
const API_BASE_URL = 'http://localhost:8080'; // Pact服务器地址

// 配置Axios实例
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer test-token'
  }
});

// 使用Pact模拟TCM代理服务API
describe('代理协调服务 -> TCM代理服务 契约测试', () => {
  
  // 在所有测试前启动Pact服务器
  beforeAll(() => agentServiceProvider.setup());
  
  // 在所有测试后验证交互并关闭Pact服务器
  afterAll(() => agentServiceProvider.finalize());
  
  // 每个测试后验证交互，但不停止服务器
  afterEach(() => agentServiceProvider.verify());
  
  describe('查询代理', () => {
    
    // 定义交互
    beforeEach(() => {
      const interaction = {
        state: '代理存在且可响应查询',
        uponReceiving: '从代理协调服务发送的查询请求',
        withRequest: {
          method: 'POST',
          path: '/api/query',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': like('Bearer test-token')
          },
          body: {
            query: like('中医如何看待维生素D的重要性?'),
            sessionId: regex('\\w{8}-\\w{4}-\\w{4}-\\w{4}-\\w{12}', 'session-123'),
            context: {
              userId: like('user-123'),
              previousResponses: eachLike({
                responseId: like('resp-123'),
                content: like('先前的回复内容'),
                timestamp: term({
                  matcher: '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3}Z',
                  generate: '2023-05-15T08:12:34.567Z'
                })
              }, { min: 0 })
            }
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            responseId: regex('\\w{8}-\\w{4}-\\w{4}-\\w{4}-\\w{12}', 'resp-456'),
            content: like('维生素D在中医理论中被视为与"阳气"相关的重要物质...'),
            source: like('tcm-agent'),
            timestamp: term({
              matcher: '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3}Z',
              generate: '2023-05-15T08:15:34.567Z'
            }),
            references: eachLike({
              title: like('中医营养学概论'),
              url: like('https://example.com/tcm-nutrition'),
              snippet: like('维生素D被视为现代营养元素中与中医"阳气"最为相关的物质之一...')
            }, { min: 0 })
          }
        }
      };
      
      return setupPactInteraction(agentServiceProvider, interaction);
    });
    
    // 测试契约
    test('应成功发送查询并接收回复', async () => {
      const sessionId = 'session-123';
      const queryText = '中医如何看待维生素D的重要性?';
      
      try {
        const response = await axiosInstance.post('/api/query', {
          query: queryText,
          sessionId,
          context: {
            userId: 'user-123',
            previousResponses: []
          }
        });
        
        // 验证响应结构
        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('responseId');
        expect(response.data).toHaveProperty('content');
        expect(response.data).toHaveProperty('source');
        expect(response.data).toHaveProperty('timestamp');
        
        // 可选：验证响应内容(仅用于调试，不要依赖于特定的响应内容)
        if (process.env.DEBUG === 'true') {
          console.log('代理服务响应:', response.data);
        }
        
      } catch (error) {
        console.error('代理服务查询失败:', error);
        throw error;
      }
    });
  });
  
  describe('检查代理健康状态', () => {
    
    // 定义交互
    beforeEach(() => {
      const interaction = {
        state: '代理服务健康',
        uponReceiving: '健康检查请求',
        withRequest: {
          method: 'GET',
          path: '/health',
          headers: {
            'Authorization': like('Bearer test-token')
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            status: like('ok'),
            version: like('1.0.0'),
            timestamp: term({
              matcher: '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3}Z',
              generate: '2023-05-15T08:15:34.567Z'
            })
          }
        }
      };
      
      return setupPactInteraction(agentServiceProvider, interaction);
    });
    
    // 测试契约
    test('应成功检查代理健康状态', async () => {
      try {
        const response = await axiosInstance.get('/health');
        
        // 验证响应
        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('status', 'ok');
        expect(response.data).toHaveProperty('version');
        expect(response.data).toHaveProperty('timestamp');
        
      } catch (error) {
        console.error('健康检查失败:', error);
        throw error;
      }
    });
  });
  
  describe('检查代理能力', () => {
    
    // 定义交互
    beforeEach(() => {
      const interaction = {
        state: '代理存在并具有特定能力',
        uponReceiving: '检查代理能力请求',
        withRequest: {
          method: 'GET',
          path: '/api/capabilities',
          query: {
            detail: 'true'
          },
          headers: {
            'Authorization': like('Bearer test-token')
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            capabilities: eachLike({
              id: like('tcm_knowledge'),
              name: like('中医知识'),
              description: like('能够回答关于中医理论、诊断和治疗方法的问题'),
              confidenceLevel: term({
                matcher: '^(1\\.0|0\\.\\d+)$',
                generate: '0.95'
              })
            }, { min: 1 })
          }
        }
      };
      
      return setupPactInteraction(agentServiceProvider, interaction);
    });
    
    // 测试契约
    test('应成功获取代理能力列表', async () => {
      try {
        const response = await axiosInstance.get('/api/capabilities?detail=true');
        
        // 验证响应
        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('capabilities');
        expect(Array.isArray(response.data.capabilities)).toBe(true);
        expect(response.data.capabilities.length).toBeGreaterThan(0);
        
        // 验证第一个能力的结构
        const firstCapability = response.data.capabilities[0];
        expect(firstCapability).toHaveProperty('id');
        expect(firstCapability).toHaveProperty('name');
        expect(firstCapability).toHaveProperty('description');
        expect(firstCapability).toHaveProperty('confidenceLevel');
        
      } catch (error) {
        console.error('获取代理能力失败:', error);
        throw error;
      }
    });
  });
}); 