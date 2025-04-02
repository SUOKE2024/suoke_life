/**
 * 服务集成测试
 * 测试用户服务与知识库服务、知识图谱服务的集成
 */
const { describe, it, beforeAll, afterAll, beforeEach, afterEach, expect, jest } = require('@jest/globals');
const axios = require('axios');
const nock = require('nock');
const { v4: uuidv4 } = require('uuid');
const { recommendationService, knowledgePreferenceService } = require('../../services');
const { knowledgePreferenceRepository } = require('../../repositories');
const config = require('../../config');

// 模拟依赖
jest.mock('../../repositories');
jest.mock('../../utils/logger');

// 测试辅助函数
const setupMockServices = () => {
  // 清除所有注册的nock拦截器
  nock.cleanAll();
  
  // 模拟知识库服务
  const knowledgeBaseUrl = new URL(config.knowledgeBaseUrl).origin;
  const knowledgeBasePath = new URL(config.knowledgeBaseUrl).pathname;
  
  nock(knowledgeBaseUrl)
    .get(`${knowledgeBasePath}/content`)
    .query(true)
    .reply(200, [
      {
        id: 'content-1',
        title: '中医基础理论',
        domain: '中医药',
        type: '文章',
        difficultyLevel: '中级',
        summary: '中医基础理论概述',
        tags: ['中医', '理论', '基础'],
        updatedAt: new Date().toISOString()
      },
      {
        id: 'content-2',
        title: '四季养生指南',
        domain: '养生保健',
        type: '视频',
        difficultyLevel: '初级',
        summary: '四季养生方法介绍',
        tags: ['养生', '四季', '保健'],
        updatedAt: new Date().toISOString()
      }
    ]);
  
  nock(knowledgeBaseUrl)
    .post(`${knowledgeBasePath}/content/details`)
    .reply(200, [
      {
        id: 'content-1',
        title: '中医基础理论',
        domain: '中医药',
        type: '文章',
        difficultyLevel: '中级',
        content: '中医基础理论详细内容...',
        author: '张三',
        publishedAt: new Date().toISOString(),
        tags: ['中医', '理论', '基础'],
        relatedNodes: ['node-1', 'node-2']
      }
    ]);
  
  // 模拟知识图谱服务
  const knowledgeGraphUrl = new URL(config.knowledgeGraphUrl).origin;
  const knowledgeGraphPath = new URL(config.knowledgeGraphUrl).pathname;
  
  nock(knowledgeGraphUrl)
    .post(`${knowledgeGraphPath}/query`)
    .reply(200, {
      nodes: [
        {
          id: 'node-1',
          type: 'TCMConcept',
          name: '阴阳学说',
          properties: {
            description: '阴阳学说是中医理论的核心概念之一'
          }
        },
        {
          id: 'node-2',
          type: 'TCMConcept',
          name: '五行学说',
          properties: {
            description: '五行学说是中医理论的基础概念之一'
          }
        }
      ],
      relationships: [
        {
          source: 'node-1',
          target: 'node-2',
          type: 'RELATED_TO',
          properties: {
            description: '阴阳学说与五行学说相互关联'
          }
        }
      ]
    });
};

describe('服务集成测试', () => {
  beforeAll(() => {
    // 确保axios请求不会实际发出
    nock.disableNetConnect();
    // 允许与Jest服务器的连接
    nock.enableNetConnect('127.0.0.1');
  });
  
  afterAll(() => {
    // 恢复正常的网络行为
    nock.enableNetConnect();
    nock.cleanAll();
  });
  
  beforeEach(() => {
    jest.clearAllMocks();
    setupMockServices();
  });
  
  afterEach(() => {
    nock.cleanAll();
  });
  
  describe('知识库服务集成', () => {
    it('应能获取推荐内容', async () => {
      // 准备
      const userId = uuidv4();
      const userPreferences = {
        domains: ['中医药', '养生保健'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      // 模拟存储库响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(userPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue([]);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue([]);
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue([]);
      
      // 执行
      const result = await recommendationService.getRecommendedContent(userId, { limit: 5 });
      
      // 验证
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('id');
      expect(result[0]).toHaveProperty('title');
      expect(result[0]).toHaveProperty('domain');
      expect(result[0]).toHaveProperty('score');
    });
    
    it('应能获取内容详情', async () => {
      // 模拟axios响应
      const mockLLMResponse = {
        data: {
          recommendations: [
            { contentId: 'content-1', reason: '基于您的兴趣推荐' }
          ]
        }
      };
      
      // 创建一个假的axios.post实现
      const originalPost = axios.post;
      axios.post = jest.fn()
        .mockResolvedValueOnce(mockLLMResponse) // 第一次调用返回LLM推荐
        .mockImplementationOnce((url) => {
          // 第二次调用是获取内容详情
          if (url.includes('/content/details')) {
            return Promise.resolve({ 
              data: [
                {
                  id: 'content-1',
                  title: '中医基础理论',
                  domain: '中医药'
                }
              ] 
            });
          }
          return originalPost(url);
        });
      
      // 准备
      const userId = uuidv4();
      const userPreferences = {
        domains: ['中医药'],
        contentTypes: ['文章'],
        difficultyLevel: '中级'
      };
      
      // 模拟存储库响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(userPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue([]);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue([]);
      
      // 执行
      const result = await recommendationService.getLLMRecommendedContent(userId, { limit: 1 });
      
      // 验证
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('id', 'content-1');
      expect(result[0]).toHaveProperty('title', '中医基础理论');
      expect(result[0]).toHaveProperty('domain', '中医药');
      expect(result[0]).toHaveProperty('recommendationReason');
      
      // 恢复axios.post
      axios.post = originalPost;
    });
  });
  
  describe('知识图谱服务集成', () => {
    it('应能记录知识图谱交互并返回交互历史', async () => {
      // 准备
      const userId = uuidv4();
      const interactionData = {
        nodeId: 'node-1',
        nodeType: 'TCMConcept',
        interactionType: '查询',
        details: '查询阴阳学说的详细信息'
      };
      
      // 模拟存储库方法
      knowledgePreferenceRepository.recordKnowledgeGraphInteraction.mockResolvedValue(true);
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue([
        {
          nodeId: 'node-1',
          nodeType: 'TCMConcept',
          interactionType: '查询',
          interactedAt: new Date()
        }
      ]);
      
      // 执行
      const recordResult = await knowledgePreferenceService.recordKnowledgeGraphInteraction(userId, interactionData);
      const historyResult = await knowledgePreferenceService.getUserKnowledgeGraphInteractions(userId, 10, 0);
      
      // 验证
      expect(recordResult).toBe(true);
      expect(historyResult.length).toBeGreaterThan(0);
      expect(historyResult[0]).toHaveProperty('nodeId', 'node-1');
      expect(historyResult[0]).toHaveProperty('interactionType', '查询');
    });
  });
});