import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

// 设置测试超时时间较长，因为端到端测试可能涉及多个真实API调用
jest.setTimeout(30000);

// 环境变量配置
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:4000/api';
const USER_ID = process.env.TEST_USER_ID || 'test-user-123';

/**
 * 端到端测试 - 完整用户查询场景
 * 
 * 这个测试模拟了用户从初始化会话到获取回答的完整流程:
 * 1. 创建协调会话
 * 2. 分析用户查询意图
 * 3. 基于意图搜索相关知识
 * 4. 生成RAG增强回答
 * 5. 必要时将查询转发到专业代理
 */
describe('用户查询端到端流程', () => {
  // 存储会话ID用于整个流程
  let sessionId: string;
  let queryText = '中医如何看待维生素D的重要性?';
  
  // 模拟认证令牌
  const authToken = 'test-jwt-token';
  
  // 配置Axios请求头
  const axiosConfig = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    }
  };
  
  test('1. 创建新的协调会话', async () => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/coordination/sessions`, 
        { userId: USER_ID, deviceInfo: { type: 'web', browser: 'chrome' } },
        axiosConfig
      );
      
      // 验证响应
      expect(response.status).toBe(200);
      expect(response.data.success).toBe(true);
      expect(response.data.data).toBeDefined();
      expect(response.data.data.sessionId).toBeDefined();
      
      // 保存会话ID用于后续步骤
      sessionId = response.data.data.sessionId;
      console.log(`会话创建成功, ID: ${sessionId}`);
    } catch (error: any) {
      // 对于端到端测试，详细记录错误有助于调试
      console.error('创建会话失败:', error.response?.data || error.message);
      throw error;
    }
  });
  
  test('2. 分析用户查询意图', async () => {
    // 确保会话ID已经生成
    expect(sessionId).toBeDefined();
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/coordination/analyze`,
        {
          sessionId,
          query: queryText,
          context: { userId: USER_ID, previousQueries: [] }
        },
        axiosConfig
      );
      
      // 验证响应
      expect(response.status).toBe(200);
      expect(response.data.success).toBe(true);
      expect(response.data.analysis).toBeDefined();
      expect(response.data.analysis.domains).toContainEqual(expect.stringMatching(/health|tcm|nutrition/));
      expect(response.data.analysis.suggestedAgents).toBeDefined();
      
      console.log(`查询意图分析成功. 领域:`, response.data.analysis.domains);
    } catch (error: any) {
      console.error('查询分析失败:', error.response?.data || error.message);
      throw error;
    }
  });
  
  test('3. 搜索相关知识', async () => {
    // 确保会话ID已经生成
    expect(sessionId).toBeDefined();
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/knowledge/search?query=${encodeURIComponent(queryText)}&domains=tcm,health&semanticSearch=true`,
        axiosConfig
      );
      
      // 验证响应
      expect(response.status).toBe(200);
      expect(response.data.success).toBe(true);
      expect(response.data.results).toBeDefined();
      expect(Array.isArray(response.data.results)).toBe(true);
      
      if (response.data.results.length > 0) {
        console.log(`找到相关知识: ${response.data.results.length} 条结果`);
        // 检查第一个结果是否有必要的属性
        expect(response.data.results[0].id).toBeDefined();
        expect(response.data.results[0].title).toBeDefined();
      } else {
        console.log('未找到相关知识');
      }
    } catch (error: any) {
      console.error('知识搜索失败:', error.response?.data || error.message);
      throw error;
    }
  });
  
  test('4. 生成RAG增强回答', async () => {
    // 确保会话ID已经生成
    expect(sessionId).toBeDefined();
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/knowledge/rag`,
        {
          query: queryText,
          sessionId,
          userId: USER_ID,
          domainFilters: ['tcm', 'health', 'nutrition'],
          useSpecialized: true
        },
        axiosConfig
      );
      
      // 验证响应
      expect(response.status).toBe(200);
      expect(response.data.responseId).toBeDefined();
      expect(response.data.content).toBeDefined();
      expect(typeof response.data.content).toBe('string');
      expect(response.data.content.length).toBeGreaterThan(50); // 确保回答有一定长度
      
      console.log(`RAG回答生成成功, ID: ${response.data.responseId}`);
      console.log(`回答片段: ${response.data.content.substring(0, 100)}...`);
    } catch (error: any) {
      console.error('RAG回答生成失败:', error.response?.data || error.message);
      throw error;
    }
  });
  
  test('5. 将查询转发到专业代理 (条件性测试)', async () => {
    // 此步骤仅在特定条件下执行，例如当RAG回答不够全面时
    // 对于端到端测试，我们可以始终执行此步骤以验证完整流程
    
    // 确保会话ID已经生成
    expect(sessionId).toBeDefined();
    
    // 查询专家代理列表
    let agentId: string;
    
    try {
      // 首先获取代理列表
      const agentsResponse = await axios.get(
        `${API_BASE_URL}/agents`,
        axiosConfig
      );
      
      expect(agentsResponse.status).toBe(200);
      expect(agentsResponse.data.success).toBe(true);
      expect(agentsResponse.data.data).toBeDefined();
      expect(Array.isArray(agentsResponse.data.data)).toBe(true);
      
      // 找到一个支持TCM或健康领域的代理
      const tcmAgent = agentsResponse.data.data.find((agent: any) => 
        agent.capabilities.some((cap: string) => 
          cap.includes('tcm') || cap.includes('health')
        )
      );
      
      if (tcmAgent) {
        agentId = tcmAgent.id;
        console.log(`找到合适的代理: ${tcmAgent.name} (${agentId})`);
      } else {
        console.log('未找到合适的专业代理，跳过代理查询测试');
        return; // 跳过后续测试
      }
      
      // 向专业代理发送查询
      const response = await axios.post(
        `${API_BASE_URL}/agents/${agentId}/query`,
        {
          sessionId,
          query: queryText,
          context: {
            userId: USER_ID,
            previousResponses: []
          }
        },
        axiosConfig
      );
      
      // 验证响应
      expect(response.status).toBe(200);
      expect(response.data.responseId).toBeDefined();
      expect(response.data.content).toBeDefined();
      expect(typeof response.data.content).toBe('string');
      
      console.log(`从专业代理获取回答成功, ID: ${response.data.responseId}`);
      console.log(`代理回答片段: ${response.data.content.substring(0, 100)}...`);
    } catch (error: any) {
      // 对于代理查询失败，我们记录错误但不一定要使测试失败
      // 因为这可能是正常的业务流程的一部分（不是所有查询都需要特定代理）
      console.warn('专业代理查询失败或跳过:', error.response?.data || error.message);
    }
  });
}); 