/**
 * 推荐服务单元测试
 */
const { describe, it, beforeEach, afterEach, expect, jest } = require('@jest/globals');
const axios = require('axios');
const { recommendationService } = require('../../services');
const { knowledgePreferenceRepository, recommendationRepository } = require('../../repositories');
const { shuffleArray, calculateContentScore } = require('../../utils/algorithm');

// 模拟依赖
jest.mock('axios');
jest.mock('../../repositories');
jest.mock('../../utils/logger');
jest.mock('../../utils/algorithm', () => ({
  shuffleArray: jest.fn(arr => arr),
  calculateContentScore: jest.fn(() => 75)
}));

describe('推荐服务测试', () => {
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('getRecommendedContent', () => {
    it('应该返回基于用户偏好的推荐内容', async () => {
      // 准备
      const userId = '12345';
      const options = {
        limit: 5,
        includeHistory: false,
        domainFilter: [],
        typeFilter: []
      };
      
      const mockPreferences = {
        domains: ['中医药', '营养健康'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      const mockViewHistory = [
        { contentId: 'view-1', domain: '中医药', contentType: '文章' }
      ];
      
      const mockFavorites = [
        { contentId: 'fav-1', domain: '营养健康', contentType: '视频' }
      ];
      
      const mockGraphInteractions = [
        { nodeId: 'node-1', nodeType: '术语', interactionType: '查询' }
      ];
      
      const mockCandidateContent = [
        { id: 'content-1', domain: '中医药', type: '文章', difficultyLevel: '中级', updatedAt: new Date() },
        { id: 'content-2', domain: '营养健康', type: '视频', difficultyLevel: '初级', updatedAt: new Date() },
        { id: 'content-3', domain: '精准医疗', type: '图解', difficultyLevel: '高级', updatedAt: new Date() }
      ];
      
      // 模拟存储库和API响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(mockPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue(mockViewHistory);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue(mockFavorites);
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue(mockGraphInteractions);
      
      axios.get.mockResolvedValue({ data: mockCandidateContent });
      
      // 执行
      const result = await recommendationService.getRecommendedContent(userId, options);
      
      // 验证
      expect(knowledgePreferenceRepository.getUserPreferences).toHaveBeenCalledWith(userId);
      expect(knowledgePreferenceRepository.getUserContentViewHistory).toHaveBeenCalledWith(userId, 100, 0);
      expect(knowledgePreferenceRepository.getUserFavorites).toHaveBeenCalledWith(userId, 100, 0);
      expect(knowledgePreferenceRepository.getUserKnowledgeGraphInteractions).toHaveBeenCalledWith(userId, 100, 0);
      expect(axios.get).toHaveBeenCalled();
      expect(result).toHaveLength(3); // 所有内容都应被推荐
      expect(result[0]).toHaveProperty('score');
    });

    it('应该过滤已查看内容（当includeHistory为false时）', async () => {
      // 准备
      const userId = '12345';
      const options = {
        limit: 5,
        includeHistory: false,
        domainFilter: [],
        typeFilter: []
      };
      
      const mockPreferences = {
        domains: ['中医药', '营养健康'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      const mockViewHistory = [
        { contentId: 'content-1', domain: '中医药', contentType: '文章' }
      ];
      
      const mockFavorites = [];
      const mockGraphInteractions = [];
      
      const mockCandidateContent = [
        { id: 'content-1', domain: '中医药', type: '文章', difficultyLevel: '中级', updatedAt: new Date() },
        { id: 'content-2', domain: '营养健康', type: '视频', difficultyLevel: '初级', updatedAt: new Date() }
      ];
      
      // 模拟存储库和API响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(mockPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue(mockViewHistory);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue(mockFavorites);
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue(mockGraphInteractions);
      
      axios.get.mockResolvedValue({ data: mockCandidateContent });
      
      // 执行
      const result = await recommendationService.getRecommendedContent(userId, options);
      
      // 验证
      expect(result).toHaveLength(1); // 应该只有content-2，因为content-1已经查看过
      expect(result[0].id).toBe('content-2');
    });

    it('应该处理API失败并返回空数组', async () => {
      // 准备
      const userId = '12345';
      const options = { limit: 5 };
      
      const mockPreferences = {
        domains: ['中医药', '营养健康'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      // 模拟存储库和API响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(mockPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue([]);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue([]);
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue([]);
      
      axios.get.mockRejectedValue(new Error('API调用失败'));
      
      // 执行
      const result = await recommendationService.getRecommendedContent(userId, options);
      
      // 验证
      expect(result).toHaveLength(0); // 应该返回空数组
    });
  });

  describe('getLLMRecommendedContent', () => {
    it('应该返回基于LLM的推荐内容', async () => {
      // 准备
      const userId = '12345';
      const options = { limit: 3 };
      
      const mockPreferences = {
        domains: ['中医药', '营养健康'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      const mockViewHistory = [
        { title: '中医基础理论', domain: '中医药', contentType: '文章' }
      ];
      
      const mockFavorites = [
        { title: '健康饮食指南', domain: '营养健康', contentType: '视频' }
      ];
      
      const mockOpenAIResponse = {
        data: {
          recommendations: [
            { contentId: 'rec-1', reason: '与您的中医兴趣相关' },
            { contentId: 'rec-2', reason: '满足您的营养健康需求' }
          ]
        }
      };
      
      const mockContentDetails = [
        { id: 'rec-1', title: '中医养生指南', domain: '中医药', type: '文章' },
        { id: 'rec-2', title: '四季饮食调理', domain: '营养健康', type: '视频' }
      ];
      
      // 模拟存储库和API响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(mockPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue(mockViewHistory);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue(mockFavorites);
      
      axios.post.mockResolvedValue(mockOpenAIResponse);
      axios.get.mockResolvedValue({ data: [] }); // 基础推荐内容（回退）
      axios.post.mockResolvedValueOnce(mockOpenAIResponse).mockResolvedValueOnce({ data: mockContentDetails });
      
      // 执行
      const result = await recommendationService.getLLMRecommendedContent(userId, options);
      
      // 验证
      expect(axios.post).toHaveBeenCalledTimes(2);
      expect(result).toHaveLength(2);
      expect(result[0]).toHaveProperty('recommendationReason');
      expect(result[0].title).toBe('中医养生指南');
    });

    it('应该在LLM推荐失败时回退到基础推荐', async () => {
      // 准备
      const userId = '12345';
      const options = { limit: 3 };
      
      const mockPreferences = {
        domains: ['中医药', '营养健康'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      const mockViewHistory = [];
      const mockFavorites = [];
      const mockGraphInteractions = [];
      
      const mockCandidateContent = [
        { id: 'content-1', domain: '中医药', type: '文章', difficultyLevel: '中级', updatedAt: new Date() },
        { id: 'content-2', domain: '营养健康', type: '视频', difficultyLevel: '初级', updatedAt: new Date() }
      ];
      
      // 模拟存储库和API响应
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(mockPreferences);
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue(mockViewHistory);
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue(mockFavorites);
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue(mockGraphInteractions);
      
      axios.post.mockRejectedValue(new Error('OpenAI调用失败'));
      axios.get.mockResolvedValue({ data: mockCandidateContent });
      
      // 执行
      const result = await recommendationService.getLLMRecommendedContent(userId, options);
      
      // 验证
      expect(axios.post).toHaveBeenCalledTimes(1); // OpenAI调用
      expect(axios.get).toHaveBeenCalledTimes(1);  // 知识库服务调用（回退）
      expect(result).toHaveLength(2);
      expect(result[0].id).toBe('content-1');
    });
  });

  describe('recordRecommendationFeedback', () => {
    it('应该记录用户对推荐内容的反馈', async () => {
      // 准备
      const userId = '12345';
      const contentId = 'content-123';
      const feedbackType = 'liked';
      
      recommendationRepository.recordRecommendationFeedback.mockResolvedValue(true);
      
      // 执行
      const result = await recommendationService.recordRecommendationFeedback(userId, contentId, feedbackType);
      
      // 验证
      expect(recommendationRepository.recordRecommendationFeedback).toHaveBeenCalledWith(userId, contentId, feedbackType);
      expect(result).toBe(true);
    });

    it('应该处理存储库错误', async () => {
      // 准备
      const userId = '12345';
      const contentId = 'content-123';
      const feedbackType = 'liked';
      
      recommendationRepository.recordRecommendationFeedback.mockRejectedValue(new Error('数据库错误'));
      
      // 执行和验证
      await expect(recommendationService.recordRecommendationFeedback(userId, contentId, feedbackType))
        .rejects.toThrow('记录推荐反馈失败');
    });
  });
});